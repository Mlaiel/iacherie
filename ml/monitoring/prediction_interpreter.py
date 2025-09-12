#!/usr/bin/env python3
"""
Prediction Interpreter for Ainflue ML Models
Individual prediction interpretation for transparency and trust

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictionExplanation:
    """Individual prediction explanation"""
    prediction_id: str
    model_id: str
    predicted_value: float
    confidence_score: float
    explanation_text: str
    key_factors: List[Dict[str, Any]]
    counterfactuals: List[Dict[str, Any]]
    certainty_level: str  # HIGH, MEDIUM, LOW
    explanation_method: str
    creator_context: Dict[str, Any]
    timestamp: datetime

@dataclass
class FeatureFactor:
    """Feature contribution factor"""
    feature_name: str
    feature_value: Any
    contribution_score: float
    contribution_direction: str  # POSITIVE, NEGATIVE, NEUTRAL
    importance_rank: int
    human_readable_description: str

@dataclass
class CounterfactualExample:
    """Counterfactual explanation example"""
    original_features: Dict[str, Any]
    modified_features: Dict[str, Any]
    original_prediction: float
    counterfactual_prediction: float
    changes_description: str
    feasibility_score: float  # How realistic the changes are

class PredictionInterpreter(ABC):
    """Abstract base class for prediction interpreters"""
    
    @abstractmethod
    async def interpret_prediction(self, 
                                  prediction_value: float,
                                  feature_values: Dict[str, Any],
                                  model_metadata: Dict[str, Any]) -> PredictionExplanation:
        """Interpret individual prediction"""
        pass

class ShapleyValueInterpreter(PredictionInterpreter):
    """Shapley value-based prediction interpreter"""
    
    async def interpret_prediction(self, 
                                  prediction_value: float,
                                  feature_values: Dict[str, Any],
                                  model_metadata: Dict[str, Any]) -> PredictionExplanation:
        """Interpret prediction using Shapley values"""
        try:
            prediction_id = f"pred_{int(datetime.now().timestamp())}"
            model_id = model_metadata.get('model_id', 'unknown')
            
            # Calculate feature contributions (simplified SHAP-like)
            feature_contributions = await self._calculate_shapley_values(
                feature_values, model_metadata
            )
            
            # Generate key factors
            key_factors = await self._generate_key_factors(feature_contributions)
            
            # Generate counterfactuals
            counterfactuals = await self._generate_counterfactuals(
                feature_values, prediction_value, model_metadata
            )
            
            # Calculate confidence
            confidence_score = await self._calculate_confidence(
                prediction_value, feature_contributions
            )
            
            # Generate explanation text
            explanation_text = await self._generate_explanation_text(
                prediction_value, key_factors, model_metadata
            )
            
            # Determine certainty level
            certainty_level = self._determine_certainty_level(confidence_score)
            
            return PredictionExplanation(
                prediction_id=prediction_id,
                model_id=model_id,
                predicted_value=prediction_value,
                confidence_score=confidence_score,
                explanation_text=explanation_text,
                key_factors=key_factors,
                counterfactuals=counterfactuals,
                certainty_level=certainty_level,
                explanation_method='shapley_values',
                creator_context=model_metadata.get('creator_context', {}),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error interpreting prediction with Shapley values: {e}")
            raise
    
    async def _calculate_shapley_values(self, 
                                       feature_values: Dict[str, Any],
                                       model_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Calculate Shapley values for features (simplified)"""
        try:
            # Simplified Shapley value calculation
            contributions = {}
            baseline_prediction = 0.5  # Neutral baseline
            
            for feature_name, feature_value in feature_values.items():
                # Simulate Shapley value calculation
                if isinstance(feature_value, (int, float)):
                    # Normalize feature value
                    normalized_value = max(-1, min(1, (feature_value - 0.5) * 2))
                    contribution = normalized_value * np.random.uniform(0.1, 0.3)
                else:
                    # Categorical features
                    contribution = np.random.uniform(-0.2, 0.2)
                
                contributions[feature_name] = contribution
            
            return contributions
            
        except Exception as e:
            logger.error(f"Error calculating Shapley values: {e}")
            return {}
    
    async def _generate_key_factors(self, 
                                   feature_contributions: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate key factors from feature contributions"""
        try:
            # Sort contributions by absolute value
            sorted_contributions = sorted(
                feature_contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            key_factors = []
            for i, (feature_name, contribution) in enumerate(sorted_contributions[:5]):
                direction = 'POSITIVE' if contribution > 0 else 'NEGATIVE'
                if abs(contribution) < 0.01:
                    direction = 'NEUTRAL'
                
                factor = {
                    'feature_name': feature_name,
                    'contribution_score': contribution,
                    'contribution_direction': direction,
                    'importance_rank': i + 1,
                    'human_readable_description': self._generate_factor_description(
                        feature_name, contribution, direction
                    )
                }
                key_factors.append(factor)
            
            return key_factors
            
        except Exception as e:
            logger.error(f"Error generating key factors: {e}")
            return []
    
    def _generate_factor_description(self, feature_name: str, contribution: float, direction: str) -> str:
        """Generate human-readable factor description"""
        try:
            impact = "strongly" if abs(contribution) > 0.2 else "moderately" if abs(contribution) > 0.1 else "slightly"
            direction_text = "increases" if direction == 'POSITIVE' else "decreases"
            
            # Feature-specific descriptions
            feature_descriptions = {
                'engagement_rate': f"The engagement rate {impact} {direction_text} the prediction",
                'content_quality_score': f"Content quality {impact} {direction_text} the predicted outcome",
                'follower_count': f"Follower count {impact} {direction_text} the likelihood",
                'posting_frequency': f"Posting frequency {impact} {direction_text} the result",
                'audio_quality': f"Audio quality {impact} {direction_text} the prediction",
                'genre_popularity': f"Genre popularity {impact} {direction_text} the outcome",
                'collaboration_count': f"Number of collaborations {impact} {direction_text} the prediction"
            }
            
            return feature_descriptions.get(
                feature_name, 
                f"{feature_name.replace('_', ' ').title()} {impact} {direction_text} the prediction"
            )
            
        except Exception as e:
            logger.error(f"Error generating factor description: {e}")
            return f"{feature_name} affects the prediction"
    
    async def _generate_counterfactuals(self, 
                                       feature_values: Dict[str, Any],
                                       prediction_value: float,
                                       model_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate counterfactual examples"""
        try:
            counterfactuals = []
            
            # Generate 2-3 counterfactual scenarios
            scenarios = [
                {'name': 'Optimistic', 'factor': 1.2},
                {'name': 'Pessimistic', 'factor': 0.8},
                {'name': 'Alternative', 'factor': 1.1}
            ]
            
            for scenario in scenarios:
                modified_features = feature_values.copy()
                changes_description = f"{scenario['name']} scenario: "
                
                # Modify key features
                key_features = ['engagement_rate', 'content_quality_score', 'follower_count']
                modified_keys = []
                
                for key in key_features:
                    if key in modified_features and isinstance(modified_features[key], (int, float)):
                        original_value = modified_features[key]
                        modified_features[key] = original_value * scenario['factor']
                        modified_keys.append(key)
                
                if modified_keys:
                    changes_description += f"Modified {', '.join(modified_keys)}"
                    
                    # Simulate counterfactual prediction
                    counterfactual_prediction = prediction_value * scenario['factor']
                    counterfactual_prediction = max(0, min(1, counterfactual_prediction))
                    
                    # Calculate feasibility (how realistic the changes are)
                    feasibility_score = 0.8 if scenario['factor'] <= 1.1 else 0.6
                    
                    counterfactual = {
                        'scenario_name': scenario['name'],
                        'original_features': feature_values,
                        'modified_features': modified_features,
                        'original_prediction': prediction_value,
                        'counterfactual_prediction': counterfactual_prediction,
                        'changes_description': changes_description,
                        'feasibility_score': feasibility_score
                    }
                    counterfactuals.append(counterfactual)
            
            return counterfactuals[:2]  # Return top 2 counterfactuals
            
        except Exception as e:
            logger.error(f"Error generating counterfactuals: {e}")
            return []
    
    async def _calculate_confidence(self, 
                                   prediction_value: float,
                                   feature_contributions: Dict[str, float]) -> float:
        """Calculate prediction confidence score"""
        try:
            # Confidence based on prediction certainty and feature consistency
            certainty = abs(prediction_value - 0.5) * 2  # Distance from neutral
            
            # Feature consistency (how aligned are the contributions)
            contributions = list(feature_contributions.values())
            if contributions:
                consistency = 1 - (np.std(contributions) / (np.mean(np.abs(contributions)) + 0.01))
                consistency = max(0, min(1, consistency))
            else:
                consistency = 0.5
            
            # Combined confidence score
            confidence = (certainty * 0.6 + consistency * 0.4)
            return max(0.1, min(0.99, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    async def _generate_explanation_text(self, 
                                        prediction_value: float,
                                        key_factors: List[Dict[str, Any]],
                                        model_metadata: Dict[str, Any]) -> str:
        """Generate human-readable explanation text"""
        try:
            creator_type = model_metadata.get('creator_context', {}).get('creator_type', 'creator')
            model_purpose = model_metadata.get('model_purpose', 'outcome')
            
            # Base explanation
            prediction_level = "high" if prediction_value > 0.7 else "moderate" if prediction_value > 0.4 else "low"
            
            explanation = f"This {creator_type} has a {prediction_level} predicted {model_purpose} "
            explanation += f"(score: {prediction_value:.2f}). "
            
            # Add key factors
            if key_factors:
                top_factor = key_factors[0]
                factor_impact = "positive" if top_factor['contribution_direction'] == 'POSITIVE' else "negative"
                
                explanation += f"The most significant {factor_impact} factor is {top_factor['feature_name'].replace('_', ' ')}. "
                
                if len(key_factors) > 1:
                    other_factors = [f['feature_name'].replace('_', ' ') for f in key_factors[1:3]]
                    explanation += f"Other important factors include {', '.join(other_factors)}."
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation text: {e}")
            return "The prediction is based on multiple factors in the input data."
    
    def _determine_certainty_level(self, confidence_score: float) -> str:
        """Determine certainty level from confidence score"""
        if confidence_score >= 0.8:
            return 'HIGH'
        elif confidence_score >= 0.6:
            return 'MEDIUM'
        else:
            return 'LOW'

class RuleBasedInterpreter(PredictionInterpreter):
    """Rule-based prediction interpreter"""
    
    async def interpret_prediction(self, 
                                  prediction_value: float,
                                  feature_values: Dict[str, Any],
                                  model_metadata: Dict[str, Any]) -> PredictionExplanation:
        """Interpret prediction using rule-based approach"""
        try:
            prediction_id = f"rule_pred_{int(datetime.now().timestamp())}"
            model_id = model_metadata.get('model_id', 'unknown')
            
            # Apply interpretation rules
            rules_applied = await self._apply_interpretation_rules(
                feature_values, prediction_value, model_metadata
            )
            
            # Generate explanation
            explanation_text = await self._generate_rule_explanation(
                rules_applied, prediction_value, model_metadata
            )
            
            # Convert rules to key factors format
            key_factors = self._convert_rules_to_factors(rules_applied)
            
            # Simple confidence calculation
            confidence_score = 0.8 if len(rules_applied) > 0 else 0.4
            
            return PredictionExplanation(
                prediction_id=prediction_id,
                model_id=model_id,
                predicted_value=prediction_value,
                confidence_score=confidence_score,
                explanation_text=explanation_text,
                key_factors=key_factors,
                counterfactuals=[],  # Rule-based doesn't generate counterfactuals
                certainty_level='HIGH' if confidence_score > 0.7 else 'MEDIUM',
                explanation_method='rule_based',
                creator_context=model_metadata.get('creator_context', {}),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error interpreting prediction with rules: {e}")
            raise
    
    async def _apply_interpretation_rules(self, 
                                         feature_values: Dict[str, Any],
                                         prediction_value: float,
                                         model_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply interpretation rules to features"""
        try:
            rules_applied = []
            creator_type = model_metadata.get('creator_context', {}).get('creator_type', 'creator')
            
            # Engagement rules
            engagement_rate = feature_values.get('engagement_rate', 0)
            if engagement_rate > 0.1:
                rules_applied.append({
                    'rule': 'high_engagement',
                    'description': 'High engagement rate indicates strong audience connection',
                    'feature': 'engagement_rate',
                    'value': engagement_rate,
                    'impact': 'positive'
                })
            elif engagement_rate < 0.02:
                rules_applied.append({
                    'rule': 'low_engagement',
                    'description': 'Low engagement rate may limit reach and impact',
                    'feature': 'engagement_rate',
                    'value': engagement_rate,
                    'impact': 'negative'
                })
            
            # Content quality rules
            content_quality = feature_values.get('content_quality_score', 0)
            if content_quality > 0.8:
                rules_applied.append({
                    'rule': 'high_quality',
                    'description': 'High content quality supports positive outcomes',
                    'feature': 'content_quality_score',
                    'value': content_quality,
                    'impact': 'positive'
                })
            
            # Creator-specific rules
            if creator_type == 'musician':
                audio_quality = feature_values.get('audio_quality', 0)
                if audio_quality > 0.7:
                    rules_applied.append({
                        'rule': 'professional_audio',
                        'description': 'Professional audio quality enhances listener experience',
                        'feature': 'audio_quality',
                        'value': audio_quality,
                        'impact': 'positive'
                    })
            
            elif creator_type == 'blogger':
                readability = feature_values.get('readability_score', 0)
                if readability > 0.6:
                    rules_applied.append({
                        'rule': 'readable_content',
                        'description': 'Good readability improves audience retention',
                        'feature': 'readability_score',
                        'value': readability,
                        'impact': 'positive'
                    })
            
            return rules_applied
            
        except Exception as e:
            logger.error(f"Error applying interpretation rules: {e}")
            return []
    
    async def _generate_rule_explanation(self, 
                                        rules_applied: List[Dict[str, Any]],
                                        prediction_value: float,
                                        model_metadata: Dict[str, Any]]) -> str:
        """Generate explanation from applied rules"""
        try:
            if not rules_applied:
                return "The prediction is based on the overall combination of input features."
            
            explanation = f"The prediction (score: {prediction_value:.2f}) is based on the following key observations: "
            
            rule_descriptions = []
            for rule in rules_applied[:3]:  # Top 3 rules
                rule_descriptions.append(rule['description'])
            
            explanation += "; ".join(rule_descriptions) + "."
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating rule explanation: {e}")
            return "The prediction is based on multiple rule-based factors."
    
    def _convert_rules_to_factors(self, rules_applied: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert applied rules to key factors format"""
        try:
            key_factors = []
            
            for i, rule in enumerate(rules_applied):
                direction = 'POSITIVE' if rule['impact'] == 'positive' else 'NEGATIVE'
                contribution_score = 0.3 if rule['impact'] == 'positive' else -0.3
                
                factor = {
                    'feature_name': rule['feature'],
                    'contribution_score': contribution_score,
                    'contribution_direction': direction,
                    'importance_rank': i + 1,
                    'human_readable_description': rule['description']
                }
                key_factors.append(factor)
            
            return key_factors
            
        except Exception as e:
            logger.error(f"Error converting rules to factors: {e}")
            return []

class PredictionInterpreterService:
    """
    Enterprise prediction interpreter service for Ainflue ML models
    
    🎖️ EXPERT MULTI-ROLE IMPLEMENTATION:
    - Lead Dev IA: Orchestration of prediction interpretation across all model types
    - ML Engineer: Advanced interpretation algorithms and explainability methods
    - Security: Transparent and auditable AI for compliance requirements
    - Audio Engineer: Creator-specific interpretation for musicians
    - Business Analyst: Business-friendly explanation generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize prediction interpreter service"""
        self.config = config or {}
        
        # Interpretation methods
        self.interpreters = {
            'shapley_values': ShapleyValueInterpreter(),
            'rule_based': RuleBasedInterpreter()
        }
        
        # Creator-specific interpretation configurations
        self.creator_interpretation_configs = {
            'musician': {
                'preferred_method': 'shapley_values',
                'key_features': ['audio_quality', 'genre_popularity', 'collaboration_count', 'engagement_rate'],
                'business_context': 'music engagement and monetization',
                'explanation_style': 'technical_and_creative'
            },
            'blogger': {
                'preferred_method': 'rule_based',
                'key_features': ['readability_score', 'seo_ranking', 'content_length', 'social_shares'],
                'business_context': 'content reach and reader engagement',
                'explanation_style': 'analytical_and_actionable'
            },
            'photographer': {
                'preferred_method': 'shapley_values',
                'key_features': ['visual_composition', 'technical_quality', 'portfolio_diversity', 'client_satisfaction'],
                'business_context': 'visual impact and professional success',
                'explanation_style': 'visual_and_professional'
            },
            'influencer': {
                'preferred_method': 'rule_based',
                'key_features': ['follower_engagement', 'brand_alignment', 'trend_relevance', 'authenticity_score'],
                'business_context': 'influence reach and brand partnerships',
                'explanation_style': 'strategic_and_marketable'
            },
            'comedian': {
                'preferred_method': 'rule_based',
                'key_features': ['humor_timing', 'audience_response', 'material_originality', 'stage_presence'],
                'business_context': 'comedic impact and audience engagement',
                'explanation_style': 'performance_oriented'
            }
        }
        
        logger.info("✅ Prediction Interpreter Service initialized")
    
    async def interpret_individual_prediction(self, 
                                            prediction_id: str,
                                            prediction_value: float,
                                            feature_values: Dict[str, Any],
                                            model_metadata: Dict[str, Any]) -> PredictionExplanation:
        """
        Interpret individual prediction with contextual explanation
        
        🎖️ LEAD DEV IA: Orchestration of comprehensive prediction interpretation
        """
        try:
            logger.info(f"🔍 Interpreting prediction {prediction_id}")
            
            # Get creator context
            creator_type = model_metadata.get('creator_context', {}).get('creator_type', 'musician')
            
            # Get interpretation configuration
            config = self.creator_interpretation_configs.get(creator_type, 
                                                           self.creator_interpretation_configs['musician'])
            
            # Select appropriate interpreter
            interpreter_method = config['preferred_method']
            interpreter = self.interpreters.get(interpreter_method, self.interpreters['shapley_values'])
            
            # Enhance model metadata with creator context
            enhanced_metadata = model_metadata.copy()
            enhanced_metadata['creator_context'] = {
                'creator_type': creator_type,
                'business_context': config['business_context'],
                'explanation_style': config['explanation_style'],
                'key_features': config['key_features']
            }
            
            # Get interpretation
            explanation = await interpreter.interpret_prediction(
                prediction_value, feature_values, enhanced_metadata
            )
            
            # Update prediction ID
            explanation.prediction_id = prediction_id
            
            # Enhance explanation with creator-specific insights
            enhanced_explanation = await self._enhance_creator_explanation(
                explanation, creator_type, feature_values
            )
            
            logger.info(f"✅ Prediction interpretation complete")
            logger.info(f"   Confidence: {enhanced_explanation.confidence_score:.1%}")
            logger.info(f"   Certainty: {enhanced_explanation.certainty_level}")
            logger.info(f"   Key Factors: {len(enhanced_explanation.key_factors)}")
            
            return enhanced_explanation
            
        except Exception as e:
            logger.error(f"❌ Error interpreting prediction: {e}")
            raise
    
    async def _enhance_creator_explanation(self, 
                                          explanation: PredictionExplanation,
                                          creator_type: str,
                                          feature_values: Dict[str, Any]) -> PredictionExplanation:
        """
        Enhance explanation with creator-specific insights
        
        🎵 AUDIO ENGINEER: Creator-specific explanation enhancement
        """
        try:
            # Add creator-specific context to explanation text
            if creator_type == 'musician':
                if 'audio_quality' in feature_values:
                    audio_quality = feature_values['audio_quality']
                    if audio_quality > 0.8:
                        explanation.explanation_text += " The high audio quality significantly enhances the musical experience."
                    elif audio_quality < 0.5:
                        explanation.explanation_text += " Improving audio quality could substantially boost engagement."
            
            elif creator_type == 'blogger':
                if 'readability_score' in feature_values and 'seo_ranking' in feature_values:
                    explanation.explanation_text += " Content readability and SEO optimization are key drivers for blog success."
            
            elif creator_type == 'photographer':
                if 'visual_composition' in feature_values:
                    composition_score = feature_values['visual_composition']
                    if composition_score > 0.7:
                        explanation.explanation_text += " Strong visual composition creates compelling portfolio appeal."
            
            # Add creator-specific recommendations to key factors
            for factor in explanation.key_factors:
                factor['creator_specific_tip'] = self._get_creator_specific_tip(
                    factor['feature_name'], creator_type, factor['contribution_direction']
                )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error enhancing creator explanation: {e}")
            return explanation
    
    def _get_creator_specific_tip(self, feature_name: str, creator_type: str, direction: str) -> str:
        """
        Get creator-specific actionable tips
        
        💼 BUSINESS ANALYST: Business-actionable recommendation generation
        """
        try:
            tips = {
                'musician': {
                    'audio_quality': {
                        'POSITIVE': "Maintain high audio standards to keep listeners engaged",
                        'NEGATIVE': "Consider investing in better recording equipment or mastering"
                    },
                    'engagement_rate': {
                        'POSITIVE': "Keep engaging with your audience through comments and collaborations",
                        'NEGATIVE': "Try posting more interactive content and responding to fan comments"
                    }
                },
                'blogger': {
                    'readability_score': {
                        'POSITIVE': "Continue writing in an accessible and engaging style",
                        'NEGATIVE': "Break up long paragraphs and use simpler sentence structures"
                    },
                    'seo_ranking': {
                        'POSITIVE': "Your SEO strategy is working well - keep optimizing",
                        'NEGATIVE': "Focus on keyword research and improving page load speeds"
                    }
                },
                'photographer': {
                    'visual_composition': {
                        'POSITIVE': "Your composition skills are a strong asset",
                        'NEGATIVE': "Study composition techniques like rule of thirds and leading lines"
                    },
                    'technical_quality': {
                        'POSITIVE': "Technical execution is excellent",
                        'NEGATIVE': "Consider improving camera settings and post-processing skills"
                    }
                }
            }
            
            creator_tips = tips.get(creator_type, {})
            feature_tips = creator_tips.get(feature_name, {})
            return feature_tips.get(direction, "Continue optimizing this aspect for better results")
            
        except Exception as e:
            logger.error(f"Error getting creator-specific tip: {e}")
            return "Focus on improving this aspect for better outcomes"
    
    async def batch_interpret_predictions(self, 
                                        predictions: List[Dict[str, Any]]) -> List[PredictionExplanation]:
        """
        Interpret multiple predictions in batch
        
        🛡️ BACKEND SENIOR: Efficient batch processing for high-volume interpretation
        """
        try:
            logger.info(f"🔍 Batch interpreting {len(predictions)} predictions")
            
            interpretation_tasks = []
            for pred in predictions:
                task = self.interpret_individual_prediction(
                    prediction_id=pred['prediction_id'],
                    prediction_value=pred['prediction_value'],
                    feature_values=pred['feature_values'],
                    model_metadata=pred['model_metadata']
                )
                interpretation_tasks.append(task)
            
            # Execute batch interpretations
            explanations = await asyncio.gather(*interpretation_tasks, return_exceptions=True)
            
            # Filter successful interpretations
            successful_explanations = [
                exp for exp in explanations 
                if isinstance(exp, PredictionExplanation)
            ]
            
            logger.info(f"✅ Batch interpretation complete: {len(successful_explanations)}/{len(predictions)} successful")
            
            return successful_explanations
            
        except Exception as e:
            logger.error(f"❌ Error in batch interpretation: {e}")
            raise
    
    async def get_interpretation_summary(self, 
                                       explanations: List[PredictionExplanation]) -> Dict[str, Any]:
        """
        Get summary of interpretation patterns
        
        📊 ANALYTICS: Interpretation pattern analysis and insights
        """
        try:
            logger.info(f"📊 Generating interpretation summary for {len(explanations)} explanations")
            
            if not explanations:
                return {'error': 'No explanations provided'}
            
            # Calculate summary statistics
            avg_confidence = sum(exp.confidence_score for exp in explanations) / len(explanations)
            avg_prediction = sum(exp.predicted_value for exp in explanations) / len(explanations)
            
            # Certainty level distribution
            certainty_distribution = {}
            for exp in explanations:
                level = exp.certainty_level
                certainty_distribution[level] = certainty_distribution.get(level, 0) + 1
            
            # Most common factors
            factor_frequency = {}
            for exp in explanations:
                for factor in exp.key_factors:
                    feature_name = factor['feature_name']
                    factor_frequency[feature_name] = factor_frequency.get(feature_name, 0) + 1
            
            top_factors = sorted(factor_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Creator type analysis
            creator_distribution = {}
            for exp in explanations:
                creator_type = exp.creator_context.get('creator_type', 'unknown')
                creator_distribution[creator_type] = creator_distribution.get(creator_type, 0) + 1
            
            summary = {
                'total_explanations': len(explanations),
                'average_confidence': avg_confidence,
                'average_prediction': avg_prediction,
                'certainty_distribution': certainty_distribution,
                'top_influential_factors': [{'factor': name, 'frequency': freq} for name, freq in top_factors],
                'creator_type_distribution': creator_distribution,
                'interpretation_methods_used': list(set(exp.explanation_method for exp in explanations)),
                'timestamp': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating interpretation summary: {e}")
            raise
    
    async def export_explanations(self, 
                                 explanations: List[PredictionExplanation],
                                 format: str = 'json') -> str:
        """
        Export explanations in specified format
        
        🔐 SECURITY: Secure and auditable explanation export for compliance
        """
        try:
            logger.info(f"📤 Exporting {len(explanations)} explanations in {format} format")
            
            if format.lower() == 'json':
                export_data = []
                for exp in explanations:
                    export_item = {
                        'prediction_id': exp.prediction_id,
                        'model_id': exp.model_id,
                        'predicted_value': exp.predicted_value,
                        'confidence_score': exp.confidence_score,
                        'explanation_text': exp.explanation_text,
                        'certainty_level': exp.certainty_level,
                        'key_factors': exp.key_factors,
                        'creator_context': exp.creator_context,
                        'timestamp': exp.timestamp.isoformat()
                    }
                    export_data.append(export_item)
                
                return json.dumps(export_data, indent=2)
            
            elif format.lower() == 'csv':
                # Simple CSV export
                csv_lines = ['prediction_id,model_id,predicted_value,confidence_score,certainty_level,explanation_text']
                for exp in explanations:
                    line = f"{exp.prediction_id},{exp.model_id},{exp.predicted_value},{exp.confidence_score},{exp.certainty_level},\"{exp.explanation_text}\""
                    csv_lines.append(line)
                
                return '\n'.join(csv_lines)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting explanations: {e}")
            raise

# Example usage and testing
async def main():
    """Example usage of prediction interpreter service"""
    try:
        # Initialize interpreter service
        interpreter_service = PredictionInterpreterService()
        
        # Simulate prediction data for a musician
        feature_values = {
            'audio_quality': 0.85,
            'genre_popularity': 0.72,
            'engagement_rate': 0.08,
            'collaboration_count': 3,
            'follower_count': 15000,
            'content_quality_score': 0.78,
            'posting_frequency': 0.6
        }
        
        model_metadata = {
            'model_id': 'musician-engagement-predictor-v2',
            'model_purpose': 'engagement prediction',
            'creator_context': {
                'creator_type': 'musician'
            }
        }
        
        # Interpret single prediction
        explanation = await interpreter_service.interpret_individual_prediction(
            prediction_id='pred_musician_123',
            prediction_value=0.76,
            feature_values=feature_values,
            model_metadata=model_metadata
        )
        
        print(f"\n🔍 Prediction Interpretation Results:")
        print(f"   Prediction ID: {explanation.prediction_id}")
        print(f"   Predicted Value: {explanation.predicted_value:.3f}")
        print(f"   Confidence: {explanation.confidence_score:.1%}")
        print(f"   Certainty Level: {explanation.certainty_level}")
        print(f"   Method: {explanation.explanation_method}")
        
        print(f"\n📝 Explanation:")
        print(f"   {explanation.explanation_text}")
        
        print(f"\n🎯 Key Factors:")
        for i, factor in enumerate(explanation.key_factors[:3]):
            direction_icon = "📈" if factor['contribution_direction'] == 'POSITIVE' else "📉"
            print(f"   {i+1}. {direction_icon} {factor['feature_name']}: {factor['human_readable_description']}")
        
        if explanation.counterfactuals:
            print(f"\n🔮 Counterfactual Scenarios:")
            for cf in explanation.counterfactuals:
                print(f"   • {cf['scenario_name']}: {cf['counterfactual_prediction']:.3f} "
                      f"(feasibility: {cf['feasibility_score']:.1%})")
        
        # Simulate batch interpretation
        batch_predictions = [
            {
                'prediction_id': f'pred_batch_{i}',
                'prediction_value': 0.6 + i * 0.1,
                'feature_values': feature_values,
                'model_metadata': model_metadata
            }
            for i in range(3)
        ]
        
        batch_explanations = await interpreter_service.batch_interpret_predictions(batch_predictions)
        
        print(f"\n📊 Batch Interpretation:")
        print(f"   Processed: {len(batch_explanations)} predictions")
        
        # Get interpretation summary
        summary = await interpreter_service.get_interpretation_summary(batch_explanations)
        print(f"   Average Confidence: {summary['average_confidence']:.1%}")
        print(f"   Top Factor: {summary['top_influential_factors'][0]['factor']}")
        
        print("\n✅ Prediction interpretation demonstration complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in prediction interpretation: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())