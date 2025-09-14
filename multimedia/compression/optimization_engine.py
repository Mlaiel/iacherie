"""Compression Optimization Engine
Advanced optimization algorithms for multimedia compression efficiency.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class OptimizationTarget:
    """Optimization target specification."""
    target_size: Optional[int] = None  # Target file size in bytes
    target_quality: Optional[float] = None  # Target quality score (0-1)
    max_processing_time: Optional[float] = None  # Max processing time in seconds
    priority: str = "balanced"  # size, quality, speed, balanced

class CompressionOptimizationEngine:
    """Advanced optimization engine for compression parameters."""
    
    def __init__(self) -> None:
        """Initialize the optimization engine."""
        self.optimization_algorithms = {
            "genetic": self._genetic_algorithm,
            "hill_climbing": self._hill_climbing,
            "simulated_annealing": self._simulated_annealing,
            "grid_search": self._grid_search
        }
        
    async def optimize_compression(
        self,
        input_path: Union[str, Path],
        media_type: str,
        target: OptimizationTarget,
        algorithm: str = "genetic",
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Optimize compression parameters for specific targets.
        
        Args:
            input_path: Path to input file
            media_type: Type of media (audio, video, image)
            target: Optimization target specification
            algorithm: Optimization algorithm to use
            max_iterations: Maximum optimization iterations
            
        Returns:
            Optimized compression parameters and results
        """
        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Get file information
            file_info = await self._analyze_file(input_path, media_type)
            
            # Select optimization algorithm
            optimizer = self.optimization_algorithms.get(algorithm)
            if not optimizer:
                raise ValueError(f"Unknown optimization algorithm: {algorithm}")
            
            # Run optimization
            result = await optimizer(
                file_info, media_type, target, max_iterations
            )
            
            return {
                "success": True,
                "algorithm": algorithm,
                "iterations": result["iterations"],
                "optimal_parameters": result["best_params"],
                "predicted_metrics": result["best_metrics"],
                "optimization_history": result["history"]
            }
            
        except Exception as e:
            logger.error(f"Compression optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_file(
        self,
        input_path: Path,
        media_type: str
    ) -> Dict[str, Any]:
        """Analyze input file characteristics."""
        # Simulate file analysis
        await asyncio.sleep(0.05)
        
        file_size = input_path.stat().st_size
        
        if media_type == "image":
            return {
                "size": file_size,
                "width": 1920,
                "height": 1080,
                "channels": 3,
                "format": "jpeg",
                "complexity": np.random.uniform(0.3, 0.9)
            }
        elif media_type == "video":
            return {
                "size": file_size,
                "duration": 120,  # seconds
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "bitrate": 10000,
                "complexity": np.random.uniform(0.4, 0.8)
            }
        elif media_type == "audio":
            return {
                "size": file_size,
                "duration": 180,  # seconds
                "sample_rate": 44100,
                "channels": 2,
                "bitrate": 1411,
                "complexity": np.random.uniform(0.2, 0.7)
            }
        else:
            return {"size": file_size, "complexity": 0.5}
    
    async def _genetic_algorithm(
        self,
        file_info: Dict[str, Any],
        media_type: str,
        target: OptimizationTarget,
        max_iterations: int
    ) -> Dict[str, Any]:
        """Genetic algorithm for compression optimization."""
        population_size = 20
        mutation_rate = 0.1
        
        # Initialize population
        population = self._initialize_population(media_type, population_size)
        history = []
        
        best_individual = None
        best_fitness = float('-inf')
        
        for generation in range(max_iterations):
            # Evaluate fitness for each individual
            fitness_scores = []
            for individual in population:
                fitness = await self._evaluate_fitness(
                    individual, file_info, target
                )
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            history.append({
                "generation": generation,
                "best_fitness": best_fitness,
                "average_fitness": np.mean(fitness_scores),
                "best_params": best_individual.copy()
            })
            
            # Selection and reproduction
            new_population = []
            
            # Elitism - keep best individuals
            elite_count = population_size // 5
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Crossover and mutation
            while len(new_population) < population_size:
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                child = self._crossover(parent1, parent2)
                
                if np.random.random() < mutation_rate:
                    child = self._mutate(child, media_type)
                
                new_population.append(child)
            
            population = new_population
        
        # Calculate final metrics for best individual
        best_metrics = await self._calculate_metrics(best_individual, file_info)
        
        return {
            "iterations": max_iterations,
            "best_params": best_individual,
            "best_metrics": best_metrics,
            "best_fitness": best_fitness,
            "history": history
        }
    
    def _initialize_population(
        self,
        media_type: str,
        population_size: int
    ) -> List[Dict[str, Any]]:
        """Initialize population for genetic algorithm."""
        population = []
        
        for _ in range(population_size):
            if media_type == "image":
                individual = {
                    "quality": np.random.randint(60, 95),
                    "progressive": np.random.choice([True, False]),
                    "optimize": np.random.choice([True, False])
                }
            elif media_type == "video":
                individual = {
                    "bitrate": np.random.randint(1000, 15000),
                    "crf": np.random.randint(18, 28),
                    "preset": np.random.choice(["fast", "medium", "slow"]),
                    "tune": np.random.choice(["film", "animation", "fastdecode"])
                }
            elif media_type == "audio":
                individual = {
                    "bitrate": np.random.randint(96, 320),
                    "quality": np.random.choice(["low", "medium", "high"]),
                    "vbr": np.random.choice([True, False])
                }
            
            population.append(individual)
        
        return population
    
    async def _evaluate_fitness(
        self,
        parameters: Dict[str, Any],
        file_info: Dict[str, Any],
        target: OptimizationTarget
    ) -> float:
        """Evaluate fitness of compression parameters."""
        # Simulate compression with these parameters
        metrics = await self._calculate_metrics(parameters, file_info)
        
        fitness = 0.0
        
        # Size fitness
        if target.target_size:
            size_ratio = metrics["size"] / target.target_size
            size_fitness = max(0, 1.0 - abs(1.0 - size_ratio))
            fitness += size_fitness * 0.4
        
        # Quality fitness
        if target.target_quality:
            quality_diff = abs(metrics["quality"] - target.target_quality)
            quality_fitness = max(0, 1.0 - quality_diff)
            fitness += quality_fitness * 0.4
        
        # Processing time fitness
        if target.max_processing_time:
            time_ratio = metrics["processing_time"] / target.max_processing_time
            time_fitness = max(0, 1.0 - max(0, time_ratio - 1.0))
            fitness += time_fitness * 0.2
        
        # Default balanced fitness if no specific targets
        if not any([target.target_size, target.target_quality, target.max_processing_time]):
            fitness = (
                metrics["quality"] * 0.5 +
                (1.0 - metrics["compression_ratio"]) * 0.3 +
                (1.0 - metrics["processing_time"] / 10.0) * 0.2
            )
        
        return fitness
    
    async def _calculate_metrics(
        self,
        parameters: Dict[str, Any],
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate predicted metrics for given parameters."""
        # Simulate compression metrics calculation
        await asyncio.sleep(0.01)
        
        original_size = file_info["size"]
        complexity = file_info.get("complexity", 0.5)
        
        # Estimate compressed size based on parameters
        if "quality" in parameters:
            quality_factor = parameters["quality"] / 100.0
            size_factor = 0.2 + quality_factor * 0.6
        elif "bitrate" in parameters:
            # For video/audio, calculate size from bitrate
            duration = file_info.get("duration", 120)
            size_factor = (parameters["bitrate"] * duration) / (original_size * 8)
        else:
            size_factor = 0.5
        
        # Adjust for complexity
        size_factor *= (0.8 + complexity * 0.4)
        
        compressed_size = int(original_size * size_factor)
        compression_ratio = original_size / compressed_size
        
        # Estimate quality based on compression ratio and parameters
        quality = min(1.0, size_factor + 0.2)
        
        # Estimate processing time
        processing_time = complexity * 2.0
        if parameters.get("preset") == "slow":
            processing_time *= 2.0
        elif parameters.get("preset") == "fast":
            processing_time *= 0.5
        
        return {
            "size": compressed_size,
            "quality": quality,
            "compression_ratio": compression_ratio,
            "processing_time": processing_time
        }
    
    def _tournament_selection(
        self,
        population: List[Dict[str, Any]],
        fitness_scores: List[float],
        tournament_size: int = 3
    ) -> Dict[str, Any]:
        """Tournament selection for genetic algorithm."""
        tournament_indices = np.random.choice(
            len(population), tournament_size, replace=False
        )
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crossover operation for genetic algorithm."""
        child = {}
        for key in parent1.keys():
            if np.random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
    
    def _mutate(
        self,
        individual: Dict[str, Any],
        media_type: str
    ) -> Dict[str, Any]:
        """Mutation operation for genetic algorithm."""
        mutated = individual.copy()
        
        for key, value in mutated.items():
            if np.random.random() < 0.3:  # 30% chance to mutate each parameter
                if isinstance(value, int):
                    # Add random noise to integer parameters
                    if key == "quality":
                        mutated[key] = np.clip(value + np.random.randint(-10, 11), 60, 95)
                    elif key == "bitrate":
                        mutated[key] = max(96, value + np.random.randint(-100, 101))
                    elif key == "crf":
                        mutated[key] = np.clip(value + np.random.randint(-3, 4), 18, 28)
                elif isinstance(value, bool):
                    mutated[key] = not value
                elif isinstance(value, str):
                    # Random choice from valid options
                    if key == "preset":
                        mutated[key] = np.random.choice(["fast", "medium", "slow"])
                    elif key == "quality":
                        mutated[key] = np.random.choice(["low", "medium", "high"])
        
        return mutated
    
    async def _hill_climbing(
        self,
        file_info: Dict[str, Any],
        media_type: str,
        target: OptimizationTarget,
        max_iterations: int
    ) -> Dict[str, Any]:
        """Hill climbing optimization algorithm."""
        # Start with random solution
        current_solution = self._initialize_population(media_type, 1)[0]
        current_fitness = await self._evaluate_fitness(
            current_solution, file_info, target
        )
        
        history = []
        
        for iteration in range(max_iterations):
            # Generate neighbor solutions
            neighbors = self._generate_neighbors(current_solution, media_type)
            
            best_neighbor = None
            best_neighbor_fitness = current_fitness
            
            for neighbor in neighbors:
                fitness = await self._evaluate_fitness(neighbor, file_info, target)
                if fitness > best_neighbor_fitness:
                    best_neighbor = neighbor
                    best_neighbor_fitness = fitness
            
            history.append({
                "iteration": iteration,
                "fitness": current_fitness,
                "params": current_solution.copy()
            })
            
            # Move to best neighbor if better
            if best_neighbor is not None:
                current_solution = best_neighbor
                current_fitness = best_neighbor_fitness
            else:
                # Local optimum reached
                break
        
        best_metrics = await self._calculate_metrics(current_solution, file_info)
        
        return {
            "iterations": len(history),
            "best_params": current_solution,
            "best_metrics": best_metrics,
            "best_fitness": current_fitness,
            "history": history
        }
    
    def _generate_neighbors(
        self,
        solution: Dict[str, Any],
        media_type: str,
        neighbor_count: int = 8
    ) -> List[Dict[str, Any]]:
        """Generate neighbor solutions for hill climbing."""
        neighbors = []
        
        for _ in range(neighbor_count):
            neighbor = solution.copy()
            
            # Randomly modify one parameter
            key = np.random.choice(list(neighbor.keys()))
            value = neighbor[key]
            
            if isinstance(value, int):
                if key == "quality":
                    neighbor[key] = np.clip(value + np.random.randint(-5, 6), 60, 95)
                elif key == "bitrate":
                    neighbor[key] = max(96, value + np.random.randint(-50, 51))
            elif isinstance(value, bool):
                neighbor[key] = not value
            
            neighbors.append(neighbor)
        
        return neighbors
    
    async def find_pareto_optimal(
        self,
        input_path: Union[str, Path],
        media_type: str,
        objectives: List[str] = ["size", "quality", "speed"]
    ) -> List[Dict[str, Any]]:
        """Find Pareto-optimal compression solutions."""
        input_path = Path(input_path)
        file_info = await self._analyze_file(input_path, media_type)
        
        # Generate diverse population
        population = self._initialize_population(media_type, 100)
        
        # Evaluate all objectives for each solution
        evaluated_solutions = []
        for solution in population:
            metrics = await self._calculate_metrics(solution, file_info)
            
            # Convert to minimization objectives
            objectives_values = {
                "size": metrics["size"],
                "quality": 1.0 - metrics["quality"],  # Minimize negative quality
                "speed": metrics["processing_time"]
            }
            
            evaluated_solutions.append({
                "parameters": solution,
                "objectives": objectives_values,
                "metrics": metrics
            })
        
        # Find Pareto frontier
        pareto_solutions = self._find_pareto_frontier(evaluated_solutions, objectives)
        
        return pareto_solutions
    
    def _find_pareto_frontier(
        self,
        solutions: List[Dict[str, Any]],
        objectives: List[str]
    ) -> List[Dict[str, Any]]:
        """Find Pareto-optimal solutions."""
        pareto_solutions = []
        
        for i, solution_a in enumerate(solutions):
            is_dominated = False
            
            for j, solution_b in enumerate(solutions):
                if i == j:
                    continue
                
                # Check if solution_a is dominated by solution_b
                dominates = True
                for objective in objectives:
                    if (solution_a["objectives"][objective] < 
                        solution_b["objectives"][objective]):
                        dominates = False
                        break
                
                if dominates:
                    # Check if at least one objective is strictly better
                    strictly_better = False
                    for objective in objectives:
                        if (solution_a["objectives"][objective] > 
                            solution_b["objectives"][objective]):
                            strictly_better = True
                            break
                    
                    if strictly_better:
                        is_dominated = True
                        break
            
            if not is_dominated:
                pareto_solutions.append(solution_a)
        
        return pareto_solutions