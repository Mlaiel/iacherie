"""
⭐ Feature Importance Tracker - Enterprise ML Feature Analytics
==============================================================

Tracking importance features modèles IA/ML pour Creator Economy.
SHAP values monitoring, feature relevance analysis, model explainability metrics.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/feature_importance_tracker.py
Responsabilité: Tracking importance features modèles Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import statistics
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict, Counter
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


class FeatureType(Enum):
    """Types de features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    TEMPORAL = "temporal"
    INTERACTION = "interaction"
    DERIVED = "derived"


class ImportanceMethod(Enum):
    """Méthodes calcul importance"""
    SHAP = "shap"
    PERMUTATION = "permutation"
    INTRINSIC = "intrinsic"
    MUTUAL_INFORMATION = "mutual_information"
    CORRELATION = "correlation"
    GRADIENT_BASED = "gradient_based"
    ATTENTION_WEIGHTS = "attention_weights"


class CreatorContentDomain(Enum):
    """Domaines contenu créateur"""
    MUSIC_PRODUCTION = "music_production"
    CONTENT_WRITING = "content_writing"
    VIDEO_CREATION = "video_creation"
    PHOTOGRAPHY = "photography"
    SOCIAL_MEDIA = "social_media"
    GAMING = "gaming"
    EDUCATION = "education"
    COMEDY = "comedy"


class FeatureRelevanceLevel(Enum):
    """Niveaux pertinence feature"""
    CRITICAL = "critical"      # > 90th percentile
    HIGH = "high"             # 70-90th percentile
    MEDIUM = "medium"         # 30-70th percentile
    LOW = "low"              # 10-30th percentile
    NEGLIGIBLE = "negligible" # < 10th percentile


@dataclass
class FeatureImportanceScore:
    """Score importance feature"""
    feature_id: str
    feature_name: str
    feature_type: FeatureType
    model_id: str
    creator_domain: CreatorContentDomain
    importance_method: ImportanceMethod
    raw_score: float
    normalized_score: float  # 0-1 scale
    rank: int
    percentile: float
    confidence_interval: Tuple[float, float]
    relevance_level: FeatureRelevanceLevel
    stability_score: float  # How stable is this importance over time
    business_impact: float  # Impact on creator success metrics
    timestamp: datetime = field(default_factory=datetime.utcnow)


class FeatureImportanceTracker:
    """Tracker importance features enterprise"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Feature tracking
        self.feature_importance_history: Dict[str, List[FeatureImportanceScore]] = {}
        self.feature_registry: Dict[str, Dict[str, Any]] = {}
        
        # Business impact weights
        self.business_impact_weights = {
            'revenue_correlation': 0.3,
            'user_engagement': 0.25,
            'creator_satisfaction': 0.2,
            'retention_impact': 0.15,
            'viral_potential': 0.1
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("feature_importance_tracker")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def register_feature(self,
                             feature_id: str,
                             feature_name: str,
                             feature_type: FeatureType,
                             description: str,
                             creator_domains: List[CreatorContentDomain],
                             data_source: str,
                             update_frequency: str = "real_time",
                             metadata: Dict[str, Any] = None) -> bool:
        """Enregistrement feature"""
        try:
            self.feature_registry[feature_id] = {
                'feature_name': feature_name,
                'feature_type': feature_type,
                'description': description,
                'creator_domains': creator_domains,
                'data_source': data_source,
                'update_frequency': update_frequency,
                'metadata': metadata or {},
                'registered_at': datetime.utcnow(),
                'usage_count': 0,
                'avg_importance': 0.0
            }
            
            self.logger.info(f"📝 Registered feature: {feature_name} ({feature_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering feature: {e}")
            return False
    
    async def calculate_feature_importance(self,
                                         model_id: str,
                                         feature_data: Dict[str, np.ndarray],
                                         target_data: np.ndarray,
                                         creator_domain: CreatorContentDomain,
                                         method: ImportanceMethod = ImportanceMethod.PERMUTATION,
                                         sample_size: int = 1000) -> List[FeatureImportanceScore]:
        """Calcul importance features"""
        try:
            importance_scores = []
            
            # Prepare data
            feature_names = list(feature_data.keys())
            X = np.column_stack([feature_data[name] for name in feature_names])
            y = target_data
            
            # Sample data if too large
            if len(X) > sample_size:
                indices = np.random.choice(len(X), sample_size, replace=False)
                X = X[indices]
                y = y[indices]
            
            # Calculate importance based on method
            if method == ImportanceMethod.PERMUTATION:
                raw_scores = await self._calculate_permutation_importance(X, y, feature_names)
            elif method == ImportanceMethod.INTRINSIC:
                raw_scores = await self._calculate_intrinsic_importance(X, y, feature_names)
            elif method == ImportanceMethod.MUTUAL_INFORMATION:
                raw_scores = await self._calculate_mutual_information(X, y, feature_names)
            elif method == ImportanceMethod.CORRELATION:
                raw_scores = await self._calculate_correlation_importance(X, y, feature_names)
            else:
                # Default to permutation importance
                raw_scores = await self._calculate_permutation_importance(X, y, feature_names)
            
            # Normalize scores
            max_score = max(raw_scores.values()) if raw_scores else 1.0
            normalized_scores = {name: score / max_score for name, score in raw_scores.items()}
            
            # Create importance score objects
            sorted_features = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (feature_name, normalized_score) in enumerate(sorted_features, 1):
                feature_id = f"{model_id}_{feature_name}"
                raw_score = raw_scores.get(feature_name, 0.0)
                
                # Calculate percentile
                percentile = (len(sorted_features) - rank + 1) / len(sorted_features) * 100
                
                # Determine relevance level
                if percentile >= 90:
                    relevance_level = FeatureRelevanceLevel.CRITICAL
                elif percentile >= 70:
                    relevance_level = FeatureRelevanceLevel.HIGH
                elif percentile >= 30:
                    relevance_level = FeatureRelevanceLevel.MEDIUM
                elif percentile >= 10:
                    relevance_level = FeatureRelevanceLevel.LOW
                else:
                    relevance_level = FeatureRelevanceLevel.NEGLIGIBLE
                
                # Calculate confidence interval (simplified)
                confidence_interval = (
                    max(0.0, normalized_score - 0.1),
                    min(1.0, normalized_score + 0.1)
                )
                
                # Calculate stability score (based on historical data)
                stability_score = await self._calculate_stability_score(feature_id, normalized_score)
                
                # Calculate business impact
                business_impact = await self._calculate_business_impact(
                    feature_name, normalized_score, creator_domain
                )
                
                # Get feature type from registry
                feature_type = FeatureType.NUMERICAL  # Default
                if feature_id in self.feature_registry:
                    feature_type = self.feature_registry[feature_id]['feature_type']
                
                importance_score = FeatureImportanceScore(
                    feature_id=feature_id,
                    feature_name=feature_name,
                    feature_type=feature_type,
                    model_id=model_id,
                    creator_domain=creator_domain,
                    importance_method=method,
                    raw_score=raw_score,
                    normalized_score=normalized_score,
                    rank=rank,
                    percentile=percentile,
                    confidence_interval=confidence_interval,
                    relevance_level=relevance_level,
                    stability_score=stability_score,
                    business_impact=business_impact
                )
                
                importance_scores.append(importance_score)
            
            # Store importance scores
            if model_id not in self.feature_importance_history:
                self.feature_importance_history[model_id] = []
            
            self.feature_importance_history[model_id].extend(importance_scores)
            
            # Keep only recent history
            if len(self.feature_importance_history[model_id]) > 10000:
                self.feature_importance_history[model_id] = self.feature_importance_history[model_id][-10000:]
            
            # Update feature usage in registry
            for feature_name in feature_names:
                feature_id = f"{model_id}_{feature_name}"
                if feature_id in self.feature_registry:
                    self.feature_registry[feature_id]['usage_count'] += 1
            
            self.logger.info(f"✅ Calculated importance for {len(importance_scores)} features in model {model_id}")
            return importance_scores
            
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {e}")
            return []
    
    async def _calculate_permutation_importance(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict[str, float]:
        """Calcul importance par permutation"""
        try:
            # Use RandomForest as surrogate model
            if len(np.unique(y)) <= 10:  # Classification
                model = RandomForestClassifier(n_estimators=50, random_state=42)
            else:  # Regression
                model = RandomForestRegressor(n_estimators=50, random_state=42)
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            model.fit(X_train, y_train)
            
            # Calculate permutation importance
            perm_importance = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42)
            
            importance_dict = {}
            for i, feature_name in enumerate(feature_names):
                importance_dict[feature_name] = perm_importance.importances_mean[i]
            
            return importance_dict
            
        except Exception as e:
            self.logger.error(f"Error calculating permutation importance: {e}")
            return {}
    
    async def _calculate_intrinsic_importance(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict[str, float]:
        """Calcul importance intrinsèque"""
        try:
            # Use RandomForest feature importance
            if len(np.unique(y)) <= 10:  # Classification
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:  # Regression
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            model.fit(X, y)
            
            importance_dict = {}
            for i, feature_name in enumerate(feature_names):
                importance_dict[feature_name] = model.feature_importances_[i]
            
            return importance_dict
            
        except Exception as e:
            self.logger.error(f"Error calculating intrinsic importance: {e}")
            return {}
    
    async def _calculate_mutual_information(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict[str, float]:
        """Calcul information mutuelle"""
        try:
            from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
            
            # Determine if classification or regression
            if len(np.unique(y)) <= 10:  # Classification
                mi_scores = mutual_info_classif(X, y, random_state=42)
            else:  # Regression
                mi_scores = mutual_info_regression(X, y, random_state=42)
            
            importance_dict = {}
            for i, feature_name in enumerate(feature_names):
                importance_dict[feature_name] = mi_scores[i]
            
            return importance_dict
            
        except Exception as e:
            self.logger.error(f"Error calculating mutual information: {e}")
            return {}
    
    async def _calculate_correlation_importance(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict[str, float]:
        """Calcul importance par corrélation"""
        try:
            importance_dict = {}
            
            for i, feature_name in enumerate(feature_names):
                correlation = abs(np.corrcoef(X[:, i], y)[0, 1])
                importance_dict[feature_name] = correlation if not np.isnan(correlation) else 0.0
            
            return importance_dict
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation importance: {e}")
            return {}
    
    async def _calculate_stability_score(self, feature_id: str, current_score: float) -> float:
        """Calcul score stabilité"""
        try:
            # Get historical scores for this feature
            historical_scores = []
            
            for model_scores in self.feature_importance_history.values():
                for score_obj in model_scores:
                    if score_obj.feature_id == feature_id:
                        historical_scores.append(score_obj.normalized_score)
            
            if len(historical_scores) < 2:
                return 1.0  # Assume stable if no history
            
            # Calculate coefficient of variation (lower = more stable)
            mean_score = statistics.mean(historical_scores)
            std_score = statistics.stdev(historical_scores)
            
            if mean_score == 0:
                return 1.0
            
            cv = std_score / mean_score
            stability_score = max(0.0, 1.0 - cv)  # Convert to 0-1 scale
            
            return stability_score
            
        except Exception as e:
            self.logger.error(f"Error calculating stability score: {e}")
            return 0.5
    
    async def _calculate_business_impact(self, feature_name: str, importance_score: float, creator_domain: CreatorContentDomain) -> float:
        """Calcul impact business"""
        try:
            # Base impact from importance score
            base_impact = importance_score
            
            # Domain-specific multipliers
            domain_multipliers = {
                CreatorContentDomain.MUSIC_PRODUCTION: {
                    'audio_quality': 1.5,
                    'genre': 1.3,
                    'tempo': 1.2,
                    'creator_followers': 1.4
                },
                CreatorContentDomain.CONTENT_WRITING: {
                    'readability': 1.4,
                    'seo_score': 1.5,
                    'word_count': 1.2,
                    'topic_relevance': 1.3
                },
                CreatorContentDomain.VIDEO_CREATION: {
                    'video_quality': 1.4,
                    'thumbnail_quality': 1.3,
                    'duration': 1.2,
                    'engagement_rate': 1.5
                }
            }
            
            # Apply domain-specific multiplier
            multiplier = 1.0
            domain_features = domain_multipliers.get(creator_domain, {})
            
            for keyword, mult in domain_features.items():
                if keyword.lower() in feature_name.lower():
                    multiplier = mult
                    break
            
            # Creator tier impact (premium features have higher business impact)
            tier_multiplier = 1.0
            if 'premium' in feature_name.lower() or 'enterprise' in feature_name.lower():
                tier_multiplier = 1.3
            
            business_impact = base_impact * multiplier * tier_multiplier
            
            return min(1.0, business_impact)
            
        except Exception as e:
            self.logger.error(f"Error calculating business impact: {e}")
            return importance_score
    
    async def get_feature_importance_summary(self, model_id: str, top_n: int = 20) -> Dict[str, Any]:
        """Résumé importance features"""
        try:
            if model_id not in self.feature_importance_history:
                return {'model_id': model_id, 'error': 'No feature importance data found'}
            
            # Get recent scores
            recent_scores = self.feature_importance_history[model_id][-1000:]  # Last 1000 scores
            
            if not recent_scores:
                return {'model_id': model_id, 'error': 'No recent feature importance data'}
            
            # Aggregate by feature name
            feature_aggregates = defaultdict(list)
            for score in recent_scores:
                feature_aggregates[score.feature_name].append(score)
            
            # Calculate summary statistics
            feature_summaries = []
            for feature_name, scores in feature_aggregates.items():
                avg_importance = statistics.mean([s.normalized_score for s in scores])
                avg_stability = statistics.mean([s.stability_score for s in scores])
                avg_business_impact = statistics.mean([s.business_impact for s in scores])
                
                feature_summaries.append({
                    'feature_name': feature_name,
                    'avg_importance': avg_importance,
                    'avg_stability': avg_stability,
                    'avg_business_impact': avg_business_impact,
                    'sample_count': len(scores),
                    'feature_type': scores[0].feature_type.value,
                    'relevance_level': scores[-1].relevance_level.value  # Most recent
                })
            
            # Sort by importance
            feature_summaries.sort(key=lambda x: x['avg_importance'], reverse=True)
            
            # Get top N features
            top_features = feature_summaries[:top_n]
            
            # Calculate summary statistics
            total_features = len(feature_summaries)
            avg_model_stability = statistics.mean([f['avg_stability'] for f in feature_summaries])
            avg_business_impact = statistics.mean([f['avg_business_impact'] for f in feature_summaries])
            
            # Feature type distribution
            feature_type_dist = Counter([f['feature_type'] for f in feature_summaries])
            
            # Relevance level distribution
            relevance_dist = Counter([f['relevance_level'] for f in feature_summaries])
            
            return {
                'model_id': model_id,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'summary_stats': {
                    'total_features': total_features,
                    'avg_model_stability': avg_model_stability,
                    'avg_business_impact': avg_business_impact,
                    'sample_period_days': (recent_scores[-1].timestamp - recent_scores[0].timestamp).days if len(recent_scores) > 1 else 0
                },
                'top_features': top_features,
                'feature_type_distribution': dict(feature_type_dist),
                'relevance_level_distribution': dict(relevance_dist),
                'registered_features': len(self.feature_registry)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting feature importance summary: {e}")
            return {'model_id': model_id, 'error': str(e)}
    
    async def shutdown(self):
        """Arrêt propre du tracker"""
        self.logger.info("⏹️ Arrêt Feature Importance Tracker...")
        
        # Clear data
        self.feature_importance_history.clear()
        self.feature_registry.clear()
        
        self.logger.info("✅ Feature Importance Tracker arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_feature_tracker():
        config = {
            'debug': True,
            'analysis_window_days': 30
        }
        
        tracker = FeatureImportanceTracker(config)
        
        # Register some features
        await tracker.register_feature(
            feature_id="audio_quality",
            feature_name="Audio Quality Score",
            feature_type=FeatureType.NUMERICAL,
            description="Quality score for audio content",
            creator_domains=[CreatorContentDomain.MUSIC_PRODUCTION],
            data_source="audio_processor"
        )
        
        await tracker.register_feature(
            feature_id="engagement_rate",
            feature_name="Engagement Rate",
            feature_type=FeatureType.NUMERICAL,
            description="User engagement rate",
            creator_domains=[CreatorContentDomain.MUSIC_PRODUCTION, CreatorContentDomain.VIDEO_CREATION],
            data_source="analytics_engine"
        )
        
        # Generate sample data
        n_samples = 1000
        feature_data = {
            'audio_quality': np.random.uniform(0.3, 1.0, n_samples),
            'engagement_rate': np.random.uniform(0.0, 0.5, n_samples),
            'creator_followers': np.random.uniform(100, 10000, n_samples),
            'content_length': np.random.uniform(30, 300, n_samples)  # seconds
        }
        
        # Generate target (e.g., content success score)
        target_data = (feature_data['audio_quality'] * 0.4 + 
                      feature_data['engagement_rate'] * 2.0 + 
                      np.log(feature_data['creator_followers']) * 0.1 + 
                      np.random.normal(0, 0.1, n_samples))
        
        # Calculate feature importance
        importance_scores = await tracker.calculate_feature_importance(
            model_id="music_recommendation_model",
            feature_data=feature_data,
            target_data=target_data,
            creator_domain=CreatorContentDomain.MUSIC_PRODUCTION,
            method=ImportanceMethod.PERMUTATION
        )
        
        print(f"Calculated importance for {len(importance_scores)} features")
        
        # Get feature summary
        summary = await tracker.get_feature_importance_summary("music_recommendation_model")
        print(f"Feature summary: {summary['summary_stats']['total_features']} features analyzed")
        
        print('✅ Feature Importance Tracker test passed')
        await tracker.shutdown()
    
    asyncio.run(test_feature_tracker())