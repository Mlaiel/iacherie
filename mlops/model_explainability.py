"""
Model Explainability for Compliance and Debugging
Implements comprehensive model explainability features
"""

import warnings
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from abc import ABC, abstractmethod
from enum import Enum

# Optional dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("numpy not available. Some explainability features will be limited.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. Some explainability features will be limited.")

# Import explanation libraries
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    warnings.warn("SHAP not available. Install with: pip install shap")

try:
    import lime
    import lime.lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    warnings.warn("LIME not available. Install with: pip install lime")

try:
    from sklearn.inspection import permutation_importance
    from sklearn.tree import export_text
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Add mock implementations for missing dependencies
if NUMPY_AVAILABLE:
    from numpy.typing import NDArray
else:
    from typing import Any
    NDArray = Any  # Fallback when numpy not available
    # Create mock numpy for basic compatibility
    class MockNumpy:
        ndarray = Any
    np = MockNumpy()

if PANDAS_AVAILABLE:
    DataFrame = pd.DataFrame
else:
    from typing import Any
    DataFrame = Any  # Fallback when pandas not available
    # Create mock pandas for basic compatibility
    class MockPandas:
        DataFrame = Any
    pd = MockPandas()

logger = logging.getLogger(__name__)


class ExplanationType(Enum):
    """Types of explanations"""
    GLOBAL = "global"
    LOCAL = "local"
    FEATURE_IMPORTANCE = "feature_importance"
    COUNTERFACTUAL = "counterfactual"
    PARTIAL_DEPENDENCE = "partial_dependence"


class ExplainerType(Enum):
    """Types of explainers"""
    SHAP = "shap"
    LIME = "lime"
    PERMUTATION = "permutation"
    BUILT_IN = "built_in"


@dataclass
class ExplanationResult:
    """Result of an explanation"""
    explanation_id: str
    explanation_type: ExplanationType
    explainer_type: ExplainerType
    model_name: str
    model_version: str
    feature_names: List[str]
    explanation_data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseExplainer(ABC):
    """Base class for model explainers"""
    
    def __init__(self, model: Any, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
    
    @abstractmethod
    def explain_global(self, X: NDArray) -> Dict[str, Any]:
        try:
            logger.info(f"Executing explain_global")
            
            # Implementation for explain_global
            # TODO: Add specific business logic here
            result = None  # Replace with actual implementation
            
            logger.info(f"explain_global completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"explain_global failed: {e}")
            raise
    @abstractmethod
    def explain_local(self, X: NDArray, instance_idx: int = 0) -> Dict[str, Any]:
        """Generate local explanation for a specific instance"""
        try:
            logger.info(f"Executing explain_local")
            
            # Implementation for explain_local
            # TODO: Add specific business logic here
            result = None  # Replace with actual implementation
            
            logger.info(f"explain_local completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"explain_local failed: {e}")
            raise


class SHAPExplainer(BaseExplainer):
    """SHAP-based explainer"""
    
    def __init__(self, model: Any, feature_names: List[str], model_type: str = "auto"):
        super().__init__(model, feature_names)
        
        if not SHAP_AVAILABLE:
            raise ImportError("SHAP is required for SHAPExplainer")
        
        self.model_type = model_type
        self.explainer = None
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize the appropriate SHAP explainer"""
        try:
            if self.model_type == "tree" or hasattr(self.model, 'feature_importances_'):
                self.explainer = shap.TreeExplainer(self.model)
            else:
                # Use sampling for other models
                self.explainer = shap.Explainer(self.model)
            
            logger.info(f"Initialized SHAP explainer: {type(self.explainer).__name__}")
            
        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {str(e)}")
            raise
    
    def explain_global(self, X: NDArray) -> Dict[str, Any]:
        """Generate global SHAP explanation"""
        try:
            shap_values = self.explainer.shap_values(X)
            
            # Handle different SHAP value formats
            if isinstance(shap_values, list):
                # Multi-class classification
                mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
            else:
                # Binary classification or regression
                mean_abs_shap = np.abs(shap_values).mean(axis=0)
            
            # Create feature importance ranking
            feature_importance = dict(zip(self.feature_names, mean_abs_shap))
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            explanation = {
                "feature_importance": feature_importance,
                "ranked_features": sorted_features,
                "shap_values_summary": {
                    "shape": shap_values.shape if not isinstance(shap_values, list) else [sv.shape for sv in shap_values],
                    "mean_abs_values": mean_abs_shap.tolist(),
                    "top_features": [f[0] for f in sorted_features[:10]]
                }
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error in global SHAP explanation: {str(e)}")
            raise
    
    def explain_local(self, X: NDArray, instance_idx: int = 0) -> Dict[str, Any]:
        """Generate local SHAP explanation"""
        try:
            if instance_idx >= len(X):
                raise ValueError(f"Instance index {instance_idx} out of bounds for data with {len(X)} samples")
            
            # Get SHAP values for the specific instance
            instance_shap = self.explainer.shap_values(X[instance_idx:instance_idx+1])
            
            if isinstance(instance_shap, list):
                # Multi-class: use the class with highest prediction
                prediction = self.model.predict_proba(X[instance_idx:instance_idx+1])[0]
                predicted_class = np.argmax(prediction)
                shap_values = instance_shap[predicted_class][0]
            else:
                shap_values = instance_shap[0]
            
            # Create feature contribution analysis
            feature_contributions = dict(zip(self.feature_names, shap_values))
            
            # Separate positive and negative contributions
            positive_contrib = {k: v for k, v in feature_contributions.items() if v > 0}
            negative_contrib = {k: v for k, v in feature_contributions.items() if v < 0}
            
            # Sort by absolute contribution
            sorted_positive = sorted(positive_contrib.items(), key=lambda x: x[1], reverse=True)
            sorted_negative = sorted(negative_contrib.items(), key=lambda x: x[1])
            
            explanation = {
                "instance_index": instance_idx,
                "feature_values": dict(zip(self.feature_names, X[instance_idx])),
                "shap_values": feature_contributions,
                "positive_contributions": dict(sorted_positive),
                "negative_contributions": dict(sorted_negative),
                "top_positive_features": sorted_positive[:5],
                "top_negative_features": sorted_negative[:5],
                "base_value": float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0,
                "prediction_explanation": {
                    "total_positive_impact": sum(positive_contrib.values()),
                    "total_negative_impact": sum(negative_contrib.values()),
                    "net_impact": sum(shap_values)
                }
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error in local SHAP explanation: {str(e)}")
            raise


class LIMEExplainer(BaseExplainer):
    """LIME-based explainer"""
    
    def __init__(self, model: Any, feature_names: List[str], training_data: NDArray):
        super().__init__(model, feature_names)
        
        if not LIME_AVAILABLE:
            raise ImportError("LIME is required for LIMEExplainer")
        
        self.training_data = training_data
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data,
            feature_names=feature_names,
            mode='classification' if hasattr(model, 'predict_proba') else 'regression'
        )
    
    def explain_global(self, X: NDArray) -> Dict[str, Any]:
        """Generate global explanation by aggregating local explanations"""
        try:
            # Sample instances for global explanation
            sample_size = min(100, len(X))
            sample_indices = np.random.choice(len(X), sample_size, replace=False)
            
            all_explanations = []
            feature_importance_sum = np.zeros(len(self.feature_names))
            
            for idx in sample_indices:
                local_exp = self.explain_local(X, idx)
                all_explanations.append(local_exp)
                
                # Aggregate feature importances
                for feature, importance in local_exp["feature_importance"].items():
                    feature_idx = self.feature_names.index(feature)
                    feature_importance_sum[feature_idx] += abs(importance)
            
            # Calculate average feature importance
            avg_feature_importance = feature_importance_sum / sample_size
            feature_importance = dict(zip(self.feature_names, avg_feature_importance))
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            explanation = {
                "feature_importance": feature_importance,
                "ranked_features": sorted_features,
                "sample_size": sample_size,
                "top_features": [f[0] for f in sorted_features[:10]],
                "explanation_consistency": self._calculate_consistency(all_explanations)
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error in global LIME explanation: {str(e)}")
            raise
    
    def explain_local(self, X: NDArray, instance_idx: int = 0) -> Dict[str, Any]:
        """Generate local LIME explanation"""
        try:
            if instance_idx >= len(X):
                raise ValueError(f"Instance index {instance_idx} out of bounds")
            
            # Explain the instance
            if hasattr(self.model, 'predict_proba'):
                explanation = self.explainer.explain_instance(
                    X[instance_idx],
                    self.model.predict_proba,
                    num_features=len(self.feature_names)
                )
            else:
                explanation = self.explainer.explain_instance(
                    X[instance_idx],
                    self.model.predict,
                    num_features=len(self.feature_names)
                )
            
            # Extract feature importance
            feature_importance = dict(explanation.as_list())
            
            # Get prediction
            if hasattr(self.model, 'predict_proba'):
                prediction_proba = self.model.predict_proba(X[instance_idx:instance_idx+1])[0]
                prediction = np.argmax(prediction_proba)
            else:
                prediction = self.model.predict(X[instance_idx:instance_idx+1])[0]
                prediction_proba = None
            
            local_explanation = {
                "instance_index": instance_idx,
                "feature_values": dict(zip(self.feature_names, X[instance_idx])),
                "feature_importance": feature_importance,
                "prediction": prediction,
                "prediction_proba": prediction_proba.tolist() if prediction_proba is not None else None,
                "explanation_score": explanation.score if hasattr(explanation, 'score') else None
            }
            
            return local_explanation
            
        except Exception as e:
            logger.error(f"Error in local LIME explanation: {str(e)}")
            raise
    
    def _calculate_consistency(self, explanations: List[Dict]) -> Dict[str, float]:
        """Calculate consistency metrics across explanations"""
        if len(explanations) < 2:
            return {"consistency_score": 1.0}
        
        # Calculate feature ranking consistency
        all_rankings = []
        for exp in explanations:
            ranking = sorted(exp["feature_importance"].items(), key=lambda x: abs(x[1]), reverse=True)
            all_rankings.append([f[0] for f in ranking])
        
        # Simple consistency measure: how often top features appear in top positions
        top_features_consistency = {}
        for i in range(min(5, len(self.feature_names))):
            feature_at_position = [ranking[i] for ranking in all_rankings if len(ranking) > i]
            if feature_at_position:
                most_common = max(set(feature_at_position), key=feature_at_position.count)
                consistency = feature_at_position.count(most_common) / len(feature_at_position)
                top_features_consistency[f"position_{i+1}"] = consistency
        
        avg_consistency = np.mean(list(top_features_consistency.values()))
        
        return {
            "consistency_score": avg_consistency,
            "top_features_consistency": top_features_consistency
        }


class PermutationExplainer(BaseExplainer):
    """Permutation importance explainer"""
    
    def __init__(self, model: Any, feature_names: List[str], scoring: str = 'accuracy'):
        super().__init__(model, feature_names)
        self.scoring = scoring
    
    def explain_global(self, X: NDArray, y: NDArray = None) -> Dict[str, Any]:
        """Generate global explanation using permutation importance"""
        try:
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn is required for permutation importance")
            
            if y is None:
                raise ValueError("Target values (y) are required for permutation importance")
            
            # Calculate permutation importance
            perm_importance = permutation_importance(
                self.model, X, y,
                scoring=self.scoring,
                n_repeats=10,
                random_state=42
            )
            
            # Create feature importance dictionary
            feature_importance = dict(zip(self.feature_names, perm_importance.importances_mean))
            feature_std = dict(zip(self.feature_names, perm_importance.importances_std))
            
            # Sort features by importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            explanation = {
                "feature_importance": feature_importance,
                "feature_importance_std": feature_std,
                "ranked_features": sorted_features,
                "top_features": [f[0] for f in sorted_features[:10]],
                "scoring_metric": self.scoring,
                "statistical_significance": self._calculate_significance(perm_importance)
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error in permutation importance: {str(e)}")
            raise
    
    def explain_local(self, X: NDArray, instance_idx: int = 0) -> Dict[str, Any]:
        """Local explanations not directly supported by permutation importance"""
        return {
            "error": "Local explanations not supported by permutation importance",
            "suggestion": "Use SHAP or LIME for local explanations"
        }
    
    def _calculate_significance(self, perm_importance) -> Dict[str, Any]:
        """Calculate statistical significance of feature importances"""
        significance = {}
        
        for i, feature in enumerate(self.feature_names):
            mean_importance = perm_importance.importances_mean[i]
            std_importance = perm_importance.importances_std[i]
            
            # Simple significance test: importance > 2 * std
            is_significant = mean_importance > 2 * std_importance
            
            significance[feature] = {
                "is_significant": is_significant,
                "mean": mean_importance,
                "std": std_importance,
                "significance_ratio": mean_importance / std_importance if std_importance > 0 else float('inf')
            }
        
        return significance


class ModelExplainabilityEngine:
    """Central engine for model explainability"""
    
    def __init__(self, model: Any, feature_names: List[str], model_name: str, model_version: str):
        self.model = model
        self.feature_names = feature_names
        self.model_name = model_name
        self.model_version = model_version
        self.explainers: Dict[ExplainerType, BaseExplainer] = {}
        self.explanations: List[ExplanationResult] = []
    
    def register_explainer(self, explainer_type: ExplainerType, explainer: BaseExplainer):
        """Register an explainer"""
        self.explainers[explainer_type] = explainer
        logger.info(f"Registered {explainer_type.value} explainer")
    
    def setup_default_explainers(self, training_data: Optional[NDArray] = None):
        """Setup default explainers"""
        
        # SHAP explainer
        if SHAP_AVAILABLE:
            try:
                shap_explainer = SHAPExplainer(self.model, self.feature_names)
                self.register_explainer(ExplainerType.SHAP, shap_explainer)
            except Exception as e:
                logger.warning(f"Could not setup SHAP explainer: {str(e)}")
        
        # LIME explainer
        if LIME_AVAILABLE and training_data is not None:
            try:
                lime_explainer = LIMEExplainer(self.model, self.feature_names, training_data)
                self.register_explainer(ExplainerType.LIME, lime_explainer)
            except Exception as e:
                logger.warning(f"Could not setup LIME explainer: {str(e)}")
        
        # Permutation explainer
        if SKLEARN_AVAILABLE:
            try:
                perm_explainer = PermutationExplainer(self.model, self.feature_names)
                self.register_explainer(ExplainerType.PERMUTATION, perm_explainer)
            except Exception as e:
                logger.warning(f"Could not setup permutation explainer: {str(e)}")
    
    def explain_global(
        self,
        X: NDArray,
        y: Optional[NDArray] = None,
        explainer_types: Optional[List[ExplainerType]] = None
    ) -> List[ExplanationResult]:
        """Generate global explanations"""
        
        if explainer_types is None:
            explainer_types = list(self.explainers.keys())
        
        results = []
        
        for explainer_type in explainer_types:
            if explainer_type not in self.explainers:
                logger.warning(f"Explainer {explainer_type.value} not available")
                continue
            
            try:
                explainer = self.explainers[explainer_type]
                
                if explainer_type == ExplainerType.PERMUTATION and y is not None:
                    explanation_data = explainer.explain_global(X, y)
                else:
                    explanation_data = explainer.explain_global(X)
                
                result = ExplanationResult(
                    explanation_id=f"global_{explainer_type.value}_{datetime.now().timestamp()}",
                    explanation_type=ExplanationType.GLOBAL,
                    explainer_type=explainer_type,
                    model_name=self.model_name,
                    model_version=self.model_version,
                    feature_names=self.feature_names,
                    explanation_data=explanation_data,
                    metadata={"sample_size": len(X)}
                )
                
                results.append(result)
                self.explanations.append(result)
                
                logger.info(f"Generated global explanation using {explainer_type.value}")
                
            except Exception as e:
                logger.error(f"Error generating global explanation with {explainer_type.value}: {str(e)}")
        
        return results
    
    def explain_local(
        self,
        X: NDArray,
        instance_idx: int = 0,
        explainer_types: Optional[List[ExplainerType]] = None
    ) -> List[ExplanationResult]:
        """Generate local explanations"""
        
        if explainer_types is None:
            explainer_types = [ExplainerType.SHAP, ExplainerType.LIME]  # Skip permutation for local
        
        results = []
        
        for explainer_type in explainer_types:
            if explainer_type not in self.explainers:
                logger.warning(f"Explainer {explainer_type.value} not available")
                continue
            
            try:
                explainer = self.explainers[explainer_type]
                explanation_data = explainer.explain_local(X, instance_idx)
                
                result = ExplanationResult(
                    explanation_id=f"local_{explainer_type.value}_{instance_idx}_{datetime.now().timestamp()}",
                    explanation_type=ExplanationType.LOCAL,
                    explainer_type=explainer_type,
                    model_name=self.model_name,
                    model_version=self.model_version,
                    feature_names=self.feature_names,
                    explanation_data=explanation_data,
                    metadata={"instance_idx": instance_idx}
                )
                
                results.append(result)
                self.explanations.append(result)
                
                logger.info(f"Generated local explanation for instance {instance_idx} using {explainer_type.value}")
                
            except Exception as e:
                logger.error(f"Error generating local explanation with {explainer_type.value}: {str(e)}")
        
        return results
    
    def explain_batch(
        self,
        X: NDArray,
        instance_indices: List[int],
        explainer_types: Optional[List[ExplainerType]] = None
    ) -> List[ExplanationResult]:
        """Generate explanations for a batch of instances"""
        
        all_results = []
        
        for idx in instance_indices:
            if idx < len(X):
                results = self.explain_local(X, idx, explainer_types)
                all_results.extend(results)
            else:
                logger.warning(f"Instance index {idx} out of bounds")
        
        return all_results
    
    def compare_explanations(
        self,
        explanation_ids: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple explanations"""
        
        explanations = [exp for exp in self.explanations if exp.explanation_id in explanation_ids]
        
        if len(explanations) < 2:
            return {"error": "At least 2 explanations required for comparison"}
        
        comparison = {
            "explanation_ids": explanation_ids,
            "explanation_types": [exp.explanation_type.value for exp in explanations],
            "explainer_types": [exp.explainer_type.value for exp in explanations],
            "feature_ranking_comparison": {},
            "agreement_metrics": {}
        }
        
        # Compare feature rankings
        rankings = {}
        for exp in explanations:
            if "ranked_features" in exp.explanation_data:
                rankings[exp.explainer_type.value] = [f[0] for f in exp.explanation_data["ranked_features"]]
            elif "feature_importance" in exp.explanation_data:
                # Create ranking from feature importance
                sorted_features = sorted(
                    exp.explanation_data["feature_importance"].items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                rankings[exp.explainer_type.value] = [f[0] for f in sorted_features]
        
        comparison["feature_ranking_comparison"] = rankings
        
        # Calculate agreement metrics
        if len(rankings) >= 2:
            ranking_pairs = list(rankings.items())
            agreement_scores = {}
            
            for i in range(len(ranking_pairs)):
                for j in range(i + 1, len(ranking_pairs)):
                    explainer1, ranking1 = ranking_pairs[i]
                    explainer2, ranking2 = ranking_pairs[j]
                    
                    # Calculate top-k agreement
                    for k in [3, 5, 10]:
                        if len(ranking1) >= k and len(ranking2) >= k:
                            top_k1 = set(ranking1[:k])
                            top_k2 = set(ranking2[:k])
                            agreement = len(top_k1 & top_k2) / k
                            
                            pair_key = f"{explainer1}_vs_{explainer2}"
                            if pair_key not in agreement_scores:
                                agreement_scores[pair_key] = {}
                            agreement_scores[pair_key][f"top_{k}_agreement"] = agreement
            
            comparison["agreement_metrics"] = agreement_scores
        
        return comparison
    
    def generate_explanation_report(
        self,
        X: NDArray,
        y: Optional[NDArray] = None,
        instance_indices: Optional[List[int]] = None,
        include_comparisons: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation report"""
        
        report = {
            "model_info": {
                "name": self.model_name,
                "version": self.model_version,
                "feature_count": len(self.feature_names),
                "feature_names": self.feature_names
            },
            "data_info": {
                "sample_size": len(X),
                "feature_dimensions": X.shape[1] if len(X.shape) > 1 else 1
            },
            "explanations": {},
            "summary": {},
            "recommendations": []
        }
        
        # Generate global explanations
        global_explanations = self.explain_global(X, y)
        report["explanations"]["global"] = [exp.__dict__ for exp in global_explanations]
        
        # Generate local explanations for sample instances
        if instance_indices is None:
            instance_indices = [0, min(1, len(X)-1), min(len(X)//2, len(X)-1)]
        
        local_explanations = self.explain_batch(X, instance_indices)
        report["explanations"]["local"] = [exp.__dict__ for exp in local_explanations]
        
        # Generate summary
        if global_explanations:
            # Find most important features across explainers
            all_feature_importance = {}
            for exp in global_explanations:
                if "feature_importance" in exp.explanation_data:
                    for feature, importance in exp.explanation_data["feature_importance"].items():
                        if feature not in all_feature_importance:
                            all_feature_importance[feature] = []
                        all_feature_importance[feature].append(abs(importance))
            
            # Calculate average importance
            avg_importance = {
                feature: np.mean(importances)
                for feature, importances in all_feature_importance.items()
            }
            
            top_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            report["summary"] = {
                "top_features": top_features,
                "explanation_count": len(global_explanations) + len(local_explanations),
                "explainer_types_used": list(set([exp.explainer_type.value for exp in global_explanations]))
            }
        
        # Generate comparisons
        if include_comparisons and len(global_explanations) >= 2:
            global_comparison = self.compare_explanations([exp.explanation_id for exp in global_explanations])
            report["comparisons"] = {"global": global_comparison}
        
        # Generate recommendations
        report["recommendations"] = self._generate_explainability_recommendations(report)
        
        return report
    
    def _generate_explainability_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on explanation results"""
        recommendations = []
        
        # Check explanation consistency
        if "comparisons" in report and "global" in report["comparisons"]:
            agreement_metrics = report["comparisons"]["global"].get("agreement_metrics", {})
            if agreement_metrics:
                avg_agreement = np.mean([
                    list(metrics.values())[0] for metrics in agreement_metrics.values()
                    if isinstance(list(metrics.values())[0], (int, float))
                ])
                
                if avg_agreement < 0.5:
                    recommendations.append(
                        "Low agreement between explainers detected. Consider investigating model stability."
                    )
                elif avg_agreement > 0.8:
                    recommendations.append(
                        "High agreement between explainers indicates consistent explanations."
                    )
        
        # Check top features
        if "summary" in report and "top_features" in report["summary"]:
            top_features = report["summary"]["top_features"]
            if len(top_features) > 0:
                top_importance = top_features[0][1]
                second_importance = top_features[1][1] if len(top_features) > 1 else 0
                
                if top_importance > 2 * second_importance:
                    recommendations.append(
                        f"Feature '{top_features[0][0]}' dominates predictions. Consider feature engineering."
                    )
        
        # Check explainer availability
        explainer_types_used = report["summary"].get("explainer_types_used", [])
        if len(explainer_types_used) == 1:
            recommendations.append(
                "Only one explainer type used. Consider adding more explainers for robust explanations."
            )
        
        if not recommendations:
            recommendations.append("Model explanations appear consistent and comprehensive.")
        
        return recommendations
    
    def export_explanations(self, format: str = "json") -> str:
        """Export explanations in specified format"""
        
        if format == "json":
            export_data = {
                "model_info": {
                    "name": self.model_name,
                    "version": self.model_version,
                    "feature_names": self.feature_names
                },
                "explanations": [exp.__dict__ for exp in self.explanations],
                "export_timestamp": datetime.now().isoformat()
            }
            
            return json.dumps(export_data, indent=2, default=str)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_explanation_by_id(self, explanation_id: str) -> Optional[ExplanationResult]:
        """Get explanation by ID"""
        for exp in self.explanations:
            if exp.explanation_id == explanation_id:
                return exp
        return None