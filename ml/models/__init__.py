"""
ML Models Module - IA Chérie Enterprise
===================================
Registry central des modèles ML avec factory patterns.
Content analysis + quality assessment + sentiment analysis + recommendations + copyright + engagement.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie ML Models
Version: 1.0 Production
"""

from typing import Dict, Any, Optional, Type, Union, List
import logging
import numpy as np

# ⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
# Cette architecture ML et tous ses algorithmes sont la propriété intellectuelle 
# EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Tous droits réservés.

logger = logging.getLogger(__name__)

# Import all model services
from .content_classification_model import (
    ContentClassificationService,
    create_content_classifier,
    ContentType,
    CreatorCategory,
    ContentInput,
    ContentClassificationResult
)

from .quality_assessment_model import (
    QualityAssessmentService,
    create_quality_assessor,
    QualityDimension,
    QualityLevel,
    QualityAssessmentResult
)

from .sentiment_analysis_model import (
    SentimentAnalysisService,
    create_sentiment_analyzer,
    SentimentPolarity,
    EmotionCategory,
    BrandSafetyLevel,
    SentimentAnalysisResult
)

from .content_recommendation_model import (
    ContentRecommendationService,
    create_content_recommender,
    RecommendationType,
    RecommendationResult
)

from .copyright_detection_model import (
    CopyrightDetectionService,
    create_copyright_detector,
    InfringementType,
    MediaType,
    CopyrightDetectionResult
)

from .engagement_prediction_model import (
    EngagementPredictionService,
    create_engagement_predictor,
    EngagementType,
    ViralityLevel,
    EngagementPredictionResult
)

class MLModelsRegistry:
    """
    Registry central pour tous les modèles ML IA Chérie.
    Factory patterns + service orchestration + model lifecycle management.
    """
    
    def __init__(self):
        self._models = {}
        self._factories = {
            'content_classification': create_content_classifier,
            'quality_assessment': create_quality_assessor,
            'sentiment_analysis': create_sentiment_analyzer,
            'content_recommendation': create_content_recommender,
            'copyright_detection': create_copyright_detector,
            'engagement_prediction': create_engagement_predictor
        }
        
        # Model capabilities mapping
        self._capabilities = {
            'content_classification': [
                'multi_modal_processing',
                'business_intelligence',
                'creator_categorization',
                'monetization_scoring'
            ],
            'quality_assessment': [
                'technical_quality_analysis',
                'aesthetic_scoring',
                'platform_compatibility',
                'business_value_assessment'
            ],
            'sentiment_analysis': [
                'emotion_detection',
                'brand_safety_assessment',
                'audience_targeting',
                'cultural_sensitivity'
            ],
            'content_recommendation': [
                'collaborative_filtering',
                'content_based_filtering',
                'viral_prediction',
                'creator_matching'
            ],
            'copyright_detection': [
                'audio_fingerprinting',
                'visual_similarity',
                'text_plagiarism',
                'legal_compliance'
            ],
            'engagement_prediction': [
                'time_series_forecasting',
                'viral_potential_analysis',
                'audience_behavior_modeling',
                'monetization_forecasting'
            ]
        }
    
    def get_model(self, model_name: str, **config_kwargs) -> Any:
        """Obtenir instance modèle avec configuration"""
        if model_name not in self._factories:
            raise ValueError(f"Unknown model: {model_name}. Available models: {list(self._factories.keys())}")
        
        # Check if model is already initialized with same config
        cache_key = f"{model_name}_{hash(str(sorted(config_kwargs.items())))}"
        
        if cache_key not in self._models:
            factory = self._factories[model_name]
            self._models[cache_key] = factory(**config_kwargs)
            logger.info(f"Initialized ML model: {model_name} with config: {config_kwargs}")
        
        return self._models[cache_key]
    
    def get_model_capabilities(self, model_name: str) -> List[str]:
        """Obtenir capabilities d'un modèle"""
        return self._capabilities.get(model_name, [])
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Lister tous les modèles disponibles avec métadonnées"""
        models_info = {}
        
        for model_name, factory in self._factories.items():
            models_info[model_name] = {
                'factory_function': factory.__name__,
                'capabilities': self._capabilities.get(model_name, []),
                'description': factory.__doc__ or "No description available",
                'initialized': any(model_name in key for key in self._models.keys())
            }
        
        return models_info
    
    def create_ml_pipeline(self, pipeline_config: Dict[str, Any]) -> 'MLPipeline':
        """Créer pipeline ML avec plusieurs modèles"""
        return MLPipeline(self, pipeline_config)
    
    def get_business_intelligence_models(self) -> Dict[str, Any]:
        """Obtenir modèles optimisés pour business intelligence"""
        bi_models = {}
        
        for model_name in ['content_classification', 'quality_assessment', 
                          'sentiment_analysis', 'engagement_prediction']:
            bi_models[model_name] = self.get_model(
                model_name,
                enable_business_scoring=True,
                enable_monetization_analysis=True
            )
        
        return bi_models
    
    def clear_cache(self):
        """Clear model cache"""
        self._models.clear()
        logger.info("ML models cache cleared")

class MLPipeline:
    """
    Pipeline ML pour orchestration multi-modèles.
    Content processing workflow avec business optimization.
    """
    
    def __init__(self, registry: MLModelsRegistry, pipeline_config: Dict[str, Any]):
        self.registry = registry
        self.config = pipeline_config
        self.models = {}
        
        # Initialize models based on pipeline config
        for model_name, model_config in pipeline_config.get('models', {}).items():
            self.models[model_name] = registry.get_model(model_name, **model_config)
    
    async def process_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pipeline complet processing contenu avec business optimization.
        
        Pipeline Features:
        - Content classification multi-modal avec business context
        - Quality assessment technique et esthétique
        - Sentiment analysis avec brand safety
        - Engagement prediction avec viral potential
        - Copyright detection avec legal compliance
        - Content recommendations avec monetization optimization
        """
        results = {
            'content_id': content_data.get('content_id', 'unknown'),
            'processing_timestamp': str(np.datetime64('now')),
            'pipeline_results': {},
            'business_insights': {},
            'optimization_recommendations': []
        }
        
        try:
            # Phase 1: Content Analysis
            if 'content_classification' in self.models:
                classification_result = await self._classify_content(content_data)
                results['pipeline_results']['classification'] = classification_result
            
            # Phase 2: Quality Assessment
            if 'quality_assessment' in self.models:
                quality_result = await self._assess_quality(content_data)
                results['pipeline_results']['quality'] = quality_result
            
            # Phase 3: Sentiment Analysis
            if 'sentiment_analysis' in self.models:
                sentiment_result = await self._analyze_sentiment(content_data)
                results['pipeline_results']['sentiment'] = sentiment_result
            
            # Phase 4: Engagement Prediction
            if 'engagement_prediction' in self.models:
                engagement_result = await self._predict_engagement(content_data)
                results['pipeline_results']['engagement'] = engagement_result
            
            # Phase 5: Copyright Detection
            if 'copyright_detection' in self.models:
                copyright_result = await self._detect_copyright(content_data)
                results['pipeline_results']['copyright'] = copyright_result
            
            # Phase 6: Generate Business Insights
            results['business_insights'] = self._generate_business_insights(
                results['pipeline_results']
            )
            
            # Phase 7: Optimization Recommendations
            results['optimization_recommendations'] = self._generate_optimization_recommendations(
                results['pipeline_results'], results['business_insights']
            )
            
        except Exception as e:
            logger.error(f"ML Pipeline processing error: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _classify_content(self, content_data: Dict[str, Any]) -> Any:
        """Classification contenu avec business context"""
        content_input = ContentInput(
            content_id=content_data.get('content_id', 'unknown'),
            content_type=ContentType(content_data.get('content_type', 'image')),
            file_path=content_data.get('file_path'),
            raw_data=content_data.get('raw_data'),
            metadata=content_data.get('metadata', {}),
            creator_context=content_data.get('creator_context', {})
        )
        
        classifier = self.models['content_classification']
        return await classifier.model.classify_content(content_input)
    
    async def _assess_quality(self, content_data: Dict[str, Any]) -> Any:
        """Assessment qualité avec business scoring"""
        quality_input = {
            'content_id': content_data.get('content_id', 'unknown'),
            'file_path': content_data.get('file_path'),
            'content_type': content_data.get('content_type', 'image')
        }
        
        assessor = self.models['quality_assessment']
        return await assessor.model.assess_content_quality(quality_input)
    
    async def _analyze_sentiment(self, content_data: Dict[str, Any]) -> Any:
        """Analyse sentiment avec brand safety"""
        from .sentiment_analysis_model import SentimentInput
        
        text_content = content_data.get('text_content', content_data.get('description', ''))
        
        sentiment_input = SentimentInput(
            content_id=content_data.get('content_id', 'unknown'),
            text_content=text_content,
            language=content_data.get('language'),
            context=content_data.get('context'),
            platform=content_data.get('platform')
        )
        
        analyzer = self.models['sentiment_analysis']
        return await analyzer.model.analyze_content_sentiment(sentiment_input)
    
    def _generate_business_insights(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Génération insights business agrégés"""
        insights = {
            'overall_business_score': 0.5,
            'monetization_potential': 0.5,
            'risk_assessment': 'LOW',
            'market_viability': 0.5,
            'creator_growth_potential': 0.5
        }
        
        scores = []
        
        # Extract business scores from each model
        if 'classification' in pipeline_results:
            scores.append(0.7)  # Mock business score
        
        if 'quality' in pipeline_results:
            scores.append(0.8)  # Mock quality score
        
        # Calculate aggregated insights
        if scores:
            insights['overall_business_score'] = np.mean(scores)
            insights['monetization_potential'] = max(scores)
        
        return insights
    
    def _generate_optimization_recommendations(self, pipeline_results: Dict[str, Any],
                                             business_insights: Dict[str, Any]) -> List[str]:
        """Génération recommandations optimization"""
        recommendations = [
            "Content analysis completed successfully",
            "Consider optimizing for target platform requirements",
            "Monitor engagement metrics for performance insights"
        ]
        
        # Business score based recommendations
        overall_score = business_insights.get('overall_business_score', 0.0)
        
        if overall_score < 0.6:
            recommendations.append("Consider content quality improvements for better business performance")
        
        if overall_score > 0.8:
            recommendations.append("High business potential detected - consider premium monetization strategies")
        
        return recommendations[:5]  # Limit to top 5 recommendations

# Global registry instance
ml_registry = MLModelsRegistry()

# Convenience functions
def get_ml_model(model_name: str, **config_kwargs):
    """Get ML model instance from global registry"""
    return ml_registry.get_model(model_name, **config_kwargs)

def create_ml_pipeline(pipeline_config: Dict[str, Any]) -> MLPipeline:
    """Create ML pipeline from global registry"""
    return ml_registry.create_ml_pipeline(pipeline_config)

def get_business_intelligence_suite() -> Dict[str, Any]:
    """Get complete business intelligence model suite"""
    return ml_registry.get_business_intelligence_models()

# Export all classes and functions
__all__ = [
    # Registry and Pipeline
    'MLModelsRegistry',
    'MLPipeline', 
    'ml_registry',
    'get_ml_model',
    'create_ml_pipeline',
    'get_business_intelligence_suite',
    
    # Content Classification
    'ContentClassificationService',
    'create_content_classifier',
    'ContentType',
    'CreatorCategory',
    'ContentInput',
    'ContentClassificationResult',
    
    # Quality Assessment
    'QualityAssessmentService',
    'create_quality_assessor', 
    'QualityDimension',
    'QualityLevel',
    'QualityAssessmentResult',
    
    # Sentiment Analysis
    'SentimentAnalysisService',
    'create_sentiment_analyzer',
    'SentimentPolarity',
    'EmotionCategory',
    'BrandSafetyLevel',
    'SentimentAnalysisResult',
    
    # Content Recommendation
    'ContentRecommendationService',
    'create_content_recommender',
    'RecommendationType',
    'RecommendationResult',
    
    # Copyright Detection
    'CopyrightDetectionService',
    'create_copyright_detector',
    'InfringementType',
    'MediaType',
    'CopyrightDetectionResult',
    
    # Engagement Prediction
    'EngagementPredictionService',
    'create_engagement_predictor',
    'EngagementType',
    'ViralityLevel',
    'EngagementPredictionResult'
]
