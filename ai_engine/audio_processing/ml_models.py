"""
🧠 Advanced ML Models for Audio Processing - Deep Learning Engine

State-of-the-art machine learning models for comprehensive audio analysis.
Includes pre-trained and custom models for various audio processing tasks.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
import librosa
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import json
from dataclasses import dataclass
from enum import Enum
import tempfile
import warnings

from .core import AudioProcessor, AudioMetadata
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of ML models available"""
    GENRE_CLASSIFIER = "genre_classifier"
    MOOD_DETECTOR = "mood_detector"
    TEMPO_ESTIMATOR = "tempo_estimator"
    KEY_DETECTOR = "key_detector"
    INSTRUMENT_RECOGNIZER = "instrument_recognizer"
    VOICE_CLASSIFIER = "voice_classifier"
    QUALITY_ASSESSOR = "quality_assessor"
    SIMILARITY_MATCHER = "similarity_matcher"
    ONSET_DETECTOR = "onset_detector"
    BEAT_TRACKER = "beat_tracker"


class ModelArchitecture(Enum):
    """Neural network architectures"""
    CNN_1D = "cnn_1d"
    CNN_2D = "cnn_2d"
    LSTM = "lstm"
    TRANSFORMER = "transformer"
    RESNET = "resnet"
    EFFICIENTNET = "efficientnet"
    HYBRID = "hybrid"


@dataclass
class ModelConfig:
    """Configuration for ML models"""
    model_type: ModelType
    architecture: ModelArchitecture
    input_features: List[str]
    output_classes: List[str]
    sample_rate: int = 22050
    n_mels: int = 128
    n_fft: int = 2048
    hop_length: int = 512
    sequence_length: int = 128
    batch_size: int = 32
    learning_rate: float = 0.001
    dropout_rate: float = 0.3
    hidden_size: int = 256
    num_layers: int = 3


@dataclass
class PredictionResult:
    """Result from model prediction"""
    model_type: ModelType
    predictions: Dict[str, float]
    confidence: float
    features_used: List[str]
    processing_time: float
    metadata: Dict[str, Any] = None


class AudioCNN1D(nn.Module):
    """
     1D Convolutional Neural Network for Audio Features
    
    Optimized for processing audio feature sequences:
    - Temporal pattern recognition
    - Feature extraction from time-series data
    - Classification and regression tasks
    """
    
    def __init__(self, 
                 input_size: int,
                 num_classes: int,
                 hidden_size: int = 256,
                 dropout_rate: float = 0.3):
        super().__init__()
        
        self.conv_layers = nn.Sequential(
            # First conv block
            nn.Conv1d(input_size, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Dropout(dropout_rate),
            
            # Second conv block
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Dropout(dropout_rate),
            
            # Third conv block
            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Dropout(dropout_rate),
        )
        
        # Calculate the size after convolutions
        self.conv_output_size = 256  # This would be calculated dynamically in practice
        
        self.classifier = nn.Sequential(
            nn.Linear(self.conv_output_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 2, num_classes)
        )
    
    def forward(self, x):
        # x shape: (batch_size, features, sequence_length)
        x = self.conv_layers(x)
        
        # Global average pooling
        x = F.adaptive_avg_pool1d(x, 1)
        x = x.view(x.size(0), -1)
        
        # Classification
        x = self.classifier(x)
        return x


class AudioCNN2D(nn.Module):
    """
     2D Convolutional Neural Network for Spectrograms
    
    Specialized for processing audio spectrograms:
    - Frequency-time pattern recognition
    - Image-like audio representations
    - Advanced feature extraction
    """
    
    def __init__(self, 
                 num_classes: int,
                 input_channels: int = 1,
                 hidden_size: int = 256,
                 dropout_rate: float = 0.3):
        super().__init__()
        
        self.conv_layers = nn.Sequential(
            # First conv block
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(dropout_rate),
            
            # Second conv block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(dropout_rate),
            
            # Third conv block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(dropout_rate),
            
            # Fourth conv block
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),  # Fixed size output
            nn.Dropout2d(dropout_rate),
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(256 * 4 * 4, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 2, num_classes)
        )
    
    def forward(self, x):
        # x shape: (batch_size, channels, height, width)
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)  # Flatten
        x = self.classifier(x)
        return x


class AudioLSTM(nn.Module):
    """
     LSTM Network for Sequential Audio Analysis
    
    Optimized for temporal dependencies:
    - Long-term pattern recognition
    - Sequential audio analysis
    - Time-series prediction
    """
    
    def __init__(self,
                 input_size: int,
                 num_classes: int,
                 hidden_size: int = 256,
                 num_layers: int = 3,
                 dropout_rate: float = 0.3,
                 bidirectional: bool = True):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout_rate if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )
        
        lstm_output_size = hidden_size * (2 if bidirectional else 1)
        
        self.attention = nn.Sequential(
            nn.Linear(lstm_output_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, 1),
            nn.Softmax(dim=1)
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(lstm_output_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 2, num_classes)
        )
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        lstm_out, _ = self.lstm(x)
        
        # Apply attention mechanism
        attention_weights = self.attention(lstm_out)
        attended_output = torch.sum(lstm_out * attention_weights, dim=1)
        
        # Classification
        output = self.classifier(attended_output)
        return output


class AudioTransformer(nn.Module):
    """
     Transformer Network for Audio Analysis
    
    State-of-the-art attention-based architecture:
    - Self-attention mechanisms
    - Parallel processing
    - Long-range dependencies
    """
    
    def __init__(self,
                 input_size: int,
                 num_classes: int,
                 d_model: int = 256,
                 nhead: int = 8,
                 num_layers: int = 6,
                 dropout_rate: float = 0.3):
        super().__init__()
        
        self.d_model = d_model
        self.input_projection = nn.Linear(input_size, d_model)
        self.positional_encoding = self._create_positional_encoding(1000, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout_rate,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, 
            num_layers=num_layers
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(d_model // 2, num_classes)
        )
    
    def _create_positional_encoding(self, max_len: int, d_model: int) -> torch.Tensor:
        """Create positional encoding for transformer"""
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        return pe.unsqueeze(0)
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        batch_size, seq_len, _ = x.shape
        
        # Project to model dimension
        x = self.input_projection(x)
        
        # Add positional encoding
        if seq_len <= self.positional_encoding.size(1):
            pos_enc = self.positional_encoding[:, :seq_len, :].to(x.device)
            x = x + pos_enc
        
        # Apply transformer
        x = self.transformer_encoder(x)
        
        # Global average pooling
        x = torch.mean(x, dim=1)
        
        # Classification
        x = self.classifier(x)
        return x


class MLModelManager:
    """
    🤖 Advanced Machine Learning Model Manager
    
    Comprehensive ML pipeline for audio processing:
    - Multi-model ensemble
    - Automatic feature extraction
    - Model training and inference
    - Performance optimization
    - Model persistence and loading
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None,
                 models_directory: Optional[Path] = None):
        self.config = config or AudioProcessingConfig()
        self.models_directory = models_directory or Path("models")
        self.models_directory.mkdir(parents=True, exist_ok=True)
        
        self.audio_processor = AudioProcessor(config)
        
        # Model registry
        self.models: Dict[ModelType, Any] = {}
        self.scalers: Dict[ModelType, StandardScaler] = {}
        self.model_configs: Dict[ModelType, ModelConfig] = {}
        
        # Feature extractors
        self.feature_extractors = self._init_feature_extractors()
        
        # Initialize default model configurations
        self._init_default_configs()
        
        logger.info("MLModelManager initialized")
    
    def _init_feature_extractors(self) -> Dict[str, Callable]:
        """Initialize feature extraction functions"""



        return {
            'mfcc': self._extract_mfcc,
            'chroma': self._extract_chroma,
            'spectral_contrast': self._extract_spectral_contrast,
            'tonnetz': self._extract_tonnetz,
            'zero_crossing_rate': self._extract_zcr,
            'spectral_centroid': self._extract_spectral_centroid,
            'spectral_bandwidth': self._extract_spectral_bandwidth,
            'spectral_rolloff': self._extract_spectral_rolloff,
            'tempo': self._extract_tempo,
            'onset_strength': self._extract_onset_strength,
            'harmonic_percussive': self._extract_harmonic_percussive,
            'mel_spectrogram': self._extract_mel_spectrogram,
            'rms_energy': self._extract_rms_energy
        }
    
    def _init_default_configs(self):
        """Initialize default model configurations"""
        self.model_configs = {
            ModelType.GENRE_CLASSIFIER: ModelConfig(
                model_type=ModelType.GENRE_CLASSIFIER,
                architecture=ModelArchitecture.CNN_2D,
                input_features=['mel_spectrogram'],
                output_classes=['rock', 'pop', 'classical', 'jazz', 'electronic', 
                              'hip_hop', 'country', 'blues', 'reggae', 'metal']
            ),
            
            ModelType.MOOD_DETECTOR: ModelConfig(
                model_type=ModelType.MOOD_DETECTOR,
                architecture=ModelArchitecture.HYBRID,
                input_features=['mfcc', 'chroma', 'spectral_contrast', 'tonnetz'],
                output_classes=['happy', 'sad', 'energetic', 'calm', 'angry', 
                              'romantic', 'mysterious', 'uplifting']
            ),
            
            ModelType.TEMPO_ESTIMATOR: ModelConfig(
                model_type=ModelType.TEMPO_ESTIMATOR,
                architecture=ModelArchitecture.LSTM,
                input_features=['onset_strength', 'tempo'],
                output_classes=['tempo_bpm']  # Regression task
            ),
            
            ModelType.KEY_DETECTOR: ModelConfig(
                model_type=ModelType.KEY_DETECTOR,
                architecture=ModelArchitecture.CNN_1D,
                input_features=['chroma'],
                output_classes=['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            ),
            
            ModelType.INSTRUMENT_RECOGNIZER: ModelConfig(
                model_type=ModelType.INSTRUMENT_RECOGNIZER,
                architecture=ModelArchitecture.CNN_2D,
                input_features=['mel_spectrogram', 'mfcc'],
                output_classes=['piano', 'guitar', 'violin', 'drums', 'flute', 
                              'trumpet', 'saxophone', 'vocals', 'bass', 'synthesizer']
            ),
            
            ModelType.QUALITY_ASSESSOR: ModelConfig(
                model_type=ModelType.QUALITY_ASSESSOR,
                architecture=ModelArchitecture.HYBRID,
                input_features=['spectral_centroid', 'spectral_bandwidth', 'rms_energy'],
                output_classes=['quality_score']  # Regression task
            )
        }
    
    async def extract_features(self,
                             audio_data: np.ndarray,
                             sample_rate: int,
                             feature_names: List[str]) -> Dict[str, np.ndarray]:
        """Extract specified features from audio data"""



        try:
            features = {}
            
            for feature_name in feature_names:
                if feature_name in self.feature_extractors:
                    extractor = self.feature_extractors[feature_name]
                    feature_data = await extractor(audio_data, sample_rate)
                    features[feature_name] = feature_data
                else:
                    logger.warning(f"Unknown feature: {feature_name}")
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
    
    async def _extract_mfcc(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract MFCC features"""



        return librosa.feature.mfcc(
            y=audio_data, 
            sr=sample_rate, 
            n_mfcc=13,
            hop_length=512
        )
    
    async def _extract_chroma(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract chroma features"""



        return librosa.feature.chroma_stft(
            y=audio_data, 
            sr=sample_rate,
            hop_length=512
        )
    
    async def _extract_spectral_contrast(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract spectral contrast features"""



        return librosa.feature.spectral_contrast(
            y=audio_data, 
            sr=sample_rate,
            hop_length=512
        )
    
    async def _extract_tonnetz(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract tonnetz (tonal centroid) features"""
        chroma = librosa.feature.chroma_cqt(y=audio_data, sr=sample_rate)
        return librosa.feature.tonnetz(chroma=chroma)
    
    async def _extract_zcr(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract zero crossing rate"""



        return librosa.feature.zero_crossing_rate(
            audio_data, 
            hop_length=512
        )
    
    async def _extract_spectral_centroid(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract spectral centroid"""



        return librosa.feature.spectral_centroid(
            y=audio_data, 
            sr=sample_rate,
            hop_length=512
        )
    
    async def _extract_spectral_bandwidth(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract spectral bandwidth"""



        return librosa.feature.spectral_bandwidth(
            y=audio_data, 
            sr=sample_rate,
            hop_length=512
        )
    
    async def _extract_spectral_rolloff(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract spectral rolloff"""



        return librosa.feature.spectral_rolloff(
            y=audio_data, 
            sr=sample_rate,
            hop_length=512
        )
    
    async def _extract_tempo(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract tempo information"""
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
        return np.array([tempo, len(beats), np.mean(onset_env)])
    
    async def _extract_onset_strength(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract onset strength"""



        return librosa.onset.onset_strength(
            y=audio_data, 
            sr=sample_rate,
            hop_length=512
        )
    
    async def _extract_harmonic_percussive(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract harmonic and percussive components"""
        y_harmonic, y_percussive = librosa.effects.hpss(audio_data)
        
        # Calculate energy ratios
        harmonic_energy = np.mean(y_harmonic ** 2)
        percussive_energy = np.mean(y_percussive ** 2)
        total_energy = harmonic_energy + percussive_energy
        
        if total_energy > 0:
            harmonic_ratio = harmonic_energy / total_energy
            percussive_ratio = percussive_energy / total_energy
        else:
            harmonic_ratio = percussive_ratio = 0.5
        
        return np.array([harmonic_ratio, percussive_ratio])
    
    async def _extract_mel_spectrogram(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract mel spectrogram"""



        return librosa.feature.melspectrogram(
            y=audio_data, 
            sr=sample_rate,
            n_mels=128,
            hop_length=512
        )
    
    async def _extract_rms_energy(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract RMS energy"""



        return librosa.feature.rms(
            y=audio_data,
            hop_length=512
        )
    
    async def create_model(self, model_config: ModelConfig) -> nn.Module:
        """Create a neural network model based on configuration"""



        try:
            architecture = model_config.architecture
            num_classes = len(model_config.output_classes)
            
            if architecture == ModelArchitecture.CNN_1D:
                # Calculate input size based on features
                input_size = self._calculate_feature_size(model_config.input_features, '1d')
                model = AudioCNN1D(
                    input_size=input_size,
                    num_classes=num_classes,
                    hidden_size=model_config.hidden_size,
                    dropout_rate=model_config.dropout_rate
                )
            
            elif architecture == ModelArchitecture.CNN_2D:
                model = AudioCNN2D(
                    num_classes=num_classes,
                    hidden_size=model_config.hidden_size,
                    dropout_rate=model_config.dropout_rate
                )
            
            elif architecture == ModelArchitecture.LSTM:
                input_size = self._calculate_feature_size(model_config.input_features, '1d')
                model = AudioLSTM(
                    input_size=input_size,
                    num_classes=num_classes,
                    hidden_size=model_config.hidden_size,
                    num_layers=model_config.num_layers,
                    dropout_rate=model_config.dropout_rate
                )
            
            elif architecture == ModelArchitecture.TRANSFORMER:
                input_size = self._calculate_feature_size(model_config.input_features, '1d')
                model = AudioTransformer(
                    input_size=input_size,
                    num_classes=num_classes,
                    d_model=model_config.hidden_size,
                    dropout_rate=model_config.dropout_rate
                )
            
            else:
                raise ValueError(f"Unsupported architecture: {architecture}")
            
            logger.info(f"Created {architecture.value} model for {model_config.model_type.value}")
            return model
            
        except Exception as e:
            logger.error(f"Model creation failed: {e}")
            raise
    
    def _calculate_feature_size(self, feature_names: List[str], dimension: str) -> int:
        """Calculate total feature size based on feature names"""
        # This is a simplified calculation - in practice, you'd calculate 
        # based on actual feature dimensions
        feature_sizes = {
            'mfcc': 13,
            'chroma': 12,
            'spectral_contrast': 7,
            'tonnetz': 6,
            'zero_crossing_rate': 1,
            'spectral_centroid': 1,
            'spectral_bandwidth': 1,
            'spectral_rolloff': 1,
            'tempo': 3,
            'harmonic_percussive': 2,
            'rms_energy': 1
        }
        
        total_size = sum(feature_sizes.get(name, 1) for name in feature_names)
        return total_size
    
    async def train_model(self,
                        model_type: ModelType,
                        training_data: List[Tuple[np.ndarray, int, Any]],
                        validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train a machine learning model
        
        Args:
            model_type: Type of model to train
            training_data: List of (audio_data, sample_rate, label) tuples
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training results and metrics
        """



        try:
            if model_type not in self.model_configs:
                raise ValueError(f"No configuration found for {model_type}")
            
            config = self.model_configs[model_type]
            
            # Extract features from training data
            logger.info(f"Extracting features for {len(training_data)} samples...")
            features = []
            labels = []
            
            for audio_data, sample_rate, label in training_data:
                # Extract features
                feature_dict = await self.extract_features(
                    audio_data, sample_rate, config.input_features
                )
                
                # Combine features into single vector
                feature_vector = self._combine_features(feature_dict, config)
                features.append(feature_vector)
                labels.append(label)
            
            features = np.array(features)
            labels = np.array(labels)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                features, labels, test_size=validation_split, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Store scaler
            self.scalers[model_type] = scaler
            
            # Train model based on architecture
            if config.architecture in [ModelArchitecture.CNN_1D, ModelArchitecture.CNN_2D, 
                                     ModelArchitecture.LSTM, ModelArchitecture.TRANSFORMER]:
                # Neural network training
                results = await self._train_neural_network(
                    config, X_train_scaled, X_val_scaled, y_train, y_val
                )
            else:
                # Traditional ML training
                results = await self._train_traditional_ml(
                    config, X_train_scaled, X_val_scaled, y_train, y_val
                )
            
            # Save model
            await self._save_model(model_type, self.models[model_type], scaler, config)
            
            logger.info(f"Model training completed for {model_type.value}")
            return results
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def _combine_features(self, feature_dict: Dict[str, np.ndarray], config: ModelConfig) -> np.ndarray:
        """Combine multiple features into a single vector"""
        combined = []
        
        for feature_name in config.input_features:
            if feature_name in feature_dict:
                feature_data = feature_dict[feature_name]
                
                # Handle different feature shapes
                if feature_data.ndim == 1:
                    combined.extend(feature_data.tolist())
                elif feature_data.ndim == 2:
                    # Take mean across time axis for 2D features
                    feature_mean = np.mean(feature_data, axis=1)
                    combined.extend(feature_mean.tolist())
                else:
                    # Flatten higher dimensional features
                    combined.extend(feature_data.flatten().tolist())
        
        return np.array(combined)
    
    async def _train_neural_network(self,
                                  config: ModelConfig,
                                  X_train: np.ndarray,
                                  X_val: np.ndarray,
                                  y_train: np.ndarray,
                                  y_val: np.ndarray) -> Dict[str, Any]:
        """Train neural network models"""



        try:
            # Create model
            model = await self.create_model(config)
            
            # Convert to PyTorch tensors
            X_train_tensor = torch.FloatTensor(X_train)
            X_val_tensor = torch.FloatTensor(X_val)
            y_train_tensor = torch.LongTensor(y_train)
            y_val_tensor = torch.LongTensor(y_val)
            
            # Training setup
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10)
            
            # Training loop
            num_epochs = 100
            best_val_acc = 0
            train_losses = []
            val_accuracies = []
            
            for epoch in range(num_epochs):
                # Training phase
                model.train()
                train_loss = 0
                
                # Simple batch processing (in practice, use DataLoader)
                batch_size = config.batch_size
                for i in range(0, len(X_train_tensor), batch_size):
                    batch_X = X_train_tensor[i:i+batch_size]
                    batch_y = y_train_tensor[i:i+batch_size]
                    
                    # Handle different input shapes for different architectures
                    if config.architecture == ModelArchitecture.CNN_2D:
                        # Add channel dimension for 2D CNN
                        batch_X = batch_X.unsqueeze(1)
                    elif config.architecture in [ModelArchitecture.LSTM, ModelArchitecture.TRANSFORMER]:
                        # Reshape for sequence models
                        batch_X = batch_X.unsqueeze(1)  # Add sequence dimension
                    
                    optimizer.zero_grad()
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    
                    train_loss += loss.item()
                
                # Validation phase
                model.eval()
                with torch.no_grad():
                    if config.architecture == ModelArchitecture.CNN_2D:
                        X_val_input = X_val_tensor.unsqueeze(1)
                    elif config.architecture in [ModelArchitecture.LSTM, ModelArchitecture.TRANSFORMER]:
                        X_val_input = X_val_tensor.unsqueeze(1)
                    else:
                        X_val_input = X_val_tensor
                    
                    val_outputs = model(X_val_input)
                    _, val_predicted = torch.max(val_outputs, 1)
                    val_acc = accuracy_score(y_val, val_predicted.numpy())
                
                train_losses.append(train_loss / len(X_train_tensor))
                val_accuracies.append(val_acc)
                
                # Learning rate scheduling
                scheduler.step(val_acc)
                
                # Save best model
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    self.models[config.model_type] = model.state_dict()
                
                if epoch % 10 == 0:
                    logger.debug(f"Epoch {epoch}: Train Loss: {train_losses[-1]:.4f}, "
                               f"Val Acc: {val_acc:.4f}")
            
            return {
                'best_validation_accuracy': best_val_acc,
                'training_losses': train_losses,
                'validation_accuracies': val_accuracies,
                'model_type': 'neural_network',
                'architecture': config.architecture.value
            }
            
        except Exception as e:
            logger.error(f"Neural network training failed: {e}")
            raise
    
    async def _train_traditional_ml(self,
                                  config: ModelConfig,
                                  X_train: np.ndarray,
                                  X_val: np.ndarray,
                                  y_train: np.ndarray,
                                  y_val: np.ndarray) -> Dict[str, Any]:
        """Train traditional ML models (Random Forest, SVM, etc.)"""



        try:
            # Determine if classification or regression
            is_regression = len(config.output_classes) == 1 and 'score' in config.output_classes[0]
            
            if is_regression:
                # Regression models
                models_to_try = {
                    'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                    'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
                }
                metric_func = mean_squared_error
                metric_name = 'mse'
            else:
                # Classification models
                models_to_try = {
                    'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                    'svm': SVC(kernel='rbf', random_state=42)
                }
                metric_func = accuracy_score
                metric_name = 'accuracy'
            
            best_score = float('-inf') if metric_name == 'accuracy' else float('inf')
            best_model = None
            best_model_name = None
            results = {}
            
            # Try different models
            for model_name, model in models_to_try.items():
                try:
                    # Train model
                    model.fit(X_train, y_train)
                    
                    # Evaluate
                    if is_regression:
                        train_pred = model.predict(X_train)
                        val_pred = model.predict(X_val)
                        train_score = -metric_func(y_train, train_pred)  # Negative MSE
                        val_score = -metric_func(y_val, val_pred)
                    else:
                        train_pred = model.predict(X_train)
                        val_pred = model.predict(X_val)
                        train_score = metric_func(y_train, train_pred)
                        val_score = metric_func(y_val, val_pred)
                    
                    results[model_name] = {
                        'train_score': train_score,
                        'val_score': val_score
                    }
                    
                    # Check if best model
                    if ((metric_name == 'accuracy' and val_score > best_score) or
                        (metric_name == 'mse' and val_score > best_score)):  # Remember: we use -MSE
                        best_score = val_score
                        best_model = model
                        best_model_name = model_name
                    
                except Exception as e:
                    logger.warning(f"Failed to train {model_name}: {e}")
            
            if best_model is not None:
                self.models[config.model_type] = best_model
                logger.info(f"Best model: {best_model_name} with {metric_name}: {best_score}")
            
            return {
                'best_model': best_model_name,
                'best_score': best_score,
                'metric': metric_name,
                'all_results': results,
                'model_type': 'traditional_ml'
            }
            
        except Exception as e:
            logger.error(f"Traditional ML training failed: {e}")
            raise
    
    async def predict(self,
                    audio_data: np.ndarray,
                    sample_rate: int,
                    model_type: ModelType) -> PredictionResult:
        """Make prediction using trained model"""
        import time
        start_time = time.time()
        
        try:
            if model_type not in self.models:
                await self._load_model(model_type)
            
            if model_type not in self.models:
                raise ValueError(f"No trained model found for {model_type}")
            
            config = self.model_configs[model_type]
            
            # Extract features
            feature_dict = await self.extract_features(
                audio_data, sample_rate, config.input_features
            )
            
            # Combine features
            feature_vector = self._combine_features(feature_dict, config)
            
            # Scale features
            if model_type in self.scalers:
                feature_vector = self.scalers[model_type].transform([feature_vector])[0]
            
            # Make prediction
            model = self.models[model_type]
            
            if hasattr(model, 'predict_proba'):  # Traditional ML classifier
                probabilities = model.predict_proba([feature_vector])[0]
                predictions = dict(zip(config.output_classes, probabilities))
                confidence = max(probabilities)
            
            elif hasattr(model, 'predict'):  # Traditional ML regressor
                prediction = model.predict([feature_vector])[0]
                predictions = {config.output_classes[0]: prediction}
                confidence = 1.0  # No confidence measure for regression
            
            else:  # Neural network
                # Load model state if it's a state dict
                if isinstance(model, dict):
                    nn_model = await self.create_model(config)
                    nn_model.load_state_dict(model)
                    model = nn_model
                
                model.eval()
                with torch.no_grad():
                    input_tensor = torch.FloatTensor([feature_vector])
                    
                    # Handle different architectures
                    if config.architecture == ModelArchitecture.CNN_2D:
                        input_tensor = input_tensor.unsqueeze(1)
                    elif config.architecture in [ModelArchitecture.LSTM, ModelArchitecture.TRANSFORMER]:
                        input_tensor = input_tensor.unsqueeze(1)
                    
                    outputs = model(input_tensor)
                    probabilities = F.softmax(outputs, dim=1)[0].numpy()
                    
                    predictions = dict(zip(config.output_classes, probabilities))
                    confidence = max(probabilities)
            
            processing_time = time.time() - start_time
            
            return PredictionResult(
                model_type=model_type,
                predictions=predictions,
                confidence=confidence,
                features_used=config.input_features,
                processing_time=processing_time,
                metadata={'feature_vector_size': len(feature_vector)}
            )
            
        except Exception as e:
            logger.error(f"Prediction failed for {model_type}: {e}")
            processing_time = time.time() - start_time
            
            return PredictionResult(
                model_type=model_type,
                predictions={},
                confidence=0.0,
                features_used=[],
                processing_time=processing_time,
                metadata={'error': str(e)}
            )
    
    async def _save_model(self,
                        model_type: ModelType,
                        model: Any,
                        scaler: StandardScaler,
                        config: ModelConfig):
        """Save trained model to disk"""



        try:
            model_dir = self.models_directory / model_type.value
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model
            if isinstance(model, dict):  # Neural network state dict
                torch.save(model, model_dir / "model.pth")
            else:  # Traditional ML model
                joblib.dump(model, model_dir / "model.joblib")
            
            # Save scaler
            joblib.dump(scaler, model_dir / "scaler.joblib")
            
            # Save config
            config_dict = {
                'model_type': config.model_type.value,
                'architecture': config.architecture.value,
                'input_features': config.input_features,
                'output_classes': config.output_classes,
                'sample_rate': config.sample_rate,
                'n_mels': config.n_mels,
                'n_fft': config.n_fft,
                'hop_length': config.hop_length,
                'hidden_size': config.hidden_size,
                'num_layers': config.num_layers,
                'dropout_rate': config.dropout_rate
            }
            
            with open(model_dir / "config.json", 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Saved model {model_type.value} to {model_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save model {model_type}: {e}")
    
    async def _load_model(self, model_type: ModelType):
        """Load trained model from disk"""



        try:
            model_dir = self.models_directory / model_type.value
            
            if not model_dir.exists():
                logger.warning(f"No saved model found for {model_type}")
                return
            
            # Load config
            config_path = model_dir / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_dict = json.load(f)
                
                config = ModelConfig(
                    model_type=ModelType(config_dict['model_type']),
                    architecture=ModelArchitecture(config_dict['architecture']),
                    input_features=config_dict['input_features'],
                    output_classes=config_dict['output_classes'],
                    sample_rate=config_dict.get('sample_rate', 22050),
                    n_mels=config_dict.get('n_mels', 128),
                    n_fft=config_dict.get('n_fft', 2048),
                    hop_length=config_dict.get('hop_length', 512),
                    hidden_size=config_dict.get('hidden_size', 256),
                    num_layers=config_dict.get('num_layers', 3),
                    dropout_rate=config_dict.get('dropout_rate', 0.3)
                )
                
                self.model_configs[model_type] = config
            
            # Load scaler
            scaler_path = model_dir / "scaler.joblib"
            if scaler_path.exists():
                self.scalers[model_type] = joblib.load(scaler_path)
            
            # Load model
            pytorch_model_path = model_dir / "model.pth"
            joblib_model_path = model_dir / "model.joblib"
            
            if pytorch_model_path.exists():
                # Neural network model
                state_dict = torch.load(pytorch_model_path, map_location='cpu')
                self.models[model_type] = state_dict
            elif joblib_model_path.exists():
                # Traditional ML model
                self.models[model_type] = joblib.load(joblib_model_path)
            
            logger.info(f"Loaded model {model_type.value} from {model_dir}")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
    
    async def ensemble_predict(self,
                             audio_data: np.ndarray,
                             sample_rate: int,
                             model_types: List[ModelType],
                             weights: Optional[List[float]] = None) -> Dict[str, PredictionResult]:
        """Make ensemble predictions using multiple models"""



        try:
            if weights is None:
                weights = [1.0] * len(model_types)
            
            if len(weights) != len(model_types):
                raise ValueError("Number of weights must match number of models")
            
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            # Get predictions from each model
            predictions = {}
            for model_type in model_types:
                result = await self.predict(audio_data, sample_rate, model_type)
                predictions[model_type.value] = result
            
            return predictions
            
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            return {}
    
    def get_available_models(self) -> List[ModelType]:
        """Get list of available model types"""



        return list(self.model_configs.keys())
    
    def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_type not in self.model_configs:
            return {}
        
        config = self.model_configs[model_type]
        is_trained = model_type in self.models
        
        return {
            'model_type': config.model_type.value,
            'architecture': config.architecture.value,
            'input_features': config.input_features,
            'output_classes': config.output_classes,
            'is_trained': is_trained,
            'sample_rate': config.sample_rate,
            'hidden_size': config.hidden_size,
            'num_layers': config.num_layers
        }
