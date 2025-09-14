"""
Multi-Task Learning Framework - Multi-Task Learning for Shared Representations
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade multi-task learning framework for shared representations across creator domains
with intelligent task balancing and domain adaptation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
import time
from datetime import datetime
import uuid

@dataclass
class TaskDefinition:
    """Definition of a learning task."""
    task_id: str
    task_name: str
    task_type: str  # "classification", "regression", "ranking", "generation"
    domain: str  # "musician", "blogger", "photographer", "influencer"
    input_modalities: List[str]  # "audio", "text", "image", "video"
    output_shape: Tuple[int, ...]
    loss_function: str
    evaluation_metrics: List[str]
    task_weight: float
    difficulty_level: float
    data_size: int
    priority: str  # "high", "medium", "low"

@dataclass
class SharedRepresentation:
    """Shared representation layer definition."""
    layer_id: str
    layer_name: str
    representation_dim: int
    sharing_strategy: str  # "full", "partial", "adaptive"
    tasks_sharing: List[str]
    encoding_type: str  # "dense", "sparse", "attention"
    regularization: Dict[str, float]
    adaptation_rate: float

@dataclass
class MTLArchitecture:
    """Multi-task learning architecture definition."""
    architecture_id: str
    backbone_network: Dict[str, Any]
    shared_layers: List[SharedRepresentation]
    task_specific_heads: Dict[str, Dict[str, Any]]
    sharing_pattern: str  # "hard", "soft", "cross_stitch", "sluice"
    adaptation_mechanism: str  # "meta_learning", "gradient_balancing", "uncertainty"
    total_parameters: int
    computational_complexity: float

class MultiTaskLearningFramework:
    """
    Advanced multi-task learning framework for creator-specific applications.
    
    Features:
    - Adaptive task balancing and weighting
    - Cross-domain knowledge transfer
    - Dynamic architecture adaptation
    - Shared representation learning with attention mechanisms
    - Task-specific optimization strategies
    - Gradient balancing and conflict resolution
    - Meta-learning for rapid task adaptation
    - Performance monitoring and task importance estimation
    """
    
    def __init__(self, framework_config -> None: Dict[str, Any] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = framework_config or self._get_default_config()
        
        # Task management
        self.tasks = {}
        self.task_relationships = {}
        self.task_performance_history = {}
        
        # Architecture components
        self.shared_representations = {}
        self.task_specific_heads = {}
        self.mtl_architectures = {}
        
        # Training state
        self.task_weights = {}
        self.gradient_norms = {}
        self.task_difficulties = {}
        
        # Creator domain specifications
        self.domain_task_templates = {
            "musician": {
                "genre_classification": {
                    "type": "classification",
                    "modalities": ["audio", "text"],
                    "metrics": ["accuracy", "f1_score"],
                    "priority": "high"
                },
                "mood_detection": {
                    "type": "classification", 
                    "modalities": ["audio"],
                    "metrics": ["accuracy", "precision"],
                    "priority": "high"
                },
                "tempo_prediction": {
                    "type": "regression",
                    "modalities": ["audio"],
                    "metrics": ["mae", "rmse"],
                    "priority": "medium"
                },
                "engagement_prediction": {
                    "type": "regression",
                    "modalities": ["audio", "text", "metadata"],
                    "metrics": ["r2", "mae"],
                    "priority": "high"
                }
            },
            "blogger": {
                "topic_classification": {
                    "type": "classification",
                    "modalities": ["text"],
                    "metrics": ["accuracy", "f1_score"],
                    "priority": "high"
                },
                "sentiment_analysis": {
                    "type": "classification",
                    "modalities": ["text"],
                    "metrics": ["accuracy", "precision"],
                    "priority": "high"
                },
                "readability_scoring": {
                    "type": "regression",
                    "modalities": ["text"],
                    "metrics": ["mae", "correlation"],
                    "priority": "medium"
                },
                "seo_optimization": {
                    "type": "ranking",
                    "modalities": ["text", "metadata"],
                    "metrics": ["ndcg", "map"],
                    "priority": "medium"
                }
            },
            "photographer": {
                "aesthetic_scoring": {
                    "type": "regression",
                    "modalities": ["image"],
                    "metrics": ["mae", "correlation"],
                    "priority": "high"
                },
                "style_classification": {
                    "type": "classification",
                    "modalities": ["image"],
                    "metrics": ["accuracy", "f1_score"],
                    "priority": "high"
                },
                "composition_analysis": {
                    "type": "regression",
                    "modalities": ["image"],
                    "metrics": ["mae", "rmse"],
                    "priority": "medium"
                },
                "commercial_potential": {
                    "type": "regression",
                    "modalities": ["image", "metadata"],
                    "metrics": ["r2", "mae"],
                    "priority": "medium"
                }
            },
            "influencer": {
                "engagement_prediction": {
                    "type": "regression",
                    "modalities": ["image", "text", "video"],
                    "metrics": ["r2", "mae"],
                    "priority": "high"
                },
                "viral_potential": {
                    "type": "classification",
                    "modalities": ["image", "text", "video", "metadata"],
                    "metrics": ["accuracy", "auc"],
                    "priority": "high"
                },
                "brand_alignment": {
                    "type": "classification",
                    "modalities": ["image", "text"],
                    "metrics": ["accuracy", "precision"],
                    "priority": "medium"
                },
                "authenticity_scoring": {
                    "type": "regression",
                    "modalities": ["image", "text", "metadata"],
                    "metrics": ["correlation", "mae"],
                    "priority": "medium"
                }
            }
        }
        
        # Sharing strategies
        self.sharing_strategies = {
            "hard": {"description": "Complete parameter sharing", "flexibility": 0.2},
            "soft": {"description": "Regularized parameter sharing", "flexibility": 0.6},
            "cross_stitch": {"description": "Learned linear combinations", "flexibility": 0.8},
            "sluice": {"description": "Selective sharing with attention", "flexibility": 0.9}
        }
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for MTL framework."""
        return {
            "max_tasks": 10,
            "adaptive_weighting": True,
            "gradient_balancing": True,
            "meta_learning_enabled": True,
            "sharing_threshold": 0.7,
            "task_similarity_threshold": 0.6,
            "uncertainty_weighting": True,
            "performance_monitoring": True,
            "architecture_adaptation": True
        }
    
    async def define_task_suite(
        self,
        domain: str,
        custom_tasks: List[Dict[str, Any]] = None
    ) -> List[TaskDefinition]:
        """Define a suite of tasks for a creator domain."""
        try:
            task_suite = []
            
            # Get domain-specific task templates
            domain_templates = self.domain_task_templates.get(domain, {})
            
            # Create tasks from templates
            for task_name, template in domain_templates.items():
                task_id = f"{domain}_{task_name}_{int(time.time())}"
                
                task_def = TaskDefinition(
                    task_id=task_id,
                    task_name=task_name,
                    task_type=template["type"],
                    domain=domain,
                    input_modalities=template["modalities"],
                    output_shape=self._determine_output_shape(template),
                    loss_function=self._select_loss_function(template["type"]),
                    evaluation_metrics=template["metrics"],
                    task_weight=self._calculate_initial_weight(template["priority"]),
                    difficulty_level=await self._estimate_task_difficulty(template),
                    data_size=10000,  # Default - would be set based on actual data
                    priority=template["priority"]
                )
                
                task_suite.append(task_def)
                self.tasks[task_id] = task_def
            
            # Add custom tasks if provided
            if custom_tasks:
                for custom_task in custom_tasks:
                    task_id = f"{domain}_custom_{int(time.time())}"
                    
                    task_def = TaskDefinition(
                        task_id=task_id,
                        task_name=custom_task["name"],
                        task_type=custom_task["type"],
                        domain=domain,
                        input_modalities=custom_task["modalities"],
                        output_shape=tuple(custom_task["output_shape"]),
                        loss_function=custom_task.get("loss", "categorical_crossentropy"),
                        evaluation_metrics=custom_task.get("metrics", ["accuracy"]),
                        task_weight=custom_task.get("weight", 1.0),
                        difficulty_level=custom_task.get("difficulty", 0.5),
                        data_size=custom_task.get("data_size", 10000),
                        priority=custom_task.get("priority", "medium")
                    )
                    
                    task_suite.append(task_def)
                    self.tasks[task_id] = task_def
            
            # Analyze task relationships
            await self._analyze_task_relationships(task_suite)
            
            self.logger.info(f"Task suite defined for {domain}: {len(task_suite)} tasks")
            return task_suite
            
        except Exception as e:
            self.logger.error(f"Error defining task suite: {e}")
            raise
    
    async def design_mtl_architecture(
        self,
        task_suite: List[TaskDefinition],
        architecture_constraints: Dict[str, Any] = None
    ) -> MTLArchitecture:
        """Design optimal multi-task learning architecture."""
        try:
            architecture_id = f"mtl_arch_{int(time.time())}"
            
            # Analyze task compatibility and sharing opportunities
            sharing_analysis = await self._analyze_sharing_opportunities(task_suite)
            
            # Design backbone network
            backbone_network = await self._design_backbone_network(
                task_suite, sharing_analysis, architecture_constraints
            )
            
            # Create shared representations
            shared_layers = await self._design_shared_layers(
                task_suite, sharing_analysis
            )
            
            # Design task-specific heads
            task_heads = await self._design_task_specific_heads(task_suite)
            
            # Select sharing pattern
            sharing_pattern = await self._select_sharing_pattern(
                task_suite, sharing_analysis
            )
            
            # Choose adaptation mechanism
            adaptation_mechanism = await self._select_adaptation_mechanism(
                task_suite, architecture_constraints
            )
            
            # Calculate architecture properties
            total_params = await self._calculate_total_parameters(
                backbone_network, shared_layers, task_heads
            )
            
            computational_complexity = await self._estimate_computational_complexity(
                backbone_network, shared_layers, task_heads
            )
            
            # Create architecture definition
            mtl_architecture = MTLArchitecture(
                architecture_id=architecture_id,
                backbone_network=backbone_network,
                shared_layers=shared_layers,
                task_specific_heads=task_heads,
                sharing_pattern=sharing_pattern,
                adaptation_mechanism=adaptation_mechanism,
                total_parameters=total_params,
                computational_complexity=computational_complexity
            )
            
            # Store architecture
            self.mtl_architectures[architecture_id] = mtl_architecture
            
            # Initialize task weights
            await self._initialize_task_weights(task_suite)
            
            self.logger.info(f"MTL architecture designed: {architecture_id} "
                           f"({total_params:,} parameters)")
            
            return mtl_architecture
            
        except Exception as e:
            self.logger.error(f"Error designing MTL architecture: {e}")
            raise
    
    async def train_multi_task_model(
        self,
        architecture_id: str,
        training_data: Dict[str, Any],
        training_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Train multi-task model with adaptive balancing."""
        try:
            if architecture_id not in self.mtl_architectures:
                raise ValueError(f"Architecture not found: {architecture_id}")
            
            architecture = self.mtl_architectures[architecture_id]
            config = training_config or {}
            
            # Initialize training state
            training_state = {
                "epoch": 0,
                "task_losses": {task_id: [] for task_id in architecture.task_specific_heads.keys()},
                "task_weights": self.task_weights.copy(),
                "gradient_norms": {},
                "performance_metrics": {},
                "adaptation_history": []
            }
            
            max_epochs = config.get("max_epochs", 100)
            
            # Training loop simulation
            for epoch in range(max_epochs):
                training_state["epoch"] = epoch
                
                # Simulate forward pass and loss calculation
                epoch_losses = await self._simulate_epoch_training(
                    architecture, training_data, training_state
                )
                
                # Update task losses
                for task_id, loss in epoch_losses.items():
                    training_state["task_losses"][task_id].append(loss)
                
                # Adaptive task weighting
                if self.config.get("adaptive_weighting", True):
                    new_weights = await self._update_task_weights(
                        training_state, epoch
                    )
                    training_state["task_weights"] = new_weights
                
                # Gradient balancing
                if self.config.get("gradient_balancing", True):
                    gradient_analysis = await self._analyze_gradient_conflicts(
                        training_state
                    )
                    training_state["gradient_norms"] = gradient_analysis
                
                # Performance monitoring
                if epoch % 10 == 0:
                    performance_metrics = await self._evaluate_multi_task_performance(
                        architecture, training_data, epoch
                    )
                    training_state["performance_metrics"][epoch] = performance_metrics
                
                # Architecture adaptation
                if (self.config.get("architecture_adaptation", True) and 
                    epoch > 0 and epoch % 25 == 0):
                    adaptation_result = await self._adapt_architecture(
                        architecture, training_state
                    )
                    training_state["adaptation_history"].append(adaptation_result)
                
                # Early stopping check
                if await self._check_early_stopping(training_state, config):
                    self.logger.info(f"Early stopping at epoch {epoch}")
                    break
            
            # Final evaluation
            final_metrics = await self._final_multi_task_evaluation(
                architecture, training_data
            )
            
            # Training summary
            training_result = {
                "architecture_id": architecture_id,
                "training_completed": True,
                "final_epoch": training_state["epoch"],
                "final_metrics": final_metrics,
                "task_convergence": await self._analyze_task_convergence(training_state),
                "sharing_effectiveness": await self._evaluate_sharing_effectiveness(
                    architecture, training_state
                ),
                "training_state": training_state,
                "model_saved_path": f"models/{architecture_id}_final.pkl"
            }
            
            # Save training results
            await self._save_training_results(training_result)
            
            self.logger.info(f"Multi-task training completed: {architecture_id}")
            return training_result
            
        except Exception as e:
            self.logger.error(f"Error training multi-task model: {e}")
            raise
    
    async def analyze_task_interference(
        self,
        architecture_id: str,
        task_combinations: List[Tuple[str, str]] = None
    ) -> Dict[str, Any]:
        """Analyze task interference and synergy effects."""
        try:
            if architecture_id not in self.mtl_architectures:
                raise ValueError(f"Architecture not found: {architecture_id}")
            
            architecture = self.mtl_architectures[architecture_id]
            task_ids = list(architecture.task_specific_heads.keys())
            
            # Define task combinations to analyze
            if task_combinations is None:
                from itertools import combinations
                task_combinations = list(combinations(task_ids, 2))
            
            interference_analysis = {
                "architecture_id": architecture_id,
                "task_pairs": {},
                "overall_interference": 0.0,
                "synergy_score": 0.0,
                "recommendations": []
            }
            
            total_interference = 0.0
            total_synergy = 0.0
            
            for task_a, task_b in task_combinations:
                # Simulate task interference analysis
                pair_analysis = await self._analyze_task_pair_interference(
                    task_a, task_b, architecture
                )
                
                interference_analysis["task_pairs"][f"{task_a}_{task_b}"] = pair_analysis
                total_interference += pair_analysis["interference_score"]
                total_synergy += pair_analysis["synergy_score"]
            
            # Calculate overall scores
            num_pairs = len(task_combinations)
            interference_analysis["overall_interference"] = total_interference / num_pairs
            interference_analysis["synergy_score"] = total_synergy / num_pairs
            
            # Generate recommendations
            recommendations = await self._generate_interference_recommendations(
                interference_analysis
            )
            interference_analysis["recommendations"] = recommendations
            
            self.logger.info(f"Task interference analysis completed: {architecture_id}")
            return interference_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing task interference: {e}")
            raise
    
    async def _analyze_sharing_opportunities(
        self,
        task_suite: List[TaskDefinition]
    ) -> Dict[str, Any]:
        """Analyze opportunities for parameter sharing between tasks."""
        sharing_analysis = {
            "modality_overlap": {},
            "domain_similarity": {},
            "task_type_compatibility": {},
            "recommended_sharing": {}
        }
        
        # Analyze modality overlap
        modality_groups = {}
        for task in task_suite:
            for modality in task.input_modalities:
                if modality not in modality_groups:
                    modality_groups[modality] = []
                modality_groups[modality].append(task.task_id)
        
        sharing_analysis["modality_overlap"] = modality_groups
        
        # Domain similarity analysis
        domain_groups = {}
        for task in task_suite:
            domain = task.domain
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(task.task_id)
        
        sharing_analysis["domain_similarity"] = domain_groups
        
        # Task type compatibility
        type_groups = {}
        for task in task_suite:
            task_type = task.task_type
            if task_type not in type_groups:
                type_groups[task_type] = []
            type_groups[task_type].append(task.task_id)
        
        sharing_analysis["task_type_compatibility"] = type_groups
        
        # Generate sharing recommendations
        sharing_recommendations = {}
        for modality, task_ids in modality_groups.items():
            if len(task_ids) > 1:
                sharing_recommendations[f"{modality}_encoder"] = {
                    "tasks": task_ids,
                    "sharing_type": "backbone",
                    "confidence": 0.8
                }
        
        sharing_analysis["recommended_sharing"] = sharing_recommendations
        
        return sharing_analysis
    
    def _determine_output_shape(self, template: Dict[str, Any]) -> Tuple[int, ...]:
        """Determine output shape based on task template."""
        task_type = template["type"]
        
        if task_type == "classification":
            # Assume multi-class classification
            return (10,)  # 10 classes default
        elif task_type == "regression":
            return (1,)  # Single regression output
        elif task_type == "ranking":
            return (100,)  # Ranking scores for 100 items
        else:
            return (10,)  # Default
    
    def _select_loss_function(self, task_type: str) -> str:
        """Select appropriate loss function for task type."""
        loss_mapping = {
            "classification": "categorical_crossentropy",
            "regression": "mse",
            "ranking": "ranking_loss",
            "generation": "sequence_loss"
        }
        return loss_mapping.get(task_type, "mse")
    
    def _calculate_initial_weight(self, priority: str) -> float:
        """Calculate initial task weight based on priority."""
        weight_mapping = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.5
        }
        return weight_mapping.get(priority, 0.7)

# Example usage and testing
async def main() -> None:
    """Example usage of MultiTaskLearningFramework."""
    mtl_framework = MultiTaskLearningFramework()
    
    # Define task suite for musician domain
    task_suite = await mtl_framework.define_task_suite("musician")
    
    print(f"Task suite defined with {len(task_suite)} tasks:")
    for task in task_suite:
        print(f"- {task.task_name} ({task.task_type}) - Priority: {task.priority}")
    
    # Design MTL architecture
    architecture = await mtl_framework.design_mtl_architecture(
        task_suite,
        {"max_parameters": 50000000, "target_latency_ms": 200}
    )
    
    print(f"\nMTL Architecture designed:")
    print(f"- Architecture ID: {architecture.architecture_id}")
    print(f"- Sharing pattern: {architecture.sharing_pattern}")
    print(f"- Total parameters: {architecture.total_parameters:,}")
    print(f"- Shared layers: {len(architecture.shared_layers)}")
    
    # Simulate training
    training_data = {
        "audio_samples": 10000,
        "text_samples": 8000,
        "metadata_samples": 12000
    }
    
    training_config = {
        "max_epochs": 50,
        "early_stopping_patience": 10,
        "adaptive_weighting": True
    }
    
    training_result = await mtl_framework.train_multi_task_model(
        architecture.architecture_id,
        training_data,
        training_config
    )
    
    print(f"\nTraining completed:")
    print(f"- Final epoch: {training_result['final_epoch']}")
    print(f"- Sharing effectiveness: {training_result['sharing_effectiveness']:.3f}")
    
    # Analyze task interference
    interference_analysis = await mtl_framework.analyze_task_interference(
        architecture.architecture_id
    )
    
    print(f"\nTask interference analysis:")
    print(f"- Overall interference: {interference_analysis['overall_interference']:.3f}")
    print(f"- Synergy score: {interference_analysis['synergy_score']:.3f}")
    print(f"- Recommendations: {len(interference_analysis['recommendations'])}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())