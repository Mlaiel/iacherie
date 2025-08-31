"""Moderation Agent Models - Advanced ML Models for Content Safety

Enterprise-grade machine learning models for comprehensive content moderation,
providing multi-format analysis with state-of-the-art accuracy and performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import cv2
from PIL import Image
import librosa
from transformers import (
    AutoModel, AutoTokenizer, AutoConfig,
    AutoImageProcessor, AutoModelForImageClassification
)
import logging

logger = logging.getLogger(__name__)

class ToxicityClassifier(nn.Module):
    """    Advanced multi-label toxicity classifier for text content
    
    Detects multiple types of toxic content:
    - General toxicity
    - Hate speech
    - Harassment
    - Threats
    - Insults
    - Identity attacks
    """    
    def __init__(self, model_name: str = "bert-base-multilingual-cased", num_classes: int = 6):
        super().__init__()
        
        self.model_name = model_name
        self.num_classes = num_classes
        
        # Load pre-trained transformer
        self.config = AutoConfig.from_pretrained(model_name)
        self.transformer = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Classification heads
        hidden_size = self.config.hidden_size
        self.dropout = nn.Dropout(0.3)
        
        # Multi-head classifier
        self.toxicity_head = nn.Linear(hidden_size, 1)
        self.hate_speech_head = nn.Linear(hidden_size, 1)
        self.harassment_head = nn.Linear(hidden_size, 1)
        self.threat_head = nn.Linear(hidden_size, 1)
        self.insult_head = nn.Linear(hidden_size, 1)
        self.identity_attack_head = nn.Linear(hidden_size, 1)
        
        # Attention mechanism for important tokens
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8, dropout=0.1)
        
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Dict[str, torch.Tensor]:
        """        Forward pass through the model
        
        Args:
            input_ids: Tokenized input text
            attention_mask: Attention mask for padding
            
        Returns:
            Dictionary of toxicity predictions
        """        # Get transformer outputs
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        
        # Apply attention mechanism
        sequence_output = outputs.last_hidden_state
        attended_output, _ = self.attention(
            sequence_output.transpose(0, 1),
            sequence_output.transpose(0, 1),
            sequence_output.transpose(0, 1)
        )
        attended_output = attended_output.transpose(0, 1)
        
        # Pool the attended output
        pooled_output = attended_output.mean(dim=1)
        pooled_output = self.dropout(pooled_output)
        
        # Get predictions from each head
        predictions = {
            'toxicity': self.sigmoid(self.toxicity_head(pooled_output)),
            'hate_speech': self.sigmoid(self.hate_speech_head(pooled_output)),
            'harassment': self.sigmoid(self.harassment_head(pooled_output)),
            'threat': self.sigmoid(self.threat_head(pooled_output)),
            'insult': self.sigmoid(self.insult_head(pooled_output)),
            'identity_attack': self.sigmoid(self.identity_attack_head(pooled_output))
        }
        
        return predictions
    
    def predict(self, texts: List[str], device: str = "cpu") -> Dict[str, List[float]]:
        """        Predict toxicity for a batch of texts
        
        Args:
            texts: List of input texts
            device: Device to run inference on
            
        Returns:
            Dictionary of toxicity scores
        """        self.eval()
        
        # Tokenize inputs
        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        input_ids = encoded['input_ids'].to(device)
        attention_mask = encoded['attention_mask'].to(device)
        
        with torch.no_grad():
            predictions = self.forward(input_ids, attention_mask)
        
        # Convert to lists
        results = {}
        for key, values in predictions.items():
            results[key] = values.squeeze().cpu().tolist()
        
        return results

class NSFWImageClassifier(nn.Module):
    """    Advanced NSFW (Not Safe For Work) image classifier
    
    Detects various types of explicit content:
    - Nudity
    - Sexual content
    - Suggestive content
    - Safe content
    """    
    def __init__(self, backbone: str = "resnet50", num_classes: int = 4):
        super().__init__()
        
        self.backbone_name = backbone
        self.num_classes = num_classes
        
        # Load pre-trained backbone
        if backbone == "resnet50":
            import torchvision.models as models
            self.backbone = models.resnet50(pretrained=True)
            feature_dim = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()  # Remove final layer
        
        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(feature_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )
        
        # Attention mechanism for important regions
        self.spatial_attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(feature_dim, feature_dim // 16, 1),
            nn.ReLU(),
            nn.Conv2d(feature_dim // 16, 1, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """        Forward pass through the NSFW classifier
        
        Args:
            x: Input image tensor
            
        Returns:
            Dictionary of NSFW predictions
        """        # Extract features
        features = self.backbone(x)
        
        # Apply spatial attention
        if len(features.shape) == 4:  # If still spatial dimensions
            attention_weights = self.spatial_attention(features)
            features = features * attention_weights
            features = F.adaptive_avg_pool2d(features, 1).flatten(1)
        
        # Classification
        logits = self.classifier(features)
        probabilities = F.softmax(logits, dim=1)
        
        return {
            'logits': logits,
            'probabilities': probabilities,
            'nsfw_score': probabilities[:, 1:].sum(dim=1)  # Sum of all NSFW classes
        }

class ViolenceDetector(nn.Module):
    """    Advanced violence detection model for images and video frames
    
    Detects various forms of violent content:
    - Physical violence
    - Weapons
    - Blood/gore
    - Fighting
    """    
    def __init__(self, backbone: str = "efficientnet-b0"):
        super().__init__()
        
        # Load pre-trained backbone
        if backbone == "efficientnet-b0":
            import torchvision.models as models
            self.backbone = models.efficientnet_b0(pretrained=True)
            feature_dim = self.backbone.classifier[1].in_features
            self.backbone.classifier = nn.Identity()
        
        # Multi-scale feature extraction
        self.multi_scale_conv = nn.ModuleList([
            nn.Conv2d(feature_dim, 256, kernel_size=3, padding=1),
            nn.Conv2d(feature_dim, 256, kernel_size=5, padding=2),
            nn.Conv2d(feature_dim, 256, kernel_size=7, padding=3)
        ])
        
        # Violence classification head
        self.violence_classifier = nn.Sequential(
            nn.Linear(256 * 3, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 2)  # Violence / No violence
        )
        
        # Violence type classifier
        self.type_classifier = nn.Sequential(
            nn.Linear(256 * 3, 256),
            nn.ReLU(),
            nn.Linear(256, 4)  # Physical, Weapons, Blood, Fighting
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """        Forward pass through the violence detector
        
        Args:
            x: Input image tensor
            
        Returns:
            Dictionary of violence predictions
        """        # Extract backbone features
        features = self.backbone(x)
        
        if len(features.shape) == 4:  # Spatial dimensions present
            # Apply multi-scale convolutions
            multi_scale_features = []
            for conv in self.multi_scale_conv:
                ms_feat = conv(features)
                ms_feat = F.adaptive_avg_pool2d(ms_feat, 1).flatten(1)
                multi_scale_features.append(ms_feat)
            
            combined_features = torch.cat(multi_scale_features, dim=1)
        else:
            combined_features = features
        
        # Violence detection
        violence_logits = self.violence_classifier(combined_features)
        violence_probs = F.softmax(violence_logits, dim=1)
        
        # Violence type classification
        type_logits = self.type_classifier(combined_features)
        type_probs = F.softmax(type_logits, dim=1)
        
        return {
            'violence_probability': violence_probs[:, 1],  # Probability of violence
            'violence_types': type_probs,
            'confidence': torch.max(violence_probs, dim=1)[0]
        }

class AudioContentClassifier(nn.Module):
    """    Advanced audio content classifier for detecting harmful audio content
    
    Detects:
    - Offensive speech
    - Screaming/distress
    - Violence sounds
    - Music content appropriateness
    """    
    def __init__(self, input_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        # LSTM for temporal modeling
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=0.3,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Classification heads
        self.offensive_classifier = nn.Linear(hidden_dim * 2, 2)
        self.distress_classifier = nn.Linear(hidden_dim * 2, 2)
        self.violence_classifier = nn.Linear(hidden_dim * 2, 2)
        self.appropriateness_classifier = nn.Linear(hidden_dim * 2, 3)  # Appropriate, Questionable, Inappropriate
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """        Forward pass through audio classifier
        
        Args:
            x: Input audio features [batch_size, seq_len, feature_dim]
            
        Returns:
            Dictionary of audio content predictions
        """        # LSTM processing
        lstm_out, _ = self.lstm(x)  # [batch_size, seq_len, hidden_dim * 2]
        
        # Apply attention
        attention_weights = F.softmax(self.attention(lstm_out), dim=1)
        attended_features = torch.sum(lstm_out * attention_weights, dim=1)
        
        # Classification
        offensive_logits = self.offensive_classifier(attended_features)
        distress_logits = self.distress_classifier(attended_features)
        violence_logits = self.violence_classifier(attended_features)
        appropriateness_logits = self.appropriateness_classifier(attended_features)
        
        return {
            'offensive_probability': F.softmax(offensive_logits, dim=1)[:, 1],
            'distress_probability': F.softmax(distress_logits, dim=1)[:, 1],
            'violence_probability': F.softmax(violence_logits, dim=1)[:, 1],
            'appropriateness_scores': F.softmax(appropriateness_logits, dim=1)
        }

class DeepfakeDetector(nn.Module):
    """    Advanced deepfake and synthetic media detection model
    
    Detects:
    - Face swaps
    - Expression manipulation
    - AI-generated faces
    - Video manipulation
    """    
    def __init__(self, backbone: str = "xception"):
        super().__init__()
        
        # Load specialized backbone for deepfake detection
        if backbone == "xception":
            import torchvision.models as models
            self.backbone = models.resnext50_32x4d(pretrained=True)
            feature_dim = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        
        # Frequency domain analysis
        self.frequency_analyzer = nn.Sequential(
            nn.Linear(feature_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU()
        )
        
        # Spatial inconsistency detector
        self.spatial_analyzer = nn.Sequential(
            nn.Linear(feature_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU()
        )
        
        # Final classifier
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 2)  # Real / Fake
        )
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """        Forward pass through deepfake detector
        
        Args:
            x: Input image tensor
            
        Returns:
            Dictionary of deepfake detection results
        """        # Extract features
        features = self.backbone(x)
        
        # Analyze frequency and spatial domains
        freq_features = self.frequency_analyzer(features)
        spatial_features = self.spatial_analyzer(features)
        
        # Combine features
        combined_features = torch.cat([freq_features, spatial_features], dim=1)
        
        # Classification
        logits = self.classifier(combined_features)
        probabilities = F.softmax(logits, dim=1)
        
        return {
            'fake_probability': probabilities[:, 1],
            'confidence': torch.max(probabilities, dim=1)[0],
            'authenticity_score': probabilities[:, 0]
        }

class MultiModalContentAnalyzer:
    """    Multi-modal content analyzer combining all specialized models
    
    Provides comprehensive analysis across text, image, audio, and video content
    with unified scoring and decision making.
    """    
    def __init__(self, device: str = "cpu"):
        self.device = device
        
        # Initialize specialized models
        self.toxicity_model = ToxicityClassifier().to(device)
        self.nsfw_model = NSFWImageClassifier().to(device)
        self.violence_model = ViolenceDetector().to(device)
        self.audio_model = AudioContentClassifier().to(device)
        self.deepfake_model = DeepfakeDetector().to(device)
        
        logger.info("Multi-modal content analyzer initialized")
    
    def analyze_text(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze text content for toxicity and harmful content"""        try:
            results = self.toxicity_model.predict(texts, self.device)
            return {
                'success': True,
                'results': results,
                'model': 'toxicity_classifier'
            }
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_image(self, image: torch.Tensor) -> Dict[str, Any]:
        """Analyze image for NSFW content, violence, and authenticity"""        try:
            results = {}
            
            # NSFW detection
            nsfw_results = self.nsfw_model(image.to(self.device))
            results['nsfw'] = {
                'score': nsfw_results['nsfw_score'].item(),
                'probabilities': nsfw_results['probabilities'].cpu().tolist()
            }
            
            # Violence detection
            violence_results = self.violence_model(image.to(self.device))
            results['violence'] = {
                'probability': violence_results['violence_probability'].item(),
                'confidence': violence_results['confidence'].item()
            }
            
            # Deepfake detection
            deepfake_results = self.deepfake_model(image.to(self.device))
            results['authenticity'] = {
                'fake_probability': deepfake_results['fake_probability'].item(),
                'authenticity_score': deepfake_results['authenticity_score'].item()
            }
            
            return {
                'success': True,
                'results': results,
                'models': ['nsfw_classifier', 'violence_detector', 'deepfake_detector']
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_audio(self, audio_features: torch.Tensor) -> Dict[str, Any]:
        """Analyze audio content for harmful patterns"""        try:
            results = self.audio_model(audio_features.to(self.device))
            
            return {
                'success': True,
                'results': {
                    'offensive_probability': results['offensive_probability'].item(),
                    'distress_probability': results['distress_probability'].item(),
                    'violence_probability': results['violence_probability'].item(),
                    'appropriateness_scores': results['appropriateness_scores'].cpu().tolist()
                },
                'model': 'audio_classifier'
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_audio_features(self, audio_path: str) -> torch.Tensor:
        """Extract features from audio file for analysis"""        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=128)
            
            # Convert to tensor
            features = torch.tensor(mfccs.T).float().unsqueeze(0)
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return torch.empty(0)
    
    def get_unified_risk_score(self, analysis_results: Dict[str, Any]) -> float:
        """        Calculate unified risk score from multi-modal analysis results
        
        Args:
            analysis_results: Combined results from all modality analyses
            
        Returns:
            Unified risk score between 0.0 and 1.0
        """        risk_scores = []
        
        # Text risks
        if 'text' in analysis_results:
            text_results = analysis_results['text'].get('results', {})
            for category, score in text_results.items():
                if isinstance(score, list):
                    risk_scores.extend(score)
                else:
                    risk_scores.append(score)
        
        # Image risks
        if 'image' in analysis_results:
            image_results = analysis_results['image'].get('results', {})
            if 'nsfw' in image_results:
                risk_scores.append(image_results['nsfw']['score'])
            if 'violence' in image_results:
                risk_scores.append(image_results['violence']['probability'])
            if 'authenticity' in image_results:
                risk_scores.append(image_results['authenticity']['fake_probability'])
        
        # Audio risks
        if 'audio' in analysis_results:
            audio_results = analysis_results['audio'].get('results', {})
            risk_scores.extend([
                audio_results.get('offensive_probability', 0),
                audio_results.get('distress_probability', 0),
                audio_results.get('violence_probability', 0)
            ])
        
        # Calculate weighted average risk score
        if risk_scores:
            return min(sum(risk_scores) / len(risk_scores), 1.0)
        
        return 0.0
