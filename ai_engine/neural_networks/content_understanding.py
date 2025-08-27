"""
Content Understanding Networks for IA-Influencer-Agent

Advanced neural networks for understanding, analyzing, and extracting insights
from multi-modal content created by influencers and content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum

from .base_networks import BaseNeuralNetwork, NetworkConfig
from .transformer_models import TransformerConfig, MultiModalTransformer


class ContentType(Enum):
    """Types of content for analysis"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    SOCIAL_POST = "social_post"
    PODCAST = "podcast"
    STREAM = "live_stream"


class AnalysisLevel(Enum):
    """Levels of content analysis"""
    BASIC = "basic"           # Genre, format, basic metadata
    INTERMEDIATE = "intermediate"  # Emotion, style, quality
    ADVANCED = "advanced"     # Deep semantics, personality, trends
    EXPERT = "expert"         # Professional insights, market analysis


@dataclass
class ContentAnalysisResult:
    """Result of content analysis"""
    
    content_id: str
    content_type: ContentType
    analysis_level: AnalysisLevel
    
    # Basic analysis
    genre: Optional[str] = None
    format_info: Optional[Dict] = None
    duration: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Semantic analysis
    topics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    emotion_scores: Optional[Dict[str, float]] = None
    
    # Style analysis
    style_features: Optional[Dict[str, float]] = None
    artistic_elements: Optional[List[str]] = None
    technical_quality: Optional[Dict[str, float]] = None
    
    # Advanced insights
    personality_traits: Optional[Dict[str, float]] = None
    target_audience: Optional[Dict[str, float]] = None
    commercial_potential: Optional[float] = None
    trend_alignment: Optional[float] = None
    
    # Confidence scores
    confidence_scores: Optional[Dict[str, float]] = None
    
    # Raw features for downstream processing
    feature_embeddings: Optional[torch.Tensor] = None


class ContentUnderstandingNetwork(BaseNeuralNetwork):
    """
    Main network for understanding content across modalities
    
    Provides unified interface for analyzing any type of content
    and extracting meaningful insights for creators.
    """
    
    def __init__(self, config: TransformerConfig):
        super().__init__(config)
        self.config = config
        
        # Multi-modal transformer backbone
        self.backbone = MultiModalTransformer(config)
        
        # Content type classifier
        self.content_type_classifier = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.d_model // 2, len(ContentType)),
            nn.Softmax(dim=-1)
        )
        
        # Quality assessment head
        self.quality_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 4),
            nn.ReLU(),
            nn.Linear(config.d_model // 4, 1),
            nn.Sigmoid()  # Quality score 0-1
        )
        
        # Genre classification head
        self.genre_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.d_model // 2, 50),  # Support for 50 genres
            nn.Softmax(dim=-1)
        )
        
        # Commercial potential head
        self.commercial_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 4),
            nn.ReLU(),
            nn.Linear(config.d_model // 4, 1),
            nn.Sigmoid()
        )
        
        # Feature extraction head
        self.feature_head = nn.Linear(config.d_model, 512)  # Standardized feature size
        
        # Analysis confidence estimator
        self.confidence_head = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 4),
            nn.ReLU(),
            nn.Linear(config.d_model // 4, 5),  # Confidence for each analysis type
            nn.Sigmoid()
        )
        
    def forward(
        self,
        inputs: Dict[str, torch.Tensor],
        analysis_level: AnalysisLevel = AnalysisLevel.INTERMEDIATE
    ) -> Dict[str, torch.Tensor]:
        
        # Get multi-modal representation
        content_embedding = self.backbone(inputs)
        
        results = {
            "content_embedding": content_embedding,
            "features": self.feature_head(content_embedding)
        }
        
        # Basic analysis
        if analysis_level.value in ["basic", "intermediate", "advanced", "expert"]:
            results["content_type"] = self.content_type_classifier(content_embedding)
            results["quality_score"] = self.quality_head(content_embedding)
            results["genre"] = self.genre_head(content_embedding)
        
        # Advanced analysis
        if analysis_level.value in ["intermediate", "advanced", "expert"]:
            results["commercial_potential"] = self.commercial_head(content_embedding)
            
        # Confidence scores
        results["confidence"] = self.confidence_head(content_embedding)
        
        return results
    
    def analyze_content(
        self,
        inputs: Dict[str, torch.Tensor],
        content_id: str,
        analysis_level: AnalysisLevel = AnalysisLevel.INTERMEDIATE
    ) -> ContentAnalysisResult:
        """
        Perform complete content analysis and return structured result
        """
        
        self.eval()
        with torch.no_grad():
            outputs = self.forward(inputs, analysis_level)
        
        # Extract predictions
        content_type_probs = outputs["content_type"].cpu().numpy()[0]
        content_type = ContentType(list(ContentType)[np.argmax(content_type_probs)])
        
        quality_score = outputs["quality_score"].cpu().item()
        
        genre_probs = outputs["genre"].cpu().numpy()[0]
        top_genre_idx = np.argmax(genre_probs)
        
        confidence_scores = outputs["confidence"].cpu().numpy()[0]
        
        # Create result
        result = ContentAnalysisResult(
            content_id=content_id,
            content_type=content_type,
            analysis_level=analysis_level,
            quality_score=quality_score,
            confidence_scores={
                "content_type": confidence_scores[0],
                "quality": confidence_scores[1],
                "genre": confidence_scores[2],
                "sentiment": confidence_scores[3],
                "style": confidence_scores[4]
            },
            feature_embeddings=outputs["features"]
        )
        
        # Add advanced analysis if requested
        if analysis_level.value in ["intermediate", "advanced", "expert"]:
            result.commercial_potential = outputs["commercial_potential"].cpu().item()
        
        return result
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Multi-task loss computation"""
        
        total_loss = 0.0
        num_tasks = 0
        
        # Content type classification loss
        if "content_type" in targets:
            loss = F.cross_entropy(predictions["content_type"], targets["content_type"])
            total_loss += loss
            num_tasks += 1
        
        # Quality regression loss
        if "quality_score" in targets:
            loss = F.mse_loss(predictions["quality_score"].squeeze(), targets["quality_score"])
            total_loss += loss
            num_tasks += 1
        
        # Genre classification loss
        if "genre" in targets:
            loss = F.cross_entropy(predictions["genre"], targets["genre"])
            total_loss += loss
            num_tasks += 1
        
        # Commercial potential loss
        if "commercial_potential" in targets:
            loss = F.mse_loss(
                predictions["commercial_potential"].squeeze(),
                targets["commercial_potential"]
            )
            total_loss += loss
            num_tasks += 1
        
        return total_loss / max(num_tasks, 1)


class SemanticAnalysisNetwork(BaseNeuralNetwork):
    """
    Network for deep semantic analysis of content
    
    Extracts topics, themes, meanings, and contextual information.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Transformer backbone for text understanding
        self.text_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=config.hidden_dims[0],
                nhead=8,
                dim_feedforward=config.hidden_dims[1],
                dropout=config.dropout_rate,
                batch_first=True
            ),
            num_layers=config.num_layers if hasattr(config, 'num_layers') else 6
        )
        
        # Topic modeling head
        self.topic_head = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 100)  # 100 topics
        )
        
        # Keyword extraction head
        self.keyword_head = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[0]),
            nn.Sigmoid()
        )
        
        # Context understanding head
        self.context_head = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 50)  # 50 context types
        )
        
        # Semantic similarity head
        self.similarity_head = nn.Linear(config.hidden_dims[0], config.output_dim)
        
    def forward(
        self,
        text_features: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        # Encode text semantically
        encoded = self.text_encoder(text_features, src_key_padding_mask=mask)
        
        # Global representation (average pooling)
        global_repr = encoded.mean(dim=1) if mask is None else encoded.sum(dim=1) / (~mask).sum(dim=1, keepdim=True)
        
        return {
            "topic_distribution": F.softmax(self.topic_head(global_repr), dim=-1),
            "keyword_scores": self.keyword_head(encoded),
            "context_distribution": F.softmax(self.context_head(global_repr), dim=-1),
            "semantic_embedding": self.similarity_head(global_repr),
            "token_representations": encoded
        }
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "topics" in targets:
            loss += F.cross_entropy(predictions["topic_distribution"], targets["topics"])
        
        if "keywords" in targets:
            loss += F.binary_cross_entropy(predictions["keyword_scores"], targets["keywords"])
        
        if "context" in targets:
            loss += F.cross_entropy(predictions["context_distribution"], targets["context"])
        
        if "semantic_similarity" in targets:
            loss += F.cosine_embedding_loss(
                predictions["semantic_embedding"],
                targets["semantic_similarity"],
                torch.ones(predictions["semantic_embedding"].size(0), device=predictions["semantic_embedding"].device)
            )
        
        return loss


class EmotionRecognitionNetwork(BaseNeuralNetwork):
    """
    Network for recognizing emotions in multi-modal content
    
    Supports audio, text, and visual emotion recognition.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Modality-specific encoders
        self.audio_encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[0])
        )
        
        self.text_encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[0])
        )
        
        self.visual_encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[0])
        )
        
        # Fusion layer
        self.fusion = nn.MultiheadAttention(
            config.hidden_dims[0], 
            8, 
            dropout=config.dropout_rate,
            batch_first=True
        )
        
        # Emotion classification heads
        self.basic_emotions = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 7)  # Joy, Sadness, Anger, Fear, Disgust, Surprise, Neutral
        )
        
        self.sentiment = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 3)  # Positive, Negative, Neutral
        )
        
        self.arousal_valence = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 2),  # Arousal, Valence
            nn.Tanh()  # Scale to [-1, 1]
        )
        
        # Emotion intensity
        self.intensity = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()  # Scale to [0, 1]
        )
        
    def forward(
        self,
        inputs: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        
        encoded_features = []
        
        # Encode each modality
        if "audio" in inputs:
            audio_feat = self.audio_encoder(inputs["audio"])
            encoded_features.append(audio_feat.unsqueeze(1))
        
        if "text" in inputs:
            text_feat = self.text_encoder(inputs["text"])
            encoded_features.append(text_feat.unsqueeze(1))
        
        if "visual" in inputs:
            visual_feat = self.visual_encoder(inputs["visual"])
            encoded_features.append(visual_feat.unsqueeze(1))
        
        if not encoded_features:
            raise ValueError("At least one modality input is required")
        
        # Concatenate features
        combined_features = torch.cat(encoded_features, dim=1)
        
        # Multi-modal fusion
        fused_features, _ = self.fusion(
            combined_features, combined_features, combined_features
        )
        
        # Global pooling
        global_features = fused_features.mean(dim=1)
        
        return {
            "basic_emotions": F.softmax(self.basic_emotions(global_features), dim=-1),
            "sentiment": F.softmax(self.sentiment(global_features), dim=-1),
            "arousal_valence": self.arousal_valence(global_features),
            "intensity": self.intensity(global_features),
            "emotion_embedding": global_features
        }
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "basic_emotions" in targets:
            loss += F.cross_entropy(predictions["basic_emotions"], targets["basic_emotions"])
        
        if "sentiment" in targets:
            loss += F.cross_entropy(predictions["sentiment"], targets["sentiment"])
        
        if "arousal_valence" in targets:
            loss += F.mse_loss(predictions["arousal_valence"], targets["arousal_valence"])
        
        if "intensity" in targets:
            loss += F.mse_loss(predictions["intensity"].squeeze(), targets["intensity"])
        
        return loss


class StyleAnalysisNetwork(BaseNeuralNetwork):
    """
    Network for analyzing artistic and stylistic elements in content
    
    Identifies style patterns, artistic techniques, and creative elements.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Style feature extractor
        self.feature_extractor = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[0])
        )
        
        # Style classification heads
        self.artistic_style = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 25)  # 25 artistic styles
        )
        
        self.technical_quality = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 10),  # 10 technical aspects
            nn.Sigmoid()
        )
        
        self.creativity_score = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        self.complexity_analysis = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 5)  # 5 complexity dimensions
        )
        
        # Style similarity encoder
        self.similarity_encoder = nn.Linear(config.hidden_dims[0], config.output_dim)
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        
        # Extract style features
        style_features = self.feature_extractor(x)
        
        return {
            "artistic_style": F.softmax(self.artistic_style(style_features), dim=-1),
            "technical_quality": self.technical_quality(style_features),
            "creativity_score": self.creativity_score(style_features),
            "complexity_analysis": self.complexity_analysis(style_features),
            "style_embedding": self.similarity_encoder(style_features),
            "raw_style_features": style_features
        }
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "artistic_style" in targets:
            loss += F.cross_entropy(predictions["artistic_style"], targets["artistic_style"])
        
        if "technical_quality" in targets:
            loss += F.mse_loss(predictions["technical_quality"], targets["technical_quality"])
        
        if "creativity_score" in targets:
            loss += F.mse_loss(predictions["creativity_score"].squeeze(), targets["creativity_score"])
        
        if "complexity_analysis" in targets:
            loss += F.mse_loss(predictions["complexity_analysis"], targets["complexity_analysis"])
        
        return loss


class QualityAssessmentNetwork(BaseNeuralNetwork):
    """
    Network for comprehensive quality assessment of content
    
    Evaluates technical quality, production value, and overall professionalism.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Multi-aspect quality analyzer
        self.quality_encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[0])
        )
        
        # Quality aspect heads
        self.technical_quality = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        self.production_value = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        self.artistic_merit = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        self.commercial_viability = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        self.engagement_potential = nn.Sequential(
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Overall quality aggregator
        self.overall_quality = nn.Sequential(
            nn.Linear(5, config.hidden_dims[1] // 4),  # 5 quality aspects
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1] // 4, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        
        # Extract quality features
        quality_features = self.quality_encoder(x)
        
        # Compute individual quality aspects
        technical = self.technical_quality(quality_features)
        production = self.production_value(quality_features)
        artistic = self.artistic_merit(quality_features)
        commercial = self.commercial_viability(quality_features)
        engagement = self.engagement_potential(quality_features)
        
        # Combine all aspects for overall quality
        all_aspects = torch.cat([technical, production, artistic, commercial, engagement], dim=-1)
        overall = self.overall_quality(all_aspects)
        
        return {
            "technical_quality": technical,
            "production_value": production,
            "artistic_merit": artistic,
            "commercial_viability": commercial,
            "engagement_potential": engagement,
            "overall_quality": overall,
            "quality_breakdown": all_aspects
        }
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        quality_aspects = ["technical_quality", "production_value", "artistic_merit", 
                         "commercial_viability", "engagement_potential", "overall_quality"]
        
        for aspect in quality_aspects:
            if aspect in targets:
                loss += F.mse_loss(predictions[aspect].squeeze(), targets[aspect])
        
        return loss
