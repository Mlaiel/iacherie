"""🚀 Model Explainer - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/monitoring/model_explainer.py
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EXPLICABILITÉ DE MODÈLES ML
Model explainability avec SHAP, LIME, et méthodes d'attribution
- SHAP values pour feature importance globale et locale
- LIME pour explications locales interprétables
- Custom attribution methods pour créateurs
- Explainability dashboards et visualisations
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path

# ML Libraries
try:
    import shap
    import lime
    from lime.lime_image import LimeImageExplainer
    from lime.lime_text import LimeTextExplainer
    from lime.lime_tabular import LimeTabularExplainer
    EXPLAINABILITY_AVAILABLE = True
except ImportError:
    EXPLAINABILITY_AVAILABLE = False
    logging.warning("SHAP or LIME not available, using simplified explanations")

# Configuration
logger = logging.getLogger(__name__)

class ExplanationType(Enum):
    """Types d'explications"""
    GLOBAL = "global"
    LOCAL = "local"
    FEATURE_IMPORTANCE = "feature_importance"
    INTERACTION = "interaction"
    COUNTERFACTUAL = "counterfactual"

class ExplainerMethod(Enum):
    """Méthodes d'explication"""
    SHAP = "shap"
    LIME = "lime"
    PERMUTATION = "permutation"
    ATTENTION = "attention"
    GRADIENT = "gradient"
    CUSTOM = "custom"

class CreatorType(Enum):
    """Types de créateurs pour explications spécialisées"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class ExplanationRequest:
    """Requête d'explication"""
    instance_id: str
    input_data: Dict[str, Any]
    prediction: Any
    explanation_type: ExplanationType
    explainer_method: ExplainerMethod
    creator_type: Optional[CreatorType] = None
    confidence_threshold: float = 0.5
    max_features: int = 10
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureAttribution:
    """Attribution d'une feature"""
    feature_name: str
    importance: float
    value: Any
    confidence: float
    contribution_direction: str  # "positive", "negative", "neutral"
    creator_relevance: Optional[float] = None

@dataclass
class ModelExplanation:
    """Explication complète d'un modèle"""
    explanation_id: str
    instance_id: str
    prediction: Any
    confidence: float
    explanation_type: ExplanationType
    explainer_method: ExplainerMethod
    feature_attributions: List[FeatureAttribution]
    global_importance: Dict[str, float]
    timestamp: datetime
    creator_type: Optional[CreatorType] = None
    visualization_data: Dict[str, Any] = field(default_factory=dict)
    counterfactuals: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExplainerConfig:
    """Configuration de l'explainer"""
    model_type: str  # "classification", "regression", "deep_learning"
    feature_names: List[str]
    categorical_features: List[str] = field(default_factory=list)
    target_names: List[str] = field(default_factory=list)
    enable_shap: bool = True
    enable_lime: bool = True
    enable_custom_attribution: bool = True
    cache_explanations: bool = True
    max_cache_size: int = 1000
    creator_specific_features: Dict[CreatorType, List[str]] = field(default_factory=dict)

class ModelExplainer:
    """🔬 Explainer de modèles ML avec SHAP, LIME et méthodes custom"""
    
    def __init__(self, config: ExplainerConfig, model: Any = None):
        self.config = config
        self.model = model
        self.explainer_id = str(uuid.uuid4())
        self.explanation_cache: Dict[str, ModelExplanation] = {}
        self.shap_explainer = None
        self.lime_explainer = None
        self._initialize_explainers()
        
        logger.info(f"Model Explainer initialized: {self.explainer_id}")
    
    def _initialize_explainers(self):
        """Initialise les explainers SHAP et LIME"""
        if not EXPLAINABILITY_AVAILABLE:
            logger.warning("SHAP/LIME not available, using simplified explanations")
            return
        
        try:
            # Initialiser SHAP explainer si disponible
            if self.config.enable_shap and self.model:
                if hasattr(self.model, 'predict_proba'):
                    self.shap_explainer = shap.Explainer(self.model.predict_proba)
                elif hasattr(self.model, 'predict'):
                    self.shap_explainer = shap.Explainer(self.model.predict)
            
            # LIME explainer sera initialisé par type de données
            logger.info("Explainers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing explainers: {e}")
    
    async def explain_prediction(self, request: ExplanationRequest) -> ModelExplanation:
        """Génère une explication pour une prédiction"""
        try:
            # Vérifier le cache
            cache_key = self._generate_cache_key(request)
            if self.config.cache_explanations and cache_key in self.explanation_cache:
                return self.explanation_cache[cache_key]
            
            # Générer l'explication selon la méthode demandée
            if request.explainer_method == ExplainerMethod.SHAP:
                explanation = await self._explain_with_shap(request)
            elif request.explainer_method == ExplainerMethod.LIME:
                explanation = await self._explain_with_lime(request)
            elif request.explainer_method == ExplainerMethod.PERMUTATION:
                explanation = await self._explain_with_permutation(request)
            elif request.explainer_method == ExplainerMethod.CUSTOM:
                explanation = await self._explain_with_custom_method(request)
            else:
                explanation = await self._explain_with_fallback(request)
            
            # Ajouter des explications spécifiques aux créateurs
            if request.creator_type:
                await self._add_creator_specific_insights(explanation, request.creator_type)
            
            # Mettre en cache
            if self.config.cache_explanations:
                self._cache_explanation(cache_key, explanation)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining prediction: {e}")
            # Retourner une explication basique en cas d'erreur
            return await self._create_fallback_explanation(request)
    
    async def _explain_with_shap(self, request: ExplanationRequest) -> ModelExplanation:
        """Explication avec SHAP"""
        try:
            if not EXPLAINABILITY_AVAILABLE or not self.shap_explainer:
                return await self._explain_with_fallback(request)
            
            # Préparer les données
            input_array = self._prepare_input_for_shap(request.input_data)
            
            # Calculer les SHAP values
            shap_values = self.shap_explainer(input_array)
            
            # Extraire les attributions
            feature_attributions = []
            for i, feature_name in enumerate(self.config.feature_names):
                if i < len(shap_values.values[0]):
                    importance = float(shap_values.values[0][i])
                    feature_attributions.append(FeatureAttribution(
                        feature_name=feature_name,
                        importance=abs(importance),
                        value=input_array[0][i] if i < len(input_array[0]) else None,
                        confidence=0.9,  # SHAP a généralement une haute confiance
                        contribution_direction="positive" if importance > 0 else "negative" if importance < 0 else "neutral"
                    ))
            
            # Trier par importance
            feature_attributions.sort(key=lambda x: x.importance, reverse=True)
            feature_attributions = feature_attributions[:request.max_features]
            
            # Importance globale
            global_importance = {
                attr.feature_name: attr.importance 
                for attr in feature_attributions
            }
            
            explanation = ModelExplanation(
                explanation_id=str(uuid.uuid4()),
                instance_id=request.instance_id,
                prediction=request.prediction,
                confidence=float(np.max(np.abs(shap_values.values[0]))),
                explanation_type=request.explanation_type,
                explainer_method=ExplainerMethod.SHAP,
                feature_attributions=feature_attributions,
                global_importance=global_importance,
                timestamp=datetime.now(),
                creator_type=request.creator_type,
                visualization_data=self._create_shap_visualization_data(shap_values),
                metadata={'shap_base_value': float(shap_values.base_values[0])}
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error with SHAP explanation: {e}")
            return await self._explain_with_fallback(request)
    
    async def _explain_with_lime(self, request: ExplanationRequest) -> ModelExplanation:
        """Explication avec LIME"""
        try:
            if not EXPLAINABILITY_AVAILABLE:
                return await self._explain_with_fallback(request)
            
            # Initialiser LIME explainer selon le type de données
            input_array = self._prepare_input_for_lime(request.input_data)
            
            if not self.lime_explainer:
                self.lime_explainer = LimeTabularExplainer(
                    training_data=np.random.randn(100, len(input_array[0])),  # Données d'entraînement simulées
                    feature_names=self.config.feature_names,
                    categorical_features=[i for i, name in enumerate(self.config.feature_names) 
                                        if name in self.config.categorical_features],
                    mode='classification' if self.config.model_type == 'classification' else 'regression'
                )
            
            # Prédiction function
            def predict_fn(x):
                if hasattr(self.model, 'predict_proba'):
                    return self.model.predict_proba(x)
                else:
                    predictions = self.model.predict(x)
                    return np.column_stack([1-predictions, predictions]) if predictions.ndim == 1 else predictions
            
            # Expliquer l'instance
            explanation = self.lime_explainer.explain_instance(
                input_array[0], 
                predict_fn, 
                num_features=request.max_features
            )
            
            # Extraire les attributions
            feature_attributions = []
            for feature_idx, importance in explanation.as_list():
                if feature_idx < len(self.config.feature_names):
                    feature_name = self.config.feature_names[feature_idx]
                    feature_attributions.append(FeatureAttribution(
                        feature_name=feature_name,
                        importance=abs(importance),
                        value=input_array[0][feature_idx],
                        confidence=0.7,  # LIME a une confiance modérée
                        contribution_direction="positive" if importance > 0 else "negative" if importance < 0 else "neutral"
                    ))
            
            # Importance globale
            global_importance = {
                attr.feature_name: attr.importance 
                for attr in feature_attributions
            }
            
            model_explanation = ModelExplanation(
                explanation_id=str(uuid.uuid4()),
                instance_id=request.instance_id,
                prediction=request.prediction,
                confidence=explanation.score if hasattr(explanation, 'score') else 0.7,
                explanation_type=request.explanation_type,
                explainer_method=ExplainerMethod.LIME,
                feature_attributions=feature_attributions,
                global_importance=global_importance,
                timestamp=datetime.now(),
                creator_type=request.creator_type,
                visualization_data=self._create_lime_visualization_data(explanation),
                metadata={'lime_intercept': getattr(explanation, 'intercept', 0)}
            )
            
            return model_explanation
            
        except Exception as e:
            logger.error(f"Error with LIME explanation: {e}")
            return await self._explain_with_fallback(request)
    
    async def _explain_with_permutation(self, request: ExplanationRequest) -> ModelExplanation:
        """Explication par permutation des features"""
        try:
            input_array = self._prepare_input_for_shap(request.input_data)
            original_prediction = request.prediction
            
            feature_attributions = []
            
            for i, feature_name in enumerate(self.config.feature_names):
                if i >= len(input_array[0]):
                    continue
                
                # Permuter la feature
                permuted_input = input_array.copy()
                permuted_input[0][i] = np.random.randn()  # Valeur aléatoire
                
                # Calculer la nouvelle prédiction
                if hasattr(self.model, 'predict_proba'):
                    new_prediction = self.model.predict_proba(permuted_input)[0]
                else:
                    new_prediction = self.model.predict(permuted_input)[0]
                
                # Calculer l'importance
                if isinstance(original_prediction, (list, np.ndarray)):
                    importance = float(np.mean(np.abs(np.array(original_prediction) - np.array(new_prediction))))
                else:
                    importance = abs(float(original_prediction) - float(new_prediction))
                
                feature_attributions.append(FeatureAttribution(
                    feature_name=feature_name,
                    importance=importance,
                    value=input_array[0][i],
                    confidence=0.6,  # Confiance modérée pour permutation
                    contribution_direction="positive" if importance > 0.1 else "neutral"
                ))
            
            # Trier par importance
            feature_attributions.sort(key=lambda x: x.importance, reverse=True)
            feature_attributions = feature_attributions[:request.max_features]
            
            global_importance = {
                attr.feature_name: attr.importance 
                for attr in feature_attributions
            }
            
            explanation = ModelExplanation(
                explanation_id=str(uuid.uuid4()),
                instance_id=request.instance_id,
                prediction=request.prediction,
                confidence=0.6,
                explanation_type=request.explanation_type,
                explainer_method=ExplainerMethod.PERMUTATION,
                feature_attributions=feature_attributions,
                global_importance=global_importance,
                timestamp=datetime.now(),
                creator_type=request.creator_type,
                metadata={'method': 'permutation_importance'}
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error with permutation explanation: {e}")
            return await self._explain_with_fallback(request)
    
    async def _explain_with_custom_method(self, request: ExplanationRequest) -> ModelExplanation:
        """Méthode d'explication personnalisée pour créateurs"""
        try:
            # Méthode simplifiée basée sur les corrélations
            input_data = request.input_data
            
            # Créer des attributions basées sur des règles métier
            feature_attributions = []
            
            creator_specific_weights = self._get_creator_specific_weights(request.creator_type)
            
            for feature_name, value in input_data.items():
                if feature_name in self.config.feature_names:
                    # Calculer l'importance basée sur la valeur et le poids spécifique au créateur
                    base_importance = abs(float(value)) if isinstance(value, (int, float)) else 0.5
                    creator_weight = creator_specific_weights.get(feature_name, 1.0)
                    importance = base_importance * creator_weight
                    
                    feature_attributions.append(FeatureAttribution(
                        feature_name=feature_name,
                        importance=importance,
                        value=value,
                        confidence=0.8,
                        contribution_direction="positive" if importance > 0.3 else "neutral",
                        creator_relevance=creator_weight
                    ))
            
            # Trier et limiter
            feature_attributions.sort(key=lambda x: x.importance, reverse=True)
            feature_attributions = feature_attributions[:request.max_features]
            
            global_importance = {
                attr.feature_name: attr.importance 
                for attr in feature_attributions
            }
            
            explanation = ModelExplanation(
                explanation_id=str(uuid.uuid4()),
                instance_id=request.instance_id,
                prediction=request.prediction,
                confidence=0.8,
                explanation_type=request.explanation_type,
                explainer_method=ExplainerMethod.CUSTOM,
                feature_attributions=feature_attributions,
                global_importance=global_importance,
                timestamp=datetime.now(),
                creator_type=request.creator_type,
                metadata={'method': 'creator_specific_custom'}
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error with custom explanation: {e}")
            return await self._explain_with_fallback(request)
    
    def _get_creator_specific_weights(self, creator_type: Optional[CreatorType]) -> Dict[str, float]:
        """Obtient les poids spécifiques au type de créateur"""
        if not creator_type:
            return {}
        
        weights = {
            CreatorType.MUSICIAN: {
                'audio_quality': 1.5,
                'tempo': 1.3,
                'genre': 1.2,
                'engagement_rate': 1.4,
                'duration': 1.1
            },
            CreatorType.BLOGGER: {
                'word_count': 1.3,
                'readability': 1.5,
                'seo_score': 1.4,
                'topic_relevance': 1.2,
                'engagement_rate': 1.3
            },
            CreatorType.PHOTOGRAPHER: {
                'image_quality': 1.5,
                'composition': 1.4,
                'color_balance': 1.2,
                'aesthetic_score': 1.3,
                'engagement_rate': 1.2
            },
            CreatorType.INFLUENCER: {
                'follower_count': 1.2,
                'engagement_rate': 1.5,
                'reach': 1.3,
                'brand_alignment': 1.4,
                'content_frequency': 1.1
            },
            CreatorType.COMEDIAN: {
                'humor_score': 1.5,
                'timing': 1.4,
                'audience_reaction': 1.3,
                'engagement_rate': 1.2,
                'content_originality': 1.3
            }
        }
        
        return weights.get(creator_type, {})
    
    async def _add_creator_specific_insights(self, explanation: ModelExplanation, creator_type: CreatorType):
        """Ajoute des insights spécifiques au type de créateur"""
        try:
            insights = []
            
            if creator_type == CreatorType.MUSICIAN:
                insights = [
                    "Audio quality is crucial for musician content success",
                    "Tempo and genre alignment affect audience engagement",
                    "Consider optimal posting times for music content"
                ]
            elif creator_type == CreatorType.BLOGGER:
                insights = [
                    "Content length and readability are key factors",
                    "SEO optimization significantly impacts visibility",
                    "Topic relevance drives audience retention"
                ]
            elif creator_type == CreatorType.PHOTOGRAPHER:
                insights = [
                    "Visual composition and image quality are primary drivers",
                    "Color balance affects aesthetic appeal",
                    "Technical excellence correlates with engagement"
                ]
            elif creator_type == CreatorType.INFLUENCER:
                insights = [
                    "Engagement rate is more important than follower count",
                    "Brand alignment affects monetization potential",
                    "Content consistency drives growth"
                ]
            elif creator_type == CreatorType.COMEDIAN:
                insights = [
                    "Timing and delivery are critical for humor content",
                    "Audience reaction patterns predict viral potential",
                    "Content originality differentiates from competitors"
                ]
            
            explanation.metadata['creator_insights'] = insights
            
        except Exception as e:
            logger.error(f"Error adding creator insights: {e}")
    
    async def _explain_with_fallback(self, request: ExplanationRequest) -> ModelExplanation:
        """Méthode d'explication de fallback"""
        return await self._create_fallback_explanation(request)
    
    async def _create_fallback_explanation(self, request: ExplanationRequest) -> ModelExplanation:
        """Crée une explication de base en cas d'erreur"""
        try:
            # Créer des attributions basiques
            feature_attributions = []
            for i, (feature_name, value) in enumerate(request.input_data.items()):
                if i >= request.max_features:
                    break
                
                importance = 1.0 / (i + 1)  # Importance décroissante
                feature_attributions.append(FeatureAttribution(
                    feature_name=feature_name,
                    importance=importance,
                    value=value,
                    confidence=0.3,
                    contribution_direction="neutral"
                ))
            
            global_importance = {
                attr.feature_name: attr.importance 
                for attr in feature_attributions
            }
            
            return ModelExplanation(
                explanation_id=str(uuid.uuid4()),
                instance_id=request.instance_id,
                prediction=request.prediction,
                confidence=0.3,
                explanation_type=request.explanation_type,
                explainer_method=ExplainerMethod.CUSTOM,
                feature_attributions=feature_attributions,
                global_importance=global_importance,
                timestamp=datetime.now(),
                creator_type=request.creator_type,
                metadata={'method': 'fallback', 'note': 'Basic explanation due to error or missing dependencies'}
            )
            
        except Exception as e:
            logger.error(f"Error creating fallback explanation: {e}")
            # Explication minimale en dernier recours
            return ModelExplanation(
                explanation_id=str(uuid.uuid4()),
                instance_id=request.instance_id,
                prediction=request.prediction,
                confidence=0.1,
                explanation_type=request.explanation_type,
                explainer_method=ExplainerMethod.CUSTOM,
                feature_attributions=[],
                global_importance={},
                timestamp=datetime.now(),
                creator_type=request.creator_type,
                metadata={'error': 'Failed to generate explanation'}
            )
    
    def _prepare_input_for_shap(self, input_data: Dict[str, Any]) -> np.ndarray:
        """Prépare les données d'entrée pour SHAP"""
        values = []
        for feature_name in self.config.feature_names:
            value = input_data.get(feature_name, 0)
            if isinstance(value, (int, float)):
                values.append(float(value))
            else:
                values.append(0.0)  # Valeur par défaut pour données non numériques
        
        return np.array([values])
    
    def _prepare_input_for_lime(self, input_data: Dict[str, Any]) -> np.ndarray:
        """Prépare les données d'entrée pour LIME"""
        return self._prepare_input_for_shap(input_data)
    
    def _create_shap_visualization_data(self, shap_values) -> Dict[str, Any]:
        """Crée les données de visualisation pour SHAP"""
        try:
            return {
                'shap_values': shap_values.values.tolist() if hasattr(shap_values, 'values') else [],
                'base_values': shap_values.base_values.tolist() if hasattr(shap_values, 'base_values') else [],
                'feature_names': self.config.feature_names
            }
        except:
            return {}
    
    def _create_lime_visualization_data(self, explanation) -> Dict[str, Any]:
        """Crée les données de visualisation pour LIME"""
        try:
            return {
                'feature_importance': explanation.as_list(),
                'score': getattr(explanation, 'score', None),
                'intercept': getattr(explanation, 'intercept', None)
            }
        except:
            return {}
    
    def _generate_cache_key(self, request: ExplanationRequest) -> str:
        """Génère une clé de cache pour une requête"""
        key_data = {
            'input_data': json.dumps(request.input_data, sort_keys=True),
            'explanation_type': request.explanation_type.value,
            'explainer_method': request.explainer_method.value,
            'creator_type': request.creator_type.value if request.creator_type else None,
            'max_features': request.max_features
        }
        return str(hash(json.dumps(key_data, sort_keys=True)))
    
    def _cache_explanation(self, cache_key: str, explanation: ModelExplanation):
        """Met en cache une explication"""
        if len(self.explanation_cache) >= self.config.max_cache_size:
            # Supprimer l'entrée la plus ancienne
            oldest_key = min(self.explanation_cache.keys(), 
                           key=lambda k: self.explanation_cache[k].timestamp)
            del self.explanation_cache[oldest_key]
        
        self.explanation_cache[cache_key] = explanation
    
    async def get_global_feature_importance(self, explanations: List[ModelExplanation]) -> Dict[str, float]:
        """Calcule l'importance globale des features sur un ensemble d'explications"""
        try:
            feature_importance = {}
            
            for explanation in explanations:
                for attr in explanation.feature_attributions:
                    if attr.feature_name not in feature_importance:
                        feature_importance[attr.feature_name] = []
                    feature_importance[attr.feature_name].append(attr.importance)
            
            # Calculer la moyenne
            global_importance = {
                feature: np.mean(importances) 
                for feature, importances in feature_importance.items()
            }
            
            return global_importance
            
        except Exception as e:
            logger.error(f"Error calculating global feature importance: {e}")
            return {}
    
    async def generate_explanation_summary(self, explanations: List[ModelExplanation]) -> Dict[str, Any]:
        """Génère un résumé des explications"""
        try:
            if not explanations:
                return {}
            
            # Statistiques générales
            total_explanations = len(explanations)
            methods_used = list(set(exp.explainer_method.value for exp in explanations))
            creator_types = list(set(exp.creator_type.value for exp in explanations if exp.creator_type))
            
            # Confiance moyenne
            avg_confidence = np.mean([exp.confidence for exp in explanations])
            
            # Top features globales
            global_importance = await self.get_global_feature_importance(explanations)
            top_features = sorted(global_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Analyse par créateur
            creator_analysis = {}
            for creator_type in creator_types:
                creator_explanations = [exp for exp in explanations if exp.creator_type and exp.creator_type.value == creator_type]
                if creator_explanations:
                    creator_importance = await self.get_global_feature_importance(creator_explanations)
                    creator_analysis[creator_type] = {
                        'count': len(creator_explanations),
                        'avg_confidence': np.mean([exp.confidence for exp in creator_explanations]),
                        'top_features': sorted(creator_importance.items(), key=lambda x: x[1], reverse=True)[:5]
                    }
            
            return {
                'explainer_id': self.explainer_id,
                'total_explanations': total_explanations,
                'methods_used': methods_used,
                'creator_types': creator_types,
                'average_confidence': avg_confidence,
                'top_global_features': top_features,
                'creator_analysis': creator_analysis,
                'cache_size': len(self.explanation_cache),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation summary: {e}")
            return {}

# Factory functions
def create_model_explainer(
    model: Any,
    feature_names: List[str],
    model_type: str = "classification",
    enable_shap: bool = True,
    enable_lime: bool = True
) -> ModelExplainer:
    """Factory pour créer un explainer de modèle"""
    config = ExplainerConfig(
        model_type=model_type,
        feature_names=feature_names,
        enable_shap=enable_shap,
        enable_lime=enable_lime
    )
    return ModelExplainer(config, model)

async def demo_model_explainer():
    """Démo du model explainer"""
    print("🔬 Model Explainer Demo")
    
    # Mock model
    class MockModel:
        def predict(self, X):
            return np.random.rand(len(X))
        
        def predict_proba(self, X):
            probs = np.random.rand(len(X), 2)
            return probs / probs.sum(axis=1, keepdims=True)
    
    model = MockModel()
    feature_names = ['audio_quality', 'tempo', 'genre_score', 'engagement_rate']
    
    explainer = create_model_explainer(model, feature_names)
    
    # Créer une requête d'explication
    request = ExplanationRequest(
        instance_id="test_instance_1",
        input_data={
            'audio_quality': 0.85,
            'tempo': 120,
            'genre_score': 0.7,
            'engagement_rate': 0.12
        },
        prediction=[0.3, 0.7],
        explanation_type=ExplanationType.LOCAL,
        explainer_method=ExplainerMethod.CUSTOM,
        creator_type=CreatorType.MUSICIAN,
        max_features=4
    )
    
    # Générer l'explication
    explanation = await explainer.explain_prediction(request)
    
    print(f"\n📊 Explanation for instance: {explanation.instance_id}")
    print(f"Method: {explanation.explainer_method.value}")
    print(f"Confidence: {explanation.confidence:.3f}")
    print(f"Creator Type: {explanation.creator_type.value if explanation.creator_type else 'N/A'}")
    
    print("\n🎯 Top Feature Attributions:")
    for attr in explanation.feature_attributions[:5]:
        print(f"  {attr.feature_name}: {attr.importance:.3f} ({attr.contribution_direction})")
    
    if explanation.metadata.get('creator_insights'):
        print("\n💡 Creator-Specific Insights:")
        for insight in explanation.metadata['creator_insights'][:3]:
            print(f"  • {insight}")

if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(level=logging.INFO)
    
    # Lancer la démo
    asyncio.run(demo_model_explainer())