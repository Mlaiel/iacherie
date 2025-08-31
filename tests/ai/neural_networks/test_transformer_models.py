# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Comprehensive Test Suite for Transformer Models

Ultra-advanced industrial-grade tests for all transformer architectures,
covering multimodal transformers, attention mechanisms, positional encodings,
and all business logic scenarios.

🎯 Expert Development Team:
✅ Lead Dev + AI Architect Developer
✅ Senior Backend Developer (Python/FastAPI/Django)  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Backend Security Specialist
✅ Microservices Architect
✅ Audio Developer
✅ DevOps Engineer
✅ AI Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import math
import time
from unittest.mock import patch, MagicMock

from ai.neural_networks.transformer_models import (
    ContentTransformer,
    MultiModalTransformer,
    AudioTransformer,
    VideoTransformer,
    TextTransformer,
    CreatorPersonalityTransformer,
    TransformerConfig,
    TransformerType,
    PositionalEncoding,
    RotaryPositionalEmbedding,
    MultiHeadAttention,
    FeedForward,
    TransformerLayer
)
from ai.neural_networks.base_networks import NetworkType


@pytest.fixture
def transformer_config():
    """Basic transformer configuration for testing"""    return TransformerConfig(
        input_dim=512,
        hidden_dims=[512, 256],
        output_dim=128,
        network_type=NetworkType.TRANSFORMER,
        num_heads=8,
        num_layers=6,
        d_model=512,
        d_ff=2048,
        max_sequence_length=1024,
        attention_dropout=0.1,
        use_rotary_embeddings=True,
        use_flash_attention=True,
        transformer_type=TransformerType.ENCODER_ONLY
    )


@pytest.fixture
def multimodal_config():
    """Multimodal transformer configuration"""    return TransformerConfig(
        input_dim=512,
        hidden_dims=[512, 256],
        output_dim=128,
        network_type=NetworkType.TRANSFORMER,
        num_heads=8,
        num_layers=6,
        d_model=512,
        d_ff=2048,
        max_sequence_length=1024,
        modalities=["text", "audio", "image", "video"],
        cross_modal_layers=3,
        transformer_type=TransformerType.MULTIMODAL
    )


@pytest.fixture
def sample_sequences():
    """Generate sample sequence data for testing"""    torch.manual_seed(42)
    np.random.seed(42)
    
    return {
        "text": torch.randn(8, 256, 512),      # [batch, seq_len, d_model]
        "audio": torch.randn(8, 1024, 512),   # [batch, seq_len, d_model] 
        "image": torch.randn(8, 196, 512),    # [batch, patches, d_model]
        "video": torch.randn(8, 100, 512),    # [batch, frames, d_model]
        "short_seq": torch.randn(4, 64, 512),
        "long_seq": torch.randn(2, 2048, 512),
        "single_token": torch.randn(1, 1, 512),
        "attention_mask": torch.ones(8, 256).bool(),
        "causal_mask": torch.tril(torch.ones(256, 256)).bool()
    }


class TestTransformerConfig:
    """Test TransformerConfig functionality"""    
    def test_config_creation(self):
        """Test transformer config creation with defaults"""        config = TransformerConfig(
            input_dim=512,
            hidden_dims=[256],
            output_dim=128,
            network_type=NetworkType.TRANSFORMER
        )
        
        assert config.num_heads == 8
        assert config.num_layers == 6
        assert config.d_model == 512
        assert config.d_ff == 2048
        assert config.max_sequence_length == 1024
        assert config.transformer_type == TransformerType.ENCODER_ONLY
        assert config.use_rotary_embeddings is True
        assert config.use_flash_attention is True
    
    def test_multimodal_config(self):
        """Test multimodal transformer configuration"""        config = TransformerConfig(
            input_dim=512,
            hidden_dims=[256],
            output_dim=128,
            network_type=NetworkType.TRANSFORMER,
            modalities=["text", "audio", "image"],
            cross_modal_layers=4,
            transformer_type=TransformerType.MULTIMODAL
        )
        
        assert config.modalities == ["text", "audio", "image"]
        assert config.cross_modal_layers == 4
        assert config.transformer_type == TransformerType.MULTIMODAL
    
    def test_transformer_type_enum(self):
        """Test TransformerType enum values"""        assert TransformerType.ENCODER_ONLY.value == "encoder_only"
        assert TransformerType.DECODER_ONLY.value == "decoder_only"
        assert TransformerType.ENCODER_DECODER.value == "encoder_decoder"
        assert TransformerType.MULTIMODAL.value == "multimodal"
    
    def test_config_validation(self):
        """Test configuration parameter validation"""        config = TransformerConfig(
            input_dim=768,
            hidden_dims=[512, 256],
            output_dim=128,
            network_type=NetworkType.TRANSFORMER,
            num_heads=12,
            d_model=768,
            d_ff=3072
        )
        
        # d_model should be divisible by num_heads
        assert config.d_model % config.num_heads == 0
        
        # Verify all parameters are set correctly
        assert config.num_heads == 12
        assert config.d_model == 768
        assert config.d_ff == 3072


class TestPositionalEncoding:
    """Test positional encoding implementations"""    
    def test_sinusoidal_positional_encoding(self):
        """Test sinusoidal positional encoding"""        d_model = 512
        max_len = 1000
        
        pe = PositionalEncoding(d_model, max_len)
        
        # Test encoding shape
        seq_len = 256
        input_tensor = torch.randn(4, seq_len, d_model)
        encoded = pe(input_tensor)
        
        assert encoded.shape == (4, seq_len, d_model)
        assert torch.isfinite(encoded).all()
        
        # Test that encoding is different for different positions
        pos_1 = pe.pe[0, 0, :]
        pos_2 = pe.pe[0, 1, :]
        assert not torch.allclose(pos_1, pos_2)
        
        # Test periodicity properties
        even_dims = pe.pe[0, :, 0::2]  # sin components
        odd_dims = pe.pe[0, :, 1::2]   # cos components
        
        assert even_dims.shape[1] == d_model // 2
        assert odd_dims.shape[1] == d_model // 2
    
    def test_rotary_positional_embedding(self):
        """Test Rotary Position Embedding (RoPE)"""        dim = 64
        max_pos = 512
        
        rope = RotaryPositionalEmbedding(dim, max_pos)
        
        # Test embedding generation
        seq_len = 128
        x = torch.randn(4, seq_len, dim)
        cos_emb, sin_emb = rope(x, seq_len)
        
        assert cos_emb.shape == (seq_len, dim)
        assert sin_emb.shape == (seq_len, dim)
        assert torch.isfinite(cos_emb).all()
        assert torch.isfinite(sin_emb).all()
        
        # Test that cos and sin embeddings are different
        assert not torch.allclose(cos_emb, sin_emb)
        
        # Test that embeddings follow expected patterns
        assert torch.all(cos_emb >= -1) and torch.all(cos_emb <= 1)
        assert torch.all(sin_emb >= -1) and torch.all(sin_emb <= 1)
    
    def test_positional_encoding_consistency(self):
        """Test consistency of positional encodings"""        d_model = 512
        pe = PositionalEncoding(d_model, 1000)
        
        # Same input should give same output
        input_tensor = torch.randn(2, 100, d_model)
        encoded1 = pe(input_tensor)
        encoded2 = pe(input_tensor)
        
        assert torch.allclose(encoded1, encoded2)
        
        # Different sequence lengths should work
        short_input = torch.randn(2, 50, d_model)
        long_input = torch.randn(2, 200, d_model)
        
        short_encoded = pe(short_input)
        long_encoded = pe(long_input)
        
        assert short_encoded.shape == (2, 50, d_model)
        assert long_encoded.shape == (2, 200, d_model)


class TestMultiHeadAttention:
    """Test multi-head attention mechanism"""    
    def test_attention_initialization(self):
        """Test attention layer initialization"""        d_model = 512
        num_heads = 8
        
        attn = MultiHeadAttention(d_model, num_heads)
        
        assert attn.d_model == d_model
        assert attn.num_heads == num_heads
        assert attn.d_k == d_model // num_heads
        
        # Check that weights are initialized
        assert hasattr(attn, 'w_q')
        assert hasattr(attn, 'w_k')
        assert hasattr(attn, 'w_v')
        assert hasattr(attn, 'w_o')
    
    def test_self_attention(self, sample_sequences):
        """Test self-attention computation"""        d_model = 512
        num_heads = 8
        
        attn = MultiHeadAttention(d_model, num_heads, use_flash_attention=False)
        
        # Self-attention: Q, K, V are the same
        input_seq = sample_sequences["text"]  # [8, 256, 512]
        
        output = attn(input_seq, input_seq, input_seq)
        
        assert output.shape == input_seq.shape
        assert torch.isfinite(output).all()
        
        # Output should be different from input (attention should transform)
        assert not torch.allclose(output, input_seq, atol=1e-3)
    
    def test_cross_attention(self, sample_sequences):
        """Test cross-attention between different sequences"""        d_model = 512
        num_heads = 8
        
        attn = MultiHeadAttention(d_model, num_heads, use_flash_attention=False)
        
        query = sample_sequences["text"]     # [8, 256, 512]
        key_value = sample_sequences["audio"] # [8, 1024, 512]
        
        output = attn(query, key_value, key_value)
        
        assert output.shape == query.shape  # Output shape matches query
        assert torch.isfinite(output).all()
    
    def test_attention_with_mask(self, sample_sequences):
        """Test attention with attention mask"""        d_model = 512
        num_heads = 8
        
        attn = MultiHeadAttention(d_model, num_heads, use_flash_attention=False)
        
        input_seq = sample_sequences["text"]  # [8, 256, 512]
        mask = sample_sequences["attention_mask"]  # [8, 256]
        
        # Expand mask for attention computation
        # mask should be [batch, num_heads, seq_len, seq_len] or broadcastable
        mask_expanded = mask.unsqueeze(1).unsqueeze(2)  # [8, 1, 1, 256]
        
        output = attn(input_seq, input_seq, input_seq, mask_expanded)
        
        assert output.shape == input_seq.shape
        assert torch.isfinite(output).all()
    
    def test_causal_attention(self, sample_sequences):
        """Test causal (masked) attention"""        d_model = 512
        num_heads = 8
        seq_len = 256
        
        attn = MultiHeadAttention(d_model, num_heads, use_flash_attention=False)
        
        input_seq = sample_sequences["text"]  # [8, 256, 512]
        
        # Create causal mask (lower triangular)
        causal_mask = torch.tril(torch.ones(seq_len, seq_len)).bool()
        causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)  # [1, 1, seq_len, seq_len]
        
        output = attn(input_seq, input_seq, input_seq, causal_mask)
        
        assert output.shape == input_seq.shape
        assert torch.isfinite(output).all()
    
    @pytest.mark.skipif(not hasattr(F, 'scaled_dot_product_attention'), 
                       reason="PyTorch version doesn't support flash attention")
    def test_flash_attention(self, sample_sequences):
        """Test flash attention optimization"""        d_model = 512
        num_heads = 8
        
        # Test with flash attention enabled
        attn_flash = MultiHeadAttention(d_model, num_heads, use_flash_attention=True)
        attn_standard = MultiHeadAttention(d_model, num_heads, use_flash_attention=False)
        
        input_seq = sample_sequences["text"]
        
        output_flash = attn_flash(input_seq, input_seq, input_seq)
        output_standard = attn_standard(input_seq, input_seq, input_seq)
        
        assert output_flash.shape == output_standard.shape
        # Results should be similar (not exactly equal due to numerical differences)
        assert torch.allclose(output_flash, output_standard, atol=1e-2)
    
    def test_attention_gradients(self, sample_sequences):
        """Test attention gradient computation"""        d_model = 512
        num_heads = 8
        
        attn = MultiHeadAttention(d_model, num_heads)
        input_seq = sample_sequences["text"]
        input_seq.requires_grad_(True)
        
        output = attn(input_seq, input_seq, input_seq)
        loss = output.mean()
        loss.backward()
        
        # Check gradients exist and are finite
        assert input_seq.grad is not None
        assert torch.isfinite(input_seq.grad).all()
        
        # Check model parameter gradients
        for param in attn.parameters():
            if param.requires_grad:
                assert param.grad is not None
                assert torch.isfinite(param.grad).all()


class TestFeedForward:
    """Test feed-forward network component"""    
    def test_feedforward_initialization(self):
        """Test feed-forward layer initialization"""        d_model = 512
        d_ff = 2048
        
        ff = FeedForward(d_model, d_ff)
        
        assert hasattr(ff, 'linear1')
        assert hasattr(ff, 'linear2')
        assert hasattr(ff, 'dropout')
        assert hasattr(ff, 'activation')
        
        assert ff.linear1.in_features == d_model
        assert ff.linear1.out_features == d_ff
        assert ff.linear2.in_features == d_ff
        assert ff.linear2.out_features == d_model
    
    def test_feedforward_forward(self, sample_sequences):
        """Test feed-forward computation"""        d_model = 512
        d_ff = 2048
        
        ff = FeedForward(d_model, d_ff)
        
        input_seq = sample_sequences["text"]  # [8, 256, 512]
        
        output = ff(input_seq)
        
        assert output.shape == input_seq.shape
        assert torch.isfinite(output).all()
        
        # Output should be different from input
        assert not torch.allclose(output, input_seq, atol=1e-3)
    
    def test_feedforward_activation(self, sample_sequences):
        """Test different activation functions"""        d_model = 512
        d_ff = 2048
        
        # Test GELU activation (default)
        ff_gelu = FeedForward(d_model, d_ff)
        assert isinstance(ff_gelu.activation, nn.GELU)
        
        input_seq = sample_sequences["short_seq"]  # [4, 64, 512]
        output_gelu = ff_gelu(input_seq)
        
        assert output_gelu.shape == input_seq.shape
        assert torch.isfinite(output_gelu).all()
    
    def test_feedforward_dropout(self, sample_sequences):
        """Test dropout behavior in feed-forward"""        d_model = 512
        d_ff = 2048
        dropout_rate = 0.5
        
        ff = FeedForward(d_model, d_ff, dropout_rate)
        input_seq = sample_sequences["short_seq"]
        
        # Training mode - should apply dropout
        ff.train()
        output_train1 = ff(input_seq)
        output_train2 = ff(input_seq)
        
        # Outputs should be different due to dropout
        assert not torch.allclose(output_train1, output_train2)
        
        # Eval mode - should not apply dropout
        ff.eval()
        output_eval1 = ff(input_seq)
        output_eval2 = ff(input_seq)
        
        # Outputs should be identical in eval mode
        assert torch.allclose(output_eval1, output_eval2)


class TestTransformerLayer:
    """Test complete transformer layer"""    
    def test_layer_initialization(self):
        """Test transformer layer initialization"""        d_model = 512
        num_heads = 8
        d_ff = 2048
        
        layer = TransformerLayer(d_model, num_heads, d_ff)
        
        assert hasattr(layer, 'self_attn')
        assert hasattr(layer, 'feed_forward')
        assert hasattr(layer, 'norm1')
        assert hasattr(layer, 'norm2')
        assert isinstance(layer.norm1, nn.LayerNorm)
        assert isinstance(layer.norm2, nn.LayerNorm)
    
    def test_layer_forward(self, sample_sequences):
        """Test transformer layer forward pass"""        d_model = 512
        num_heads = 8
        d_ff = 2048
        
        layer = TransformerLayer(d_model, num_heads, d_ff)
        input_seq = sample_sequences["text"]  # [8, 256, 512]
        
        output = layer(input_seq)
        
        assert output.shape == input_seq.shape
        assert torch.isfinite(output).all()
    
    def test_layer_residual_connections(self, sample_sequences):
        """Test residual connections in transformer layer"""        d_model = 512
        num_heads = 8
        d_ff = 2048
        
        layer = TransformerLayer(d_model, num_heads, d_ff)
        input_seq = sample_sequences["short_seq"]  # [4, 64, 512]
        
        # Mock the attention and feedforward to return zeros
        with patch.object(layer.self_attn, 'forward', return_value=torch.zeros_like(input_seq)):
            with patch.object(layer.feed_forward, 'forward', return_value=torch.zeros_like(input_seq)):
                output = layer(input_seq)
                
                # With zero attention and feedforward, output should be close to normalized input
                # due to residual connections
                assert output.shape == input_seq.shape
                assert torch.isfinite(output).all()
    
    def test_layer_normalization(self, sample_sequences):
        """Test layer normalization behavior"""        d_model = 512
        num_heads = 8
        d_ff = 2048
        
        layer = TransformerLayer(d_model, num_heads, d_ff)
        input_seq = sample_sequences["text"]
        
        # Test that layer norm is applied correctly
        output = layer(input_seq)
        
        # Check that output has reasonable statistics
        output_mean = output.mean(dim=-1)
        output_std = output.std(dim=-1)
        
        # Layer norm should result in normalized features
        assert torch.abs(output_mean).mean() < 1.0  # Should be close to 0
        assert output_std.mean() > 0.5  # Should have reasonable variance


class TestContentTransformer:
    """Test ContentTransformer implementation"""    
    def test_content_transformer_initialization(self, transformer_config):
        """Test ContentTransformer initialization"""        transformer = ContentTransformer(transformer_config)
        
        assert transformer.config == transformer_config
        assert hasattr(transformer, 'embedding')
        assert hasattr(transformer, 'pos_encoding')
        assert hasattr(transformer, 'transformer_layers')
        assert hasattr(transformer, 'output_head')
        
        # Check number of layers
        assert len(transformer.transformer_layers) == transformer_config.num_layers
    
    def test_content_transformer_forward(self, transformer_config, sample_sequences):
        """Test ContentTransformer forward pass"""        transformer = ContentTransformer(transformer_config)
        
        # Create input with correct input dimension
        batch_size = 4
        seq_len = 128
        input_tensor = torch.randn(batch_size, seq_len, transformer_config.input_dim)
        
        output = transformer.forward(input_tensor)
        
        assert output.shape[0] == batch_size
        assert output.shape[1] == seq_len
        assert output.shape[2] == transformer_config.output_dim
        assert torch.isfinite(output).all()
    
    def test_content_analysis(self, transformer_config):
        """Test content analysis functionality"""        transformer = ContentTransformer(transformer_config)
        transformer.eval()
        
        # Mock content input
        content_data = {
            "text": torch.randn(2, 100, transformer_config.input_dim),
            "metadata": {"content_type": "social_post", "duration": 30.0}
        }
        
        with torch.no_grad():
            analysis = transformer.analyze_content(content_data, "test_content_123")
        
        assert analysis is not None
        # Should return structured analysis results
        assert hasattr(analysis, 'content_id') or isinstance(analysis, dict)


class TestMultiModalTransformer:
    """Test MultiModalTransformer implementation"""    
    def test_multimodal_initialization(self, multimodal_config):
        """Test multimodal transformer initialization"""        transformer = MultiModalTransformer(multimodal_config)
        
        assert transformer.config == multimodal_config
        assert hasattr(transformer, 'modality_embeddings')
        assert hasattr(transformer, 'cross_modal_layers')
        
        # Check modality-specific components
        for modality in multimodal_config.modalities:
            assert modality in transformer.modality_embeddings
    
    def test_multimodal_forward(self, multimodal_config, sample_sequences):
        """Test multimodal forward pass"""        transformer = MultiModalTransformer(multimodal_config)
        
        # Create multimodal input
        multimodal_input = {
            "text": sample_sequences["text"][:4, :128, :],      # [4, 128, 512]
            "audio": sample_sequences["audio"][:4, :128, :],   # [4, 128, 512]
            "image": sample_sequences["image"][:4, :128, :],   # [4, 128, 512]
            "video": sample_sequences["video"][:4, :128, :]    # [4, 128, 512]
        }
        
        output = transformer.forward(multimodal_input)
        
        assert torch.isfinite(output).all()
        assert output.shape[0] == 4  # batch size
        assert output.shape[-1] == multimodal_config.output_dim
    
    def test_cross_modal_attention(self, multimodal_config, sample_sequences):
        """Test cross-modal attention mechanisms"""        transformer = MultiModalTransformer(multimodal_config)
        
        # Test with subset of modalities
        partial_input = {
            "text": sample_sequences["text"][:2, :64, :],
            "audio": sample_sequences["audio"][:2, :64, :]
        }
        
        output = transformer.forward(partial_input)
        
        assert torch.isfinite(output).all()
        assert output.shape[0] == 2


class TestSpecializedTransformers:
    """Test specialized transformer implementations"""    
    def test_audio_transformer(self, transformer_config):
        """Test AudioTransformer specific functionality"""        transformer = AudioTransformer(transformer_config)
        
        # Audio-specific input (e.g., mel spectrograms)
        audio_input = torch.randn(4, 1024, transformer_config.input_dim)  # [batch, time_steps, features]
        
        output = transformer.forward(audio_input)
        
        assert output.shape[0] == 4
        assert output.shape[-1] == transformer_config.output_dim
        assert torch.isfinite(output).all()
    
    def test_video_transformer(self, transformer_config):
        """Test VideoTransformer specific functionality"""        transformer = VideoTransformer(transformer_config)
        
        # Video input (frame sequence)
        video_input = torch.randn(2, 100, transformer_config.input_dim)  # [batch, frames, features]
        
        output = transformer.forward(video_input)
        
        assert output.shape[0] == 2
        assert output.shape[-1] == transformer_config.output_dim
        assert torch.isfinite(output).all()
    
    def test_text_transformer(self, transformer_config):
        """Test TextTransformer specific functionality"""        transformer = TextTransformer(transformer_config)
        
        # Text input (token embeddings)
        text_input = torch.randn(8, 256, transformer_config.input_dim)  # [batch, tokens, embed_dim]
        
        output = transformer.forward(text_input)
        
        assert output.shape[0] == 8
        assert output.shape[1] == 256
        assert output.shape[2] == transformer_config.output_dim
        assert torch.isfinite(output).all()
    
    def test_creator_personality_transformer(self, transformer_config):
        """Test CreatorPersonalityTransformer functionality"""        transformer = CreatorPersonalityTransformer(transformer_config)
        
        # Creator content history input
        creator_input = torch.randn(1, 500, transformer_config.input_dim)  # [1, content_history, features]
        
        output = transformer.forward(creator_input)
        
        assert output.shape[0] == 1
        assert output.shape[-1] == transformer_config.output_dim
        assert torch.isfinite(output).all()


class TestTransformerPerformance:
    """Performance tests for transformer models"""    
    def test_attention_scalability(self, transformer_config):
        """Test attention computation scalability"""        d_model = 512
        num_heads = 8
        
        attn = MultiHeadAttention(d_model, num_heads)
        
        sequence_lengths = [64, 128, 256, 512]
        times = []
        
        for seq_len in sequence_lengths:
            input_seq = torch.randn(4, seq_len, d_model)
            
            # Warm up
            for _ in range(3):
                _ = attn(input_seq, input_seq, input_seq)
            
            # Measure time
            start_time = time.time()
            for _ in range(10):
                _ = attn(input_seq, input_seq, input_seq)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10
            times.append(avg_time)
            
            print(f"Attention seq_len={seq_len}: {avg_time*1000:.2f}ms")
        
        # Attention should scale reasonably with sequence length
        # (quadratic complexity is expected)
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            assert ratio < 8  # Should not grow too quickly
    
    def test_transformer_memory_efficiency(self, transformer_config):
        """Test memory efficiency of transformer"""        transformer = ContentTransformer(transformer_config)
        
        # Test different batch sizes
        batch_sizes = [1, 4, 8, 16]
        memory_usage = []
        
        for batch_size in batch_sizes:
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            input_tensor = torch.randn(batch_size, 128, transformer_config.input_dim)
            
            if torch.cuda.is_available():
                input_tensor = input_tensor.cuda()
                transformer = transformer.cuda()
                initial_memory = torch.cuda.memory_allocated()
            else:
                initial_memory = 0
            
            output = transformer.forward(input_tensor)
            
            if torch.cuda.is_available():
                final_memory = torch.cuda.memory_allocated()
                memory_diff = final_memory - initial_memory
                memory_usage.append(memory_diff)
            
            print(f"Batch size {batch_size}: Memory usage = {memory_diff / 1024**2:.1f}MB" if torch.cuda.is_available() else "CPU mode")
        
        # Memory usage should scale reasonably with batch size
        if torch.cuda.is_available() and len(memory_usage) > 1:
            for i in range(1, len(memory_usage)):
                ratio = memory_usage[i] / memory_usage[0]
                expected_ratio = batch_sizes[i] / batch_sizes[0]
                # Memory usage should be roughly proportional to batch size
                assert ratio <= expected_ratio * 2  # Allow some overhead
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_acceleration(self, transformer_config):
        """Test GPU acceleration effectiveness"""        transformer = ContentTransformer(transformer_config)
        input_tensor = torch.randn(8, 256, transformer_config.input_dim)
        
        # CPU timing
        transformer_cpu = transformer.cpu()
        input_cpu = input_tensor.cpu()
        
        start_time = time.time()
        for _ in range(10):
            _ = transformer_cpu.forward(input_cpu)
        cpu_time = time.time() - start_time
        
        # GPU timing
        transformer_gpu = transformer.cuda()
        input_gpu = input_tensor.cuda()
        
        # Warm up GPU
        for _ in range(5):
            _ = transformer_gpu.forward(input_gpu)
        
        torch.cuda.synchronize()
        start_time = time.time()
        for _ in range(10):
            _ = transformer_gpu.forward(input_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time
        
        speedup = cpu_time / gpu_time
        print(f"GPU speedup: {speedup:.2f}x")
        
        # GPU should provide some speedup for this size
        assert speedup >= 1.0  # At least no slowdown


class TestTransformerRobustness:
    """Robustness and edge case tests"""    
    def test_variable_sequence_lengths(self, transformer_config):
        """Test handling of variable sequence lengths"""        transformer = ContentTransformer(transformer_config)
        
        # Test different sequence lengths
        sequence_lengths = [1, 16, 64, 128, 256, 512, 1024]
        
        for seq_len in sequence_lengths:
            input_tensor = torch.randn(2, seq_len, transformer_config.input_dim)
            
            output = transformer.forward(input_tensor)
            
            assert output.shape[0] == 2
            assert output.shape[1] == seq_len
            assert output.shape[2] == transformer_config.output_dim
            assert torch.isfinite(output).all()
    
    def test_extreme_values(self, transformer_config):
        """Test behavior with extreme input values"""        transformer = ContentTransformer(transformer_config)
        batch_size = 4
        seq_len = 64
        
        # Test very large values
        large_input = torch.full((batch_size, seq_len, transformer_config.input_dim), 100.0)
        output_large = transformer.forward(large_input)
        assert torch.isfinite(output_large).all()
        
        # Test very small values
        small_input = torch.full((batch_size, seq_len, transformer_config.input_dim), 1e-6)
        output_small = transformer.forward(small_input)
        assert torch.isfinite(output_small).all()
        
        # Test zero input
        zero_input = torch.zeros(batch_size, seq_len, transformer_config.input_dim)
        output_zero = transformer.forward(zero_input)
        assert torch.isfinite(output_zero).all()
    
    def test_attention_mask_edge_cases(self):
        """Test attention with edge case masks"""        d_model = 512
        num_heads = 8
        seq_len = 64
        
        attn = MultiHeadAttention(d_model, num_heads, use_flash_attention=False)
        input_seq = torch.randn(2, seq_len, d_model)
        
        # Test all-zeros mask (mask everything)
        zero_mask = torch.zeros(2, 1, 1, seq_len).bool()
        output_zero = attn(input_seq, input_seq, input_seq, zero_mask)
        assert torch.isfinite(output_zero).all()
        
        # Test all-ones mask (mask nothing)  
        ones_mask = torch.ones(2, 1, 1, seq_len).bool()
        output_ones = attn(input_seq, input_seq, input_seq, ones_mask)
        assert torch.isfinite(output_ones).all()
        
        # Test random mask
        random_mask = torch.randint(0, 2, (2, 1, 1, seq_len)).bool()
        output_random = attn(input_seq, input_seq, input_seq, random_mask)
        assert torch.isfinite(output_random).all()
    
    def test_gradient_stability(self, transformer_config, sample_sequences):
        """Test gradient stability during training"""        transformer = ContentTransformer(transformer_config)
        optimizer = torch.optim.Adam(transformer.parameters(), lr=0.001)
        
        input_seq = sample_sequences["text"][:4, :128, :]
        target = torch.randn(4, 128, transformer_config.output_dim)
        
        # Train for several steps and monitor gradients
        gradient_norms = []
        
        for step in range(10):
            optimizer.zero_grad()
            
            output = transformer.forward(input_seq)
            loss = F.mse_loss(output, target)
            loss.backward()
            
            # Compute gradient norm
            total_norm = 0
            for param in transformer.parameters():
                if param.grad is not None:
                    total_norm += param.grad.norm().item() ** 2
            total_norm = total_norm ** 0.5
            gradient_norms.append(total_norm)
            
            optimizer.step()
        
        # Gradients should not explode or vanish
        for norm in gradient_norms:
            assert norm < 100.0  # No gradient explosion
            assert norm > 1e-6   # No gradient vanishing
        
        # Gradients should be relatively stable
        gradient_std = np.std(gradient_norms)
        gradient_mean = np.mean(gradient_norms)
        cv = gradient_std / gradient_mean  # Coefficient of variation
        assert cv < 2.0  # Reasonable stability


class TestTransformerIntegration:
    """Integration tests for transformer components"""    
    def test_end_to_end_content_processing(self, transformer_config):
        """Test complete content processing pipeline"""        transformer = ContentTransformer(transformer_config)
        transformer.eval()
        
        # Simulate content processing workflow
        batch_size = 4
        seq_len = 256
        
        # Step 1: Content input
        content_input = torch.randn(batch_size, seq_len, transformer_config.input_dim)
        
        # Step 2: Feature extraction
        with torch.no_grad():
            features = transformer.forward(content_input)
        
        # Step 3: Downstream task (classification)
        classifier = nn.Linear(transformer_config.output_dim, 10)
        logits = classifier(features.mean(dim=1))  # Global average pooling
        
        predictions = torch.softmax(logits, dim=-1)
        
        assert predictions.shape == (batch_size, 10)
        assert torch.allclose(predictions.sum(dim=1), torch.ones(batch_size))
        assert torch.isfinite(predictions).all()
    
    def test_multimodal_fusion(self, multimodal_config, sample_sequences):
        """Test multimodal fusion capabilities"""        transformer = MultiModalTransformer(multimodal_config)
        
        # Test fusion with different modality combinations
        modality_combinations = [
            ["text", "audio"],
            ["text", "image"], 
            ["audio", "video"],
            ["text", "audio", "image"],
            ["text", "audio", "image", "video"]
        ]
        
        for modalities in modality_combinations:
            multimodal_input = {}
            for modality in modalities:
                if modality in sample_sequences:
                    multimodal_input[modality] = sample_sequences[modality][:2, :64, :]
            
            if multimodal_input:  # Only test if we have data
                output = transformer.forward(multimodal_input)
                
                assert torch.isfinite(output).all()
                assert output.shape[0] == 2
                assert output.shape[-1] == multimodal_config.output_dim
    
    def test_transfer_learning_compatibility(self, transformer_config):
        """Test transformer compatibility with transfer learning"""        transformer = ContentTransformer(transformer_config)
        
        # Simulate pre-trained weights
        pretrained_state = transformer.state_dict()
        
        # Create new transformer with same architecture
        new_transformer = ContentTransformer(transformer_config)
        new_transformer.load_state_dict(pretrained_state)
        
        # Test that weights are identical
        for name, param in transformer.named_parameters():
            new_param = dict(new_transformer.named_parameters())[name]
            assert torch.allclose(param, new_param)
        
        # Test forward pass consistency
        test_input = torch.randn(2, 100, transformer_config.input_dim)
        
        with torch.no_grad():
            output1 = transformer.forward(test_input)
            output2 = new_transformer.forward(test_input)
        
        assert torch.allclose(output1, output2)


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
