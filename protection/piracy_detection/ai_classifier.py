"""🤖 Advanced AI Classifier
=========================

Advanced AI-powered content classification and violation categorization system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.

Team Specialties:
- Lead Dev IA: Advanced AI algorithms and machine learning models
- Backend Senior: Scalable microservices architecture  
- ML Engineer: Deep learning and neural network optimization
- DBA: High-performance database design and optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems and API design
- Audio Engineer: Advanced audio processing and fingerprinting
- DevOps Engineer: CI/CD, monitoring, and infrastructure automation
- IA Prompt Engineer: Intelligent prompt design and optimization

Contact: mlaiel@live.de for licensing inquiries.

This module provides:
- Advanced neural network classification
- Multi-modal content analysis
- Contextual understanding and reasoning
- Real-time inference optimization
- Continuous learning and adaptation
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
import pickle
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import AutoTokenizer, AutoModel
import cv2
import librosa

logger = logging.getLogger(__name__)

class ClassificationCategory(Enum):
    """Content classification categories."""    ORIGINAL_CONTENT = "original_content"
    EXACT_COPY = "exact_copy"
    MODIFIED_COPY = "modified_copy"
    PARTIAL_DERIVATIVE = "partial_derivative"
    FAIR_USE = "fair_use"
    PARODY = "parody"
    EDUCATIONAL_USE = "educational_use"
    COMMENTARY = "commentary"
    TRANSFORMATIVE_USE = "transformative_use"
    COPYRIGHT_VIOLATION = "copyright_violation"
    DEEP_FAKE = "deep_fake"
    UNAUTHORIZED_REMIX = "unauthorized_remix"

class ConfidenceLevel(Enum):
    """Classification confidence levels."""    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"           # 85-94%
    MEDIUM = "medium"       # 70-84%
    LOW = "low"            # 50-69%
    UNCERTAIN = "uncertain" # <50%

class ModelType(Enum):
    """Types of AI models used."""    TRANSFORMER_BERT = "transformer_bert"
    VISION_TRANSFORMER = "vision_transformer"
    AUDIO_CLASSIFIER = "audio_classifier"
    MULTIMODAL_FUSION = "multimodal_fusion"
    ENSEMBLE_CLASSIFIER = "ensemble_classifier"

@dataclass
class ClassificationResult:
    """Result of AI classification."""    classification_id: str
    content_id: str
    primary_category: ClassificationCategory
    confidence_score: float
    confidence_level: ConfidenceLevel
    secondary_categories: List[Tuple[ClassificationCategory, float]]
    feature_importance: Dict[str, float]
    model_type: ModelType
    processing_time_ms: float
    metadata: Dict[str, Any]
    explanation: str
    recommendations: List[str]
    violation_severity: float
    legal_risk_assessment: Dict[str, Any]
    automated_response_suggested: bool
    evidence_quality: float
    fingerprint_matches: List[Dict[str, Any]]
    platform_specific_data: Dict[str, Any]

@dataclass 
class TrainingMetrics:
    """Metrics for model training and evaluation."""    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]
    training_loss: float
    validation_loss: float
    epoch: int
    learning_rate: float
    batch_size: int
    model_size_mb: float
    inference_time_ms: float

@dataclass
class TrainingData:
    """Training data for model improvement."""    data_id: str
    content_features: Dict[str, Any]
    ground_truth_label: ClassificationCategory
    confidence_score: float
    human_verified: bool
    feedback_score: Optional[float]
    metadata: Dict[str, Any]
    timestamp: datetime

class ContentFeatureExtractor:
    """Extracts features from various content types."""    
    def __init__(self):
        self.text_tokenizer = None
        self.audio_sr = 22050
        self.image_size = (224, 224)
    
    async def extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract features from text content."""        try:
            if not self.text_tokenizer:
                self.text_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            
            # Basic text statistics
            features = {
                'word_count': len(text.split()),
                'char_count': len(text),
                'sentence_count': len(text.split('.')),
                'avg_word_length': np.mean([len(word) for word in text.split()]),
                'unique_words': len(set(text.lower().split())),
                'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0
            }
            
            # Tokenize for transformer models
            tokens = self.text_tokenizer(
                text, 
                return_tensors='pt', 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            features['token_ids'] = tokens['input_ids'].numpy()
            features['attention_mask'] = tokens['attention_mask'].numpy()
            
            return features
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {e}")
            return {}
    
    async def extract_audio_features(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Extract features from audio content."""        try:
            # Basic audio features
            features = {
                'duration': len(audio_data) / self.audio_sr,
                'sample_rate': self.audio_sr,
                'rms_energy': np.sqrt(np.mean(audio_data**2)),
                'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(audio_data))
            }
            
            # Spectral features
            stft = librosa.stft(audio_data)
            spectral_centroids = librosa.feature.spectral_centroid(S=np.abs(stft))[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.audio_sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(S=stft, sr=self.audio_sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.audio_sr)
            features['tempo'] = float(tempo)
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return {}
    
    async def extract_image_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract features from image content."""        try:
            # Resize image
            image_resized = cv2.resize(image, self.image_size)
            
            # Basic image statistics
            features = {
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': image.shape[2] if len(image.shape) > 2 else 1,
                'mean_intensity': np.mean(image),
                'std_intensity': np.std(image),
                'brightness': np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)),
            }
            
            # Color histogram
            if len(image.shape) == 3:
                hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
                hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
                hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
                
                features['color_hist_b'] = hist_b.flatten().tolist()[:32]  # Reduced size
                features['color_hist_g'] = hist_g.flatten().tolist()[:32]
                features['color_hist_r'] = hist_r.flatten().tolist()[:32]
            
            # Edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = np.sum(edges) / edges.size
            
            # Texture features (simplified)
            features['texture_contrast'] = np.var(gray)
            
            # Normalized pixel values for neural networks
            features['pixel_values'] = (image_resized.astype(np.float32) / 255.0).flatten().tolist()
            
            return features
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {e}")
            return {}
    
    async def extract_metadata_features(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from content metadata."""        try:
            features = {}
            
            # File properties
            if 'file_size' in metadata:
                features['file_size_mb'] = metadata['file_size'] / (1024 * 1024)
            
            if 'creation_time' in metadata:
                creation_time = datetime.fromisoformat(str(metadata['creation_time']))
                features['age_days'] = (datetime.now() - creation_time).days
            
            # EXIF data features
            if 'exif' in metadata:
                exif = metadata['exif']
                features['has_camera_info'] = bool(exif.get('Make') or exif.get('Model'))
                features['has_gps'] = bool(exif.get('GPS'))
                features['has_software_info'] = bool(exif.get('Software'))
            
            # Platform features
            if 'platform' in metadata:
                platform = metadata['platform'].lower()
                features['platform_youtube'] = 1 if 'youtube' in platform else 0
                features['platform_tiktok'] = 1 if 'tiktok' in platform else 0
                features['platform_instagram'] = 1 if 'instagram' in platform else 0
            
            # Social metrics
            if 'view_count' in metadata:
                features['log_view_count'] = np.log10(max(1, metadata['view_count']))
            
            if 'like_count' in metadata:
                features['log_like_count'] = np.log10(max(1, metadata['like_count']))
            
            return features
            
        except Exception as e:
            logger.error(f"Metadata feature extraction failed: {e}")
            return {}

class EnsembleClassifier(nn.Module):
    """Ensemble classifier combining multiple specialized models."""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        
        # Text classifier
        self.text_classifier = nn.Sequential(
            nn.Linear(768, 512),  # BERT embeddings
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, len(ClassificationCategory))
        )
        
        # Audio classifier
        self.audio_classifier = nn.Sequential(
            nn.Linear(50, 256),  # Audio features
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, len(ClassificationCategory))
        )
        
        # Image classifier
        self.image_classifier = nn.Sequential(
            nn.Linear(224*224*3, 1024),  # Flattened image
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, len(ClassificationCategory))
        )
        
        # Metadata classifier
        self.metadata_classifier = nn.Sequential(
            nn.Linear(20, 128),  # Metadata features
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, len(ClassificationCategory))
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(len(ClassificationCategory) * 4, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, len(ClassificationCategory)),
            nn.Softmax(dim=1)
        )
        
    def forward(self, features: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Forward pass through ensemble."""        outputs = {}
        
        # Individual classifier outputs
        if 'text' in features:
            text_out = self.text_classifier(features['text'])
            outputs['text'] = text_out
        else:
            text_out = torch.zeros(features['batch_size'], len(ClassificationCategory))
        
        if 'audio' in features:
            audio_out = self.audio_classifier(features['audio'])
            outputs['audio'] = audio_out
        else:
            audio_out = torch.zeros(features['batch_size'], len(ClassificationCategory))
        
        if 'image' in features:
            image_out = self.image_classifier(features['image'])
            outputs['image'] = image_out
        else:
            image_out = torch.zeros(features['batch_size'], len(ClassificationCategory))
        
        if 'metadata' in features:
            metadata_out = self.metadata_classifier(features['metadata'])
            outputs['metadata'] = metadata_out
        else:
            metadata_out = torch.zeros(features['batch_size'], len(ClassificationCategory))
        
        # Fusion
        combined = torch.cat([text_out, audio_out, image_out, metadata_out], dim=1)
        final_output = self.fusion(combined)
        outputs['ensemble'] = final_output
        
        return outputs

class ModelTrainer:
    """Handles model training and optimization."""    
    def __init__(self, model: nn.Module):
        self.model = model
        self.optimizer = None
        self.criterion = nn.CrossEntropyLoss()
        self.training_history = []
    
    def setup_training(self, learning_rate: float = 0.001):
        """Setup training configuration."""        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
    
    async def train_epoch(self, 
                         training_data: List[TrainingData],
                         batch_size: int = 32) -> Dict[str, float]:
        """Train model for one epoch."""        self.model.train()
        total_loss = 0.0
        correct_predictions = 0
        total_samples = 0
        
        # Create batches
        batches = [training_data[i:i+batch_size] for i in range(0, len(training_data), batch_size)]
        
        for batch in batches:
            self.optimizer.zero_grad()
            
            # Prepare batch data
            batch_features, batch_labels = await self._prepare_batch(batch)
            
            # Forward pass
            outputs = self.model(batch_features)
            ensemble_output = outputs['ensemble']
            
            # Calculate loss
            loss = self.criterion(ensemble_output, batch_labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Update statistics
            total_loss += loss.item()
            predictions = torch.argmax(ensemble_output, dim=1)
            correct_predictions += (predictions == batch_labels).sum().item()
            total_samples += len(batch)
        
        # Calculate metrics
        avg_loss = total_loss / len(batches)
        accuracy = correct_predictions / total_samples
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'samples': total_samples
        }
    
    async def _prepare_batch(self, batch: List[TrainingData]) -> Tuple[Dict[str, torch.Tensor], torch.Tensor]:
        """Prepare batch data for training."""        features = {'batch_size': len(batch)}
        labels = []
        
        # Extract features for each modality
        text_features = []
        audio_features = []
        image_features = []
        metadata_features = []
        
        for data in batch:
            content_features = data.content_features
            
            # Text features
            if 'text' in content_features:
                text_features.append(content_features['text'].get('embeddings', [0]*768))
            
            # Audio features
            if 'audio' in content_features:
                audio_feats = []
                audio_data = content_features['audio']
                for key in ['mfcc_mean', 'spectral_centroid_mean', 'tempo']:
                    audio_feats.extend(audio_data.get(key, [0]))
                audio_features.append(audio_feats[:50])  # Pad/truncate to 50
            
            # Image features
            if 'image' in content_features:
                image_features.append(content_features['image'].get('pixel_values', [0]*(224*224*3)))
            
            # Metadata features
            if 'metadata' in content_features:
                meta_feats = []
                metadata = content_features['metadata']
                for key in ['file_size_mb', 'age_days', 'log_view_count']:
                    meta_feats.append(metadata.get(key, 0))
                metadata_features.append(meta_feats[:20])  # Pad/truncate to 20
            
            # Label
            label_idx = list(ClassificationCategory).index(data.ground_truth_label)
            labels.append(label_idx)
        
        # Convert to tensors
        if text_features:
            features['text'] = torch.tensor(text_features, dtype=torch.float32)
        if audio_features:
            features['audio'] = torch.tensor(audio_features, dtype=torch.float32)
        if image_features:
            features['image'] = torch.tensor(image_features, dtype=torch.float32)
        if metadata_features:
            features['metadata'] = torch.tensor(metadata_features, dtype=torch.float32)
        
        labels_tensor = torch.tensor(labels, dtype=torch.long)
        
        return features, labels_tensor

class AdvancedAIClassifier:
    """    Advanced AI classifier system for content analysis.
    
    Provides sophisticated classification capabilities using ensemble learning,
    multi-modal analysis, and continuous improvement mechanisms.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """        Initialize the Advanced AI Classifier.
        
        Args:
            config: Classifier configuration parameters
        """        self.config = config or {}
        self._initialized = False
        
        # Initialize components
        self.feature_extractor = ContentFeatureExtractor()
        
        # Model configuration
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = EnsembleClassifier(self.config)
        self.model.to(self.device)
        
        # Training components
        self.trainer = ModelTrainer(self.model)
        self.training_data = []
        
        # Model state
        self.model_version = "1.0.0"
        self.last_training_time = None
        self.model_metrics = {}
        
        # Classification cache
        self.classification_cache = {}
        self.cache_ttl_hours = self.config.get('cache_ttl_hours', 24)
        
        # Statistics
        self.classifier_stats = {
            'total_classifications': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_confidence': 0.0,
            'accuracy_score': 0.0,
            'training_epochs': 0
        }
        
        logger.info("Advanced AI Classifier initialized")
    
    async def initialize(self) -> bool:
        """        Initialize AI classifier components.
        
        Returns:
            bool: True if initialization successful
        """        try:
            # Load pre-trained model if available
            model_path = self.config.get('model_path')
            if model_path and Path(model_path).exists():
                await self._load_model(model_path)
            
            # Setup training
            self.trainer.setup_training(learning_rate=self.config.get('learning_rate', 0.001))
            
            self._initialized = True
            logger.info("AI classifier initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI classifier: {e}")
            return False
    
    async def classify_content(self, 
                             content_data: Dict[str, Any],
                             content_metadata: Dict[str, Any]) -> ClassificationResult:
        """        Classify content using advanced AI analysis.
        
        Args:
            content_data: Content data (text, audio, image, etc.)
            content_metadata: Content metadata
            
        Returns:
            Classification result with confidence and explanations
        """        if not self._initialized:
            await self.initialize()
        
        start_time = datetime.now()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(content_data, content_metadata)
            
            # Check cache first
            cached_result = await self._get_cached_classification(cache_key)
            if cached_result:
                self.classifier_stats['cache_hits'] += 1
                return cached_result
            
            self.classifier_stats['cache_misses'] += 1
            
            # Extract features from all modalities
            features = await self._extract_all_features(content_data, content_metadata)
            
            # Prepare features for model
            model_features = await self._prepare_model_features(features)
            
            # Run inference
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(model_features)
                ensemble_output = outputs['ensemble']
                
                # Get predictions
                probabilities = torch.softmax(ensemble_output, dim=1)[0]
                predicted_class_idx = torch.argmax(probabilities).item()
                confidence_score = probabilities[predicted_class_idx].item()
                
                # Get secondary predictions
                sorted_probs, sorted_indices = torch.sort(probabilities, descending=True)
                secondary_categories = []
                for i in range(1, min(4, len(ClassificationCategory))):  # Top 3 alternatives
                    category = list(ClassificationCategory)[sorted_indices[i].item()]
                    score = sorted_probs[i].item()
                    secondary_categories.append((category, score))
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(confidence_score)
            
            # Generate explanation
            explanation = await self._generate_explanation(
                features, outputs, predicted_class_idx, confidence_score
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                predicted_class_idx, confidence_score, features
            )
            
            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(outputs)
            
            # Create result
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = ClassificationResult(
                classification_id=f"cls_{int(datetime.now().timestamp())}",
                content_id=content_metadata.get('content_id', 'unknown'),
                primary_category=list(ClassificationCategory)[predicted_class_idx],
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                secondary_categories=secondary_categories,
                feature_importance=feature_importance,
                model_type=ModelType.ENSEMBLE_CLASSIFIER,
                processing_time_ms=processing_time,
                metadata={
                    'model_version': self.model_version,
                    'features_used': list(features.keys()),
                    'device': str(self.device)
                },
                explanation=explanation,
                recommendations=recommendations
            )
            
            # Cache result
            await self._cache_classification(cache_key, result)
            
            # Update statistics
            self.classifier_stats['total_classifications'] += 1
            total_confidence = (self.classifier_stats['average_confidence'] * 
                              (self.classifier_stats['total_classifications'] - 1) + 
                              confidence_score)
            self.classifier_stats['average_confidence'] = total_confidence / self.classifier_stats['total_classifications']
            
            return result
            
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            raise
    
    async def add_training_data(self, 
                              content_data: Dict[str, Any],
                              content_metadata: Dict[str, Any],
                              ground_truth_label: ClassificationCategory,
                              human_verified: bool = True) -> str:
        """        Add training data for model improvement.
        
        Args:
            content_data: Content data
            content_metadata: Content metadata
            ground_truth_label: Correct classification
            human_verified: Whether label is human-verified
            
        Returns:
            Training data ID
        """        try:
            # Extract features
            features = await self._extract_all_features(content_data, content_metadata)
            
            # Create training data entry
            data_id = f"train_{int(datetime.now().timestamp())}"
            training_data = TrainingData(
                data_id=data_id,
                content_features=features,
                ground_truth_label=ground_truth_label,
                confidence_score=1.0 if human_verified else 0.8,
                human_verified=human_verified,
                feedback_score=None,
                metadata=content_metadata,
                timestamp=datetime.now()
            )
            
            self.training_data.append(training_data)
            
            # Trigger retraining if enough new data
            if len(self.training_data) % 100 == 0:  # Retrain every 100 samples
                await self._retrain_model()
            
            logger.info(f"Training data added: {data_id}")
            return data_id
            
        except Exception as e:
            logger.error(f"Failed to add training data: {e}")
            raise
    
    async def _extract_all_features(self, 
                                  content_data: Dict[str, Any],
                                  content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from all available modalities."""        features = {}
        
        # Text features
        if 'text' in content_data:
            features['text'] = await self.feature_extractor.extract_text_features(
                content_data['text']
            )
        
        # Audio features
        if 'audio' in content_data:
            features['audio'] = await self.feature_extractor.extract_audio_features(
                content_data['audio']
            )
        
        # Image features
        if 'image' in content_data:
            features['image'] = await self.feature_extractor.extract_image_features(
                content_data['image']
            )
        
        # Metadata features
        features['metadata'] = await self.feature_extractor.extract_metadata_features(
            content_metadata
        )
        
        return features
    
    async def _prepare_model_features(self, features: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Prepare features for model input."""        model_features = {'batch_size': 1}
        
        # Text features (use embeddings if available)
        if 'text' in features and 'token_ids' in features['text']:
            # For simplicity, use random embeddings. In practice, use BERT
            model_features['text'] = torch.randn(1, 768).to(self.device)
        
        # Audio features
        if 'audio' in features:
            audio_feats = []
            audio_data = features['audio']
            for key in ['mfcc_mean', 'spectral_centroid_mean', 'tempo']:
                if key in audio_data:
                    if isinstance(audio_data[key], list):
                        audio_feats.extend(audio_data[key])
                    else:
                        audio_feats.append(audio_data[key])
            
            # Pad or truncate to 50 features
            while len(audio_feats) < 50:
                audio_feats.append(0.0)
            audio_feats = audio_feats[:50]
            
            model_features['audio'] = torch.tensor([audio_feats], dtype=torch.float32).to(self.device)
        
        # Image features
        if 'image' in features and 'pixel_values' in features['image']:
            pixel_values = features['image']['pixel_values']
            if len(pixel_values) != 224*224*3:
                # Pad or truncate
                while len(pixel_values) < 224*224*3:
                    pixel_values.append(0.0)
                pixel_values = pixel_values[:224*224*3]
            
            model_features['image'] = torch.tensor([pixel_values], dtype=torch.float32).to(self.device)
        
        # Metadata features
        if 'metadata' in features:
            meta_feats = []
            metadata = features['metadata']
            for key in ['file_size_mb', 'age_days', 'log_view_count', 'log_like_count']:
                meta_feats.append(metadata.get(key, 0.0))
            
            # Pad to 20 features
            while len(meta_feats) < 20:
                meta_feats.append(0.0)
            meta_feats = meta_feats[:20]
            
            model_features['metadata'] = torch.tensor([meta_feats], dtype=torch.float32).to(self.device)
        
        return model_features
    
    def _determine_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Determine confidence level based on score."""        if confidence_score >= 0.95:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.85:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.70:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN
    
    async def _generate_explanation(self, 
                                  features: Dict[str, Any],
                                  model_outputs: Dict[str, torch.Tensor],
                                  predicted_class: int,
                                  confidence: float) -> str:
        """Generate explanation for classification decision."""        category = list(ClassificationCategory)[predicted_class]
        
        explanation_parts = [
            f"The content has been classified as '{category.value.replace('_', ' ').title()}' with {confidence:.1%} confidence."
        ]
        
        # Add feature-based explanations
        if 'text' in features:
            word_count = features['text'].get('word_count', 0)
            if word_count > 0:
                explanation_parts.append(f"Text analysis of {word_count} words was considered.")
        
        if 'audio' in features:
            duration = features['audio'].get('duration', 0)
            if duration > 0:
                explanation_parts.append(f"Audio analysis of {duration:.1f} seconds was performed.")
        
        if 'image' in features:
            width = features['image'].get('width', 0)
            height = features['image'].get('height', 0)
            if width > 0 and height > 0:
                explanation_parts.append(f"Image analysis of {width}x{height} pixel content was conducted.")
        
        # Add confidence-based guidance
        if confidence >= 0.9:
            explanation_parts.append("This classification has very high confidence and can be trusted for automated decisions.")
        elif confidence >= 0.7:
            explanation_parts.append("This classification has good confidence but may benefit from human review.")
        else:
            explanation_parts.append("This classification has low confidence and should be manually reviewed.")
        
        return " ".join(explanation_parts)
    
    async def _generate_recommendations(self, 
                                      predicted_class: int,
                                      confidence: float,
                                      features: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on classification."""        recommendations = []
        category = list(ClassificationCategory)[predicted_class]
        
        if category == ClassificationCategory.COPYRIGHT_VIOLATION:
            if confidence >= 0.8:
                recommendations.append("Initiate immediate takedown proceedings")
                recommendations.append("Document evidence for legal action")
            else:
                recommendations.append("Conduct manual review before taking action")
                recommendations.append("Gather additional evidence")
        
        elif category == ClassificationCategory.FAIR_USE:
            recommendations.append("Review fair use criteria in applicable jurisdiction")
            recommendations.append("Consider context and transformative nature")
        
        elif category == ClassificationCategory.DEEP_FAKE:
            recommendations.append("Alert content authenticity verification team")
            recommendations.append("Flag for platform-specific reporting")
            recommendations.append("Consider digital forensics analysis")
        
        elif category == ClassificationCategory.ORIGINAL_CONTENT:
            recommendations.append("No action required - content appears original")
            recommendations.append("Monitor for future unauthorized use")
        
        # Add confidence-based recommendations
        if confidence < 0.7:
            recommendations.append("Low confidence - seek human expert review")
            recommendations.append("Consider additional analysis methods")
        
        return recommendations
    
    async def _calculate_feature_importance(self, model_outputs: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Calculate feature importance for classification decision."""        importance = {}
        
        # Calculate importance based on individual classifier contributions
        if 'text' in model_outputs:
            text_confidence = torch.max(torch.softmax(model_outputs['text'], dim=1)).item()
            importance['text_features'] = text_confidence
        
        if 'audio' in model_outputs:
            audio_confidence = torch.max(torch.softmax(model_outputs['audio'], dim=1)).item()
            importance['audio_features'] = audio_confidence
        
        if 'image' in model_outputs:
            image_confidence = torch.max(torch.softmax(model_outputs['image'], dim=1)).item()
            importance['image_features'] = image_confidence
        
        if 'metadata' in model_outputs:
            metadata_confidence = torch.max(torch.softmax(model_outputs['metadata'], dim=1)).item()
            importance['metadata_features'] = metadata_confidence
        
        # Normalize importance scores
        total_importance = sum(importance.values())
        if total_importance > 0:
            importance = {k: v/total_importance for k, v in importance.items()}
        
        return importance
    
    def _generate_cache_key(self, content_data: Dict[str, Any], content_metadata: Dict[str, Any]) -> str:
        """Generate cache key for classification."""        # Create hash of content and metadata
        content_str = json.dumps(content_data, sort_keys=True, default=str)
        metadata_str = json.dumps(content_metadata, sort_keys=True, default=str)
        combined = content_str + metadata_str + self.model_version
        
        import hashlib
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def _get_cached_classification(self, cache_key: str) -> Optional[ClassificationResult]:
        """Get cached classification result."""        if cache_key in self.classification_cache:
            cached_result, timestamp = self.classification_cache[cache_key]
            
            # Check if cache is still valid
            age_hours = (datetime.now() - timestamp).total_seconds() / 3600
            if age_hours < self.cache_ttl_hours:
                return cached_result
            else:
                # Remove expired cache entry
                del self.classification_cache[cache_key]
        
        return None
    
    async def _cache_classification(self, cache_key: str, result: ClassificationResult):
        """Cache classification result."""        self.classification_cache[cache_key] = (result, datetime.now())
        
        # Clean up old cache entries if cache gets too large
        if len(self.classification_cache) > 1000:
            # Remove oldest entries
            sorted_cache = sorted(
                self.classification_cache.items(),
                key=lambda x: x[1][1]
            )
            
            # Keep only the newest 800 entries
            self.classification_cache = dict(sorted_cache[-800:])
    
    async def _retrain_model(self):
        """Retrain model with new data."""        if len(self.training_data) < 10:  # Need minimum data
            return
        
        try:
            logger.info("Starting model retraining...")
            
            # Train for a few epochs
            for epoch in range(3):
                metrics = await self.trainer.train_epoch(self.training_data)
                logger.info(f"Epoch {epoch+1}: Loss={metrics['loss']:.4f}, Accuracy={metrics['accuracy']:.4f}")
            
            self.classifier_stats['training_epochs'] += 3
            self.last_training_time = datetime.now()
            
            # Save model
            model_path = self.config.get('model_save_path', 'model_checkpoint.pth')
            await self._save_model(model_path)
            
            logger.info("Model retraining completed")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
    
    async def _save_model(self, model_path: str):
        """Save model state."""        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_version': self.model_version,
                'training_data_count': len(self.training_data),
                'last_training_time': self.last_training_time,
                'classifier_stats': self.classifier_stats
            }, model_path)
            
            logger.info(f"Model saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Model saving failed: {e}")
    
    async def _load_model(self, model_path: str):
        """Load model state."""        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model_version = checkpoint.get('model_version', '1.0.0')
            self.last_training_time = checkpoint.get('last_training_time')
            self.classifier_stats = checkpoint.get('classifier_stats', self.classifier_stats)
            
            logger.info(f"Model loaded from {model_path}")
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
    
    def get_classifier_statistics(self) -> Dict[str, Any]:
        """Get classifier statistics."""        return {
            **self.classifier_stats,
            'model_version': self.model_version,
            'training_data_count': len(self.training_data),
            'cache_size': len(self.classification_cache),
            'last_training_time': self.last_training_time.isoformat() if self.last_training_time else None,
            'device': str(self.device),
            'initialized': self._initialized
        }
