"""🧬 Neural Evolution System - Automated Architecture Search
========================================================
Module: ml/experiments/neural_evolution_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 NEURAL EVOLUTION & ARCHITECTURE SEARCH
Neural evolution research for automated model architecture design
- Genetic algorithm-based architecture search
- Evolutionary neural architecture optimization
- Multi-objective evolution (accuracy vs efficiency)
- Population-based training strategies
"""

import asyncio
import logging
import json
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, precision_score
from copy import deepcopy

logger = logging.getLogger(__name__)

class LayerType(Enum):
    """Neural network layer types"""
    DENSE = "dense"
    CONV2D = "conv2d"
    CONV1D = "conv1d"
    LSTM = "lstm"
    GRU = "gru"
    ATTENTION = "attention"
    DROPOUT = "dropout"
    BATCH_NORM = "batch_norm"
    ACTIVATION = "activation"
    POOLING = "pooling"

class ActivationType(Enum):
    """Activation function types"""
    RELU = "relu"
    TANH = "tanh"
    SIGMOID = "sigmoid"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    SWISH = "swish"
    GELU = "gelu"

class OptimizationType(Enum):
    """Optimization objectives"""
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    MULTI_OBJECTIVE = "multi_objective"
    PARETO_OPTIMAL = "pareto_optimal"

@dataclass
class LayerGenome:
    """Genetic representation of a neural network layer"""
    layer_type: LayerType
    parameters: Dict[str, Any]
    activation: Optional[ActivationType] = None
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    
    def mutate(self, mutation_rate: float = 0.1) -> 'LayerGenome':
        """Mutate layer parameters"""
        new_genome = deepcopy(self)
        
        if random.random() < mutation_rate:
            # Mutate layer type occasionally
            if random.random() < 0.1:
                compatible_types = self._get_compatible_layer_types()
                if compatible_types:
                    new_genome.layer_type = random.choice(compatible_types)
            
            # Mutate parameters
            for param, value in new_genome.parameters.items():
                if isinstance(value, int):
                    new_genome.parameters[param] = max(1, value + random.randint(-value//4, value//4))
                elif isinstance(value, float):
                    new_genome.parameters[param] = max(0.0, value * random.uniform(0.8, 1.2))
            
            # Mutate activation
            if random.random() < 0.3:
                new_genome.activation = random.choice(list(ActivationType))
        
        return new_genome
    
    def _get_compatible_layer_types(self) -> List[LayerType]:
        """Get compatible layer types for mutation"""
        if self.layer_type in [LayerType.DENSE, LayerType.DROPOUT]:
            return [LayerType.DENSE, LayerType.DROPOUT]
        elif self.layer_type in [LayerType.CONV2D, LayerType.CONV1D]:
            return [LayerType.CONV2D, LayerType.CONV1D]
        else:
            return [self.layer_type]

@dataclass
class NetworkGenome:
    """Genetic representation of entire neural network"""
    genome_id: str
    layers: List[LayerGenome]
    optimizer_config: Dict[str, Any]
    fitness_score: float = 0.0
    accuracy: float = 0.0
    efficiency_score: float = 0.0
    parameter_count: int = 0
    training_time: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    
    def mutate(self, mutation_rate: float = 0.15) -> 'NetworkGenome':
        """Mutate entire network architecture"""
        new_genome = deepcopy(self)
        new_genome.genome_id = f"mutated_{self.genome_id}_{random.randint(1000, 9999)}"
        new_genome.parent_ids = [self.genome_id]
        new_genome.fitness_score = 0.0
        
        # Mutate layers
        new_genome.layers = [layer.mutate(mutation_rate) for layer in self.layers]
        
        # Add/remove layers occasionally
        if random.random() < 0.1:
            if len(new_genome.layers) > 2 and random.random() < 0.5:
                # Remove a layer
                idx = random.randint(1, len(new_genome.layers) - 2)
                new_genome.layers.pop(idx)
            elif len(new_genome.layers) < 10:
                # Add a layer
                idx = random.randint(1, len(new_genome.layers) - 1)
                new_layer = self._generate_random_layer()
                new_genome.layers.insert(idx, new_layer)
        
        # Mutate optimizer configuration
        if random.random() < mutation_rate:
            new_genome.optimizer_config = self._mutate_optimizer_config(new_genome.optimizer_config)
        
        return new_genome
    
    def crossover(self, other: 'NetworkGenome') -> Tuple['NetworkGenome', 'NetworkGenome']:
        """Crossover with another network genome"""
        # Create offspring genomes
        offspring1 = deepcopy(self)
        offspring2 = deepcopy(other)
        
        offspring1.genome_id = f"cross_{self.genome_id}_{other.genome_id}_{random.randint(1000, 9999)}_1"
        offspring2.genome_id = f"cross_{self.genome_id}_{other.genome_id}_{random.randint(1000, 9999)}_2"
        
        offspring1.parent_ids = [self.genome_id, other.genome_id]
        offspring2.parent_ids = [self.genome_id, other.genome_id]
        
        # Layer crossover
        min_layers = min(len(self.layers), len(other.layers))
        crossover_point = random.randint(1, min_layers - 1)
        
        offspring1.layers = self.layers[:crossover_point] + other.layers[crossover_point:min_layers]
        offspring2.layers = other.layers[:crossover_point] + self.layers[crossover_point:min_layers]
        
        # Handle different layer counts
        if len(self.layers) != len(other.layers):
            longer_parent = self if len(self.layers) > len(other.layers) else other
            extra_layers = longer_parent.layers[min_layers:]
            
            if random.random() < 0.5:
                offspring1.layers.extend(extra_layers)
            else:
                offspring2.layers.extend(extra_layers)
        
        # Optimizer crossover
        offspring1.optimizer_config = self._crossover_optimizer_config(
            self.optimizer_config, other.optimizer_config
        )
        offspring2.optimizer_config = self._crossover_optimizer_config(
            other.optimizer_config, self.optimizer_config
        )
        
        # Reset fitness scores
        offspring1.fitness_score = 0.0
        offspring2.fitness_score = 0.0
        
        return offspring1, offspring2
    
    def _generate_random_layer(self) -> LayerGenome:
        """Generate a random layer for mutation"""
        layer_type = random.choice(list(LayerType))
        
        if layer_type == LayerType.DENSE:
            parameters = {"units": random.randint(32, 512)}
        elif layer_type == LayerType.CONV2D:
            parameters = {
                "filters": random.randint(16, 256),
                "kernel_size": random.choice([3, 5, 7]),
                "stride": random.choice([1, 2])
            }
        elif layer_type == LayerType.DROPOUT:
            parameters = {"rate": random.uniform(0.1, 0.5)}
        else:
            parameters = {}
        
        return LayerGenome(
            layer_type=layer_type,
            parameters=parameters,
            activation=random.choice(list(ActivationType))
        )
    
    def _mutate_optimizer_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutate optimizer configuration"""
        new_config = deepcopy(config)
        
        if 'learning_rate' in new_config:
            new_config['learning_rate'] *= random.uniform(0.5, 2.0)
            new_config['learning_rate'] = max(1e-6, min(0.1, new_config['learning_rate']))
        
        if 'weight_decay' in new_config:
            new_config['weight_decay'] *= random.uniform(0.5, 2.0)
            new_config['weight_decay'] = max(0.0, min(0.01, new_config['weight_decay']))
        
        return new_config
    
    def _crossover_optimizer_config(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
        """Crossover optimizer configurations"""
        new_config = {}
        
        for key in set(config1.keys()) | set(config2.keys()):
            if key in config1 and key in config2:
                # Average numerical values
                if isinstance(config1[key], (int, float)) and isinstance(config2[key], (int, float)):
                    new_config[key] = (config1[key] + config2[key]) / 2
                else:
                    new_config[key] = random.choice([config1[key], config2[key]])
            elif key in config1:
                new_config[key] = config1[key]
            else:
                new_config[key] = config2[key]
        
        return new_config

class PytorchNetworkBuilder:
    """Build PyTorch networks from genomes"""
    
    @staticmethod
    def build_network(genome: NetworkGenome, input_size: int, output_size: int) -> nn.Module:
        """Build PyTorch network from genome"""
        layers = []
        current_size = input_size
        
        for i, layer_genome in enumerate(genome.layers):
            layer = PytorchNetworkBuilder._build_layer(layer_genome, current_size, output_size)
            
            if layer is not None:
                layers.append(layer)
                
                # Update current size for next layer
                if hasattr(layer, 'out_features'):
                    current_size = layer.out_features
                elif hasattr(layer, 'out_channels'):
                    current_size = layer.out_channels
            
            # Add activation if specified
            if layer_genome.activation:
                activation = PytorchNetworkBuilder._get_activation(layer_genome.activation)
                if activation:
                    layers.append(activation)
        
        # Ensure final output layer
        if layers and not hasattr(layers[-1], 'out_features'):
            layers.append(nn.Linear(current_size, output_size))
        elif not layers:
            layers.append(nn.Linear(input_size, output_size))
        
        return nn.Sequential(*layers)
    
    @staticmethod
    def _build_layer(layer_genome: LayerGenome, input_size: int, output_size: int) -> Optional[nn.Module]:
        """Build individual layer from genome"""
        layer_type = layer_genome.layer_type
        params = layer_genome.parameters
        
        if layer_type == LayerType.DENSE:
            units = params.get('units', 64)
            return nn.Linear(input_size, units)
        
        elif layer_type == LayerType.DROPOUT:
            rate = params.get('rate', 0.2)
            return nn.Dropout(rate)
        
        elif layer_type == LayerType.BATCH_NORM:
            return nn.BatchNorm1d(input_size)
        
        elif layer_type == LayerType.CONV2D:
            # Simplified for demonstration
            filters = params.get('filters', 32)
            kernel_size = params.get('kernel_size', 3)
            return nn.Conv2d(input_size, filters, kernel_size)
        
        # Add more layer types as needed
        return None
    
    @staticmethod
    def _get_activation(activation_type: ActivationType) -> Optional[nn.Module]:
        """Get activation function"""
        activation_map = {
            ActivationType.RELU: nn.ReLU(),
            ActivationType.TANH: nn.Tanh(),
            ActivationType.SIGMOID: nn.Sigmoid(),
            ActivationType.LEAKY_RELU: nn.LeakyReLU(),
            ActivationType.ELU: nn.ELU(),
            ActivationType.GELU: nn.GELU()
        }
        return activation_map.get(activation_type)

class FitnessEvaluator:
    """Evaluate fitness of neural network genomes"""
    
    def __init__(self, optimization_type -> None: OptimizationType = OptimizationType.MULTI_OBJECTIVE) -> None:
        self.optimization_type = optimization_type
        self.accuracy_weight = 0.7
        self.efficiency_weight = 0.3
    
    async def evaluate_genome(
        self,
        genome: NetworkGenome,
        train_data: torch.Tensor,
        train_labels: torch.Tensor,
        val_data: torch.Tensor,
        val_labels: torch.Tensor,
        epochs: int = 5
    ) -> NetworkGenome:
        """Evaluate a single genome's fitness"""
        try:
            # Build network
            input_size = train_data.shape[1]
            output_size = len(torch.unique(train_labels))
            
            network = PytorchNetworkBuilder.build_network(genome, input_size, output_size)
            
            # Count parameters
            genome.parameter_count = sum(p.numel() for p in network.parameters())
            
            # Train and evaluate
            start_time = datetime.utcnow()
            accuracy = await self._train_and_evaluate(
                network, train_data, train_labels, val_data, val_labels, 
                genome.optimizer_config, epochs
            )
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(
                genome.parameter_count, training_time, accuracy
            )
            
            # Update genome
            genome.accuracy = accuracy
            genome.efficiency_score = efficiency_score
            genome.training_time = training_time
            genome.fitness_score = self._calculate_fitness(accuracy, efficiency_score)
            
            logger.info(f"Genome {genome.genome_id}: Accuracy={accuracy:.4f}, Fitness={genome.fitness_score:.4f}")
            return genome
            
        except Exception as e:
            logger.error(f"Failed to evaluate genome {genome.genome_id}: {e}")
            genome.fitness_score = 0.0
            return genome
    
    async def _train_and_evaluate(
        self,
        network: nn.Module,
        train_data: torch.Tensor,
        train_labels: torch.Tensor,
        val_data: torch.Tensor,
        val_labels: torch.Tensor,
        optimizer_config: Dict[str, Any],
        epochs: int
    ) -> float:
        """Train network and return validation accuracy"""
        try:
            # Setup training
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(
                network.parameters(),
                lr=optimizer_config.get('learning_rate', 0.001),
                weight_decay=optimizer_config.get('weight_decay', 0.0001)
            )
            
            # Training loop
            network.train()
            for epoch in range(epochs):
                optimizer.zero_grad()
                outputs = network(train_data.float())
                loss = criterion(outputs, train_labels.long())
                loss.backward()
                optimizer.step()
            
            # Evaluation
            network.eval()
            with torch.no_grad():
                val_outputs = network(val_data.float())
                _, predicted = torch.max(val_outputs.data, 1)
                accuracy = (predicted == val_labels.long()).float().mean().item()
            
            return accuracy
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return 0.0
    
    def _calculate_efficiency_score(self, param_count: int, training_time: float, accuracy: float) -> float:
        """Calculate efficiency score based on parameters and training time"""
        # Normalize metrics
        param_penalty = 1.0 / (1.0 + param_count / 1000000)  # Penalty for large models
        time_penalty = 1.0 / (1.0 + training_time / 60)      # Penalty for long training
        accuracy_bonus = accuracy                              # Bonus for good accuracy
        
        efficiency_score = (param_penalty + time_penalty + accuracy_bonus) / 3
        return min(1.0, max(0.0, efficiency_score))
    
    def _calculate_fitness(self, accuracy: float, efficiency_score: float) -> float:
        """Calculate overall fitness score"""
        if self.optimization_type == OptimizationType.ACCURACY:
            return accuracy
        elif self.optimization_type == OptimizationType.EFFICIENCY:
            return efficiency_score
        else:  # Multi-objective
            return self.accuracy_weight * accuracy + self.efficiency_weight * efficiency_score

class NeuralEvolutionSystem:
    """Main neural evolution system"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.population_size = self.config.get('population_size', 20)
        self.generations = self.config.get('generations', 10)
        self.mutation_rate = self.config.get('mutation_rate', 0.15)
        self.crossover_rate = self.config.get('crossover_rate', 0.7)
        self.elite_size = self.config.get('elite_size', 3)
        
        self.populations: Dict[int, List[NetworkGenome]] = {}
        self.evolution_history: List[Dict[str, Any]] = []
        self.best_genomes: List[NetworkGenome] = []
        
        self.fitness_evaluator = FitnessEvaluator(
            OptimizationType[self.config.get('optimization_type', 'MULTI_OBJECTIVE')]
        )
        
        logger.info(f"Neural Evolution System initialized: {self.population_size} population")
    
    def _create_initial_population(self, input_size: int, output_size: int) -> List[NetworkGenome]:
        """Create initial random population"""
        population = []
        
        for i in range(self.population_size):
            genome_id = f"gen0_individual_{i}"
            
            # Random architecture
            num_layers = random.randint(2, 6)
            layers = []
            
            for j in range(num_layers):
                if j == 0:  # Input layer
                    layer_type = LayerType.DENSE
                    parameters = {"units": random.randint(32, 256)}
                elif j == num_layers - 1:  # Output layer
                    layer_type = LayerType.DENSE
                    parameters = {"units": output_size}
                else:  # Hidden layers
                    layer_type = random.choice([LayerType.DENSE, LayerType.DROPOUT, LayerType.BATCH_NORM])
                    if layer_type == LayerType.DENSE:
                        parameters = {"units": random.randint(32, 512)}
                    elif layer_type == LayerType.DROPOUT:
                        parameters = {"rate": random.uniform(0.1, 0.5)}
                    else:
                        parameters = {}
                
                layer = LayerGenome(
                    layer_type=layer_type,
                    parameters=parameters,
                    activation=random.choice(list(ActivationType)) if j < num_layers - 1 else None
                )
                layers.append(layer)
            
            # Random optimizer config
            optimizer_config = {
                'learning_rate': random.uniform(0.0001, 0.01),
                'weight_decay': random.uniform(0.0001, 0.001)
            }
            
            genome = NetworkGenome(
                genome_id=genome_id,
                layers=layers,
                optimizer_config=optimizer_config,
                generation=0
            )
            
            population.append(genome)
        
        return population
    
    async def evolve_architecture(
        self,
        train_data: np.ndarray,
        train_labels: np.ndarray,
        val_data: np.ndarray,
        val_labels: np.ndarray
    ) -> Dict[str, Any]:
        """Main evolution loop"""
        try:
            # Convert to PyTorch tensors
            train_tensor = torch.from_numpy(train_data)
            train_labels_tensor = torch.from_numpy(train_labels)
            val_tensor = torch.from_numpy(val_data)
            val_labels_tensor = torch.from_numpy(val_labels)
            
            input_size = train_data.shape[1]
            output_size = len(np.unique(train_labels))
            
            # Create initial population
            population = self._create_initial_population(input_size, output_size)
            
            logger.info(f"Starting evolution: {self.generations} generations, {self.population_size} individuals")
            
            # Evolution loop
            for generation in range(self.generations):
                logger.info(f"Generation {generation + 1}/{self.generations}")
                
                # Evaluate population
                population = await self._evaluate_population(
                    population, train_tensor, train_labels_tensor, 
                    val_tensor, val_labels_tensor
                )
                
                # Store population
                self.populations[generation] = deepcopy(population)
                
                # Track best genome
                best_genome = max(population, key=lambda g: g.fitness_score)
                self.best_genomes.append(deepcopy(best_genome))
                
                # Evolution statistics
                fitness_scores = [g.fitness_score for g in population]
                generation_stats = {
                    'generation': generation,
                    'best_fitness': max(fitness_scores),
                    'average_fitness': np.mean(fitness_scores),
                    'worst_fitness': min(fitness_scores),
                    'best_accuracy': best_genome.accuracy,
                    'best_efficiency': best_genome.efficiency_score,
                    'best_parameters': best_genome.parameter_count
                }
                self.evolution_history.append(generation_stats)
                
                logger.info(f"Gen {generation}: Best fitness={generation_stats['best_fitness']:.4f}, "
                           f"Accuracy={generation_stats['best_accuracy']:.4f}")
                
                # Create next generation (if not final generation)
                if generation < self.generations - 1:
                    population = await self._create_next_generation(population)
            
            # Return results
            final_best = max(self.best_genomes, key=lambda g: g.fitness_score)
            
            return {
                'best_genome': final_best,
                'evolution_history': self.evolution_history,
                'final_population': self.populations[self.generations - 1],
                'summary': {
                    'generations_completed': self.generations,
                    'best_fitness': final_best.fitness_score,
                    'best_accuracy': final_best.accuracy,
                    'best_efficiency': final_best.efficiency_score,
                    'parameter_count': final_best.parameter_count,
                    'convergence_generation': self._find_convergence_generation()
                }
            }
            
        except Exception as e:
            logger.error(f"Evolution failed: {e}")
            raise
    
    async def _evaluate_population(
        self,
        population: List[NetworkGenome],
        train_data: torch.Tensor,
        train_labels: torch.Tensor,
        val_data: torch.Tensor,
        val_labels: torch.Tensor
    ) -> List[NetworkGenome]:
        """Evaluate entire population"""
        evaluated_population = []
        
        # Evaluate each genome
        for genome in population:
            evaluated_genome = await self.fitness_evaluator.evaluate_genome(
                genome, train_data, train_labels, val_data, val_labels
            )
            evaluated_population.append(evaluated_genome)
        
        return evaluated_population
    
    async def _create_next_generation(self, population: List[NetworkGenome]) -> List[NetworkGenome]:
        """Create next generation through selection, crossover, and mutation"""
        # Sort by fitness
        population.sort(key=lambda g: g.fitness_score, reverse=True)
        
        next_generation = []
        
        # Elite selection
        elites = population[:self.elite_size]
        for elite in elites:
            elite_copy = deepcopy(elite)
            elite_copy.generation += 1
            next_generation.append(elite_copy)
        
        # Generate offspring
        while len(next_generation) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_selection(population)
            parent2 = self._tournament_selection(population)
            
            # Crossover
            if random.random() < self.crossover_rate:
                offspring1, offspring2 = parent1.crossover(parent2)
            else:
                offspring1, offspring2 = deepcopy(parent1), deepcopy(parent2)
            
            # Mutation
            offspring1 = offspring1.mutate(self.mutation_rate)
            offspring2 = offspring2.mutate(self.mutation_rate)
            
            # Update generation
            offspring1.generation = population[0].generation + 1
            offspring2.generation = population[0].generation + 1
            
            next_generation.extend([offspring1, offspring2])
        
        # Trim to population size
        return next_generation[:self.population_size]
    
    def _tournament_selection(self, population: List[NetworkGenome], tournament_size: int = 3) -> NetworkGenome:
        """Tournament selection for parent selection"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda g: g.fitness_score)
    
    def _find_convergence_generation(self) -> int:
        """Find generation where algorithm converged"""
        if len(self.evolution_history) < 3:
            return len(self.evolution_history)
        
        # Look for plateau in best fitness
        for i in range(2, len(self.evolution_history)):
            recent_improvements = [
                self.evolution_history[j]['best_fitness'] - self.evolution_history[j-1]['best_fitness']
                for j in range(max(0, i-3), i)
            ]
            
            if all(improvement < 0.001 for improvement in recent_improvements):
                return i
        
        return len(self.evolution_history)
    
    async def analyze_evolution_results(self) -> Dict[str, Any]:
        """Analyze evolution results and provide insights"""
        try:
            if not self.evolution_history:
                return {"error": "No evolution history available"}
            
            # Fitness progression analysis
            fitness_progression = [gen['best_fitness'] for gen in self.evolution_history]
            accuracy_progression = [gen['best_accuracy'] for gen in self.evolution_history]
            
            # Architecture diversity analysis
            final_population = self.populations.get(self.generations - 1, [])
            layer_counts = [len(genome.layers) for genome in final_population]
            parameter_counts = [genome.parameter_count for genome in final_population]
            
            # Convergence analysis
            convergence_gen = self._find_convergence_generation()
            
            # Calculate architecture diversity without hashing LayerGenome objects
            unique_architectures = set()
            for genome in final_population:
                # Create a hashable representation of the architecture
                arch_signature = tuple(
                    (layer.layer_type.value, str(layer.parameters), layer.activation.value if layer.activation else None)
                    for layer in genome.layers
                )
                unique_architectures.add(arch_signature)
            
            architecture_diversity = len(unique_architectures) / len(final_population) if final_population else 0
            
            analysis = {
                'fitness_analysis': {
                    'initial_fitness': fitness_progression[0],
                    'final_fitness': fitness_progression[-1],
                    'improvement': fitness_progression[-1] - fitness_progression[0],
                    'convergence_generation': convergence_gen,
                    'fitness_progression': fitness_progression
                },
                'accuracy_analysis': {
                    'initial_accuracy': accuracy_progression[0],
                    'final_accuracy': accuracy_progression[-1],
                    'accuracy_improvement': accuracy_progression[-1] - accuracy_progression[0],
                    'accuracy_progression': accuracy_progression
                },
                'diversity_analysis': {
                    'layer_count_range': [min(layer_counts), max(layer_counts)] if layer_counts else [0, 0],
                    'parameter_count_range': [min(parameter_counts), max(parameter_counts)] if parameter_counts else [0, 0],
                    'architecture_diversity': architecture_diversity
                },
                'best_architecture': self._analyze_best_architecture(),
                'insights': self._generate_evolution_insights()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Evolution analysis failed: {e}")
            raise
    
    def _analyze_best_architecture(self) -> Dict[str, Any]:
        """Analyze the best evolved architecture"""
        if not self.best_genomes:
            return {}
        
        best_genome = max(self.best_genomes, key=lambda g: g.fitness_score)
        
        return {
            'genome_id': best_genome.genome_id,
            'layer_count': len(best_genome.layers),
            'parameter_count': best_genome.parameter_count,
            'layer_types': [layer.layer_type.value for layer in best_genome.layers],
            'activations': [layer.activation.value if layer.activation else None for layer in best_genome.layers],
            'optimizer_config': best_genome.optimizer_config,
            'performance': {
                'fitness': best_genome.fitness_score,
                'accuracy': best_genome.accuracy,
                'efficiency': best_genome.efficiency_score,
                'training_time': best_genome.training_time
            }
        }
    
    def _generate_evolution_insights(self) -> List[str]:
        """Generate insights from evolution process"""
        insights = []
        
        if self.evolution_history:
            final_improvement = (self.evolution_history[-1]['best_fitness'] - 
                                self.evolution_history[0]['best_fitness'])
            
            if final_improvement > 0.1:
                insights.append("Significant fitness improvement achieved through evolution")
            elif final_improvement > 0.01:
                insights.append("Moderate fitness improvement observed")
            else:
                insights.append("Limited fitness improvement - consider different parameters")
            
            convergence_gen = self._find_convergence_generation()
            if convergence_gen < self.generations * 0.5:
                insights.append("Early convergence detected - increase diversity or mutation rate")
            
            if self.best_genomes:
                best_genome = max(self.best_genomes, key=lambda g: g.fitness_score)
                if best_genome.parameter_count > 1000000:
                    insights.append("Best architecture is parameter-heavy - consider efficiency constraints")
                
                if len(best_genome.layers) > 8:
                    insights.append("Deep architecture evolved - monitor for overfitting")
        
        insights.append("Consider ensemble methods with top-performing architectures")
        insights.append("Fine-tune hyperparameters of best architecture")
        
        return insights

# Example usage and testing
async def main() -> None:
    """Test neural evolution system"""
    try:
        # Initialize evolution system
        config = {
            'population_size': 10,
            'generations': 5,
            'mutation_rate': 0.2,
            'optimization_type': 'MULTI_OBJECTIVE'
        }
        
        evolution_system = NeuralEvolutionSystem(config)
        
        # Generate synthetic dataset
        np.random.seed(42)
        n_samples = 200
        n_features = 10
        n_classes = 3
        
        train_data = np.random.randn(n_samples, n_features)
        train_labels = np.random.randint(0, n_classes, n_samples)
        
        val_data = np.random.randn(n_samples // 4, n_features)
        val_labels = np.random.randint(0, n_classes, n_samples // 4)
        
        # Evolve architecture
        results = await evolution_system.evolve_architecture(
            train_data, train_labels, val_data, val_labels
        )
        
        print(f"Evolution completed: {results['summary']['generations_completed']} generations")
        print(f"Best fitness: {results['summary']['best_fitness']:.4f}")
        print(f"Best accuracy: {results['summary']['best_accuracy']:.4f}")
        
        # Analyze results
        analysis = await evolution_system.analyze_evolution_results()
        print(f"Fitness improvement: {analysis['fitness_analysis']['improvement']:.4f}")
        print(f"Architecture diversity: {analysis['diversity_analysis']['architecture_diversity']:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Neural evolution test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())