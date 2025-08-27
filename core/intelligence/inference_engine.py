"""
Inference Engine - Real-time Intelligent Reasoning and Prediction

Advanced inference system for real-time content analysis, prediction,
and intelligent decision making. Implements multiple inference methods
including rule-based reasoning, probabilistic inference, and neural inference.

Features:
- Real-time inference processing
- Multiple inference algorithms
- Probabilistic reasoning
- Rule-based expert systems
- Bayesian networks
- Fuzzy logic inference
- Neural inference systems

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict, deque
import threading
import queue

# Scientific Computing
import scipy.stats as stats
from scipy.special import softmax

# Probabilistic Programming
import pymc3 as pm
import theano.tensor as tt

# Fuzzy Logic
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Rule Engine
from experta import KnowledgeEngine, Rule, Fact, DefFacts, AS

# Machine Learning
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
import torch
import torch.nn as nn
import torch.nn.functional as F

# Core Dependencies
from ..processors.inference_processor import InferenceProcessor
from ..engines.rule_engine import RuleEngine
from ..networks.bayesian_network import BayesianNetwork
from ..storage.inference_storage import InferenceStorage


class InferenceType(Enum):
    """Inference algorithm types"""
    RULE_BASED = "rule_based"
    PROBABILISTIC = "probabilistic"
    FUZZY = "fuzzy"
    BAYESIAN = "bayesian"
    NEURAL = "neural"
    HYBRID = "hybrid"
    CAUSAL = "causal"
    TEMPORAL = "temporal"


class ConfidenceLevel(Enum):
    """Confidence levels for inferences"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class InferenceRule:
    """Inference rule representation"""
    rule_id: str
    condition: str
    conclusion: str
    confidence: float
    priority: int
    rule_type: str
    parameters: Dict[str, Any]


@dataclass
class InferenceResult:
    """Inference result"""
    inference_id: str
    predictions: Dict[str, Any]
    confidence_scores: Dict[str, float]
    reasoning_path: List[str]
    inference_time: float
    used_rules: List[str]
    evidence: Dict[str, Any]


class RuleBasedInference:
    """Rule-based inference engine"""
    
    def __init__(self):
        self.rules = {}
        self.facts = {}
        self.inference_chain = []
        
    def add_rule(self, rule: InferenceRule) -> bool:
        """Add inference rule"""
        try:
            self.rules[rule.rule_id] = rule
            return True
        except Exception as e:
            logging.error(f"Failed to add rule {rule.rule_id}: {e}")
            return False
    
    def add_fact(self, fact_id: str, fact_data: Dict[str, Any]) -> bool:
        """Add fact to knowledge base"""
        try:
            self.facts[fact_id] = fact_data
            return True
        except Exception as e:
            logging.error(f"Failed to add fact {fact_id}: {e}")
            return False
    
    def infer(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Perform rule-based inference"""
        try:
            self.inference_chain = []
            conclusions = {}
            
            # Forward chaining inference
            changed = True
            max_iterations = 100
            iterations = 0
            
            while changed and iterations < max_iterations:
                changed = False
                iterations += 1
                
                for rule_id, rule in self.rules.items():
                    if self._evaluate_condition(rule.condition, query):
                        conclusion = self._apply_rule(rule, query)
                        
                        if conclusion and rule_id not in [step['rule_id'] for step in self.inference_chain]:
                            conclusions.update(conclusion)
                            self.inference_chain.append({
                                'rule_id': rule_id,
                                'conclusion': conclusion,
                                'confidence': rule.confidence
                            })
                            changed = True
            
            return conclusions
            
        except Exception as e:
            logging.error(f"Rule-based inference failed: {e}")
            return {}
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate rule condition"""
        try:
            # Simple condition evaluation (expandable)
            # Format: "key operator value" (e.g., "engagement > 0.5")
            
            parts = condition.split()
            if len(parts) != 3:
                return False
            
            key, operator, value = parts
            
            if key not in data:
                return False
            
            data_value = data[key]
            
            try:
                value = float(value)
                data_value = float(data_value)
            except ValueError:
                # String comparison
                pass
            
            if operator == ">":
                return data_value > value
            elif operator == ">=":
                return data_value >= value
            elif operator == "<":
                return data_value < value
            elif operator == "<=":
                return data_value <= value
            elif operator == "==":
                return data_value == value
            elif operator == "!=":
                return data_value != value
            elif operator == "contains":
                return str(value) in str(data_value)
            
            return False
            
        except Exception as e:
            logging.error(f"Condition evaluation failed: {e}")
            return False
    
    def _apply_rule(self, rule: InferenceRule, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply inference rule"""
        try:
            # Parse conclusion (format: "key = value")
            if "=" in rule.conclusion:
                key, value = rule.conclusion.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Try to convert to appropriate type
                try:
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    else:
                        value = float(value)
                except ValueError:
                    pass  # Keep as string
                
                return {key: value}
            
            return None
            
        except Exception as e:
            logging.error(f"Rule application failed: {e}")
            return None


class ProbabilisticInference:
    """Probabilistic inference using Bayesian methods"""
    
    def __init__(self):
        self.variables = {}
        self.distributions = {}
        self.dependencies = {}
        
    def add_variable(
        self,
        var_name: str,
        distribution: str,
        parameters: Dict[str, Any],
        dependencies: Optional[List[str]] = None
    ) -> bool:
        """Add probabilistic variable"""
        try:
            self.variables[var_name] = {
                'distribution': distribution,
                'parameters': parameters,
                'dependencies': dependencies or []
            }
            
            if dependencies:
                self.dependencies[var_name] = dependencies
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to add variable {var_name}: {e}")
            return False
    
    def infer(self, evidence: Dict[str, Any], query_vars: List[str]) -> Dict[str, Any]:
        """Perform probabilistic inference"""
        try:
            results = {}
            
            for var in query_vars:
                if var in self.variables:
                    # Simple probabilistic inference
                    var_info = self.variables[var]
                    
                    if var_info['distribution'] == 'bernoulli':
                        # Binary variable
                        prob = self._compute_probability(var, evidence)
                        results[var] = {
                            'probability': prob,
                            'prediction': prob > 0.5,
                            'confidence': abs(prob - 0.5) * 2
                        }
                    
                    elif var_info['distribution'] == 'normal':
                        # Continuous variable
                        mean, std = self._compute_normal_parameters(var, evidence)
                        results[var] = {
                            'mean': mean,
                            'std': std,
                            'confidence': 1.0 / (1.0 + std)
                        }
                    
                    elif var_info['distribution'] == 'categorical':
                        # Categorical variable
                        probabilities = self._compute_categorical_probabilities(var, evidence)
                        results[var] = {
                            'probabilities': probabilities,
                            'prediction': max(probabilities, key=probabilities.get),
                            'confidence': max(probabilities.values())
                        }
            
            return results
            
        except Exception as e:
            logging.error(f"Probabilistic inference failed: {e}")
            return {}
    
    def _compute_probability(self, var: str, evidence: Dict[str, Any]) -> float:
        """Compute probability for binary variable"""
        var_info = self.variables[var]
        base_prob = var_info['parameters'].get('prob', 0.5)
        
        # Adjust based on dependencies
        if var in self.dependencies:
            for dep in self.dependencies[var]:
                if dep in evidence:
                    # Simple adjustment based on dependency
                    dep_value = evidence[dep]
                    if isinstance(dep_value, (int, float)):
                        base_prob = base_prob * (1.0 + 0.1 * dep_value)
                    elif isinstance(dep_value, bool):
                        base_prob = base_prob * (1.2 if dep_value else 0.8)
        
        return max(0.0, min(1.0, base_prob))
    
    def _compute_normal_parameters(self, var: str, evidence: Dict[str, Any]) -> Tuple[float, float]:
        """Compute mean and std for normal variable"""
        var_info = self.variables[var]
        base_mean = var_info['parameters'].get('mean', 0.0)
        base_std = var_info['parameters'].get('std', 1.0)
        
        # Adjust based on dependencies
        if var in self.dependencies:
            for dep in self.dependencies[var]:
                if dep in evidence:
                    dep_value = evidence[dep]
                    if isinstance(dep_value, (int, float)):
                        base_mean += 0.1 * dep_value
                        base_std *= (1.0 - 0.05 * abs(dep_value))
        
        return base_mean, max(0.1, base_std)
    
    def _compute_categorical_probabilities(self, var: str, evidence: Dict[str, Any]) -> Dict[str, float]:
        """Compute probabilities for categorical variable"""
        var_info = self.variables[var]
        base_probs = var_info['parameters'].get('probabilities', {})
        
        # Adjust based on dependencies
        adjusted_probs = base_probs.copy()
        
        if var in self.dependencies:
            for dep in self.dependencies[var]:
                if dep in evidence:
                    dep_value = evidence[dep]
                    # Simple adjustment logic
                    for category in adjusted_probs:
                        if isinstance(dep_value, (int, float)):
                            adjusted_probs[category] *= (1.0 + 0.05 * dep_value)
        
        # Normalize probabilities
        total = sum(adjusted_probs.values())
        if total > 0:
            adjusted_probs = {k: v/total for k, v in adjusted_probs.items()}
        
        return adjusted_probs


class FuzzyInference:
    """Fuzzy logic inference system"""
    
    def __init__(self):
        self.linguistic_variables = {}
        self.rules = []
        self.control_system = None
        
    def add_linguistic_variable(
        self,
        var_name: str,
        universe: np.ndarray,
        membership_functions: Dict[str, Any]
    ) -> bool:
        """Add fuzzy linguistic variable"""
        try:
            # Create fuzzy variable
            if var_name.endswith('_input'):
                var = ctrl.Antecedent(universe, var_name)
            else:
                var = ctrl.Consequent(universe, var_name)
            
            # Add membership functions
            for mf_name, mf_params in membership_functions.items():
                if mf_params['type'] == 'triangular':
                    var[mf_name] = fuzz.trimf(universe, mf_params['points'])
                elif mf_params['type'] == 'trapezoidal':
                    var[mf_name] = fuzz.trapmf(universe, mf_params['points'])
                elif mf_params['type'] == 'gaussian':
                    var[mf_name] = fuzz.gaussmf(universe, mf_params['mean'], mf_params['sigma'])
            
            self.linguistic_variables[var_name] = var
            return True
            
        except Exception as e:
            logging.error(f"Failed to add linguistic variable {var_name}: {e}")
            return False
    
    def add_fuzzy_rule(self, antecedent: str, consequent: str) -> bool:
        """Add fuzzy rule"""
        try:
            # Parse and create fuzzy rule
            # Format: "IF input1 is high AND input2 is medium THEN output is good"
            
            # This is a simplified parser - would need more sophisticated parsing
            rule_dict = {
                'antecedent': antecedent,
                'consequent': consequent
            }
            self.rules.append(rule_dict)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to add fuzzy rule: {e}")
            return False
    
    def infer(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """Perform fuzzy inference"""
        try:
            results = {}
            
            # Simple fuzzy inference implementation
            # In practice, would use scikit-fuzzy's control system
            
            for output_var in self.linguistic_variables:
                if not output_var.endswith('_input'):
                    # Calculate output using centroid defuzzification
                    output_value = self._defuzzify(inputs, output_var)
                    results[output_var] = output_value
            
            return results
            
        except Exception as e:
            logging.error(f"Fuzzy inference failed: {e}")
            return {}
    
    def _defuzzify(self, inputs: Dict[str, float], output_var: str) -> float:
        """Defuzzify output using centroid method"""
        try:
            # Simplified defuzzification
            # Would implement proper fuzzy inference in production
            
            # For now, return weighted average based on input values
            total_weight = 0.0
            weighted_sum = 0.0
            
            for input_var, input_value in inputs.items():
                weight = 1.0 / (1.0 + abs(input_value - 0.5))
                weighted_sum += weight * input_value
                total_weight += weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return 0.5
                
        except Exception as e:
            logging.error(f"Defuzzification failed: {e}")
            return 0.5


class NeuralInference:
    """Neural network-based inference"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], output_dim: int):
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        
        # Build neural network
        self.model = self._build_network()
        self.is_trained = False
        
    def _build_network(self) -> nn.Module:
        """Build neural inference network"""
        layers = []
        prev_dim = self.input_dim
        
        for hidden_dim in self.hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, self.output_dim))
        
        return nn.Sequential(*layers)
    
    def train(self, training_data: List[Tuple[np.ndarray, np.ndarray]], epochs: int = 100) -> bool:
        """Train neural inference model"""
        try:
            if not training_data:
                return False
            
            # Prepare data
            X = torch.FloatTensor([x for x, y in training_data])
            y = torch.FloatTensor([y for x, y in training_data])
            
            # Training setup
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            
            # Training loop
            self.model.train()
            for epoch in range(epochs):
                optimizer.zero_grad()
                outputs = self.model(X)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
                
                if epoch % 20 == 0:
                    logging.info(f"Neural inference training epoch {epoch}, loss: {loss.item():.4f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logging.error(f"Neural inference training failed: {e}")
            return False
    
    def infer(self, inputs: np.ndarray) -> np.ndarray:
        """Perform neural inference"""
        try:
            if not self.is_trained:
                logging.warning("Neural model not trained, returning random predictions")
                return np.random.rand(self.output_dim)
            
            self.model.eval()
            with torch.no_grad():
                input_tensor = torch.FloatTensor(inputs).unsqueeze(0)
                output = self.model(input_tensor)
                return output.numpy().flatten()
                
        except Exception as e:
            logging.error(f"Neural inference failed: {e}")
            return np.zeros(self.output_dim)


class InferenceEngine:
    """
    Comprehensive inference engine for real-time reasoning
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize inference engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize inference methods
        self._initialize_inference_methods()
        self._initialize_processors()
        
        # Real-time processing
        self.inference_queue = queue.Queue()
        self.is_processing = False
        self.processing_thread = None
        
        # Performance tracking
        self.performance_metrics = {
            "total_inferences": 0,
            "average_inference_time": 0.0,
            "successful_inferences": 0,
            "confidence_scores": [],
            "method_usage": defaultdict(int)
        }
        
        # Results cache
        self.results_cache = {}
        self.cache_size = config.get("cache_size", 1000)
    
    def _initialize_inference_methods(self) -> None:
        """Initialize inference methods"""
        try:
            # Rule-based inference
            self.rule_engine = RuleBasedInference()
            self._setup_default_rules()
            
            # Probabilistic inference
            self.probabilistic_engine = ProbabilisticInference()
            self._setup_probabilistic_variables()
            
            # Fuzzy inference
            self.fuzzy_engine = FuzzyInference()
            self._setup_fuzzy_variables()
            
            # Neural inference
            input_dim = self.config.get("neural_input_dim", 50)
            hidden_dims = self.config.get("neural_hidden_dims", [100, 50])
            output_dim = self.config.get("neural_output_dim", 10)
            
            self.neural_engine = NeuralInference(input_dim, hidden_dims, output_dim)
            
            self.logger.info("Inference methods initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize inference methods: {e}")
            raise
    
    def _initialize_processors(self) -> None:
        """Initialize inference processors"""
        try:
            self.inference_processor = InferenceProcessor(self.config)
            self.rule_engine_processor = RuleEngine(self.config)
            self.bayesian_network = BayesianNetwork(self.config)
            self.inference_storage = InferenceStorage(self.config)
        except Exception as e:
            self.logger.warning(f"Some processors could not be initialized: {e}")
    
    def _setup_default_rules(self) -> None:
        """Setup default inference rules"""
        default_rules = [
            InferenceRule(
                rule_id="high_engagement_viral",
                condition="engagement_rate > 0.1",
                conclusion="viral_potential = high",
                confidence=0.8,
                priority=1,
                rule_type="engagement",
                parameters={}
            ),
            InferenceRule(
                rule_id="high_quality_premium",
                condition="quality_score > 0.8",
                conclusion="monetization_tier = premium",
                confidence=0.9,
                priority=1,
                rule_type="monetization",
                parameters={}
            ),
            InferenceRule(
                rule_id="long_duration_tutorial",
                condition="duration > 600",
                conclusion="content_type = tutorial",
                confidence=0.7,
                priority=2,
                rule_type="classification",
                parameters={}
            ),
            InferenceRule(
                rule_id="high_views_trending",
                condition="views > 10000",
                conclusion="trending_status = true",
                confidence=0.85,
                priority=1,
                rule_type="trending",
                parameters={}
            )
        ]
        
        for rule in default_rules:
            self.rule_engine.add_rule(rule)
    
    def _setup_probabilistic_variables(self) -> None:
        """Setup probabilistic variables"""
        # Engagement prediction
        self.probabilistic_engine.add_variable(
            "engagement_success",
            "bernoulli",
            {"prob": 0.3},
            ["quality_score", "timing_score"]
        )
        
        # Revenue prediction
        self.probabilistic_engine.add_variable(
            "revenue_amount",
            "normal",
            {"mean": 100.0, "std": 50.0},
            ["engagement_success", "monetization_tier"]
        )
        
        # Content category
        self.probabilistic_engine.add_variable(
            "content_category",
            "categorical",
            {"probabilities": {
                "entertainment": 0.3,
                "educational": 0.25,
                "music": 0.2,
                "tutorial": 0.15,
                "news": 0.1
            }},
            ["duration", "keywords"]
        )
    
    def _setup_fuzzy_variables(self) -> None:
        """Setup fuzzy variables"""
        # Quality assessment
        quality_universe = np.arange(0, 1.1, 0.1)
        quality_mfs = {
            "low": {"type": "triangular", "points": [0, 0, 0.4]},
            "medium": {"type": "triangular", "points": [0.2, 0.5, 0.8]},
            "high": {"type": "triangular", "points": [0.6, 1.0, 1.0]}
        }
        self.fuzzy_engine.add_linguistic_variable("quality_input", quality_universe, quality_mfs)
        
        # Engagement assessment
        engagement_universe = np.arange(0, 1.1, 0.1)
        engagement_mfs = {
            "poor": {"type": "triangular", "points": [0, 0, 0.3]},
            "average": {"type": "triangular", "points": [0.2, 0.5, 0.8]},
            "excellent": {"type": "triangular", "points": [0.7, 1.0, 1.0]}
        }
        self.fuzzy_engine.add_linguistic_variable("engagement_input", engagement_universe, engagement_mfs)
        
        # Recommendation output
        recommendation_universe = np.arange(0, 1.1, 0.1)
        recommendation_mfs = {
            "reject": {"type": "triangular", "points": [0, 0, 0.3]},
            "review": {"type": "triangular", "points": [0.2, 0.5, 0.8]},
            "approve": {"type": "triangular", "points": [0.7, 1.0, 1.0]}
        }
        self.fuzzy_engine.add_linguistic_variable("recommendation", recommendation_universe, recommendation_mfs)
    
    async def infer(
        self,
        input_data: Dict[str, Any],
        inference_type: InferenceType = InferenceType.HYBRID,
        real_time: bool = False
    ) -> InferenceResult:
        """
        Perform inference on input data
        
        Args:
            input_data: Input data for inference
            inference_type: Type of inference to perform
            real_time: Whether to process in real-time
            
        Returns:
            InferenceResult: Inference results and metadata
        """
        if real_time:
            # Add to real-time processing queue
            return await self._queue_inference(input_data, inference_type)
        else:
            return await self._process_inference(input_data, inference_type)
    
    async def _queue_inference(
        self,
        input_data: Dict[str, Any],
        inference_type: InferenceType
    ) -> InferenceResult:
        """Queue inference for real-time processing"""
        inference_id = f"inf_{int(datetime.now().timestamp())}"
        
        self.inference_queue.put({
            'inference_id': inference_id,
            'input_data': input_data,
            'inference_type': inference_type,
            'timestamp': datetime.now()
        })
        
        # Start processing if not already running
        if not self.is_processing:
            await self._start_real_time_processing()
        
        # Wait for result (simplified - would use proper async notification)
        await asyncio.sleep(0.1)
        
        # Check if result is ready
        if inference_id in self.results_cache:
            return self.results_cache[inference_id]
        
        # Return placeholder result if not ready
        return InferenceResult(
            inference_id=inference_id,
            predictions={},
            confidence_scores={},
            reasoning_path=["Queued for processing"],
            inference_time=0.0,
            used_rules=[],
            evidence={}
        )
    
    async def _start_real_time_processing(self) -> None:
        """Start real-time inference processing"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_queue)
        self.processing_thread.start()
    
    def _process_queue(self) -> None:
        """Process inference queue"""
        while self.is_processing:
            try:
                if not self.inference_queue.empty():
                    item = self.inference_queue.get(timeout=1)
                    
                    # Process inference
                    result = asyncio.run(self._process_inference(
                        item['input_data'],
                        item['inference_type']
                    ))
                    
                    # Store result
                    self.results_cache[item['inference_id']] = result
                    
                    # Clean cache if too large
                    if len(self.results_cache) > self.cache_size:
                        oldest_key = min(self.results_cache.keys())
                        del self.results_cache[oldest_key]
                
                else:
                    # No items to process, sleep briefly
                    threading.Event().wait(0.1)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")
    
    async def _process_inference(
        self,
        input_data: Dict[str, Any],
        inference_type: InferenceType
    ) -> InferenceResult:
        """Process single inference"""
        start_time = datetime.now()
        inference_id = f"inf_{int(start_time.timestamp())}"
        
        try:
            predictions = {}
            confidence_scores = {}
            reasoning_path = []
            used_rules = []
            evidence = input_data.copy()
            
            if inference_type == InferenceType.RULE_BASED or inference_type == InferenceType.HYBRID:
                # Rule-based inference
                rule_results = self.rule_engine.infer(input_data)
                if rule_results:
                    predictions.update(rule_results)
                    reasoning_path.append("Applied rule-based inference")
                    used_rules.extend([step['rule_id'] for step in self.rule_engine.inference_chain])
                    
                    # Calculate confidence from used rules
                    if self.rule_engine.inference_chain:
                        avg_confidence = np.mean([step['confidence'] for step in self.rule_engine.inference_chain])
                        confidence_scores['rule_based'] = avg_confidence
            
            if inference_type == InferenceType.PROBABILISTIC or inference_type == InferenceType.HYBRID:
                # Probabilistic inference
                query_vars = ['engagement_success', 'revenue_amount', 'content_category']
                prob_results = self.probabilistic_engine.infer(input_data, query_vars)
                
                if prob_results:
                    for var, result in prob_results.items():
                        if 'prediction' in result:
                            predictions[f"prob_{var}"] = result['prediction']
                        if 'mean' in result:
                            predictions[f"prob_{var}_mean"] = result['mean']
                        if 'probabilities' in result:
                            predictions[f"prob_{var}_dist"] = result['probabilities']
                        
                        confidence_scores[f"prob_{var}"] = result.get('confidence', 0.5)
                    
                    reasoning_path.append("Applied probabilistic inference")
            
            if inference_type == InferenceType.FUZZY or inference_type == InferenceType.HYBRID:
                # Fuzzy inference
                fuzzy_inputs = self._prepare_fuzzy_inputs(input_data)
                if fuzzy_inputs:
                    fuzzy_results = self.fuzzy_engine.infer(fuzzy_inputs)
                    
                    if fuzzy_results:
                        for var, value in fuzzy_results.items():
                            predictions[f"fuzzy_{var}"] = value
                            confidence_scores[f"fuzzy_{var}"] = min(value, 1.0 - value) * 2
                        
                        reasoning_path.append("Applied fuzzy logic inference")
            
            if inference_type == InferenceType.NEURAL or inference_type == InferenceType.HYBRID:
                # Neural inference
                neural_inputs = self._prepare_neural_inputs(input_data)
                if neural_inputs is not None:
                    neural_results = self.neural_engine.infer(neural_inputs)
                    
                    if neural_results is not None and len(neural_results) > 0:
                        for i, value in enumerate(neural_results):
                            predictions[f"neural_output_{i}"] = float(value)
                            confidence_scores[f"neural_output_{i}"] = min(abs(value), 1.0)
                        
                        reasoning_path.append("Applied neural inference")
            
            # Calculate overall confidence
            if confidence_scores:
                overall_confidence = np.mean(list(confidence_scores.values()))
            else:
                overall_confidence = 0.5
            
            # Calculate inference time
            inference_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = InferenceResult(
                inference_id=inference_id,
                predictions=predictions,
                confidence_scores=confidence_scores,
                reasoning_path=reasoning_path,
                inference_time=inference_time,
                used_rules=used_rules,
                evidence=evidence
            )
            
            # Update metrics
            self._update_performance_metrics(result, inference_type)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Inference processing failed: {e}")
            return InferenceResult(
                inference_id=inference_id,
                predictions={},
                confidence_scores={},
                reasoning_path=[f"Error: {e}"],
                inference_time=(datetime.now() - start_time).total_seconds(),
                used_rules=[],
                evidence={}
            )
    
    def _prepare_fuzzy_inputs(self, input_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Prepare inputs for fuzzy inference"""
        try:
            fuzzy_inputs = {}
            
            if 'quality_score' in input_data:
                fuzzy_inputs['quality_input'] = float(input_data['quality_score'])
            
            if 'engagement_rate' in input_data:
                fuzzy_inputs['engagement_input'] = float(input_data['engagement_rate'])
            
            return fuzzy_inputs if fuzzy_inputs else None
            
        except Exception as e:
            self.logger.error(f"Fuzzy input preparation failed: {e}")
            return None
    
    def _prepare_neural_inputs(self, input_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Prepare inputs for neural inference"""
        try:
            # Extract numerical features
            features = []
            
            # Standard features
            features.append(input_data.get('quality_score', 0.5))
            features.append(input_data.get('engagement_rate', 0.0))
            features.append(input_data.get('duration', 0) / 3600)  # Normalize to hours
            features.append(input_data.get('views', 0) / 10000)    # Normalize
            features.append(input_data.get('likes', 0) / 1000)     # Normalize
            
            # Content type encoding
            content_type = input_data.get('content_type', 'unknown')
            type_encoding = {'audio': 1, 'video': 2, 'image': 3, 'text': 4, 'unknown': 0}
            features.append(type_encoding.get(content_type, 0) / 4)  # Normalize
            
            # Pad or truncate to expected dimension
            target_dim = self.neural_engine.input_dim
            while len(features) < target_dim:
                features.append(0.0)
            
            return np.array(features[:target_dim])
            
        except Exception as e:
            self.logger.error(f"Neural input preparation failed: {e}")
            return None
    
    def _update_performance_metrics(
        self,
        result: InferenceResult,
        inference_type: InferenceType
    ) -> None:
        """Update performance metrics"""
        self.performance_metrics["total_inferences"] += 1
        
        # Update average inference time
        current_avg = self.performance_metrics["average_inference_time"]
        total_inferences = self.performance_metrics["total_inferences"]
        
        self.performance_metrics["average_inference_time"] = (
            (current_avg * (total_inferences - 1) + result.inference_time) / total_inferences
        )
        
        # Track successful inferences
        if result.predictions:
            self.performance_metrics["successful_inferences"] += 1
        
        # Track confidence scores
        if result.confidence_scores:
            overall_confidence = np.mean(list(result.confidence_scores.values()))
            self.performance_metrics["confidence_scores"].append(overall_confidence)
            
            # Keep only recent scores
            if len(self.performance_metrics["confidence_scores"]) > 1000:
                self.performance_metrics["confidence_scores"] = \
                    self.performance_metrics["confidence_scores"][-1000:]
        
        # Track method usage
        self.performance_metrics["method_usage"][inference_type.value] += 1
    
    async def train_neural_inference(
        self,
        training_data: List[Tuple[Dict[str, Any], Dict[str, Any]]]
    ) -> bool:
        """Train neural inference model"""
        try:
            # Prepare training data
            processed_data = []
            
            for input_data, target_data in training_data:
                neural_input = self._prepare_neural_inputs(input_data)
                if neural_input is not None:
                    # Prepare target
                    target = np.zeros(self.neural_engine.output_dim)
                    
                    # Map target data to output vector
                    for i, (key, value) in enumerate(target_data.items()):
                        if i < self.neural_engine.output_dim:
                            try:
                                target[i] = float(value)
                            except (ValueError, TypeError):
                                target[i] = 1.0 if value else 0.0
                    
                    processed_data.append((neural_input, target))
            
            if processed_data:
                success = self.neural_engine.train(processed_data)
                if success:
                    self.logger.info(f"Neural inference model trained on {len(processed_data)} samples")
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Neural inference training failed: {e}")
            return False
    
    async def add_inference_rule(self, rule: InferenceRule) -> bool:
        """Add new inference rule"""
        return self.rule_engine.add_rule(rule)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get inference engine performance metrics"""
        metrics = self.performance_metrics.copy()
        
        # Calculate additional metrics
        if metrics["confidence_scores"]:
            metrics["average_confidence"] = np.mean(metrics["confidence_scores"])
            metrics["confidence_std"] = np.std(metrics["confidence_scores"])
        else:
            metrics["average_confidence"] = 0.0
            metrics["confidence_std"] = 0.0
        
        if metrics["total_inferences"] > 0:
            metrics["success_rate"] = metrics["successful_inferences"] / metrics["total_inferences"]
        else:
            metrics["success_rate"] = 0.0
        
        return metrics
    
    def stop_real_time_processing(self) -> None:
        """Stop real-time processing"""
        self.is_processing = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
    
    def clear_cache(self) -> None:
        """Clear results cache"""
        self.results_cache.clear()
        self.logger.info("Inference cache cleared")
