"""🚀 Multimodal Feature Fusion - IA Influencer Agent Platform Enterprise
====================================================================== 
Module: backend/ml/feature_stores/multimodal_feature_fusion.py
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer + Lead Dev IA
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 FUSION DE CARACTÉRISTIQUES MULTIMODALES
Fusion intelligente de caractéristiques audio, vidéo, image et texte
- Cross-modal feature alignment
- Attention-based fusion mechanisms  
- Creator-specific multimodal models
- Real-time feature synchronization
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torchaudio
import torchvision
import transformers
from transformers import AutoTokenizer, AutoModel
import cv2
import librosa
from PIL import Image
import spacy

# Configuration
logger = logging.getLogger(__name__)

class ModalityType(Enum):
    """Types de modalités"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"

class CreatorType(Enum):
    """Types de créateurs"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class FusionStrategy(Enum):
    """Stratégies de fusion"""
    EARLY_FUSION = "early_fusion"
    LATE_FUSION = "late_fusion"
    CROSS_ATTENTION = "cross_attention"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"

@dataclass
class ModalityFeatures:
    """Features d'une modalité"""
    modality: ModalityType
    features: np.ndarray
    timestamp: datetime
    creator_type: CreatorType
    content_id: str
    
    # Metadata spécifique à la modalité
    sample_rate: Optional[int] = None  # Audio
    fps: Optional[float] = None  # Video
    resolution: Optional[Tuple[int, int]] = None  # Image/Video
    language: Optional[str] = None  # Text
    duration_ms: Optional[int] = None
    
    # Quality metrics
    quality_score: float = 1.0
    confidence_score: float = 1.0
    noise_level: float = 0.0

@dataclass 
class FusedFeatures:
    """Features fusionnées"""
    content_id: str
    creator_type: CreatorType
    fusion_strategy: FusionStrategy
    fused_features: np.ndarray
    
    # Individual modality features
    modality_features: Dict[ModalityType, ModalityFeatures]
    
    # Fusion metadata
    fusion_weights: Dict[ModalityType, float]
    attention_scores: Optional[np.ndarray] = None
    synchronization_offset_ms: Dict[ModalityType, float] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)

class CrossModalAttention(nn.Module):
    """Module d'attention croisée entre modalités"""
    
    def __init__(self, feature_dim -> None: int, num_heads -> None: int = 8) -> None:
        super().__init__()
        self.feature_dim = feature_dim
        self.num_heads = num_heads
        self.head_dim = feature_dim // num_heads
        
        self.query_proj = nn.Linear(feature_dim, feature_dim)
        self.key_proj = nn.Linear(feature_dim, feature_dim)
        self.value_proj = nn.Linear(feature_dim, feature_dim)
        
        self.attention_dropout = nn.Dropout(0.1)
        self.output_proj = nn.Linear(feature_dim, feature_dim)
        
    def forward(self, query_features: torch.Tensor, 
                key_features: torch.Tensor,
                value_features: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            query_features: [batch_size, seq_len, feature_dim]
            key_features: [batch_size, seq_len, feature_dim]  
            value_features: [batch_size, seq_len, feature_dim]
        """
        batch_size, seq_len, _ = query_features.shape
        
        # Project to query, key, value
        Q = self.query_proj(query_features)
        K = self.key_proj(key_features)
        V = self.value_proj(value_features)
        
        # Reshape for multi-head attention
        Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        attention_scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.head_dim)
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.attention_dropout(attention_weights)
        
        # Apply attention to values
        attended_values = torch.matmul(attention_weights, V)
        
        # Reshape and project output
        attended_values = attended_values.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.feature_dim
        )
        output = self.output_proj(attended_values)
        
        return output, attention_weights.mean(dim=1)  # Average attention across heads

class MultimodalFusionNetwork(nn.Module):
    """Réseau de fusion multimodale adaptatif"""
    
    def __init__(self, 
                 modality_dims -> None: Dict[ModalityType, int],
                 fusion_dim -> None: int = 512,
                 creator_embedding_dim -> None: int = 64) -> None:
        super().__init__()
        
        self.modality_dims = modality_dims
        self.fusion_dim = fusion_dim
        self.creator_embedding_dim = creator_embedding_dim
        
        # Encoders pour chaque modalité
        self.modality_encoders = nn.ModuleDict()
        for modality, input_dim in modality_dims.items():
            self.modality_encoders[modality.value] = nn.Sequential(
                nn.Linear(input_dim, fusion_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(fusion_dim, fusion_dim),
                nn.LayerNorm(fusion_dim)
            )
        
        # Creator type embeddings
        self.creator_embeddings = nn.Embedding(5, creator_embedding_dim)  # 5 creator types
        
        # Cross-modal attention
        self.cross_attention = CrossModalAttention(fusion_dim)
        
        # Adaptive fusion weights
        self.fusion_weight_net = nn.Sequential(
            nn.Linear(fusion_dim + creator_embedding_dim, fusion_dim // 2),
            nn.ReLU(),
            nn.Linear(fusion_dim // 2, len(modality_dims)),
            nn.Softmax(dim=-1)
        )
        
        # Final fusion layers
        self.fusion_layers = nn.Sequential(
            nn.Linear(fusion_dim * len(modality_dims), fusion_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(fusion_dim, fusion_dim),
            nn.LayerNorm(fusion_dim)
        )
        
    def forward(self, 
                modality_features: Dict[str, torch.Tensor],
                creator_type: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float], torch.Tensor]:
        """
        Forward pass avec fusion adaptative
        
        Returns:
            fused_features: Features fusionnées
            fusion_weights: Poids de fusion par modalité
            attention_scores: Scores d'attention croisée
        """
        batch_size = creator_type.shape[0]
        
        # Encoder chaque modalité
        encoded_features = {}
        for modality_name, features in modality_features.items():
            if modality_name in self.modality_encoders:
                encoded_features[modality_name] = self.modality_encoders[modality_name](features)
        
        # Creator embeddings
        creator_emb = self.creator_embeddings(creator_type)
        
        # Cross-modal attention entre toutes les paires de modalités
        attended_features = {}
        attention_scores_all = {}
        
        modality_names = list(encoded_features.keys())
        
        for i, mod1 in enumerate(modality_names):
            attended_mod = encoded_features[mod1]
            
            for j, mod2 in enumerate(modality_names):
                if i != j:  # Attention entre modalités différentes
                    att_output, att_scores = self.cross_attention(
                        attended_mod,
                        encoded_features[mod2], 
                        encoded_features[mod2]
                    )
                    attended_mod = attended_mod + att_output  # Residual connection
                    attention_scores_all[f"{mod1}_{mod2}"] = att_scores
            
            attended_features[mod1] = attended_mod
        
        # Calculer les poids de fusion adaptatifs
        # Utiliser la moyenne des features pour calculer les poids
        avg_features = torch.stack(list(attended_features.values())).mean(dim=0).mean(dim=1)
        fusion_input = torch.cat([avg_features, creator_emb], dim=-1)
        fusion_weights = self.fusion_weight_net(fusion_input)
        
        # Fusion pondérée
        weighted_features = []
        for i, (modality_name, features) in enumerate(attended_features.items()):
            weight = fusion_weights[:, i:i+1, None]  # [batch_size, 1, 1]
            weighted_feat = features * weight
            weighted_features.append(weighted_feat.mean(dim=1))  # Pool temporal dimension
        
        # Concatener et fusionner
        concatenated = torch.cat(weighted_features, dim=-1)
        fused_features = self.fusion_layers(concatenated)
        
        # Convertir les poids en dictionnaire
        weight_dict = {}
        for i, modality_name in enumerate(modality_names):
            weight_dict[modality_name] = fusion_weights[0, i].item()
        
        return fused_features, weight_dict, attention_scores_all

class MultimodalFeatureFusion:
    """🔧 Moteur de fusion de caractéristiques multimodales"""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        
        # Models pour extraction de features
        self.audio_model = None
        self.image_model = None
        self.text_model = None
        self.text_tokenizer = None
        
        # NLP model
        self.nlp = None
        
        # Fusion network
        self.fusion_network = None
        
        # Configuration des dimensions par modalité
        self.modality_dims = {
            ModalityType.AUDIO: 768,  # Audio features (e.g., wav2vec2)
            ModalityType.VIDEO: 2048,  # Video features (e.g., ResNet)
            ModalityType.IMAGE: 2048,  # Image features (e.g., ResNet)
            ModalityType.TEXT: 768,   # Text features (e.g., BERT)
            ModalityType.METADATA: 64  # Metadata features
        }
        
        # Cache des features
        self.feature_cache: Dict[str, ModalityFeatures] = {}
        
        # Mappage creator type vers index
        self.creator_type_to_idx = {
            CreatorType.MUSICIAN: 0,
            CreatorType.BLOGGER: 1,
            CreatorType.PHOTOGRAPHER: 2,
            CreatorType.INFLUENCER: 3,
            CreatorType.COMEDIAN: 4
        }
        
        # Métriques
        self.fusion_count = 0
        self.fusion_times = []
        
    async def initialize(self) -> None:
        """Initialise les modèles de feature extraction"""
        try:
            # Text model (BERT)
            self.text_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.text_model = AutoModel.from_pretrained('bert-base-uncased').to(self.device)
            self.text_model.eval()
            
            # Image model (ResNet) 
            self.image_model = torchvision.models.resnet50(pretrained=True)
            self.image_model = nn.Sequential(*list(self.image_model.children())[:-1])  # Remove classifier
            self.image_model = self.image_model.to(self.device)
            self.image_model.eval()
            
            # Audio model (wav2vec2 simulation avec simple CNN)
            self.audio_model = nn.Sequential(
                nn.Conv1d(1, 64, kernel_size=80, stride=16),
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(768),
                nn.Flatten()
            ).to(self.device)
            
            # NLP model pour text preprocessing
            self.nlp = spacy.load("en_core_web_sm")
            
            # Fusion network
            self.fusion_network = MultimodalFusionNetwork(
                modality_dims=self.modality_dims,
                fusion_dim=512,
                creator_embedding_dim=64
            ).to(self.device)
            
            logger.info("MultimodalFeatureFusion initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MultimodalFeatureFusion: {e}")
            raise
    
    async def extract_audio_features(self, 
                                   audio_data: np.ndarray,
                                   sample_rate: int,
                                   content_id: str,
                                   creator_type: CreatorType) -> ModalityFeatures:
        """Extrait les features audio"""
        try:
            # Preprocessing audio
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)  # Convert to mono
            
            # Normaliser
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Features temporelles avec librosa
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Agréger les features temporelles
            audio_features = np.concatenate([
                mfccs.mean(axis=1),
                mfccs.std(axis=1),
                spectral_centroids.mean(axis=1),
                spectral_rolloff.mean(axis=1),
                zero_crossing_rate.mean(axis=1)
            ])
            
            # Neural network features (simulation)
            audio_tensor = torch.FloatTensor(audio_data).unsqueeze(0).unsqueeze(0).to(self.device)
            with torch.no_grad():
                neural_features = self.audio_model(audio_tensor).cpu().numpy().flatten()
            
            # Combiner les features
            combined_features = np.concatenate([audio_features, neural_features])
            
            # Pad ou truncate pour avoir la dimension attendue
            if len(combined_features) > self.modality_dims[ModalityType.AUDIO]:
                combined_features = combined_features[:self.modality_dims[ModalityType.AUDIO]]
            else:
                padding = self.modality_dims[ModalityType.AUDIO] - len(combined_features)
                combined_features = np.pad(combined_features, (0, padding), 'constant')
            
            # Calculer quality score basé sur SNR
            signal_power = np.mean(audio_data ** 2)
            noise_estimate = np.std(audio_data[:int(0.1 * len(audio_data))])  # First 10% as noise estimate
            snr = 10 * np.log10(signal_power / (noise_estimate ** 2 + 1e-8))
            quality_score = min(1.0, max(0.0, (snr + 10) / 40))  # Normalize SNR to 0-1
            
            return ModalityFeatures(
                modality=ModalityType.AUDIO,
                features=combined_features,
                timestamp=datetime.utcnow(),
                creator_type=creator_type,
                content_id=content_id,
                sample_rate=sample_rate,
                duration_ms=int(len(audio_data) / sample_rate * 1000),
                quality_score=quality_score,
                confidence_score=0.95,
                noise_level=noise_estimate
            )
            
        except Exception as e:
            logger.error(f"Failed to extract audio features: {e}")
            raise
    
    async def extract_image_features(self,
                                   image_data: np.ndarray,
                                   content_id: str,
                                   creator_type: CreatorType) -> ModalityFeatures:
        """Extrait les features image"""
        try:
            # Preprocessing image
            if len(image_data.shape) == 3 and image_data.shape[2] == 3:
                # RGB image
                image = Image.fromarray(image_data.astype(np.uint8))
            else:
                # Grayscale to RGB
                image = Image.fromarray(image_data.astype(np.uint8)).convert('RGB')
            
            # Resize pour ResNet
            transform = torchvision.transforms.Compose([
                torchvision.transforms.Resize((224, 224)),
                torchvision.transforms.ToTensor(),
                torchvision.transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            image_tensor = transform(image).unsqueeze(0).to(self.device)
            
            # Extraire features avec ResNet
            with torch.no_grad():
                features = self.image_model(image_tensor)
                features = features.view(features.size(0), -1)  # Flatten
                image_features = features.cpu().numpy().flatten()
            
            # Features traditionnelles (couleur, texture)
            hsv = cv2.cvtColor(image_data, cv2.COLOR_RGB2HSV)
            color_hist = np.concatenate([
                cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten(),  # Hue
                cv2.calcHist([hsv], [1], None, [32], [0, 256]).flatten(),  # Saturation
                cv2.calcHist([hsv], [2], None, [32], [0, 256]).flatten()   # Value
            ])
            
            # Combiner neural + traditional features
            combined_features = np.concatenate([image_features, color_hist])
            
            # Ajuster à la dimension attendue
            if len(combined_features) > self.modality_dims[ModalityType.IMAGE]:
                combined_features = combined_features[:self.modality_dims[ModalityType.IMAGE]]
            else:
                padding = self.modality_dims[ModalityType.IMAGE] - len(combined_features)
                combined_features = np.pad(combined_features, (0, padding), 'constant')
            
            # Quality metrics
            gray = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_score = min(1.0, blur_score / 1000)  # Normalize blur score
            
            return ModalityFeatures(
                modality=ModalityType.IMAGE,
                features=combined_features,
                timestamp=datetime.utcnow(),
                creator_type=creator_type,
                content_id=content_id,
                resolution=(image_data.shape[1], image_data.shape[0]),
                quality_score=quality_score,
                confidence_score=0.92
            )
            
        except Exception as e:
            logger.error(f"Failed to extract image features: {e}")
            raise
    
    async def extract_text_features(self,
                                  text: str,
                                  content_id: str,
                                  creator_type: CreatorType,
                                  language: str = "en") -> ModalityFeatures:
        """Extrait les features texte"""
        try:
            # Preprocessing avec spaCy
            doc = self.nlp(text)
            
            # Features linguistiques
            linguistic_features = np.array([
                len(doc),  # Number of tokens
                len([token for token in doc if token.is_alpha]),  # Number of words
                len(doc.ents),  # Number of entities
                len([token for token in doc if token.pos_ == 'NOUN']),  # Nouns
                len([token for token in doc if token.pos_ == 'VERB']),  # Verbs
                len([token for token in doc if token.pos_ == 'ADJ']),   # Adjectives
                np.mean([token.sentiment for token in doc if hasattr(token, 'sentiment')]) if doc else 0,
                doc._.sentiment if hasattr(doc._, 'sentiment') else 0
            ], dtype=np.float32)
            
            # BERT features
            inputs = self.text_tokenizer(
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                # Utiliser [CLS] token comme représentation du texte
                text_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()
            
            # Combiner features linguistiques et embeddings
            # Pad linguistic features pour correspondre à la dimension
            linguistic_padded = np.pad(
                linguistic_features, 
                (0, self.modality_dims[ModalityType.TEXT] - len(text_embeddings) - len(linguistic_features)), 
                'constant'
            )
            
            combined_features = np.concatenate([text_embeddings, linguistic_padded])
            
            # Ajuster la dimension
            if len(combined_features) > self.modality_dims[ModalityType.TEXT]:
                combined_features = combined_features[:self.modality_dims[ModalityType.TEXT]]
            else:
                padding = self.modality_dims[ModalityType.TEXT] - len(combined_features)
                combined_features = np.pad(combined_features, (0, padding), 'constant')
            
            # Quality metrics
            word_count = len([token for token in doc if token.is_alpha])
            quality_score = min(1.0, word_count / 100)  # More words = better quality
            
            return ModalityFeatures(
                modality=ModalityType.TEXT,
                features=combined_features,
                timestamp=datetime.utcnow(),
                creator_type=creator_type,
                content_id=content_id,
                language=language,
                quality_score=quality_score,
                confidence_score=0.90
            )
            
        except Exception as e:
            logger.error(f"Failed to extract text features: {e}")
            raise
    
    async def extract_metadata_features(self,
                                      metadata: Dict[str, Any],
                                      content_id: str,
                                      creator_type: CreatorType) -> ModalityFeatures:
        """Extrait les features des métadonnées"""
        try:
            # Features numériques des métadonnées
            numeric_features = []
            
            # Creator-specific features
            if creator_type == CreatorType.MUSICIAN:
                numeric_features.extend([
                    metadata.get('tempo', 0),
                    metadata.get('key', 0),
                    metadata.get('duration_seconds', 0),
                    metadata.get('energy', 0),
                    metadata.get('danceability', 0)
                ])
            elif creator_type == CreatorType.PHOTOGRAPHER:
                numeric_features.extend([
                    metadata.get('iso', 0),
                    metadata.get('aperture', 0),
                    metadata.get('shutter_speed', 0),
                    metadata.get('focal_length', 0),
                    metadata.get('exposure_compensation', 0)
                ])
            elif creator_type == CreatorType.BLOGGER:
                numeric_features.extend([
                    metadata.get('word_count', 0),
                    metadata.get('reading_time_minutes', 0),
                    metadata.get('readability_score', 0),
                    metadata.get('sentiment_score', 0),
                    metadata.get('engagement_score', 0)
                ])
            
            # Features générales
            general_features = [
                metadata.get('likes', 0),
                metadata.get('shares', 0),
                metadata.get('comments', 0),
                metadata.get('views', 0),
                metadata.get('timestamp', time.time()),
                metadata.get('file_size_mb', 0),
                hash(str(metadata.get('tags', []))) % 1000,  # Hash of tags
                len(metadata.get('description', '')),
                metadata.get('quality_score', 0.5)
            ]
            
            numeric_features.extend(general_features)
            
            # Convertir en array et normaliser
            features = np.array(numeric_features, dtype=np.float32)
            
            # Normalisation simple (z-score sur les valeurs non-nulles)
            non_zero_mask = features != 0
            if np.any(non_zero_mask):
                features[non_zero_mask] = (features[non_zero_mask] - np.mean(features[non_zero_mask])) / (np.std(features[non_zero_mask]) + 1e-8)
            
            # Ajuster à la dimension attendue
            if len(features) > self.modality_dims[ModalityType.METADATA]:
                features = features[:self.modality_dims[ModalityType.METADATA]]
            else:
                padding = self.modality_dims[ModalityType.METADATA] - len(features)
                features = np.pad(features, (0, padding), 'constant')
            
            return ModalityFeatures(
                modality=ModalityType.METADATA,
                features=features,
                timestamp=datetime.utcnow(),
                creator_type=creator_type,
                content_id=content_id,
                quality_score=1.0,
                confidence_score=1.0
            )
            
        except Exception as e:
            logger.error(f"Failed to extract metadata features: {e}")
            raise
    
    async def fuse_features(self,
                          modality_features: Dict[ModalityType, ModalityFeatures],
                          fusion_strategy: FusionStrategy = FusionStrategy.CROSS_ATTENTION) -> FusedFeatures:
        """Fusionne les features de plusieurs modalités"""
        try:
            start_time = time.time()
            
            if not modality_features:
                raise ValueError("No modality features provided")
            
            # Vérifier que toutes les features sont du même content_id et creator_type
            content_ids = {feat.content_id for feat in modality_features.values()}
            creator_types = {feat.creator_type for feat in modality_features.values()}
            
            if len(content_ids) > 1:
                raise ValueError("All features must be from the same content")
            if len(creator_types) > 1:
                raise ValueError("All features must be from the same creator type")
            
            content_id = list(content_ids)[0]
            creator_type = list(creator_types)[0]
            
            # Stratégies de fusion
            if fusion_strategy == FusionStrategy.EARLY_FUSION:
                fused_features = await self._early_fusion(modality_features)
                fusion_weights = {mod: 1.0/len(modality_features) for mod in modality_features.keys()}
                attention_scores = None
                
            elif fusion_strategy == FusionStrategy.LATE_FUSION:
                fused_features = await self._late_fusion(modality_features)
                fusion_weights = {mod: 1.0/len(modality_features) for mod in modality_features.keys()}
                attention_scores = None
                
            elif fusion_strategy == FusionStrategy.CROSS_ATTENTION:
                fused_features, fusion_weights, attention_scores = await self._cross_attention_fusion(
                    modality_features, creator_type
                )
                
            elif fusion_strategy == FusionStrategy.ADAPTIVE:
                fused_features, fusion_weights, attention_scores = await self._adaptive_fusion(
                    modality_features, creator_type
                )
                
            else:
                raise ValueError(f"Unsupported fusion strategy: {fusion_strategy}")
            
            # Calculer les offsets de synchronisation
            base_timestamp = min(feat.timestamp for feat in modality_features.values())
            sync_offsets = {
                modality: (feat.timestamp - base_timestamp).total_seconds() * 1000  # ms
                for modality, feat in modality_features.items()
            }
            
            fusion_result = FusedFeatures(
                content_id=content_id,
                creator_type=creator_type,
                fusion_strategy=fusion_strategy,
                fused_features=fused_features,
                modality_features=modality_features,
                fusion_weights=fusion_weights,
                attention_scores=attention_scores,
                synchronization_offset_ms=sync_offsets
            )
            
            # Métriques
            self.fusion_count += 1
            fusion_time = time.time() - start_time
            self.fusion_times.append(fusion_time)
            
            logger.info(f"Fused {len(modality_features)} modalities in {fusion_time:.3f}s using {fusion_strategy.value}")
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"Failed to fuse features: {e}")
            raise
    
    async def _early_fusion(self, modality_features: Dict[ModalityType, ModalityFeatures]) -> np.ndarray:
        """Fusion précoce - concaténation simple"""
        features_list = []
        for modality in sorted(modality_features.keys(), key=lambda x: x.value):
            features_list.append(modality_features[modality].features)
        
        return np.concatenate(features_list)
    
    async def _late_fusion(self, modality_features: Dict[ModalityType, ModalityFeatures]) -> np.ndarray:
        """Fusion tardive - moyenne pondérée"""
        features_list = []
        weights = []
        
        for modality, feat in modality_features.items():
            features_list.append(feat.features)
            weights.append(feat.quality_score * feat.confidence_score)
        
        # Normaliser les poids
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        
        # Moyenne pondérée
        weighted_features = np.zeros_like(features_list[0])
        for i, features in enumerate(features_list):
            weighted_features += features * weights[i]
        
        return weighted_features
    
    async def _cross_attention_fusion(self, 
                                    modality_features: Dict[ModalityType, ModalityFeatures],
                                    creator_type: CreatorType) -> Tuple[np.ndarray, Dict[ModalityType, float], np.ndarray]:
        """Fusion avec attention croisée"""
        
        # Préparer les inputs pour le réseau
        features_dict = {}
        for modality, feat in modality_features.items():
            features_tensor = torch.FloatTensor(feat.features).unsqueeze(0).unsqueeze(0).to(self.device)
            features_dict[modality.value] = features_tensor
        
        creator_idx = torch.LongTensor([self.creator_type_to_idx[creator_type]]).to(self.device)
        
        # Forward pass
        with torch.no_grad():
            fused_features, fusion_weights, attention_scores = self.fusion_network(
                features_dict, creator_idx
            )
        
        # Convertir fusion_weights pour utiliser ModalityType comme clés
        fusion_weights_converted = {}
        for modality_str, weight in fusion_weights.items():
            modality_type = ModalityType(modality_str)
            fusion_weights_converted[modality_type] = weight
        
        return (
            fused_features.cpu().numpy().flatten(),
            fusion_weights_converted,
            attention_scores
        )
    
    async def _adaptive_fusion(self,
                             modality_features: Dict[ModalityType, ModalityFeatures],
                             creator_type: CreatorType) -> Tuple[np.ndarray, Dict[ModalityType, float], np.ndarray]:
        """Fusion adaptative basée sur la qualité et le type de créateur"""
        
        # Poids adaptatifs basés sur:
        # 1. Quality score des features
        # 2. Confidence score
        # 3. Type de créateur (certaines modalités plus importantes pour certains créateurs)
        
        creator_modality_preferences = {
            CreatorType.MUSICIAN: {
                ModalityType.AUDIO: 1.5,
                ModalityType.TEXT: 0.8,
                ModalityType.IMAGE: 0.7,
                ModalityType.METADATA: 1.2
            },
            CreatorType.PHOTOGRAPHER: {
                ModalityType.IMAGE: 1.8,
                ModalityType.METADATA: 1.3,
                ModalityType.TEXT: 0.9,
                ModalityType.AUDIO: 0.4
            },
            CreatorType.BLOGGER: {
                ModalityType.TEXT: 1.6,
                ModalityType.IMAGE: 1.1,
                ModalityType.METADATA: 1.2,
                ModalityType.AUDIO: 0.5
            },
            CreatorType.INFLUENCER: {
                ModalityType.IMAGE: 1.3,
                ModalityType.TEXT: 1.2,
                ModalityType.METADATA: 1.4,
                ModalityType.AUDIO: 0.8,
                ModalityType.VIDEO: 1.5
            },
            CreatorType.COMEDIAN: {
                ModalityType.AUDIO: 1.4,
                ModalityType.TEXT: 1.3,
                ModalityType.VIDEO: 1.6,
                ModalityType.IMAGE: 0.8,
                ModalityType.METADATA: 1.0
            }
        }
        
        preferences = creator_modality_preferences.get(creator_type, {})
        
        fusion_weights = {}
        weighted_features = []
        
        total_weight = 0
        for modality, feat in modality_features.items():
            # Poids adaptatif
            quality_weight = feat.quality_score * feat.confidence_score
            preference_weight = preferences.get(modality, 1.0)
            
            final_weight = quality_weight * preference_weight
            fusion_weights[modality] = final_weight
            total_weight += final_weight
            
            weighted_features.append(feat.features * final_weight)
        
        # Normaliser les poids
        for modality in fusion_weights:
            fusion_weights[modality] /= total_weight
        
        # Fusion pondérée
        fused = np.zeros_like(weighted_features[0])
        for weighted_feat in weighted_features:
            fused += weighted_feat / len(weighted_features)
        
        return fused, fusion_weights, None
    
    async def get_fusion_stats(self) -> Dict[str, Any]:
        """Obtient les statistiques de fusion"""
        if not self.fusion_times:
            return {"error": "No fusion operations performed yet"}
        
        return {
            "total_fusions": self.fusion_count,
            "avg_fusion_time_ms": np.mean(self.fusion_times) * 1000,
            "min_fusion_time_ms": np.min(self.fusion_times) * 1000,
            "max_fusion_time_ms": np.max(self.fusion_times) * 1000,
            "cache_size": len(self.feature_cache),
            "modality_dimensions": {mod.value: dim for mod, dim in self.modality_dims.items()}
        }

# Usage example
async def demo_multimodal_fusion() -> None:
    """Démo du système de fusion multimodale"""
    fusion_engine = MultimodalFeatureFusion()
    await fusion_engine.initialize()
    
    # Simuler des données multimodales
    # Audio simulé
    audio_data = np.random.randn(16000)  # 1 seconde à 16kHz
    audio_features = await fusion_engine.extract_audio_features(
        audio_data, 16000, "content-123", CreatorType.MUSICIAN
    )
    
    # Image simulée  
    image_data = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    image_features = await fusion_engine.extract_image_features(
        image_data, "content-123", CreatorType.MUSICIAN
    )
    
    # Texte simulé
    text = "This is a beautiful song with amazing melody and great lyrics"
    text_features = await fusion_engine.extract_text_features(
        text, "content-123", CreatorType.MUSICIAN
    )
    
    # Métadonnées simulées
    metadata = {
        "tempo": 120,
        "key": 5,
        "duration_seconds": 180,
        "energy": 0.8,
        "danceability": 0.7,
        "likes": 1000,
        "shares": 50,
        "views": 5000
    }
    metadata_features = await fusion_engine.extract_metadata_features(
        metadata, "content-123", CreatorType.MUSICIAN
    )
    
    # Fusion multimodale
    modality_features = {
        ModalityType.AUDIO: audio_features,
        ModalityType.IMAGE: image_features,
        ModalityType.TEXT: text_features,
        ModalityType.METADATA: metadata_features
    }
    
    # Test différentes stratégies de fusion
    strategies = [
        FusionStrategy.EARLY_FUSION,
        FusionStrategy.LATE_FUSION,
        FusionStrategy.CROSS_ATTENTION,
        FusionStrategy.ADAPTIVE
    ]
    
    for strategy in strategies:
        fused_result = await fusion_engine.fuse_features(modality_features, strategy)
        
        print(f"✅ {strategy.value} fusion:")
        print(f"  - Fused features shape: {fused_result.fused_features.shape}")
        print(f"  - Fusion weights: {fused_result.fusion_weights}")
        print(f"  - Sync offsets: {fused_result.synchronization_offset_ms}")
    
    # Statistiques
    stats = await fusion_engine.get_fusion_stats()
    print(f"✅ Fusion stats: {stats}")

if __name__ == "__main__":
    asyncio.run(demo_multimodal_fusion())