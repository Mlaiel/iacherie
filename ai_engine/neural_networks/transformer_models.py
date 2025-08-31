"""Transformer Models for IA-Influencer-Agent

Advanced transformer architectures for multi-modal content processing,
understanding, and generation for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import math
import numpy as np
from dataclasses import dataclass
from enum import Enum

from .base_networks import BaseNeuralNetwork, NetworkConfig, NetworkType


class TransformerType(Enum):
    """Transformer architecture variants"""    ENCODER_ONLY = "encoder_only"
    DECODER_ONLY = "decoder_only"
    ENCODER_DECODER = "encoder_decoder"
    MULTIMODAL = "multimodal"


@dataclass
class TransformerConfig(NetworkConfig):
    """Transformer-specific configuration"""    
    # Architecture
    num_heads: int = 8
    num_layers: int = 6
    d_model: int = 512
    d_ff: int = 2048
    max_sequence_length: int = 1024
    
    # Attention
    attention_dropout: float = 0.1
    use_rotary_embeddings: bool = True
    use_flash_attention: bool = True
    
    # Positional encoding
    positional_encoding: str = "sinusoidal"  # sinusoidal, learned, rope
    
    # Multimodal
    modalities: List[str] = None  # ["text", "audio", "image", "video"]
    cross_modal_layers: int = 2
    
    # Transformer type
    transformer_type: TransformerType = TransformerType.ENCODER_ONLY


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding"""    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * 
            -(math.log(10000.0) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


class RotaryPositionalEmbedding(nn.Module):
    """Rotary Position Embedding (RoPE)"""    
    def __init__(self, dim: int, max_position_embeddings: int = 2048):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
    
    def forward(self, x: torch.Tensor, seq_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
        t = torch.arange(seq_len, device=x.device, dtype=self.inv_freq.dtype)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        return emb.cos(), emb.sin()


class MultiHeadAttention(nn.Module):
    """Multi-head attention with optional flash attention"""    
    def __init__(
        self,
        d_model: int,
        num_heads: int,
        dropout: float = 0.1,
        use_flash_attention: bool = True
    ):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.use_flash_attention = use_flash_attention
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        batch_size, seq_len = query.size(0), query.size(1)
        
        # Linear projections
        Q = self.w_q(query).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Attention
        if self.use_flash_attention and hasattr(F, 'scaled_dot_product_attention'):
            # Use PyTorch 2.0+ optimized attention
            attn_output = F.scaled_dot_product_attention(
                Q, K, V, attn_mask=mask, dropout_p=self.dropout.p if self.training else 0.0
            )
        else:
            # Standard attention
            scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
            
            if mask is not None:
                scores = scores.masked_fill(mask == 0, -1e9)
            
            attn_weights = F.softmax(scores, dim=-1)
            attn_weights = self.dropout(attn_weights)
            attn_output = torch.matmul(attn_weights, V)
        
        # Concatenate heads
        attn_output = attn_output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.d_model
        )
        
        return self.w_o(attn_output)


class FeedForward(nn.Module):
    """Position-wise feed-forward network"""    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(self.activation(self.linear1(x))))


class TransformerLayer(nn.Module):
    """Single transformer layer"""    
    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1,
        use_flash_attention: bool = True
    ):
        super().__init__()
        
        self.self_attn = MultiHeadAttention(
            d_model, num_heads, dropout, use_flash_attention
        )
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self, 
        x: torch.Tensor, 
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        # Self-attention with residual connection
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        
        return x


class ContentTransformer(BaseNeuralNetwork):
    """    General-purpose transformer for content processing
    
    Supports text, audio features, image features, and mixed content.
    """    
    def __init__(self, config: TransformerConfig):
        super().__init__(config)
        self.config: TransformerConfig = config
        
        # Input embedding
        self.input_embedding = nn.Linear(config.input_dim, config.d_model)
        
        # Positional encoding
        if config.positional_encoding == "sinusoidal":
            self.pos_encoding = PositionalEncoding(
                config.d_model, config.max_sequence_length
            )
        elif config.positional_encoding == "learned":
            self.pos_encoding = nn.Embedding(
                config.max_sequence_length, config.d_model
            )
        elif config.positional_encoding == "rope":
            self.pos_encoding = RotaryPositionalEmbedding(config.d_model // config.num_heads)
        
        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerLayer(
                config.d_model,
                config.num_heads,
                config.d_ff,
                config.dropout_rate,
                config.use_flash_attention
            )
            for _ in range(config.num_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(config.d_model, config.output_dim)
        
        # Layer normalization
        self.layer_norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(config.dropout_rate)
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights"""        for module in self.modules():
            if isinstance(module, nn.Linear):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    torch.nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                torch.nn.init.zeros_(module.bias)
                torch.nn.init.ones_(module.weight)
    
    def forward(
        self, 
        x: torch.Tensor, 
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        # Input embedding
        x = self.input_embedding(x)
        
        # Add positional encoding
        if self.config.positional_encoding == "learned":
            seq_len = x.size(1)
            positions = torch.arange(seq_len, device=x.device)
            pos_emb = self.pos_encoding(positions).unsqueeze(0)
            x = x + pos_emb
        elif self.config.positional_encoding == "sinusoidal":
            x = self.pos_encoding(x)
        # RoPE is applied in attention layers
        
        x = self.dropout(x)
        
        # Apply transformer layers
        for layer in self.layers:
            x = layer(x, mask)
        
        x = self.layer_norm(x)
        
        # Output projection
        output = self.output_projection(x)
        
        return output
    
    def compute_loss(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """Compute appropriate loss based on task"""        
        if self.config.output_dim == 1:
            # Regression task
            return F.mse_loss(predictions.squeeze(), targets.squeeze())
        else:
            # Classification or multi-output task
            if len(targets.shape) == len(predictions.shape) - 1:
                # Cross-entropy classification
                return F.cross_entropy(
                    predictions.view(-1, predictions.size(-1)),
                    targets.view(-1)
                )
            else:
                # Multi-label or regression
                return F.mse_loss(predictions, targets)


class MultiModalTransformer(BaseNeuralNetwork):
    """    Multi-modal transformer for processing different content types
    
    Handles audio, text, image, and video features simultaneously.
    """    
    def __init__(self, config: TransformerConfig):
        super().__init__(config)
        self.config: TransformerConfig = config
        
        if not config.modalities:
            config.modalities = ["text", "audio", "image"]
        
        self.modalities = config.modalities
        
        # Modality-specific encoders
        self.modality_encoders = nn.ModuleDict()
        
        for modality in self.modalities:
            if modality == "text":
                self.modality_encoders[modality] = nn.Sequential(
                    nn.Linear(config.input_dim, config.d_model),
                    nn.LayerNorm(config.d_model),
                    nn.Dropout(config.dropout_rate)
                )
            elif modality == "audio":
                self.modality_encoders[modality] = nn.Sequential(
                    nn.Linear(config.input_dim, config.d_model),
                    nn.LayerNorm(config.d_model),
                    nn.Dropout(config.dropout_rate)
                )
            elif modality == "image":
                self.modality_encoders[modality] = nn.Sequential(
                    nn.Linear(config.input_dim, config.d_model),
                    nn.LayerNorm(config.d_model),
                    nn.Dropout(config.dropout_rate)
                )
            elif modality == "video":
                self.modality_encoders[modality] = nn.Sequential(
                    nn.Linear(config.input_dim, config.d_model),
                    nn.LayerNorm(config.d_model),
                    nn.Dropout(config.dropout_rate)
                )
        
        # Modality embeddings
        self.modality_embeddings = nn.Embedding(len(self.modalities), config.d_model)
        
        # Position encoding
        self.pos_encoding = PositionalEncoding(config.d_model, config.max_sequence_length)
        
        # Cross-modal attention layers
        self.cross_modal_layers = nn.ModuleList([
            TransformerLayer(
                config.d_model,
                config.num_heads,
                config.d_ff,
                config.dropout_rate,
                config.use_flash_attention
            )
            for _ in range(config.cross_modal_layers)
        ])
        
        # Self-attention layers
        self.self_attn_layers = nn.ModuleList([
            TransformerLayer(
                config.d_model,
                config.num_heads,
                config.d_ff,
                config.dropout_rate,
                config.use_flash_attention
            )
            for _ in range(config.num_layers)
        ])
        
        # Fusion layer
        self.fusion_layer = nn.MultiheadAttention(
            config.d_model, 
            config.num_heads,
            dropout=config.dropout_rate,
            batch_first=True
        )
        
        # Output projection
        self.output_projection = nn.Linear(config.d_model, config.output_dim)
        
        self.layer_norm = nn.LayerNorm(config.d_model)
        self.dropout = nn.Dropout(config.dropout_rate)
    
    def forward(
        self,
        inputs: Dict[str, torch.Tensor],
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        encoded_modalities = []
        
        # Process each modality
        for i, (modality, data) in enumerate(inputs.items()):
            if modality in self.modality_encoders:
                # Encode modality-specific features
                encoded = self.modality_encoders[modality](data)
                
                # Add modality embedding
                modality_id = torch.tensor(i, device=encoded.device)
                modality_emb = self.modality_embeddings(modality_id)
                encoded = encoded + modality_emb.unsqueeze(0).unsqueeze(0)
                
                encoded_modalities.append(encoded)
        
        if not encoded_modalities:
            raise ValueError("No valid modalities provided")
        
        # Concatenate along sequence dimension
        x = torch.cat(encoded_modalities, dim=1)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        x = self.dropout(x)
        
        # Cross-modal attention
        for layer in self.cross_modal_layers:
            x = layer(x, mask)
        
        # Self-attention
        for layer in self.self_attn_layers:
            x = layer(x, mask)
        
        # Multi-modal fusion
        fused, _ = self.fusion_layer(x, x, x)
        x = x + fused
        
        x = self.layer_norm(x)
        
        # Global pooling or use [CLS] token
        if x.size(1) > 1:
            x = x.mean(dim=1)  # Average pooling
        else:
            x = x.squeeze(1)
        
        # Output projection
        output = self.output_projection(x)
        
        return output
    
    def compute_loss(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """Multi-task loss computation"""        
        if isinstance(targets, dict):
            # Multi-task learning
            total_loss = 0.0
            
            for task, target in targets.items():
                if task == "classification":
                    loss = F.cross_entropy(predictions, target)
                elif task == "regression":
                    loss = F.mse_loss(predictions, target)
                elif task == "similarity":
                    loss = F.cosine_embedding_loss(
                        predictions, target, torch.ones(predictions.size(0))
                    )
                else:
                    loss = F.mse_loss(predictions, target)
                
                total_loss += loss
            
            return total_loss
        else:
            # Single task
            return F.mse_loss(predictions, targets)


class AudioTransformer(ContentTransformer):
    """Specialized transformer for audio content processing"""    
    def __init__(self, config: TransformerConfig):
        super().__init__(config)
        
        # Audio-specific layers
        self.spectral_attention = MultiHeadAttention(
            config.d_model, config.num_heads, config.dropout_rate
        )
        
        self.temporal_attention = MultiHeadAttention(
            config.d_model, config.num_heads, config.dropout_rate
        )
        
        # Audio feature projection
        self.audio_projection = nn.Linear(config.input_dim, config.d_model)
        
    def forward(
        self,
        audio_features: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        # Project audio features
        x = self.audio_projection(audio_features)
        
        # Apply spectral attention (frequency domain)
        spectral_output = self.spectral_attention(x, x, x, mask)
        
        # Apply temporal attention (time domain)
        temporal_output = self.temporal_attention(spectral_output, spectral_output, spectral_output, mask)
        
        # Regular transformer processing
        return super().forward(temporal_output, mask)


class VideoTransformer(ContentTransformer):
    """Specialized transformer for video content processing"""    
    def __init__(self, config: TransformerConfig):
        super().__init__(config)
        
        # Video-specific processing
        self.spatial_attention = MultiHeadAttention(
            config.d_model, config.num_heads, config.dropout_rate
        )
        
        self.temporal_attention = MultiHeadAttention(
            config.d_model, config.num_heads, config.dropout_rate
        )
        
        # Frame-level processing
        self.frame_encoder = nn.Linear(config.input_dim, config.d_model)
        
    def forward(
        self,
        video_features: torch.Tensor,  # [batch, frames, features]
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        batch_size, num_frames, feature_dim = video_features.shape
        
        # Encode frame features
        x = self.frame_encoder(video_features)
        
        # Spatial attention within frames
        x = self.spatial_attention(x, x, x, mask)
        
        # Temporal attention across frames
        x = self.temporal_attention(x, x, x, mask)
        
        # Regular transformer processing
        return super().forward(x, mask)


class TextTransformer(ContentTransformer):
    """Specialized transformer for text content processing"""    
    def __init__(self, config: TransformerConfig, vocab_size: int = 50000):
        super().__init__(config)
        
        # Text-specific components
        self.vocab_size = vocab_size
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, config.d_model)
        
        # Text-specific attention patterns
        self.linguistic_attention = MultiHeadAttention(
            config.d_model, config.num_heads, config.dropout_rate
        )
        
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        
        # Token embedding
        x = self.token_embedding(input_ids)
        
        # Linguistic attention
        x = self.linguistic_attention(x, x, x, attention_mask)
        
        # Regular transformer processing
        return super().forward(x, attention_mask)


class CreatorPersonalityTransformer(MultiModalTransformer):
    """    Transformer for understanding and modeling creator personality
    
    Analyzes content patterns to understand creator style and preferences.
    """    
    def __init__(self, config: TransformerConfig):
        super().__init__(config)
        
        # Personality modeling layers
        self.style_encoder = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Linear(config.d_model // 2, config.d_model)
        )
        
        self.preference_encoder = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(), 
            nn.Linear(config.d_model // 2, config.d_model)
        )
        
        # Personality dimensions
        self.personality_projection = nn.Linear(config.d_model, 16)  # Big 5 + custom dimensions
        
    def forward(
        self,
        inputs: Dict[str, torch.Tensor],
        mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        # Get base multimodal representation
        base_output = super().forward(inputs, mask)
        
        # Extract personality features
        style_features = self.style_encoder(base_output)
        preference_features = self.preference_encoder(base_output)
        
        # Personality dimensions
        personality_scores = self.personality_projection(base_output)
        
        return {
            "content_representation": base_output,
            "style_features": style_features,
            "preference_features": preference_features,
            "personality_scores": personality_scores
        }
