"""
Content Classification Model - Ainflue Enterprise
===============================================
Modèle classification contenu multi-modal avec deep learning.
Support audio, video, image, text avec transfer learning et fine-tuning.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue ML Models
Version: 1.0 Production
"""

import torch
import torch.nn as nn
import torchvision.models as models
# import transformers
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import librosa
import cv2
from PIL import Image
import asyncio
import logging
from pathlib import Path
import json

# ⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
# Cette architecture ML et tous ses algorithmes sont la propriété intellectuelle 
# EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Tous droits réservés.

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types de contenu supportés par Ainflue"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"

class CreatorCategory(Enum):
    """Catégories de créateurs Ainflue"""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    PODCASTER = "podcaster"

@dataclass
class ContentInput:
    """Input data pour classification contenu"""
    content_id: str
    content_type: ContentType
    file_path: Optional[str] = None
    raw_data: Optional[bytes] = None
    metadata: Dict[str, Any] = None
    creator_context: Dict[str, Any] = None

@dataclass
class ContentClassificationResult:
    """Résultat classification contenu avec métadonnées Ainflue"""
    content_id: str
    content_type: ContentType
    creator_category: CreatorCategory
    quality_score: float
    engagement_potential: float
    monetization_potential: float 
    collaboration_opportunities: List[str]
    seo_keywords: List[str]
    content_tags: List[str]
    business_value_score: float
    processing_recommendations: Dict[str, Any]
    confidence_scores: Dict[str, float]
    timestamp: str

@dataclass
class ContentClassificationConfig:
    """Configuration pour le classificateur"""
    model_version: str = "1.0"
    device: str = "cpu"
    batch_size: int = 32
    confidence_threshold: float = 0.75
    enable_ensemble: bool = True
    cache_predictions: bool = True

class MultiModalContentClassifier(nn.Module):
    """
    Classificateur contenu multi-modal enterprise avec business intelligence.
    Deep learning + transfer learning + Ainflue business logic integration.
    """
    
    def __init__(self, model_config: ContentClassificationConfig):
        super().__init__()
        self.model_config = model_config
        self.device = torch.device(model_config.device)
        
        # Audio Classification Branch
        self.audio_encoder = self._build_audio_encoder()
        self.audio_classifier = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, len(CreatorCategory))
        )
        
        # Visual Classification Branch (Images/Video frames)
        self.visual_encoder = models.efficientnet_b4(pretrained=True)
        self.visual_encoder.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(1792, 1024),
            nn.ReLU(), 
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, len(CreatorCategory))
        )
        
        # Text Classification Branch
        self.text_encoder = transformers.AutoModel.from_pretrained(
            'bert-base-multilingual-cased'
        )
        self.text_classifier = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, len(CreatorCategory))
        )
        
        # Multi-modal Fusion Layer
        self.fusion_layer = nn.Sequential(
            nn.Linear(1536, 1024),  # 512 * 3 modalities
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 256)
        )
        
        # Business Intelligence Layers
        self.quality_predictor = nn.Linear(256, 1)
        self.engagement_predictor = nn.Linear(256, 1)
        self.monetization_predictor = nn.Linear(256, 1)
        self.business_value_predictor = nn.Linear(256, 1)
        
        # Final Classification
        self.final_classifier = nn.Linear(256, len(CreatorCategory))
        
        # Move to device
        self.to(self.device)
        
    def _build_audio_encoder(self) -> nn.Module:
        """Construction encodeur audio avec spectrograms et MFCC."""
        return nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((8, 8)),
            nn.Flatten(),
            nn.Linear(256 * 64, 2048)
        )
    
    def forward(self, content_input: ContentInput) -> torch.Tensor:
        """
        Forward pass classification avec business intelligence.
        
        Content Classification Features:
        - Multi-modal content analysis (audio, visual, text)
        - Creator category prediction avec business context
        - Quality assessment pour content optimization
        - Engagement potential prediction basé sur historical data
        - Monetization potential analysis pour revenue optimization
        """
        features = []
        
        # Process different content types
        if content_input.content_type == ContentType.AUDIO:
            audio_features = self._process_audio(content_input)
            features.append(audio_features)
            
        elif content_input.content_type == ContentType.IMAGE:
            visual_features = self._process_image(content_input)
            features.append(visual_features)
            
        elif content_input.content_type == ContentType.TEXT:
            text_features = self._process_text(content_input)
            features.append(text_features)
            
        elif content_input.content_type == ContentType.VIDEO:
            # Video combines visual and audio
            visual_features = self._process_video_frames(content_input)
            audio_features = self._process_video_audio(content_input)
            features.extend([visual_features, audio_features])
        
        # Pad features if needed for multi-modal fusion  
        while len(features) < 3:
            features.append(torch.zeros(512).to(self.device))
            
        # Multi-modal feature fusion
        fused_features = torch.cat(features[:3], dim=-1)
        fused_output = self.fusion_layer(fused_features)
        
        return fused_output
    
    def _process_audio(self, content_input: ContentInput) -> torch.Tensor:
        """Process audio content pour feature extraction"""
        try:
            # Load audio file
            if content_input.file_path:
                audio_data, sr = librosa.load(content_input.file_path, sr=22050)
            else:
                # Process raw audio data
                audio_data = np.frombuffer(content_input.raw_data, dtype=np.float32)
                sr = 22050
            
            # Generate mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio_data, sr=sr, n_mels=128, fmax=8000
            )
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Convert to tensor
            spec_tensor = torch.FloatTensor(mel_spec_db).unsqueeze(0).unsqueeze(0)
            spec_tensor = spec_tensor.to(self.device)
            
            # Extract features
            audio_features = self.audio_encoder(spec_tensor)
            return self.audio_classifier(audio_features)
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return torch.zeros(512).to(self.device)
    
    def _process_image(self, content_input: ContentInput) -> torch.Tensor:
        """Process image content pour feature extraction"""
        try:
            # Load and preprocess image
            if content_input.file_path:
                image = Image.open(content_input.file_path).convert('RGB')
            else:
                # Process raw image data
                image = Image.frombytes('RGB', (224, 224), content_input.raw_data)
            
            # Standard image preprocessing
            import torchvision.transforms as transforms
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            image_tensor = transform(image).unsqueeze(0).to(self.device)
            
            # Extract visual features
            visual_features = self.visual_encoder(image_tensor)
            return visual_features
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return torch.zeros(512).to(self.device)
    
    def _process_text(self, content_input: ContentInput) -> torch.Tensor:
        """Process text content pour feature extraction"""
        try:
            # Get text content
            if content_input.file_path:
                with open(content_input.file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = content_input.raw_data.decode('utf-8')
            
            # Tokenize text
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                'bert-base-multilingual-cased'
            )
            tokens = tokenizer(
                text, return_tensors='pt', max_length=512, 
                truncation=True, padding=True
            )
            
            # Move to device
            input_ids = tokens['input_ids'].to(self.device)
            attention_mask = tokens['attention_mask'].to(self.device)
            
            # Extract text features
            with torch.no_grad():
                outputs = self.text_encoder(
                    input_ids=input_ids, 
                    attention_mask=attention_mask
                )
                text_features = outputs.last_hidden_state.mean(dim=1)
            
            return self.text_classifier(text_features)
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            return torch.zeros(512).to(self.device)
    
    def _process_video_frames(self, content_input: ContentInput) -> torch.Tensor:
        """Extract visual features from video frames"""
        try:
            # Use OpenCV to extract frames
            cap = cv2.VideoCapture(content_input.file_path)
            frames = []
            
            # Sample frames at intervals
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 10)  # Sample 10 frames
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    
            cap.release()
            
            if not frames:
                return torch.zeros(512).to(self.device)
            
            # Process frames through visual encoder
            frame_features = []
            for frame in frames[:5]:  # Limit to 5 frames
                frame_pil = Image.fromarray(frame)
                # Use same preprocessing as images
                import torchvision.transforms as transforms
                transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                       std=[0.229, 0.224, 0.225])
                ])
                
                frame_tensor = transform(frame_pil).unsqueeze(0).to(self.device)
                features = self.visual_encoder(frame_tensor)
                frame_features.append(features)
            
            # Average frame features
            avg_features = torch.stack(frame_features).mean(dim=0)
            return avg_features
            
        except Exception as e:
            logger.error(f"Video frame processing error: {e}")
            return torch.zeros(512).to(self.device)
    
    def _process_video_audio(self, content_input: ContentInput) -> torch.Tensor:
        """Extract audio features from video"""
        try:
            # Extract audio from video
            audio_data, sr = librosa.load(content_input.file_path, sr=22050)
            
            # Create temporary audio input
            audio_input = ContentInput(
                content_id=content_input.content_id + "_audio",
                content_type=ContentType.AUDIO,
                raw_data=audio_data.tobytes()
            )
            
            return self._process_audio(audio_input)
            
        except Exception as e:
            logger.error(f"Video audio processing error: {e}")
            return torch.zeros(512).to(self.device)
    
    async def classify_content(self, content_input: ContentInput) -> ContentClassificationResult:
        """Classification contenu avec business intelligence scoring."""
        try:
            # Forward pass
            with torch.no_grad():
                features = self.forward(content_input)
                
                # Get predictions
                category_logits = self.final_classifier(features)
                category_probs = torch.softmax(category_logits, dim=-1)
                
                # Business intelligence predictions
                quality_score = torch.sigmoid(self.quality_predictor(features)).item()
                engagement_potential = torch.sigmoid(self.engagement_predictor(features)).item()
                monetization_potential = torch.sigmoid(self.monetization_predictor(features)).item()
                business_value_score = torch.sigmoid(self.business_value_predictor(features)).item()
                
                # Get most likely category
                category_idx = torch.argmax(category_probs).item()
                category = list(CreatorCategory)[category_idx]
                
                # Generate recommendations
                recommendations = self._generate_recommendations(
                    category, quality_score, engagement_potential
                )
                
                # Generate SEO keywords and tags
                seo_keywords = self._generate_seo_keywords(content_input, category)
                content_tags = self._generate_content_tags(content_input, category)
                
                # Collaboration opportunities
                collaboration_ops = self._identify_collaboration_opportunities(category)
                
                return ContentClassificationResult(
                    content_id=content_input.content_id,
                    content_type=content_input.content_type,
                    creator_category=category,
                    quality_score=quality_score,
                    engagement_potential=engagement_potential,
                    monetization_potential=monetization_potential,
                    collaboration_opportunities=collaboration_ops,
                    seo_keywords=seo_keywords,
                    content_tags=content_tags,
                    business_value_score=business_value_score,
                    processing_recommendations=recommendations,
                    confidence_scores={
                        "category_confidence": torch.max(category_probs).item(),
                        "quality_confidence": quality_score,
                        "engagement_confidence": engagement_potential
                    },
                    timestamp=str(np.datetime64('now'))
                )
                
        except Exception as e:
            logger.error(f"Content classification error: {e}")
            # Return default result
            return ContentClassificationResult(
                content_id=content_input.content_id,
                content_type=content_input.content_type,
                creator_category=CreatorCategory.INFLUENCER,
                quality_score=0.5,
                engagement_potential=0.5,
                monetization_potential=0.5,
                collaboration_opportunities=[],
                seo_keywords=[],
                content_tags=[],
                business_value_score=0.5,
                processing_recommendations={},
                confidence_scores={},
                timestamp=str(np.datetime64('now'))
            )
    
    def _generate_recommendations(self, category: CreatorCategory, 
                                quality_score: float, engagement_potential: float) -> Dict[str, Any]:
        """Génération recommandations basées sur classification"""
        recommendations = {
            "content_optimization": [],
            "monetization_strategies": [],
            "distribution_channels": [],
            "collaboration_suggestions": []
        }
        
        # Quality-based recommendations
        if quality_score < 0.6:
            recommendations["content_optimization"].append(
                "Consider improving technical quality (resolution, audio clarity)"
            )
        
        # Engagement-based recommendations  
        if engagement_potential > 0.8:
            recommendations["distribution_channels"].extend([
                "Prime time posting recommended",
                "Cross-platform distribution advised"
            ])
        
        # Category-specific recommendations
        if category == CreatorCategory.MUSICIAN:
            recommendations["monetization_strategies"].extend([
                "Music streaming optimization",
                "Live performance booking",
                "Merchandise opportunities"
            ])
        elif category == CreatorCategory.PHOTOGRAPHER:
            recommendations["monetization_strategies"].extend([
                "Print sales potential",
                "Stock photography licensing",
                "Photography services"
            ])
        
        return recommendations
    
    def _generate_seo_keywords(self, content_input: ContentInput, 
                             category: CreatorCategory) -> List[str]:
        """Génération mots-clés SEO basés sur contenu et catégorie"""
        base_keywords = {
            CreatorCategory.MUSICIAN: ["music", "song", "artist", "album", "streaming"],
            CreatorCategory.PHOTOGRAPHER: ["photography", "photo", "image", "visual", "art"],
            CreatorCategory.VIDEOGRAPHER: ["video", "film", "cinematic", "production", "visual"],
            CreatorCategory.BLOGGER: ["blog", "article", "content", "writing", "story"],
            CreatorCategory.INFLUENCER: ["influence", "social", "content", "trending", "viral"],
            CreatorCategory.COMEDIAN: ["comedy", "humor", "entertainment", "funny", "laugh"],
            CreatorCategory.ARTIST: ["art", "creative", "design", "artistic", "visual"],
            CreatorCategory.PODCASTER: ["podcast", "audio", "talk", "discussion", "voice"]
        }
        
        keywords = base_keywords.get(category, ["content", "creative", "media"])
        
        # Add content-type specific keywords
        if content_input.content_type == ContentType.AUDIO:
            keywords.extend(["audio", "sound", "music", "podcast"])
        elif content_input.content_type == ContentType.VIDEO:
            keywords.extend(["video", "visual", "cinematic", "film"])
        elif content_input.content_type == ContentType.IMAGE:
            keywords.extend(["image", "photo", "visual", "picture"])
        
        return keywords[:10]  # Limit to top 10
    
    def _generate_content_tags(self, content_input: ContentInput, 
                             category: CreatorCategory) -> List[str]:
        """Génération tags contenu pour categorization"""
        tags = [
            f"#{category.value}",
            f"#{content_input.content_type.value}",
            "#ainflue",
            "#creator"
        ]
        
        # Add category-specific tags
        category_tags = {
            CreatorCategory.MUSICIAN: ["#music", "#audio", "#songwriter", "#producer"],
            CreatorCategory.PHOTOGRAPHER: ["#photography", "#visual", "#capture", "#lens"],
            CreatorCategory.VIDEOGRAPHER: ["#videography", "#filmmaker", "#cinematic"],
            CreatorCategory.BLOGGER: ["#writing", "#content", "#storytelling"],
            CreatorCategory.INFLUENCER: ["#influence", "#social", "#trending"],
            CreatorCategory.COMEDIAN: ["#comedy", "#entertainment", "#humor"],
            CreatorCategory.ARTIST: ["#art", "#creative", "#design"],
            CreatorCategory.PODCASTER: ["#podcast", "#talk", "#voice", "#discussion"]
        }
        
        tags.extend(category_tags.get(category, []))
        return tags[:8]  # Limit to 8 tags
    
    def _identify_collaboration_opportunities(self, category: CreatorCategory) -> List[str]:
        """Identification opportunités collaboration basées sur catégorie"""
        collaboration_matrix = {
            CreatorCategory.MUSICIAN: [
                "Video creators for music videos",
                "Podcasters for interviews", 
                "Influencers for promotion"
            ],
            CreatorCategory.PHOTOGRAPHER: [
                "Models and influencers",
                "Event organizers",
                "Artists for creative projects"
            ],
            CreatorCategory.VIDEOGRAPHER: [
                "Musicians for music videos",
                "Brands for commercial content",
                "Other creators for collaborations"
            ],
            CreatorCategory.BLOGGER: [
                "Photographers for visual content",
                "Experts for interviews",
                "Brands for sponsored content"
            ],
            CreatorCategory.INFLUENCER: [
                "Brands for partnerships",
                "Other influencers for collaborations",
                "Content creators for cross-promotion"
            ],
            CreatorCategory.COMEDIAN: [
                "Video creators for skits",
                "Podcasters for comedy shows",
                "Event organizers for performances"
            ],
            CreatorCategory.ARTIST: [
                "Photographers for portfolio shoots",
                "Galleries for exhibitions",
                "Other artists for collaborations"
            ],
            CreatorCategory.PODCASTER: [
                "Industry experts for interviews",
                "Musicians for music discussions",
                "Other podcasters for cross-episodes"
            ]
        }
        
        return collaboration_matrix.get(category, [])


class ContentClassificationService:
    """
    Service principal pour classification contenu Ainflue.
    Orchestration des modèles + cache + business logic.
    """
    
    def __init__(self, config: ContentClassificationConfig):
        self.config = config
        self.model = MultiModalContentClassifier(config)
        self.cache = {} if config.cache_predictions else None
        
    async def classify_content_batch(self, 
                                   content_inputs: List[ContentInput]) -> List[ContentClassificationResult]:
        """Classification batch pour optimisation performance"""
        results = []
        
        for content_input in content_inputs:
            # Check cache first
            if self.cache and content_input.content_id in self.cache:
                results.append(self.cache[content_input.content_id])
                continue
                
            # Classify content
            result = await self.model.classify_content(content_input)
            
            # Cache result
            if self.cache:
                self.cache[content_input.content_id] = result
                
            results.append(result)
        
        return results
    
    async def get_business_insights(self, results: List[ContentClassificationResult]) -> Dict[str, Any]:
        """Génération insights business agrégés"""
        if not results:
            return {}
        
        insights = {
            "total_content": len(results),
            "category_distribution": {},
            "avg_quality_score": sum(r.quality_score for r in results) / len(results),
            "avg_engagement_potential": sum(r.engagement_potential for r in results) / len(results),
            "avg_monetization_potential": sum(r.monetization_potential for r in results) / len(results),
            "high_value_content_count": sum(1 for r in results if r.business_value_score > 0.8),
            "top_collaboration_opportunities": [],
            "trending_keywords": []
        }
        
        # Analyse distribution catégories
        for result in results:
            category = result.creator_category.value
            insights["category_distribution"][category] = insights["category_distribution"].get(category, 0) + 1
        
        # Top collaboration opportunities
        all_collaborations = []
        for result in results:
            all_collaborations.extend(result.collaboration_opportunities)
        
        from collections import Counter
        collab_counts = Counter(all_collaborations)
        insights["top_collaboration_opportunities"] = [item for item, count in collab_counts.most_common(5)]
        
        # Trending keywords
        all_keywords = []
        for result in results:
            all_keywords.extend(result.seo_keywords)
        
        keyword_counts = Counter(all_keywords)
        insights["trending_keywords"] = [item for item, count in keyword_counts.most_common(10)]
        
        return insights


# Factory function pour faciliter l'utilisation
def create_content_classifier(device: str = "cpu", 
                            batch_size: int = 32) -> ContentClassificationService:
    """Factory function pour créer classificateur contenu"""
    config = ContentClassificationConfig(
        device=device,
        batch_size=batch_size,
        enable_ensemble=True,
        cache_predictions=True
    )
    
    return ContentClassificationService(config)


# Export des classes principales
__all__ = [
    "ContentType",
    "CreatorCategory", 
    "ContentInput",
    "ContentClassificationResult",
    "ContentClassificationConfig",
    "MultiModalContentClassifier",
    "ContentClassificationService",
    "create_content_classifier"
]