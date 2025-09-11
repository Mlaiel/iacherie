"""
🔍 **Model Explainer - AI Interpretability & Transparency**

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0

**⚠️ WARNUNG:** Dieser Code ist urheberrechtlich geschützt und vertraulich.

Enterprise model explainability system with SHAP, LIME, and custom attribution methods
for transparent and trustworthy AI decisions in creator content analysis.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from abc import ABC, abstractmethod
import base64
from io import BytesIO

# ML Interpretability libraries
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available. Install with: pip install shap")

try:
    import lime
    from lime import lime_tabular, lime_text, lime_image
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logging.warning("LIME not available. Install with: pip install lime")

# Ainflue ML Core Imports
from ..model_registry.mlflow_registry import MLflowRegistry
from ..monitoring.performance_monitor import PerformanceMonitor
from ..monitoring.audit_trail_generator import AuditTrailGenerator

class ExplanationMethod(ABC):
    """Abstract base class for explanation methods."""
    
    @abstractmethod
    async def explain(self, model: nn.Module, input_data: Any, **kwargs) -> Dict[str, Any]:
        """Generate explanation for model prediction."""
        pass
    
    @abstractmethod
    def get_feature_importance(self, explanation: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance from explanation."""
        pass

@dataclass
class ExplanationConfig:
    """Configuration for model explanations."""
    method: str  # 'shap', 'lime', 'gradient', 'integrated_gradients'
    model_type: str  # 'tabular', 'text', 'image', 'audio'
    num_samples: int = 1000
    background_samples: int = 100
    confidence_threshold: float = 0.8
    visualization_enabled: bool = True
    save_explanations: bool = True
    explanation_depth: str = "full"  # 'summary', 'detailed', 'full'

@dataclass
class ExplanationResult:
    """Result of model explanation."""
    explanation_id: str
    method_used: str
    model_id: str
    input_data_hash: str
    prediction: Dict[str, Any]
    feature_importances: Dict[str, float]
    explanation_data: Dict[str, Any]
    confidence_score: float
    processing_time_seconds: float
    visualizations: Dict[str, str]  # base64 encoded images
    created_at: datetime
    metadata: Dict[str, Any]

class SHAPExplainer(ExplanationMethod):
    """SHAP (SHapley Additive exPlanations) explainer."""
    
    def __init__(self, config: ExplanationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.explainer = None
    
    def _initialize_explainer(self, model: nn.Module, background_data: np.ndarray):
        """Initialize SHAP explainer based on model type."""
        if not SHAP_AVAILABLE:
            raise ImportError("SHAP not available")
        
        model.eval()
        
        if self.config.model_type == 'tabular':
            # For tabular data
            def model_predict(x):
                with torch.no_grad():
                    tensor_x = torch.FloatTensor(x)
                    outputs = model(tensor_x)
                    if hasattr(outputs, 'softmax'):
                        return outputs.softmax(dim=-1).numpy()
                    else:
                        return torch.softmax(outputs, dim=-1).numpy()
            
            self.explainer = shap.KernelExplainer(model_predict, background_data)
            
        elif self.config.model_type == 'image':
            # For image data
            def model_predict(x):
                with torch.no_grad():
                    if isinstance(x, np.ndarray):
                        x = torch.FloatTensor(x)
                    outputs = model(x)
                    return torch.softmax(outputs, dim=-1).cpu().numpy()
            
            # Use background images for baseline
            background_tensor = torch.FloatTensor(background_data)
            self.explainer = shap.DeepExplainer(model, background_tensor)
            
        elif self.config.model_type == 'text':
            # For text data (using transformers)
            tokenizer = getattr(model, 'tokenizer', None)
            if tokenizer:
                self.explainer = shap.Explainer(model, tokenizer)
            else:
                # Fallback to kernel explainer
                def model_predict(x):
                    with torch.no_grad():
                        # Assume x is already tokenized
                        tensor_x = torch.LongTensor(x)
                        outputs = model(tensor_x)
                        return torch.softmax(outputs, dim=-1).numpy()
                
                self.explainer = shap.KernelExplainer(model_predict, background_data)
        
        else:
            raise ValueError(f"Unsupported model type for SHAP: {self.config.model_type}")
    
    async def explain(self, model: nn.Module, input_data: Any, background_data: np.ndarray = None, **kwargs) -> Dict[str, Any]:
        """Generate SHAP explanation."""
        try:
            if self.explainer is None:
                if background_data is None:
                    raise ValueError("Background data required for SHAP initialization")
                self._initialize_explainer(model, background_data)
            
            # Convert input data to appropriate format
            if isinstance(input_data, torch.Tensor):
                input_array = input_data.cpu().numpy()
            elif isinstance(input_data, np.ndarray):
                input_array = input_data
            else:
                input_array = np.array(input_data)
            
            # Ensure proper shape for single sample
            if len(input_array.shape) == 1:
                input_array = input_array.reshape(1, -1)
            
            # Generate SHAP values
            if self.config.model_type == 'image':
                shap_values = self.explainer.shap_values(torch.FloatTensor(input_array))
            else:
                shap_values = self.explainer.shap_values(input_array)
            
            # Handle multi-class output
            if isinstance(shap_values, list):
                # Multi-class: take the predicted class
                with torch.no_grad():
                    model_output = model(torch.FloatTensor(input_array))
                    predicted_class = torch.argmax(model_output, dim=-1).item()
                main_shap_values = shap_values[predicted_class]
            else:
                main_shap_values = shap_values
            
            # Process results
            if len(main_shap_values.shape) > 1:
                main_shap_values = main_shap_values[0]  # First sample
            
            explanation_data = {
                'shap_values': main_shap_values.tolist(),
                'expected_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0,
                'feature_names': kwargs.get('feature_names', [f"feature_{i}" for i in range(len(main_shap_values))]),
                'base_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0
            }
            
            return explanation_data
            
        except Exception as e:
            self.logger.error(f"Error in SHAP explanation: {e}")
            raise
    
    def get_feature_importance(self, explanation: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance from SHAP explanation."""
        shap_values = np.array(explanation['shap_values'])
        feature_names = explanation.get('feature_names', [f"feature_{i}" for i in range(len(shap_values))])
        
        # Use absolute SHAP values for importance
        importance_scores = np.abs(shap_values)
        
        return dict(zip(feature_names, importance_scores.tolist()))

class LIMEExplainer(ExplanationMethod):
    """LIME (Local Interpretable Model-agnostic Explanations) explainer."""
    
    def __init__(self, config: ExplanationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.explainer = None
    
    def _initialize_explainer(self, training_data: np.ndarray, feature_names: List[str] = None):
        """Initialize LIME explainer."""
        if not LIME_AVAILABLE:
            raise ImportError("LIME not available")
        
        if self.config.model_type == 'tabular':
            self.explainer = lime_tabular.LimeTabularExplainer(
                training_data,
                feature_names=feature_names or [f"feature_{i}" for i in range(training_data.shape[1])],
                class_names=['Class_0', 'Class_1'],  # Adjust based on your classes
                mode='classification',
                discretize_continuous=True
            )
        elif self.config.model_type == 'text':
            self.explainer = lime_text.LimeTextExplainer(
                class_names=['Negative', 'Positive'],  # Adjust based on your classes
                mode='classification'
            )
        elif self.config.model_type == 'image':
            self.explainer = lime_image.LimeImageExplainer()
        else:
            raise ValueError(f"Unsupported model type for LIME: {self.config.model_type}")
    
    async def explain(self, model: nn.Module, input_data: Any, training_data: np.ndarray = None, **kwargs) -> Dict[str, Any]:
        """Generate LIME explanation."""
        try:
            if self.explainer is None:
                if training_data is None:
                    raise ValueError("Training data required for LIME initialization")
                self._initialize_explainer(training_data, kwargs.get('feature_names'))
            
            # Define prediction function
            def predict_fn(x):
                model.eval()
                with torch.no_grad():
                    if isinstance(x, np.ndarray):
                        tensor_x = torch.FloatTensor(x)
                    else:
                        tensor_x = x
                    
                    outputs = model(tensor_x)
                    probabilities = torch.softmax(outputs, dim=-1)
                    return probabilities.cpu().numpy()
            
            # Generate explanation based on data type
            if self.config.model_type == 'tabular':
                if isinstance(input_data, torch.Tensor):
                    input_array = input_data.cpu().numpy()
                else:
                    input_array = np.array(input_data)
                
                if len(input_array.shape) > 1:
                    input_array = input_array[0]  # Take first sample
                
                explanation = self.explainer.explain_instance(
                    input_array,
                    predict_fn,
                    num_features=min(len(input_array), 10),
                    num_samples=self.config.num_samples
                )
                
                # Extract explanation data
                explanation_data = {
                    'lime_explanation': explanation.as_list(),
                    'intercept': explanation.intercept[1] if len(explanation.intercept) > 1 else explanation.intercept[0],
                    'prediction_local': explanation.local_pred,
                    'score': explanation.score
                }
                
            elif self.config.model_type == 'text':
                # For text data
                text_input = input_data if isinstance(input_data, str) else str(input_data)
                
                def text_predict_fn(texts):
                    # This would need to be adapted based on your text model
                    return np.array([[0.3, 0.7] for _ in texts])  # Mock prediction
                
                explanation = self.explainer.explain_instance(
                    text_input,
                    text_predict_fn,
                    num_features=10
                )
                
                explanation_data = {
                    'lime_explanation': explanation.as_list(),
                    'available_labels': explanation.available_labels,
                    'class_names': explanation.class_names
                }
                
            else:
                # For image data (simplified)
                explanation_data = {
                    'lime_explanation': [],
                    'message': 'Image LIME explanation not fully implemented'
                }
            
            return explanation_data
            
        except Exception as e:
            self.logger.error(f"Error in LIME explanation: {e}")
            raise
    
    def get_feature_importance(self, explanation: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance from LIME explanation."""
        lime_explanation = explanation.get('lime_explanation', [])
        
        importance_dict = {}
        for feature_name, importance_value in lime_explanation:
            importance_dict[str(feature_name)] = abs(float(importance_value))
        
        return importance_dict

class GradientExplainer(ExplanationMethod):
    """Gradient-based explanation method."""
    
    def __init__(self, config: ExplanationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def explain(self, model: nn.Module, input_data: torch.Tensor, target_class: int = None, **kwargs) -> Dict[str, Any]:
        """Generate gradient-based explanation."""
        try:
            model.eval()
            
            # Ensure input requires gradient
            if isinstance(input_data, torch.Tensor):
                input_tensor = input_data.clone().detach().requires_grad_(True)
            else:
                input_tensor = torch.FloatTensor(input_data).requires_grad_(True)
            
            # Forward pass
            outputs = model(input_tensor)
            
            # Determine target class
            if target_class is None:
                target_class = torch.argmax(outputs, dim=-1).item()
            
            # Backward pass
            target_output = outputs[0, target_class] if outputs.dim() > 1 else outputs[target_class]
            target_output.backward()
            
            # Get gradients
            gradients = input_tensor.grad.cpu().numpy()
            
            # Process gradients
            if len(gradients.shape) > 1:
                gradients = gradients.flatten()
            
            explanation_data = {
                'gradients': gradients.tolist(),
                'target_class': target_class,
                'prediction_confidence': float(torch.softmax(outputs, dim=-1)[0, target_class])
            }
            
            return explanation_data
            
        except Exception as e:
            self.logger.error(f"Error in gradient explanation: {e}")
            raise
    
    def get_feature_importance(self, explanation: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance from gradient explanation."""
        gradients = np.array(explanation['gradients'])
        feature_names = [f"feature_{i}" for i in range(len(gradients))]
        
        # Use absolute gradients for importance
        importance_scores = np.abs(gradients)
        
        return dict(zip(feature_names, importance_scores.tolist()))

class IntegratedGradientsExplainer(ExplanationMethod):
    """Integrated Gradients explanation method."""
    
    def __init__(self, config: ExplanationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def _compute_gradients(self, model: nn.Module, inputs: torch.Tensor, target_class: int):
        """Compute gradients for given inputs."""
        inputs.requires_grad_(True)
        outputs = model(inputs)
        
        target_output = outputs[0, target_class] if outputs.dim() > 1 else outputs[target_class]
        gradients = torch.autograd.grad(target_output, inputs, create_graph=True)[0]
        
        return gradients
    
    async def explain(self, model: nn.Module, input_data: torch.Tensor, baseline: torch.Tensor = None, 
                     target_class: int = None, steps: int = 50, **kwargs) -> Dict[str, Any]:
        """Generate Integrated Gradients explanation."""
        try:
            model.eval()
            
            # Convert input to tensor
            if isinstance(input_data, torch.Tensor):
                input_tensor = input_data.clone().detach()
            else:
                input_tensor = torch.FloatTensor(input_data)
            
            # Create baseline (zeros if not provided)
            if baseline is None:
                baseline = torch.zeros_like(input_tensor)
            
            # Determine target class
            if target_class is None:
                with torch.no_grad():
                    outputs = model(input_tensor)
                    target_class = torch.argmax(outputs, dim=-1).item()
            
            # Generate path from baseline to input
            alphas = torch.linspace(0, 1, steps)
            integrated_gradients = torch.zeros_like(input_tensor)
            
            for alpha in alphas:
                # Interpolate between baseline and input
                interpolated_input = baseline + alpha * (input_tensor - baseline)
                
                # Compute gradients
                gradients = self._compute_gradients(model, interpolated_input, target_class)
                integrated_gradients += gradients
            
            # Average the gradients and multiply by input difference
            integrated_gradients = integrated_gradients / steps
            integrated_gradients = integrated_gradients * (input_tensor - baseline)
            
            # Convert to numpy
            integrated_gradients_np = integrated_gradients.detach().cpu().numpy()
            
            if len(integrated_gradients_np.shape) > 1:
                integrated_gradients_np = integrated_gradients_np.flatten()
            
            explanation_data = {
                'integrated_gradients': integrated_gradients_np.tolist(),
                'target_class': target_class,
                'steps_used': steps,
                'baseline_used': baseline.cpu().numpy().tolist()
            }
            
            return explanation_data
            
        except Exception as e:
            self.logger.error(f"Error in Integrated Gradients explanation: {e}")
            raise
    
    def get_feature_importance(self, explanation: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance from Integrated Gradients explanation."""
        ig_values = np.array(explanation['integrated_gradients'])
        feature_names = [f"feature_{i}" for i in range(len(ig_values))]
        
        # Use absolute integrated gradients for importance
        importance_scores = np.abs(ig_values)
        
        return dict(zip(feature_names, importance_scores.tolist()))

class ModelExplainer:
    """
    🔍 **Enterprise Model Explainer**
    
    Advanced model explainability system with multiple interpretation methods
    for transparent and trustworthy AI decisions.
    """
    
    def __init__(self, config: ExplanationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.model_registry = MLflowRegistry()
        self.performance_monitor = PerformanceMonitor()
        self.audit_trail = AuditTrailGenerator()
        
        # Explanation methods
        self.explainers = {}
        self._initialize_explainers()
        
        # Results storage
        self.explanation_results = {}
        
        self.logger.info(f"ModelExplainer initialized with method: {config.method}")
    
    def _initialize_explainers(self):
        """Initialize available explanation methods."""
        try:
            if SHAP_AVAILABLE:
                self.explainers['shap'] = SHAPExplainer(self.config)
            
            if LIME_AVAILABLE:
                self.explainers['lime'] = LIMEExplainer(self.config)
            
            self.explainers['gradient'] = GradientExplainer(self.config)
            self.explainers['integrated_gradients'] = IntegratedGradientsExplainer(self.config)
            
        except Exception as e:
            self.logger.error(f"Error initializing explainers: {e}")
    
    async def explain_prediction(
        self,
        model: nn.Module,
        input_data: Any,
        model_id: str = "unknown",
        method: str = None,
        **kwargs
    ) -> ExplanationResult:
        """
        🎯 **Generate Model Explanation**
        
        Create comprehensive explanation for model prediction.
        """
        try:
            start_time = datetime.now()
            
            # Select explanation method
            explanation_method = method or self.config.method
            
            if explanation_method not in self.explainers:
                raise ValueError(f"Explanation method '{explanation_method}' not available")
            
            explainer = self.explainers[explanation_method]
            
            # Generate model prediction
            model.eval()
            with torch.no_grad():
                if isinstance(input_data, torch.Tensor):
                    model_output = model(input_data)
                else:
                    tensor_input = torch.FloatTensor(input_data)
                    model_output = model(tensor_input)
                
                prediction_probs = torch.softmax(model_output, dim=-1)
                predicted_class = torch.argmax(prediction_probs, dim=-1).item()
                confidence = prediction_probs[0, predicted_class].item()
            
            # Generate explanation
            explanation_data = await explainer.explain(model, input_data, **kwargs)
            
            # Extract feature importance
            feature_importances = explainer.get_feature_importance(explanation_data)
            
            # Create visualizations if enabled
            visualizations = {}
            if self.config.visualization_enabled:
                visualizations = await self._create_visualizations(
                    explanation_data, feature_importances, explanation_method
                )
            
            # Calculate input data hash for caching
            if isinstance(input_data, torch.Tensor):
                input_hash = hash(input_data.cpu().numpy().tobytes())
            else:
                input_hash = hash(str(input_data))
            
            # Create result
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            explanation_id = f"explanation_{model_id}_{datetime.now().timestamp()}"
            
            result = ExplanationResult(
                explanation_id=explanation_id,
                method_used=explanation_method,
                model_id=model_id,
                input_data_hash=str(input_hash),
                prediction={
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'probabilities': prediction_probs.cpu().numpy().tolist()
                },
                feature_importances=feature_importances,
                explanation_data=explanation_data,
                confidence_score=confidence,
                processing_time_seconds=processing_time,
                visualizations=visualizations,
                created_at=datetime.now(),
                metadata={
                    'model_type': self.config.model_type,
                    'explanation_depth': self.config.explanation_depth,
                    'num_features': len(feature_importances)
                }
            )
            
            # Store result if enabled
            if self.config.save_explanations:
                self.explanation_results[explanation_id] = result
            
            # Log metrics
            await self.performance_monitor.log_metrics(
                model_id=model_id,
                metrics={
                    'explanation_processing_time': processing_time,
                    'explanation_confidence': confidence,
                    'explanation_features_count': len(feature_importances)
                }
            )
            
            # Audit trail
            await self.audit_trail.log_event(
                event_type='model_explanation_generated',
                entity_id=explanation_id,
                metadata={
                    'model_id': model_id,
                    'method': explanation_method,
                    'confidence': confidence,
                    'processing_time': processing_time
                }
            )
            
            self.logger.info(
                f"Explanation generated for model {model_id} using {explanation_method}. "
                f"Confidence: {confidence:.3f}, Time: {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {e}")
            raise
    
    async def _create_visualizations(
        self, 
        explanation_data: Dict[str, Any], 
        feature_importances: Dict[str, float],
        method: str
    ) -> Dict[str, str]:
        """Create visualizations for explanations."""
        visualizations = {}
        
        try:
            # Feature importance plot
            if feature_importances:
                plt.figure(figsize=(12, 8))
                
                # Sort features by importance
                sorted_features = sorted(feature_importances.items(), key=lambda x: abs(x[1]), reverse=True)
                
                # Take top 20 features
                top_features = sorted_features[:20]
                feature_names = [item[0] for item in top_features]
                importance_values = [item[1] for item in top_features]
                
                # Create horizontal bar plot
                colors = ['red' if val < 0 else 'blue' for val in importance_values]
                plt.barh(range(len(feature_names)), importance_values, color=colors, alpha=0.7)
                plt.yticks(range(len(feature_names)), feature_names)
                plt.xlabel('Feature Importance')
                plt.title(f'Top Features - {method.upper()} Explanation')
                plt.grid(True, alpha=0.3)
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                plot_data = buffer.read()
                buffer.close()
                plt.close()
                
                visualizations['feature_importance'] = base64.b64encode(plot_data).decode('utf-8')
            
            # Method-specific visualizations
            if method == 'shap' and 'shap_values' in explanation_data:
                # SHAP summary plot (simplified)
                shap_values = np.array(explanation_data['shap_values'])
                
                plt.figure(figsize=(10, 6))
                plt.bar(range(len(shap_values)), shap_values, alpha=0.7)
                plt.xlabel('Feature Index')
                plt.ylabel('SHAP Value')
                plt.title('SHAP Values per Feature')
                plt.grid(True, alpha=0.3)
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                plot_data = buffer.read()
                buffer.close()
                plt.close()
                
                visualizations['shap_summary'] = base64.b64encode(plot_data).decode('utf-8')
            
            elif method == 'gradient' and 'gradients' in explanation_data:
                # Gradient visualization
                gradients = np.array(explanation_data['gradients'])
                
                plt.figure(figsize=(10, 6))
                plt.plot(gradients, alpha=0.7, linewidth=2)
                plt.xlabel('Feature Index')
                plt.ylabel('Gradient Value')
                plt.title('Gradient-based Feature Attribution')
                plt.grid(True, alpha=0.3)
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                plot_data = buffer.read()
                buffer.close()
                plt.close()
                
                visualizations['gradient_plot'] = base64.b64encode(plot_data).decode('utf-8')
            
        except Exception as e:
            self.logger.warning(f"Error creating visualizations: {e}")
        
        return visualizations
    
    async def batch_explain(
        self,
        model: nn.Module,
        input_batch: List[Any],
        model_id: str = "unknown",
        method: str = None,
        **kwargs
    ) -> List[ExplanationResult]:
        """
        📊 **Batch Model Explanations**
        
        Generate explanations for multiple inputs efficiently.
        """
        try:
            results = []
            
            for i, input_data in enumerate(input_batch):
                try:
                    result = await self.explain_prediction(
                        model=model,
                        input_data=input_data,
                        model_id=f"{model_id}_batch_{i}",
                        method=method,
                        **kwargs
                    )
                    results.append(result)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to explain batch item {i}: {e}")
                    continue
            
            self.logger.info(f"Batch explanation completed: {len(results)}/{len(input_batch)} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in batch explanation: {e}")
            raise
    
    async def compare_explanations(
        self,
        model: nn.Module,
        input_data: Any,
        methods: List[str],
        model_id: str = "unknown",
        **kwargs
    ) -> Dict[str, ExplanationResult]:
        """
        🔍 **Compare Different Explanation Methods**
        
        Generate explanations using multiple methods for comparison.
        """
        try:
            comparison_results = {}
            
            for method in methods:
                if method in self.explainers:
                    try:
                        result = await self.explain_prediction(
                            model=model,
                            input_data=input_data,
                            model_id=model_id,
                            method=method,
                            **kwargs
                        )
                        comparison_results[method] = result
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to generate {method} explanation: {e}")
                else:
                    self.logger.warning(f"Explanation method '{method}' not available")
            
            # Create comparison visualization
            if len(comparison_results) > 1 and self.config.visualization_enabled:
                comparison_viz = await self._create_comparison_visualization(comparison_results)
                
                # Add comparison visualization to all results
                for result in comparison_results.values():
                    result.visualizations['method_comparison'] = comparison_viz
            
            self.logger.info(f"Explanation comparison completed for {len(comparison_results)} methods")
            
            return comparison_results
            
        except Exception as e:
            self.logger.error(f"Error in explanation comparison: {e}")
            raise
    
    async def _create_comparison_visualization(self, comparison_results: Dict[str, ExplanationResult]) -> str:
        """Create comparison visualization for different explanation methods."""
        try:
            plt.figure(figsize=(15, 10))
            
            methods = list(comparison_results.keys())
            num_methods = len(methods)
            
            # Create subplots for each method
            for i, (method, result) in enumerate(comparison_results.items()):
                plt.subplot(2, (num_methods + 1) // 2, i + 1)
                
                # Get top 10 features for this method
                sorted_features = sorted(
                    result.feature_importances.items(), 
                    key=lambda x: abs(x[1]), 
                    reverse=True
                )[:10]
                
                feature_names = [item[0] for item in sorted_features]
                importance_values = [item[1] for item in sorted_features]
                
                colors = ['red' if val < 0 else 'blue' for val in importance_values]
                plt.barh(range(len(feature_names)), importance_values, color=colors, alpha=0.7)
                plt.yticks(range(len(feature_names)), feature_names)
                plt.xlabel('Importance')
                plt.title(f'{method.upper()} Method')
                plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            plot_data = buffer.read()
            buffer.close()
            plt.close()
            
            return base64.b64encode(plot_data).decode('utf-8')
            
        except Exception as e:
            self.logger.warning(f"Error creating comparison visualization: {e}")
            return ""
    
    async def get_explanation_summary(self, explanation_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of stored explanation."""
        if explanation_id not in self.explanation_results:
            return None
        
        result = self.explanation_results[explanation_id]
        
        # Create summary
        top_features = sorted(
            result.feature_importances.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        
        summary = {
            'explanation_id': result.explanation_id,
            'method_used': result.method_used,
            'prediction': result.prediction,
            'confidence_score': result.confidence_score,
            'top_features': top_features,
            'processing_time': result.processing_time_seconds,
            'created_at': result.created_at.isoformat()
        }
        
        return summary
    
    async def export_explanation(self, explanation_id: str, format: str = 'json') -> Optional[str]:
        """Export explanation in specified format."""
        if explanation_id not in self.explanation_results:
            return None
        
        result = self.explanation_results[explanation_id]
        
        if format == 'json':
            export_data = {
                'explanation_id': result.explanation_id,
                'method_used': result.method_used,
                'model_id': result.model_id,
                'prediction': result.prediction,
                'feature_importances': result.feature_importances,
                'explanation_data': result.explanation_data,
                'confidence_score': result.confidence_score,
                'processing_time_seconds': result.processing_time_seconds,
                'created_at': result.created_at.isoformat(),
                'metadata': result.metadata
            }
            
            return json.dumps(export_data, indent=2)
        
        elif format == 'html':
            # Create HTML report
            html_content = f"""
            <html>
            <head><title>Model Explanation Report</title></head>
            <body>
                <h1>Model Explanation Report</h1>
                <h2>Explanation ID: {result.explanation_id}</h2>
                <p><strong>Method:</strong> {result.method_used}</p>
                <p><strong>Model ID:</strong> {result.model_id}</p>
                <p><strong>Prediction:</strong> Class {result.prediction['predicted_class']} (Confidence: {result.prediction['confidence']:.3f})</p>
                <p><strong>Processing Time:</strong> {result.processing_time_seconds:.2f} seconds</p>
                
                <h3>Top Features</h3>
                <ul>
            """
            
            top_features = sorted(result.feature_importances.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            for feature, importance in top_features:
                html_content += f"<li>{feature}: {importance:.4f}</li>"
            
            html_content += """
                </ul>
            </body>
            </html>
            """
            
            return html_content
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Factory for creating model explainers
class ModelExplainerFactory:
    """Factory for creating optimized model explainers."""
    
    @staticmethod
    def create_for_creator_type(creator_type: str, model_type: str = 'tabular') -> ModelExplainer:
        """Create explainer optimized for specific creator type."""
        if creator_type == 'musician':
            config = ExplanationConfig(
                method='shap',
                model_type='tabular',  # Audio features
                num_samples=500,
                visualization_enabled=True,
                explanation_depth='detailed'
            )
        elif creator_type == 'blogger':
            config = ExplanationConfig(
                method='lime',
                model_type='text',
                num_samples=1000,
                visualization_enabled=True,
                explanation_depth='full'
            )
        elif creator_type == 'photographer':
            config = ExplanationConfig(
                method='integrated_gradients',
                model_type='image',
                num_samples=100,
                visualization_enabled=True,
                explanation_depth='detailed'
            )
        else:
            config = ExplanationConfig(
                method='shap',
                model_type=model_type,
                num_samples=500,
                visualization_enabled=True
            )
        
        return ModelExplainer(config)
    
    @staticmethod
    def create_comparison_explainer() -> ModelExplainer:
        """Create explainer for method comparison."""
        config = ExplanationConfig(
            method='shap',  # Default method
            model_type='tabular',
            num_samples=500,
            visualization_enabled=True,
            explanation_depth='full'
        )
        
        return ModelExplainer(config)

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Example usage
    async def demo_model_explainer():
        # Create dummy model and data
        model = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )
        
        input_data = torch.randn(1, 10)
        background_data = torch.randn(100, 10).numpy()
        
        # Create explainer
        explainer = ModelExplainerFactory.create_for_creator_type("musician")
        
        # Generate explanation
        result = await explainer.explain_prediction(
            model=model,
            input_data=input_data,
            model_id="demo_model",
            background_data=background_data,
            feature_names=[f"audio_feature_{i}" for i in range(10)]
        )
        
        print(f"Explanation generated: {result.explanation_id}")
        print(f"Prediction: Class {result.prediction['predicted_class']}")
        print(f"Top features: {list(result.feature_importances.items())[:5]}")
        
        # Compare methods
        comparison = await explainer.compare_explanations(
            model=model,
            input_data=input_data,
            methods=['shap', 'gradient', 'integrated_gradients'],
            background_data=background_data
        )
        
        print(f"Comparison completed for {len(comparison)} methods")
    
    # Run demo
    asyncio.run(demo_model_explainer())