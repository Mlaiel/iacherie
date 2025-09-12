"""🎯 Content Classifier Model - IA Influencer Agent Platform Enterprise
=========================================================================
Module: ml/models/content_classifier.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 CONTENT CLASSIFIER MODEL
Modèle de classification de contenu multi-modal
- Classification automatique du contenu (audio, video, image, text)
- Support multi-créateur (musiciens, bloggers, photographes, etc.)
- Performance temps réel <100ms
- Intégration avec pipeline ML enterprise
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import json
import numpy as np
import pandas as pd

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from transformers import AutoTokenizer, AutoModel
import torchvision.transforms as transforms
from PIL import Image
import librosa

from .base_model import BaseModel, ModelType, ModelStatus, CreatorSpecificModel

logger = logging.getLogger(__name__)

class ContentType:
    """Types de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"

class ContentDataset(Dataset):
    """Dataset pour le contenu multi-modal"""
    
    def __init__(self, data: List[Dict], labels: List[int], transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, label

class MultiModalEncoder(nn.Module):
    """Encodeur multi-modal pour différents types de contenu"""
    
    def __init__(self, text_model_name='distilbert-base-uncased', 
                 hidden_dim=768, output_dim=256):
        super().__init__()
        
        # Encodeur texte
        self.text_tokenizer = AutoTokenizer.from_pretrained(text_model_name)
        self.text_encoder = AutoModel.from_pretrained(text_model_name)
        
        # Encodeurs pour autres modalités
        self.audio_encoder = nn.Sequential(
            nn.Linear(128, hidden_dim),  # MFCC features
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, output_dim)
        )
        
        self.image_encoder = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((8, 8)),
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Fusion layer
        self.fusion_layer = nn.Sequential(
            nn.Linear(output_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def encode_text(self, text: str) -> torch.Tensor:
        """Encode le texte"""
        if not text:
            return torch.zeros(256)
        
        tokens = self.text_tokenizer(text, return_tensors='pt', 
                                   truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.text_encoder(**tokens)
            # Utiliser le pooled output
            text_embedding = outputs.pooler_output.squeeze()
        
        return text_embedding
    
    def encode_audio(self, audio_features: np.ndarray) -> torch.Tensor:
        """Encode les features audio (MFCC)"""
        if audio_features is None or len(audio_features) == 0:
            return torch.zeros(256)
        
        # Normaliser et convertir en tensor
        audio_tensor = torch.FloatTensor(audio_features)
        if len(audio_tensor.shape) == 1:
            audio_tensor = audio_tensor.unsqueeze(0)
        
        return self.audio_encoder(audio_tensor)
    
    def encode_image(self, image: np.ndarray) -> torch.Tensor:
        """Encode l'image"""
        if image is None:
            return torch.zeros(256)
        
        # Convertir en tensor et normaliser
        if len(image.shape) == 3:
            image_tensor = torch.FloatTensor(image).permute(2, 0, 1)
        else:
            image_tensor = torch.FloatTensor(image)
        
        image_tensor = image_tensor.unsqueeze(0) / 255.0
        
        return self.image_encoder(image_tensor).squeeze()
    
    def forward(self, text_emb: torch.Tensor, audio_emb: torch.Tensor, 
                image_emb: torch.Tensor) -> torch.Tensor:
        """Forward pass avec fusion des modalités"""
        combined = torch.cat([text_emb, audio_emb, image_emb], dim=-1)
        return self.fusion_layer(combined)

class ContentClassifierModel(nn.Module):
    """Modèle de classification de contenu multi-modal"""
    
    def __init__(self, num_classes: int, num_creators: int = 5, 
                 hidden_dim: int = 768, dropout: float = 0.3):
        super().__init__()
        
        self.encoder = MultiModalEncoder(hidden_dim=hidden_dim)
        
        # Classifier principal
        self.classifier = nn.Sequential(
            nn.Linear(256, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes)
        )
        
        # Classifier pour type de créateur
        self.creator_classifier = nn.Sequential(
            nn.Linear(256, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_creators)
        )
        
        # Classifier de qualité
        self.quality_regressor = nn.Sequential(
            nn.Linear(256, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, text_emb: torch.Tensor, audio_emb: torch.Tensor, 
                image_emb: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Forward pass du modèle"""
        # Encoder les features
        encoded = self.encoder(text_emb, audio_emb, image_emb)
        
        # Prédictions
        content_pred = self.classifier(encoded)
        creator_pred = self.creator_classifier(encoded)
        quality_pred = self.quality_regressor(encoded)
        
        return {
            'content_class': content_pred,
            'creator_type': creator_pred,
            'quality_score': quality_pred
        }

class ContentClassifier(CreatorSpecificModel):
    """
    Classificateur de contenu intelligent pour la plateforme Ainflue.
    
    Ce modèle classifie automatiquement le contenu multi-modal des créateurs
    et prédit le type de créateur et la qualité du contenu.
    """
    
    def __init__(self, creator_type: str = "general", **kwargs):
        super().__init__(creator_type=creator_type, **kwargs)
        
        # Configuration spécifique
        self.num_classes = kwargs.get('num_classes', 10)  # Catégories de contenu
        self.num_creators = kwargs.get('num_creators', 5)  # Types de créateurs
        self.hidden_dim = kwargs.get('hidden_dim', 768)
        self.dropout = kwargs.get('dropout', 0.3)
        
        # Encodeurs pour les labels
        self.label_encoder = LabelEncoder()
        self.creator_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
        # Métriques
        self.training_history = []
        
        logger.info(f"Initialized ContentClassifier for {creator_type}")
    
    def get_model_type(self) -> ModelType:
        """Retourne le type du modèle"""
        return ModelType.CONTENT_CLASSIFIER
    
    def build_model(self, input_shape: Optional[Tuple] = None, **kwargs) -> ContentClassifierModel:
        """
        Construit le modèle de classification.
        
        Args:
            input_shape: Non utilisé pour ce modèle
            **kwargs: Arguments supplémentaires
            
        Returns:
            Modèle PyTorch construit
        """
        self.model = ContentClassifierModel(
            num_classes=self.num_classes,
            num_creators=self.num_creators,
            hidden_dim=self.hidden_dim,
            dropout=self.dropout
        )
        
        # Définir le device
        device = torch.device(self.config['device'] if torch.cuda.is_available() else 'cpu')
        self.model.to(device)
        
        self.metadata.status = ModelStatus.INITIALIZED
        logger.info(f"Built ContentClassifier model with {self.num_classes} classes")
        
        return self.model
    
    def _extract_content_features(self, content_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les features des différents types de contenu.
        
        Args:
            content_item: Item de contenu avec différentes modalités
            
        Returns:
            Features extraites
        """
        features = {
            'text_emb': torch.zeros(256),
            'audio_emb': torch.zeros(256), 
            'image_emb': torch.zeros(256)
        }
        
        try:
            # Traitement texte
            if 'text' in content_item and content_item['text']:
                text_emb = self.model.encoder.encode_text(content_item['text'])
                features['text_emb'] = text_emb
            
            # Traitement audio
            if 'audio' in content_item and content_item['audio'] is not None:
                # Extraire MFCC features
                if isinstance(content_item['audio'], str):
                    # Chemin vers fichier audio
                    y, sr = librosa.load(content_item['audio'], sr=22050)
                    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=128)
                    audio_features = np.mean(mfcc.T, axis=0)
                else:
                    audio_features = content_item['audio']
                
                audio_emb = self.model.encoder.encode_audio(audio_features)
                features['audio_emb'] = audio_emb
            
            # Traitement image
            if 'image' in content_item and content_item['image'] is not None:
                if isinstance(content_item['image'], str):
                    # Chemin vers fichier image
                    image = Image.open(content_item['image'])
                    image_array = np.array(image.resize((224, 224)))
                else:
                    image_array = content_item['image']
                
                image_emb = self.model.encoder.encode_image(image_array)
                features['image_emb'] = image_emb
        
        except Exception as e:
            logger.warning(f"Error extracting features: {str(e)}")
        
        return features
    
    def train(self, X_train: List[Dict], y_train: List[str],
              X_val: Optional[List[Dict]] = None, y_val: Optional[List[str]] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Entraîne le modèle de classification.
        
        Args:
            X_train: Liste des items de contenu d'entraînement
            y_train: Labels de contenu
            X_val: Données de validation (optionnel)
            y_val: Labels de validation (optionnel)
            **kwargs: Arguments d'entraînement
            
        Returns:
            Historique d'entraînement
        """
        if self.model is None:
            self.build_model()
        
        self.metadata.status = ModelStatus.TRAINING
        
        # Encoder les labels
        y_encoded = self.label_encoder.fit_transform(y_train)
        
        # Extraire les creators types depuis les métadonnées
        creator_types = [item.get('creator_type', 'general') for item in X_train]
        creator_encoded = self.creator_encoder.fit_transform(creator_types)
        
        # Préparer les données
        train_features = [self._extract_content_features(item) for item in X_train]
        
        # Configuration d'entraînement
        epochs = kwargs.get('epochs', self.config['epochs'])
        learning_rate = kwargs.get('learning_rate', self.config['learning_rate'])
        batch_size = kwargs.get('batch_size', self.config['batch_size'])
        
        # Optimizer et loss
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        content_criterion = nn.CrossEntropyLoss()
        creator_criterion = nn.CrossEntropyLoss()
        quality_criterion = nn.MSELoss()
        
        device = torch.device(self.config['device'] if torch.cuda.is_available() else 'cpu')
        
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
        for epoch in range(epochs):
            self.model.train()
            epoch_loss = 0.0
            correct_predictions = 0
            total_predictions = 0
            
            # Entraînement par batch
            for i in range(0, len(train_features), batch_size):
                batch_features = train_features[i:i+batch_size]
                batch_content_labels = torch.LongTensor(y_encoded[i:i+batch_size]).to(device)
                batch_creator_labels = torch.LongTensor(creator_encoded[i:i+batch_size]).to(device)
                
                # Préparer les inputs
                text_embs = torch.stack([f['text_emb'] for f in batch_features]).to(device)
                audio_embs = torch.stack([f['audio_emb'] for f in batch_features]).to(device)
                image_embs = torch.stack([f['image_emb'] for f in batch_features]).to(device)
                
                # Forward pass
                outputs = self.model(text_embs, audio_embs, image_embs)
                
                # Calcul des losses
                content_loss = content_criterion(outputs['content_class'], batch_content_labels)
                creator_loss = creator_criterion(outputs['creator_type'], batch_creator_labels)
                
                # Quality score (simulation)
                quality_targets = torch.rand(len(batch_features)).to(device)
                quality_loss = quality_criterion(outputs['quality_score'].squeeze(), quality_targets)
                
                # Loss totale
                total_loss = content_loss + 0.3 * creator_loss + 0.2 * quality_loss
                
                # Backward pass
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()
                
                epoch_loss += total_loss.item()
                
                # Accuracy
                _, predicted = torch.max(outputs['content_class'], 1)
                total_predictions += batch_content_labels.size(0)
                correct_predictions += (predicted == batch_content_labels).sum().item()
            
            # Métriques de l'époque
            avg_loss = epoch_loss / (len(train_features) / batch_size)
            accuracy = correct_predictions / total_predictions
            
            history['train_loss'].append(avg_loss)
            history['train_acc'].append(accuracy)
            
            # Validation si fournie
            if X_val is not None and y_val is not None:
                val_metrics = self._validate(X_val, y_val)
                history['val_loss'].append(val_metrics['loss'])
                history['val_acc'].append(val_metrics['accuracy'])
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}, Acc: {accuracy:.4f}")
        
        # Finaliser l'entraînement
        self.is_trained = True
        self.metadata.status = ModelStatus.TRAINED
        self.training_history.append(history)
        
        # Calculer les métriques finales
        final_metrics = {
            'final_accuracy': accuracy,
            'final_loss': avg_loss,
            'epochs_trained': epochs,
            'total_samples': len(X_train)
        }
        
        self.metadata.performance_metrics.update(final_metrics)
        self.metadata.updated_at = datetime.now()
        
        logger.info(f"Training completed - Final accuracy: {accuracy:.4f}")
        
        return history
    
    def predict(self, X: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Effectue des prédictions sur le contenu.
        
        Args:
            X: Liste des items de contenu
            **kwargs: Arguments de prédiction
            
        Returns:
            Prédictions avec scores de confiance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        self.model.eval()
        device = torch.device(self.config['device'] if torch.cuda.is_available() else 'cpu')
        
        predictions = {
            'content_classes': [],
            'creator_types': [],
            'quality_scores': [],
            'confidence_scores': [],
            'processing_times': []
        }
        
        with torch.no_grad():
            for item in X:
                start_time = time.time()
                
                # Extraire features
                features = self._extract_content_features(item)
                
                # Préparer inputs
                text_emb = features['text_emb'].unsqueeze(0).to(device)
                audio_emb = features['audio_emb'].unsqueeze(0).to(device)
                image_emb = features['image_emb'].unsqueeze(0).to(device)
                
                # Prédiction
                outputs = self.model(text_emb, audio_emb, image_emb)
                
                # Traitement des outputs
                content_probs = F.softmax(outputs['content_class'], dim=1)
                creator_probs = F.softmax(outputs['creator_type'], dim=1)
                quality_score = outputs['quality_score'].item()
                
                # Classes prédites
                content_class_idx = torch.argmax(content_probs, dim=1).item()
                creator_type_idx = torch.argmax(creator_probs, dim=1).item()
                
                # Confiance
                content_confidence = torch.max(content_probs).item()
                creator_confidence = torch.max(creator_probs).item()
                
                # Décoder les labels
                content_class = self.label_encoder.inverse_transform([content_class_idx])[0]
                creator_type = self.creator_encoder.inverse_transform([creator_type_idx])[0]
                
                predictions['content_classes'].append(content_class)
                predictions['creator_types'].append(creator_type)
                predictions['quality_scores'].append(quality_score)
                predictions['confidence_scores'].append({
                    'content': content_confidence,
                    'creator': creator_confidence
                })
                predictions['processing_times'].append(time.time() - start_time)
        
        avg_processing_time = np.mean(predictions['processing_times'])
        logger.info(f"Processed {len(X)} items in {avg_processing_time:.3f}s avg per item")
        
        return predictions
    
    def evaluate(self, X_test: List[Dict], y_test: List[str], **kwargs) -> Dict[str, float]:
        """
        Évalue les performances du modèle.
        
        Args:
            X_test: Données de test
            y_test: Labels de test
            **kwargs: Arguments d'évaluation
            
        Returns:
            Métriques de performance
        """
        predictions = self.predict(X_test)
        predicted_classes = predictions['content_classes']
        
        # Calculer les métriques
        accuracy = accuracy_score(y_test, predicted_classes)
        precision = precision_score(y_test, predicted_classes, average='weighted')
        recall = recall_score(y_test, predicted_classes, average='weighted')
        f1 = f1_score(y_test, predicted_classes, average='weighted')
        
        # Temps de traitement moyen
        avg_processing_time = np.mean(predictions['processing_times'])
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'avg_processing_time_ms': avg_processing_time * 1000,
            'total_test_samples': len(X_test)
        }
        
        # Ajouter rapport détaillé si demandé
        if kwargs.get('detailed', False):
            report = classification_report(y_test, predicted_classes, output_dict=True)
            metrics['detailed_report'] = report
        
        logger.info(f"Evaluation completed - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        
        return metrics
    
    def _validate(self, X_val: List[Dict], y_val: List[str]) -> Dict[str, float]:
        """Validation interne pendant l'entraînement"""
        self.model.eval()
        device = torch.device(self.config['device'] if torch.cuda.is_available() else 'cpu')
        
        val_loss = 0.0
        correct = 0
        total = 0
        
        y_val_encoded = self.label_encoder.transform(y_val)
        criterion = nn.CrossEntropyLoss()
        
        with torch.no_grad():
            for i, item in enumerate(X_val):
                features = self._extract_content_features(item)
                
                text_emb = features['text_emb'].unsqueeze(0).to(device)
                audio_emb = features['audio_emb'].unsqueeze(0).to(device)
                image_emb = features['image_emb'].unsqueeze(0).to(device)
                
                outputs = self.model(text_emb, audio_emb, image_emb)
                
                target = torch.LongTensor([y_val_encoded[i]]).to(device)
                loss = criterion(outputs['content_class'], target)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs['content_class'], 1)
                total += 1
                correct += (predicted == target).sum().item()
        
        return {
            'loss': val_loss / len(X_val),
            'accuracy': correct / total
        }
    
    def get_creator_features(self, content: Dict[str, Any]) -> Dict[str, float]:
        """
        Extrait les features spécifiques au créateur.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            Features spécifiques au créateur
        """
        features = {}
        
        if self.creator_type == "musician":
            # Features audio spécifiques
            if 'audio' in content:
                features.update({
                    'tempo': content.get('tempo', 0.0),
                    'energy': content.get('energy', 0.0),
                    'valence': content.get('valence', 0.0),
                    'danceability': content.get('danceability', 0.0)
                })
        
        elif self.creator_type == "blogger":
            # Features texte spécifiques
            if 'text' in content:
                text = content['text']
                features.update({
                    'word_count': len(text.split()) if text else 0,
                    'readability_score': content.get('readability', 0.0),
                    'seo_score': content.get('seo_score', 0.0)
                })
        
        elif self.creator_type == "photographer":
            # Features image spécifiques
            if 'image' in content:
                features.update({
                    'composition_score': content.get('composition', 0.0),
                    'color_harmony': content.get('color_harmony', 0.0),
                    'lighting_quality': content.get('lighting', 0.0)
                })
        
        return features
    
    def optimize_for_creator(self, content_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimise le modèle pour un créateur spécifique.
        
        Args:
            content_history: Historique du contenu du créateur
            
        Returns:
            Recommandations d'optimisation
        """
        if not content_history:
            return {"status": "no_history_provided"}
        
        # Analyser les patterns du créateur
        creator_patterns = self._analyze_creator_patterns(content_history)
        
        # Générer des recommandations
        recommendations = {
            "content_type_preference": creator_patterns.get('preferred_type'),
            "optimal_posting_time": creator_patterns.get('best_timing'),
            "content_quality_trend": creator_patterns.get('quality_trend'),
            "engagement_factors": creator_patterns.get('engagement_drivers'),
            "improvement_suggestions": []
        }
        
        # Suggestions d'amélioration
        if creator_patterns.get('quality_trend', 0) < 0.7:
            recommendations["improvement_suggestions"].append(
                "Consider focusing on higher quality content creation"
            )
        
        if self.creator_type == "musician":
            recommendations["improvement_suggestions"].extend([
                "Experiment with different musical genres",
                "Focus on audio quality optimization"
            ])
        
        return recommendations
    
    def _analyze_creator_patterns(self, content_history: List[Dict]) -> Dict[str, Any]:
        """Analyse les patterns dans l'historique du créateur"""
        if not content_history:
            return {}
        
        # Analyser les types de contenu
        content_types = [item.get('type', 'unknown') for item in content_history]
        most_common_type = max(set(content_types), key=content_types.count)
        
        # Analyser la qualité moyenne
        quality_scores = [item.get('quality_score', 0.5) for item in content_history]
        avg_quality = np.mean(quality_scores) if quality_scores else 0.5
        
        # Analyser l'engagement
        engagement_scores = [item.get('engagement', 0.0) for item in content_history]
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.0
        
        return {
            'preferred_type': most_common_type,
            'quality_trend': avg_quality,
            'engagement_trend': avg_engagement,
            'total_content': len(content_history),
            'content_variety': len(set(content_types))
        }

# Export
__all__ = ['ContentClassifier', 'ContentType', 'MultiModalEncoder', 'ContentClassifierModel']