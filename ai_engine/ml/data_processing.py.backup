"""Data Processing Module

Advanced data processing and feature engineering capabilities for ML pipelines
including data transformation, feature extraction, and data validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""
import asyncio
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
import logging
from pathlib import Path
import json
import pickle
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, Normalizer,
    LabelEncoder, OneHotEncoder, OrdinalEncoder
)
from sklearn.feature_selection import (
    SelectKBest, f_classif, chi2, mutual_info_classif,
    RFE, SelectFromModel
)
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.manifold import TSNE

# Optional UMAP import
try:
    from umap import UMAP
    UMAP_AVAILABLE = True
except ImportError:
    try:
        from umap.umap_ import UMAP
        UMAP_AVAILABLE = True
    except ImportError:
        UMAP_AVAILABLE = False
        UMAP = None

from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import tensorflow as tf
import torch
from transformers import AutoTokenizer, AutoModel
import cv2
import librosa
from PIL import Image
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass


class DataType(Enum):
    """Data type categories"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TIME_SERIES = "time_series"
    GRAPH = "graph"
    TABULAR = "tabular"


class ProcessingStrategy(Enum):
    """Data processing strategies"""
    BATCH = "batch"
    STREAM = "stream"
    INCREMENTAL = "incremental"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"


class FeatureType(Enum):
    """Feature types for extraction"""
    STATISTICAL = "statistical"
    STRUCTURAL = "structural"
    TEMPORAL = "temporal"
    SPECTRAL = "spectral"
    SEMANTIC = "semantic"
    VISUAL = "visual"
    ACOUSTIC = "acoustic"


@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    # General settings
    strategy: ProcessingStrategy = ProcessingStrategy.BATCH
    chunk_size: int = 10000
    n_jobs: int = -1
    random_state: int = 42
    
    # Preprocessing options
    handle_missing_values: bool = True
    missing_value_strategy: str = "mean"  # mean, median, mode, knn, drop
    remove_outliers: bool = True
    outlier_method: str = "iqr"  # iqr, zscore, isolation_forest
    
    # Scaling and normalization
    scaling_method: str = "standard"  # standard, minmax, robust, none
    normalize_features: bool = False
    
    # Feature selection
    feature_selection: bool = True
    feature_selection_method: str = "univariate"  # univariate, rfe, model_based
    n_features: Optional[int] = None
    
    # Dimensionality reduction
    dimensionality_reduction: bool = False
    reduction_method: str = "pca"  # pca, ica, tsne, umap
    n_components: Optional[int] = None
    
    # Text processing
    text_lowercase: bool = True
    remove_punctuation: bool = True
    remove_stopwords: bool = True
    lemmatize: bool = True
    max_features: int = 10000
    
    # Image processing
    image_size: Tuple[int, int] = (224, 224)
    image_channels: int = 3
    image_augmentation: bool = True
    
    # Audio processing
    sample_rate: int = 22050
    n_mels: int = 128
    hop_length: int = 512
    
    # Validation
    validate_output: bool = True
    output_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result from data processing operation"""
    processed_data: Any
    feature_names: List[str] = field(default_factory=list)
    processing_stats: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    transformers: Dict[str, Any] = field(default_factory=dict)
    processing_time_seconds: float = 0.0
    original_shape: Optional[Tuple] = None
    processed_shape: Optional[Tuple] = None
    error: Optional[str] = None


class DataValidator:
    """Data validation and quality checking"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive data quality validation"""
        quality_report = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'missing_values': {},
            'duplicates': {},
            'data_types': {},
            'outliers': {},
            'unique_values': {},
            'quality_score': 0.0
        }
        
        # Missing values analysis
        missing_counts = data.isnull().sum()
        quality_report['missing_values'] = {
            'total_missing': int(missing_counts.sum()),
            'missing_percentage': float((missing_counts.sum() / data.size) * 100),
            'columns_with_missing': missing_counts[missing_counts > 0].to_dict()
        }
        
        # Duplicate analysis
        duplicate_count = data.duplicated().sum()
        quality_report['duplicates'] = {
            'duplicate_rows': int(duplicate_count),
            'duplicate_percentage': float((duplicate_count / len(data)) * 100)
        }
        
        # Data types analysis
        quality_report['data_types'] = data.dtypes.astype(str).to_dict()
        
        # Outlier detection for numerical columns
        numerical_columns = data.select_dtypes(include=[np.number]).columns
        for col in numerical_columns:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)]
            
            quality_report['outliers'][col] = {
                'count': len(outliers),
                'percentage': float((len(outliers) / len(data)) * 100),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            }
        
        # Unique values analysis
        for col in data.columns:
            unique_count = data[col].nunique()
            quality_report['unique_values'][col] = {
                'unique_count': int(unique_count),
                'unique_percentage': float((unique_count / len(data)) * 100),
                'is_unique': unique_count == len(data)
            }
        
        # Calculate quality score
        missing_score = max(0, 100 - quality_report['missing_values']['missing_percentage'])
        duplicate_score = max(0, 100 - quality_report['duplicates']['duplicate_percentage'])
        quality_report['quality_score'] = (missing_score + duplicate_score) / 2
        
        return quality_report
    
    def validate_schema(self, data: pd.DataFrame, expected_schema: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate data against expected schema"""
        errors = []
        
        # Check columns exist
        missing_columns = set(expected_schema.keys()) - set(data.columns)
        if missing_columns:
            errors.append(f"Missing columns: {missing_columns}")
        
        # Check data types
        for col, expected_dtype in expected_schema.items():
            if col in data.columns:
                actual_dtype = str(data[col].dtype)
                if actual_dtype != expected_dtype:
                    errors.append(f"Column {col} has type {actual_dtype}, expected {expected_dtype}")
        
        return len(errors) == 0, errors


class DataTransformer(ABC):
    """Abstract base class for data transformers"""
    
    @abstractmethod
    def fit(self, data: Any, **kwargs) -> 'DataTransformer':
        """Fit transformer to data"""
        pass
    
    @abstractmethod
    def transform(self, data: Any, **kwargs) -> Any:
        """Transform data"""
        pass
    
    def fit_transform(self, data: Any, **kwargs) -> Any:
        """Fit and transform data"""
        return self.fit(data, **kwargs).transform(data, **kwargs)


class NumericalTransformer(DataTransformer):
    """Transformer for numerical data"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.scaler = None
        self.imputer = None
        self.outlier_detector = None
        self.feature_selector = None
        self.dimensionality_reducer = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def fit(self, data: pd.DataFrame, **kwargs) -> 'NumericalTransformer':
        """Fit numerical transformer"""
        self.logger.info("Fitting numerical transformer")
        
        # Fit imputer for missing values
        if self.config.handle_missing_values:
            if self.config.missing_value_strategy == "knn":
                self.imputer = KNNImputer(n_neighbors=5)
            else:
                strategy_map = {"mean": "mean", "median": "median", "mode": "most_frequent"}
                strategy = strategy_map.get(self.config.missing_value_strategy, "mean")
                self.imputer = SimpleImputer(strategy=strategy)
            
            self.imputer.fit(data)
        
        # Fit scaler
        if self.config.scaling_method != "none":
            scaler_map = {
                "standard": StandardScaler(),
                "minmax": MinMaxScaler(),
                "robust": RobustScaler()
            }
            self.scaler = scaler_map.get(self.config.scaling_method, StandardScaler())
            self.scaler.fit(data if not self.imputer else self.imputer.transform(data))
        
        # Fit feature selector
        if self.config.feature_selection:
            if self.config.feature_selection_method == "univariate":
                self.feature_selector = SelectKBest(
                    f_classif,
                    k=self.config.n_features or min(10, data.shape[1])
                )
                # This would need target variable - placeholder
                # self.feature_selector.fit(transformed_data, target)
        
        # Fit dimensionality reducer
        if self.config.dimensionality_reduction:
            n_components = self.config.n_components or min(10, data.shape[1])
            if self.config.reduction_method == "pca":
                self.dimensionality_reducer = PCA(n_components=n_components)
            elif self.config.reduction_method == "ica":
                self.dimensionality_reducer = FastICA(n_components=n_components)
            elif self.config.reduction_method == "tsne":
                self.dimensionality_reducer = TSNE(n_components=min(n_components, 3))
            
            if self.dimensionality_reducer:
                transformed_data = data.copy()
                if self.imputer:
                    transformed_data = self.imputer.transform(transformed_data)
                if self.scaler:
                    transformed_data = self.scaler.transform(transformed_data)
                self.dimensionality_reducer.fit(transformed_data)
        
        return self
    
    def transform(self, data: pd.DataFrame, **kwargs) -> np.ndarray:
        """Transform numerical data"""
        transformed_data = data.copy()
        
        # Handle missing values
        if self.imputer:
            transformed_data = self.imputer.transform(transformed_data)
        
        # Remove outliers
        if self.config.remove_outliers:
            transformed_data = self._remove_outliers(transformed_data)
        
        # Scale data
        if self.scaler:
            transformed_data = self.scaler.transform(transformed_data)
        
        # Normalize
        if self.config.normalize_features:
            normalizer = Normalizer()
            transformed_data = normalizer.fit_transform(transformed_data)
        
        # Feature selection
        if self.feature_selector:
            # transformed_data = self.feature_selector.transform(transformed_data)
            pass  # Placeholder - needs target
        
        # Dimensionality reduction
        if self.dimensionality_reducer:
            transformed_data = self.dimensionality_reducer.transform(transformed_data)
        
        return transformed_data
    
    def _remove_outliers(self, data: np.ndarray) -> np.ndarray:
        """Remove outliers from numerical data"""
        if self.config.outlier_method == "iqr":
            Q1 = np.percentile(data, 25, axis=0)
            Q3 = np.percentile(data, 75, axis=0)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Keep only rows without outliers
            mask = np.all((data >= lower_bound) & (data <= upper_bound), axis=1)
            return data[mask]
        elif self.config.outlier_method == "zscore":
            z_scores = np.abs((data - np.mean(data, axis=0)) / np.std(data, axis=0))
            mask = np.all(z_scores < 3, axis=1)
            return data[mask]
        else:
            return data


class CategoricalTransformer(DataTransformer):
    """Transformer for categorical data"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.encoders = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def fit(self, data: pd.DataFrame, **kwargs) -> 'CategoricalTransformer':
        """Fit categorical transformer"""
        self.logger.info("Fitting categorical transformer")
        
        for column in data.select_dtypes(include=['object', 'category']).columns:
            unique_values = data[column].nunique()
            
            if unique_values <= 2:
                # Binary encoding
                self.encoders[column] = LabelEncoder()
            elif unique_values <= 10:
                # One-hot encoding for low cardinality
                self.encoders[column] = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            else:
                # Ordinal encoding for high cardinality
                self.encoders[column] = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            
            self.encoders[column].fit(data[column].values.reshape(-1, 1))
        
        return self
    
    def transform(self, data: pd.DataFrame, **kwargs) -> np.ndarray:
        """Transform categorical data"""
        transformed_data = []
        
        for column in data.columns:
            if column in self.encoders:
                encoder = self.encoders[column]
                encoded = encoder.transform(data[column].values.reshape(-1, 1))
                
                if isinstance(encoder, OneHotEncoder):
                    # One-hot encoding returns multiple columns
                    for i in range(encoded.shape[1]):
                        transformed_data.append(encoded[:, i])
                else:
                    # Label/Ordinal encoding returns single column
                    transformed_data.append(encoded.flatten())
            else:
                # Numerical column, keep as is
                transformed_data.append(data[column].values)
        
        return np.column_stack(transformed_data) if transformed_data else np.array([])


class TextTransformer(DataTransformer):
    """Transformer for text data"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.vectorizer = None
        self.lemmatizer = None
        self.stemmer = None
        self.stop_words = set()
        self.nlp = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize text processing tools
        self._initialize_text_tools()
    
    def _initialize_text_tools(self):
        """Initialize text processing tools"""
        try:
            # Initialize spaCy
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy English model not found, using NLTK instead")
        
        # Initialize NLTK tools
        if self.config.lemmatize:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.stemmer = PorterStemmer()
        
        if self.config.remove_stopwords:
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = set()
    
    def fit(self, data: List[str], **kwargs) -> 'TextTransformer':
        """Fit text transformer"""
        self.logger.info("Fitting text transformer")
        
        # For transformer-based models
        if kwargs.get('use_transformers', False):
            model_name = kwargs.get('model_name', 'bert-base-uncased')
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name)
            except Exception as e:
                self.logger.warning(f"Failed to load transformer model: {e}")
        
        return self
    
    def transform(self, data: List[str], **kwargs) -> np.ndarray:
        """Transform text data"""
        if self.tokenizer and self.model:
            return self._transform_with_transformers(data)
        else:
            return self._transform_with_traditional_methods(data)
    
    def _transform_with_transformers(self, texts: List[str]) -> np.ndarray:
        """Transform text using transformer models"""
        embeddings = []
        
        for text in texts:
            # Tokenize and encode
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
                embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _transform_with_traditional_methods(self, texts: List[str]) -> List[str]:
        """Transform text using traditional NLP methods"""
        processed_texts = []
        
        for text in texts:
            # Lowercase
            if self.config.text_lowercase:
                text = text.lower()
            
            # Remove punctuation
            if self.config.remove_punctuation:
                import string
                text = text.translate(str.maketrans('', '', string.punctuation))
            
            # Tokenize
            if self.nlp:
                doc = self.nlp(text)
                tokens = [token.text for token in doc if not token.is_space]
            else:
                tokens = word_tokenize(text)
            
            # Remove stopwords
            if self.config.remove_stopwords:
                tokens = [token for token in tokens if token.lower() not in self.stop_words]
            
            # Lemmatize or stem
            if self.lemmatizer:
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            elif self.stemmer:
                tokens = [self.stemmer.stem(token) for token in tokens]
            
            processed_texts.append(' '.join(tokens))
        
        return processed_texts
    
    def extract_features(self, texts: List[str]) -> Dict[str, Any]:
        """Extract statistical features from text"""
        features = {
            'char_count': [],
            'word_count': [],
            'sentence_count': [],
            'avg_word_length': [],
            'unique_word_ratio': [],
            'punctuation_ratio': []
        }
        
        for text in texts:
            # Character count
            features['char_count'].append(len(text))
            
            # Word count
            words = word_tokenize(text.lower())
            features['word_count'].append(len(words))
            
            # Sentence count
            sentences = sent_tokenize(text)
            features['sentence_count'].append(len(sentences))
            
            # Average word length
            avg_word_len = np.mean([len(word) for word in words]) if words else 0
            features['avg_word_length'].append(avg_word_len)
            
            # Unique word ratio
            unique_words = len(set(words))
            ratio = unique_words / len(words) if words else 0
            features['unique_word_ratio'].append(ratio)
            
            # Punctuation ratio
            import string
            punct_count = sum(1 for char in text if char in string.punctuation)
            punct_ratio = punct_count / len(text) if text else 0
            features['punctuation_ratio'].append(punct_ratio)
        
        return features


class ImageTransformer(DataTransformer):
    """Transformer for image data"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def fit(self, data: List[str], **kwargs) -> 'ImageTransformer':
        """Fit image transformer (usually no fitting required)"""
        return self
    
    def transform(self, image_paths: List[str], **kwargs) -> np.ndarray:
        """Transform images to numerical arrays"""
        images = []
        
        for image_path in image_paths:
            try:
                # Load and preprocess image
                image = cv2.imread(image_path)
                if image is None:
                    # Try with PIL
                    image = np.array(Image.open(image_path))
                
                # Resize
                image = cv2.resize(image, self.config.image_size)
                
                # Normalize
                image = image.astype(np.float32) / 255.0
                
                images.append(image)
                
            except Exception as e:
                self.logger.error(f"Failed to process image {image_path}: {e}")
                # Add zeros for failed images
                images.append(np.zeros((*self.config.image_size, self.config.image_channels)))
        
        return np.array(images)
    
    def extract_features(self, image_paths: List[str]) -> Dict[str, Any]:
        """Extract features from images"""
        features = {
            'mean_intensity': [],
            'std_intensity': [],
            'edge_density': [],
            'histogram_features': []
        }
        
        for image_path in image_paths:
            try:
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                
                # Mean and std intensity
                features['mean_intensity'].append(float(np.mean(image)))
                features['std_intensity'].append(float(np.std(image)))
                
                # Edge density
                edges = cv2.Canny(image, 50, 150)
                edge_density = np.sum(edges > 0) / image.size
                features['edge_density'].append(edge_density)
                
                # Histogram features
                hist = cv2.calcHist([image], [0], None, [256], [0, 256])
                hist_features = hist.flatten()[:10]  # Take first 10 bins
                features['histogram_features'].append(hist_features.tolist())
                
            except Exception as e:
                self.logger.error(f"Failed to extract features from {image_path}: {e}")
                # Add default values for failed images
                features['mean_intensity'].append(0.0)
                features['std_intensity'].append(0.0)
                features['edge_density'].append(0.0)
                features['histogram_features'].append([0.0] * 10)
        
        return features


class AudioTransformer(DataTransformer):
    """Transformer for audio data"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def fit(self, data: List[str], **kwargs) -> 'AudioTransformer':
        """Fit audio transformer"""
        return self
    
    def transform(self, audio_paths: List[str], **kwargs) -> np.ndarray:
        """Transform audio files to feature arrays"""
        features = []
        
        for audio_path in audio_paths:
            try:
                # Load audio
                y, sr = librosa.load(audio_path, sr=self.config.sample_rate)
                
                # Extract mel spectrogram
                mel_spec = librosa.feature.melspectrogram(
                    y=y,
                    sr=sr,
                    n_mels=self.config.n_mels,
                    hop_length=self.config.hop_length
                )
                
                # Convert to log scale
                log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
                
                features.append(log_mel_spec)
                
            except Exception as e:
                self.logger.error(f"Failed to process audio {audio_path}: {e}")
                # Add zeros for failed audio
                features.append(np.zeros((self.config.n_mels, 100)))  # Default size
        
        return np.array(features)
    
    def extract_features(self, audio_paths: List[str]) -> Dict[str, Any]:
        """Extract audio features"""
        features = {
            'duration': [],
            'tempo': [],
            'spectral_centroid': [],
            'spectral_rolloff': [],
            'zero_crossing_rate': [],
            'mfcc_mean': [],
            'chroma_mean': []
        }
        
        for audio_path in audio_paths:
            try:
                y, sr = librosa.load(audio_path, sr=self.config.sample_rate)
                
                # Duration
                duration = librosa.get_duration(y=y, sr=sr)
                features['duration'].append(duration)
                
                # Tempo
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                features['tempo'].append(float(tempo))
                
                # Spectral features
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                features['spectral_centroid'].append(float(np.mean(spectral_centroid)))
                
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                features['spectral_rolloff'].append(float(np.mean(spectral_rolloff)))
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(y)
                features['zero_crossing_rate'].append(float(np.mean(zcr)))
                
                # MFCC
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                features['mfcc_mean'].append(np.mean(mfccs, axis=1).tolist())
                
                # Chroma
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                features['chroma_mean'].append(np.mean(chroma, axis=1).tolist())
                
            except Exception as e:
                self.logger.error(f"Failed to extract features from {audio_path}: {e}")
                # Add default values
                features['duration'].append(0.0)
                features['tempo'].append(0.0)
                features['spectral_centroid'].append(0.0)
                features['spectral_rolloff'].append(0.0)
                features['zero_crossing_rate'].append(0.0)
                features['mfcc_mean'].append([0.0] * 13)
                features['chroma_mean'].append([0.0] * 12)
        
        return features


class DataProcessor:
    """Main data processing orchestrator"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.transformers = {}
        self.validator = DataValidator()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def process_data(
        self,
        data: Any,
        data_type: DataType,
        **kwargs
    ) -> ProcessingResult:
        """Process data based on its type"""
        start_time = time.time()
        
        try:
            # Validate input data
            if self.config.validate_output:
                quality_report = self._validate_input_data(data, data_type)
                self.logger.info(f"Data quality score: {quality_report.get('quality_score', 0):.2f}%")
            
            # Select appropriate transformer
            transformer = self._get_transformer(data_type)
            
            # Fit and transform data
            if data_type == DataType.TABULAR:
                processed_data = await self._process_tabular_data(data, transformer)
            elif data_type == DataType.TEXT:
                processed_data = await self._process_text_data(data, transformer, **kwargs)
            elif data_type == DataType.IMAGE:
                processed_data = await self._process_image_data(data, transformer)
            elif data_type == DataType.AUDIO:
                processed_data = await self._process_audio_data(data, transformer)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create result
            result = ProcessingResult(
                processed_data=processed_data,
                processing_time_seconds=processing_time,
                original_shape=getattr(data, 'shape', None),
                processed_shape=getattr(processed_data, 'shape', None),
                transformers={data_type.value: transformer}
            )
            
            self.logger.info(f"Data processing completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            return ProcessingResult(
                processed_data=None,
                error=str(e),
                processing_time_seconds=time.time() - start_time
            )
    
    def _get_transformer(self, data_type: DataType) -> DataTransformer:
        """Get appropriate transformer for data type"""
        if data_type not in self.transformers:
            if data_type == DataType.NUMERICAL or data_type == DataType.TABULAR:
                self.transformers[data_type] = NumericalTransformer(self.config)
            elif data_type == DataType.CATEGORICAL:
                self.transformers[data_type] = CategoricalTransformer(self.config)
            elif data_type == DataType.TEXT:
                self.transformers[data_type] = TextTransformer(self.config)
            elif data_type == DataType.IMAGE:
                self.transformers[data_type] = ImageTransformer(self.config)
            elif data_type == DataType.AUDIO:
                self.transformers[data_type] = AudioTransformer(self.config)
            else:
                raise ValueError(f"No transformer available for {data_type}")
        
        return self.transformers[data_type]
    
    async def _process_tabular_data(
        self,
        data: pd.DataFrame,
        transformer: DataTransformer
    ) -> np.ndarray:
        """Process tabular data"""
        # Separate numerical and categorical columns
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        processed_parts = []
        
        # Process numerical columns
        if not numerical_cols.empty:
            numerical_transformer = NumericalTransformer(self.config)
            numerical_data = numerical_transformer.fit_transform(data[numerical_cols])
            processed_parts.append(numerical_data)
        
        # Process categorical columns
        if not categorical_cols.empty:
            categorical_transformer = CategoricalTransformer(self.config)
            categorical_data = categorical_transformer.fit_transform(data[categorical_cols])
            processed_parts.append(categorical_data)
        
        # Combine processed data
        if processed_parts:
            return np.hstack(processed_parts)
        else:
            return np.array([])
    
    async def _process_text_data(
        self,
        data: List[str],
        transformer: TextTransformer,
        **kwargs
    ) -> Union[np.ndarray, List[str]]:
        """Process text data"""
        # Fit and transform
        transformer.fit(data, **kwargs)
        processed_data = transformer.transform(data, **kwargs)
        
        # Extract additional features if needed
        if kwargs.get('extract_features', False):
            text_features = transformer.extract_features(data)
            # Could combine with processed_data if both are arrays
        
        return processed_data
    
    async def _process_image_data(
        self,
        data: List[str],
        transformer: ImageTransformer
    ) -> np.ndarray:
        """Process image data"""
        return transformer.fit_transform(data)
    
    async def _process_audio_data(
        self,
        data: List[str],
        transformer: AudioTransformer
    ) -> np.ndarray:
        """Process audio data"""
        return transformer.fit_transform(data)
    
    def _validate_input_data(self, data: Any, data_type: DataType) -> Dict[str, Any]:
        """Validate input data quality"""
        if data_type == DataType.TABULAR and isinstance(data, pd.DataFrame):
            return self.validator.validate_data_quality(data)
        else:
            # Basic validation for other data types
            return {
                'data_type': data_type.value,
                'data_length': len(data) if hasattr(data, '__len__') else 1,
                'quality_score': 100.0  # Assume good quality for non-tabular data
            }


class FeatureExtractor:
    """Advanced feature extraction for different data types"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def extract_statistical_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract statistical features from numerical data"""
        return {
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'median': float(np.median(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'q25': float(np.percentile(data, 25)),
            'q75': float(np.percentile(data, 75)),
            'skewness': float(self._calculate_skewness(data)),
            'kurtosis': float(self._calculate_kurtosis(data))
        }
    
    def extract_temporal_features(self, time_series: np.ndarray) -> Dict[str, float]:
        """Extract temporal features from time series data"""
        features = {}
        
        # Trend analysis
        features['trend_slope'] = self._calculate_trend_slope(time_series)
        
        # Seasonality detection
        features['seasonality_strength'] = self._calculate_seasonality_strength(time_series)
        
        # Autocorrelation
        features['autocorr_lag1'] = self._calculate_autocorrelation(time_series, lag=1)
        
        # Volatility
        features['volatility'] = float(np.std(np.diff(time_series)))
        
        return features
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def _calculate_trend_slope(self, time_series: np.ndarray) -> float:
        """Calculate trend slope using linear regression"""
        x = np.arange(len(time_series))
        coeffs = np.polyfit(x, time_series, 1)
        return float(coeffs[0])
    
    def _calculate_seasonality_strength(self, time_series: np.ndarray) -> float:
        """Calculate seasonality strength"""
        # Simple seasonality detection using FFT
        fft = np.fft.fft(time_series)
        power_spectrum = np.abs(fft) ** 2
        return float(np.max(power_spectrum[1:len(power_spectrum)//2]))
    
    def _calculate_autocorrelation(self, time_series: np.ndarray, lag: int) -> float:
        """Calculate autocorrelation at specified lag"""
        if len(time_series) <= lag:
            return 0.0
        
        x1 = time_series[:-lag]
        x2 = time_series[lag:]
        
        return float(np.corrcoef(x1, x2)[0, 1])


# Export main classes
__all__ = [
    'DataProcessor',
    'DataTransformer',
    'FeatureExtractor',
    'ProcessingConfig',
    'ProcessingResult',
    'DataValidator',
    'NumericalTransformer',
    'CategoricalTransformer',
    'TextTransformer',
    'ImageTransformer',
    'AudioTransformer',
    'DataType',
    'ProcessingStrategy',
    'FeatureType'
]
