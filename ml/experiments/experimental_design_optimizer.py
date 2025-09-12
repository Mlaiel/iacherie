"""🧬 Experimental Design Optimizer - Enterprise ML Infrastructure
=================================================================
Module: ml/experiments/experimental_design_optimizer.py
Author: Fahed Mlaiel (mlaiel@live.de)
=================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EXPERIMENTAL DESIGN OPTIMIZATION SYSTEM
Optimal experimental design for efficient model development
- Bayesian optimization for hyperparameter tuning
- Multi-objective experiment optimization
- Creator-specific experimental strategies
- Statistical power analysis and sample size optimization
"""

import asyncio
import logging
import time
import uuid
import random
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from itertools import product
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class ExperimentType(Enum):
    """Types of ML experiments"""
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    ARCHITECTURE_SEARCH = "architecture_search"
    FEATURE_SELECTION = "feature_selection"
    ABLATION_STUDY = "ablation_study"
    A_B_TESTING = "a_b_testing"
    MULTI_OBJECTIVE = "multi_objective"
    CREATOR_COMPARISON = "creator_comparison"
    PERFORMANCE_BENCHMARK = "performance_benchmark"


class OptimizationStrategy(Enum):
    """Optimization strategies"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    EVOLUTIONARY = "evolutionary"
    BANDIT_OPTIMIZATION = "bandit_optimization"
    LATIN_HYPERCUBE = "latin_hypercube"
    QUASI_RANDOM = "quasi_random"


class ObjectiveType(Enum):
    """Optimization objective types"""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class ParameterType(Enum):
    """Parameter types for optimization"""
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"


@dataclass
class Parameter:
    """Experiment parameter definition"""
    name: str
    param_type: ParameterType
    bounds: Union[Tuple[float, float], List[Any]]
    default_value: Any = None
    log_scale: bool = False
    description: str = ""


@dataclass
class Objective:
    """Optimization objective"""
    name: str
    objective_type: ObjectiveType
    weight: float = 1.0
    threshold: Optional[float] = None
    creator_specific: bool = False


@dataclass
class ExperimentConfiguration:
    """Experiment configuration"""
    experiment_id: str
    name: str
    experiment_type: ExperimentType
    parameters: List[Parameter]
    objectives: List[Objective]
    optimization_strategy: OptimizationStrategy
    budget: int  # Number of trials
    parallel_trials: int = 1
    creator_filters: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    early_stopping: bool = True
    statistical_power: float = 0.8
    significance_level: float = 0.05


@dataclass
class Trial:
    """Individual experiment trial"""
    trial_id: str
    experiment_id: str
    parameters: Dict[str, Any]
    objectives: Dict[str, float] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    creator_specific_results: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Experiment result summary"""
    experiment_id: str
    best_trial: Trial
    pareto_front: List[Trial]  # For multi-objective optimization
    convergence_history: List[float]
    statistical_significance: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    effect_sizes: Dict[str, float]
    recommendations: List[str]


class ExperimentalDesignOptimizer:
    """Enterprise Experimental Design Optimizer"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Storage
        self.experiments: Dict[str, ExperimentConfiguration] = {}
        self.trials: Dict[str, List[Trial]] = {}
        self.results: Dict[str, ExperimentResult] = {}
        
        # Configuration
        self.max_parallel_experiments = self.config.get('max_parallel_experiments', 5)
        self.default_budget = self.config.get('default_budget', 100)
        self.enable_early_stopping = self.config.get('enable_early_stopping', True)
        self.acquisition_function = self.config.get('acquisition_function', 'expected_improvement')
        
        # Creator-specific experiment profiles
        self.creator_experiment_profiles = {
            'musician': {
                'audio_weight': 1.5,
                'latency_sensitivity': 1.2,
                'quality_preference': 1.3,
                'compute_budget_multiplier': 1.4
            },
            'blogger': {
                'text_weight': 1.5,
                'latency_sensitivity': 0.8,
                'quality_preference': 1.1,
                'compute_budget_multiplier': 0.9
            },
            'photographer': {
                'visual_weight': 1.5,
                'latency_sensitivity': 0.9,
                'quality_preference': 1.4,
                'compute_budget_multiplier': 1.3
            },
            'influencer': {
                'engagement_weight': 1.5,
                'latency_sensitivity': 1.3,
                'quality_preference': 1.2,
                'compute_budget_multiplier': 1.1
            }
        }
        
        # Performance tracking
        self.optimizer_metrics = {
            'experiments_run': 0,
            'trials_completed': 0,
            'optimization_efficiency': 0.0,
            'average_convergence_time': 0.0,
            'successful_optimizations': 0
        }
        
        logger.info("🧬 Experimental Design Optimizer initialized")
    
    async def create_experiment(
        self,
        name: str,
        experiment_type: ExperimentType,
        parameters: List[Parameter],
        objectives: List[Objective],
        strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN_OPTIMIZATION,
        budget: Optional[int] = None,
        creator_specific: bool = False
    ) -> str:
        """Create new experiment configuration"""
        try:
            experiment_id = str(uuid.uuid4())
            
            # Optimize budget based on experiment complexity
            if budget is None:
                budget = await self._estimate_optimal_budget(parameters, objectives)
            
            # Adjust for creator-specific experiments
            if creator_specific:
                budget = int(budget * 1.5)  # More trials for creator-specific experiments
            
            experiment = ExperimentConfiguration(
                experiment_id=experiment_id,
                name=name,
                experiment_type=experiment_type,
                parameters=parameters,
                objectives=objectives,
                optimization_strategy=strategy,
                budget=budget,
                early_stopping=self.enable_early_stopping
            )
            
            self.experiments[experiment_id] = experiment
            self.trials[experiment_id] = []
            
            logger.info(f"✅ Created experiment: {name} ({experiment_id})")
            return experiment_id
            
        except Exception as e:
            logger.error(f"❌ Error creating experiment: {e}")
            raise
    
    async def run_experiment(
        self,
        experiment_id: str,
        evaluation_function: Callable
    ) -> ExperimentResult:
        """Run optimization experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            start_time = time.time()
            
            logger.info(f"🚀 Starting experiment: {experiment.name}")
            
            # Initialize optimization based on strategy
            if experiment.optimization_strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
                result = await self._run_bayesian_optimization(experiment, evaluation_function)
            elif experiment.optimization_strategy == OptimizationStrategy.EVOLUTIONARY:
                result = await self._run_evolutionary_optimization(experiment, evaluation_function)
            elif experiment.optimization_strategy == OptimizationStrategy.GRID_SEARCH:
                result = await self._run_grid_search(experiment, evaluation_function)
            elif experiment.optimization_strategy == OptimizationStrategy.RANDOM_SEARCH:
                result = await self._run_random_search(experiment, evaluation_function)
            else:
                result = await self._run_random_search(experiment, evaluation_function)
            
            # Calculate statistical significance
            result.statistical_significance = await self._calculate_statistical_significance(
                experiment_id, result
            )
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(experiment, result)
            
            self.results[experiment_id] = result
            
            # Update metrics
            optimization_time = time.time() - start_time
            await self._update_optimizer_metrics(optimization_time, True)
            
            logger.info(f"✅ Experiment completed: {experiment.name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error running experiment: {e}")
            await self._update_optimizer_metrics(0, False)
            raise
    
    async def _run_bayesian_optimization(
        self,
        experiment: ExperimentConfiguration,
        evaluation_function: Callable
    ) -> ExperimentResult:
        """Run Bayesian optimization"""
        try:
            trials = []
            convergence_history = []
            
            # Initialize with random samples
            n_init = min(10, experiment.budget // 4)
            
            for i in range(n_init):
                trial = await self._create_random_trial(experiment)
                objectives = await self._evaluate_trial(trial, evaluation_function)
                trial.objectives = objectives
                trial.status = "completed"
                trials.append(trial)
            
            # Bayesian optimization loop
            for i in range(n_init, experiment.budget):
                # Select next trial using acquisition function
                trial = await self._select_next_trial_bayesian(experiment, trials)
                objectives = await self._evaluate_trial(trial, evaluation_function)
                trial.objectives = objectives
                trial.status = "completed"
                trials.append(trial)
                
                # Update convergence history
                best_so_far = self._get_best_objective_value(trials, experiment.objectives[0])
                convergence_history.append(best_so_far)
                
                # Early stopping check
                if experiment.early_stopping and await self._should_stop_early(convergence_history):
                    logger.info(f"Early stopping at trial {i}")
                    break
            
            self.trials[experiment.experiment_id] = trials
            
            # Find best trial and Pareto front
            best_trial = self._find_best_trial(trials, experiment.objectives)
            pareto_front = self._find_pareto_front(trials, experiment.objectives)
            
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                best_trial=best_trial,
                pareto_front=pareto_front,
                convergence_history=convergence_history,
                statistical_significance={},
                confidence_intervals={},
                effect_sizes={},
                recommendations=[]
            )
            
        except Exception as e:
            logger.error(f"❌ Error in Bayesian optimization: {e}")
            raise
    
    async def _run_evolutionary_optimization(
        self,
        experiment: ExperimentConfiguration,
        evaluation_function: Callable
    ) -> ExperimentResult:
        """Run evolutionary optimization"""
        try:
            population_size = min(20, experiment.budget // 5)
            generations = experiment.budget // population_size
            
            # Initialize population
            population = []
            for _ in range(population_size):
                trial = await self._create_random_trial(experiment)
                objectives = await self._evaluate_trial(trial, evaluation_function)
                trial.objectives = objectives
                trial.status = "completed"
                population.append(trial)
            
            convergence_history = []
            all_trials = population.copy()
            
            # Evolution loop
            for generation in range(generations):
                # Select parents
                parents = await self._select_parents(population, experiment.objectives)
                
                # Create offspring through crossover and mutation
                offspring = []
                while len(offspring) < population_size:
                    parent1, parent2 = random.sample(parents, 2)
                    child = await self._crossover_and_mutate(parent1, parent2, experiment)
                    objectives = await self._evaluate_trial(child, evaluation_function)
                    child.objectives = objectives
                    child.status = "completed"
                    offspring.append(child)
                    all_trials.append(child)
                
                # Selection for next generation
                population = await self._select_survivors(
                    population + offspring, population_size, experiment.objectives
                )
                
                # Update convergence
                best_value = self._get_best_objective_value(population, experiment.objectives[0])
                convergence_history.append(best_value)
            
            self.trials[experiment.experiment_id] = all_trials
            
            best_trial = self._find_best_trial(all_trials, experiment.objectives)
            pareto_front = self._find_pareto_front(all_trials, experiment.objectives)
            
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                best_trial=best_trial,
                pareto_front=pareto_front,
                convergence_history=convergence_history,
                statistical_significance={},
                confidence_intervals={},
                effect_sizes={},
                recommendations=[]
            )
            
        except Exception as e:
            logger.error(f"❌ Error in evolutionary optimization: {e}")
            raise
    
    async def _run_grid_search(
        self,
        experiment: ExperimentConfiguration,
        evaluation_function: Callable
    ) -> ExperimentResult:
        """Run grid search optimization"""
        try:
            # Generate grid points
            grid_points = await self._generate_grid_points(experiment)
            
            # Limit to budget
            if len(grid_points) > experiment.budget:
                grid_points = random.sample(grid_points, experiment.budget)
            
            trials = []
            convergence_history = []
            
            for i, point in enumerate(grid_points):
                trial = Trial(
                    trial_id=str(uuid.uuid4()),
                    experiment_id=experiment.experiment_id,
                    parameters=point
                )
                
                objectives = await self._evaluate_trial(trial, evaluation_function)
                trial.objectives = objectives
                trial.status = "completed"
                trials.append(trial)
                
                # Update convergence
                best_value = self._get_best_objective_value(trials, experiment.objectives[0])
                convergence_history.append(best_value)
            
            self.trials[experiment.experiment_id] = trials
            
            best_trial = self._find_best_trial(trials, experiment.objectives)
            pareto_front = self._find_pareto_front(trials, experiment.objectives)
            
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                best_trial=best_trial,
                pareto_front=pareto_front,
                convergence_history=convergence_history,
                statistical_significance={},
                confidence_intervals={},
                effect_sizes={},
                recommendations=[]
            )
            
        except Exception as e:
            logger.error(f"❌ Error in grid search: {e}")
            raise
    
    async def _run_random_search(
        self,
        experiment: ExperimentConfiguration,
        evaluation_function: Callable
    ) -> ExperimentResult:
        """Run random search optimization"""
        try:
            trials = []
            convergence_history = []
            
            for i in range(experiment.budget):
                trial = await self._create_random_trial(experiment)
                objectives = await self._evaluate_trial(trial, evaluation_function)
                trial.objectives = objectives
                trial.status = "completed"
                trials.append(trial)
                
                # Update convergence
                best_value = self._get_best_objective_value(trials, experiment.objectives[0])
                convergence_history.append(best_value)
            
            self.trials[experiment.experiment_id] = trials
            
            best_trial = self._find_best_trial(trials, experiment.objectives)
            pareto_front = self._find_pareto_front(trials, experiment.objectives)
            
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                best_trial=best_trial,
                pareto_front=pareto_front,
                convergence_history=convergence_history,
                statistical_significance={},
                confidence_intervals={},
                effect_sizes={},
                recommendations=[]
            )
            
        except Exception as e:
            logger.error(f"❌ Error in random search: {e}")
            raise
    
    async def _create_random_trial(self, experiment: ExperimentConfiguration) -> Trial:
        """Create random trial within parameter bounds"""
        try:
            parameters = {}
            
            for param in experiment.parameters:
                if param.param_type == ParameterType.CONTINUOUS:
                    low, high = param.bounds
                    if param.log_scale:
                        value = np.exp(np.random.uniform(np.log(low), np.log(high)))
                    else:
                        value = np.random.uniform(low, high)
                    parameters[param.name] = value
                
                elif param.param_type == ParameterType.DISCRETE:
                    low, high = param.bounds
                    parameters[param.name] = np.random.randint(low, high + 1)
                
                elif param.param_type == ParameterType.CATEGORICAL:
                    parameters[param.name] = np.random.choice(param.bounds)
                
                elif param.param_type == ParameterType.BOOLEAN:
                    parameters[param.name] = np.random.choice([True, False])
            
            trial = Trial(
                trial_id=str(uuid.uuid4()),
                experiment_id=experiment.experiment_id,
                parameters=parameters
            )
            
            return trial
            
        except Exception as e:
            logger.error(f"❌ Error creating random trial: {e}")
            raise
    
    async def _evaluate_trial(
        self,
        trial: Trial,
        evaluation_function: Callable
    ) -> Dict[str, float]:
        """Evaluate trial using provided function"""
        try:
            trial.start_time = datetime.utcnow()
            
            # Call evaluation function with parameters
            results = await evaluation_function(trial.parameters)
            
            trial.end_time = datetime.utcnow()
            
            # Ensure results is a dictionary
            if isinstance(results, (int, float)):
                results = {'objective': results}
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error evaluating trial {trial.trial_id}: {e}")
            # Return default poor performance
            return {'objective': 0.0}
    
    async def _select_next_trial_bayesian(
        self,
        experiment: ExperimentConfiguration,
        completed_trials: List[Trial]
    ) -> Trial:
        """Select next trial using Bayesian optimization (simplified)"""
        try:
            # For simplicity, use random selection with bias toward unexplored regions
            # In practice, this would use Gaussian Processes and acquisition functions
            
            # Generate random candidate
            trial = await self._create_random_trial(experiment)
            
            # Add some exploration vs exploitation logic
            if len(completed_trials) > 10:
                # Exploitation: slight bias toward good regions
                best_trial = self._find_best_trial(completed_trials, experiment.objectives)
                
                # Add noise to best parameters
                for param in experiment.parameters:
                    if param.param_type == ParameterType.CONTINUOUS:
                        best_value = best_trial.parameters[param.name]
                        noise_scale = (param.bounds[1] - param.bounds[0]) * 0.1
                        trial.parameters[param.name] = np.clip(
                            best_value + np.random.normal(0, noise_scale),
                            param.bounds[0], param.bounds[1]
                        )
            
            return trial
            
        except Exception as e:
            logger.error(f"❌ Error selecting next trial: {e}")
            return await self._create_random_trial(experiment)
    
    def _find_best_trial(
        self,
        trials: List[Trial],
        objectives: List[Objective]
    ) -> Trial:
        """Find best trial based on objectives"""
        try:
            if not trials:
                raise ValueError("No trials to evaluate")
            
            # For single objective
            if len(objectives) == 1:
                objective = objectives[0]
                if objective.objective_type == ObjectiveType.MAXIMIZE:
                    return max(trials, key=lambda t: t.objectives.get(objective.name, 0))
                else:
                    return min(trials, key=lambda t: t.objectives.get(objective.name, float('inf')))
            
            # For multiple objectives, use weighted sum
            def weighted_score(trial):
                score = 0
                for obj in objectives:
                    value = trial.objectives.get(obj.name, 0)
                    if obj.objective_type == ObjectiveType.MINIMIZE:
                        value = -value
                    score += obj.weight * value
                return score
            
            return max(trials, key=weighted_score)
            
        except Exception as e:
            logger.error(f"❌ Error finding best trial: {e}")
            return trials[0] if trials else None
    
    def _find_pareto_front(
        self,
        trials: List[Trial],
        objectives: List[Objective]
    ) -> List[Trial]:
        """Find Pareto front for multi-objective optimization"""
        try:
            if len(objectives) <= 1:
                best_trial = self._find_best_trial(trials, objectives)
                return [best_trial] if best_trial else []
            
            pareto_front = []
            
            for trial in trials:
                is_dominated = False
                
                for other_trial in trials:
                    if trial == other_trial:
                        continue
                    
                    # Check if other_trial dominates trial
                    dominates = True
                    for obj in objectives:
                        trial_value = trial.objectives.get(obj.name, 0)
                        other_value = other_trial.objectives.get(obj.name, 0)
                        
                        if obj.objective_type == ObjectiveType.MAXIMIZE:
                            if trial_value > other_value:
                                dominates = False
                                break
                        else:
                            if trial_value < other_value:
                                dominates = False
                                break
                    
                    if dominates:
                        # Check if at least one objective is strictly better
                        strictly_better = False
                        for obj in objectives:
                            trial_value = trial.objectives.get(obj.name, 0)
                            other_value = other_trial.objectives.get(obj.name, 0)
                            
                            if obj.objective_type == ObjectiveType.MAXIMIZE:
                                if other_value > trial_value:
                                    strictly_better = True
                                    break
                            else:
                                if other_value < trial_value:
                                    strictly_better = True
                                    break
                        
                        if strictly_better:
                            is_dominated = True
                            break
                
                if not is_dominated:
                    pareto_front.append(trial)
            
            return pareto_front
            
        except Exception as e:
            logger.error(f"❌ Error finding Pareto front: {e}")
            return []
    
    def _get_best_objective_value(
        self,
        trials: List[Trial],
        objective: Objective
    ) -> float:
        """Get best objective value from trials"""
        try:
            if not trials:
                return 0.0
            
            values = [trial.objectives.get(objective.name, 0) for trial in trials]
            
            if objective.objective_type == ObjectiveType.MAXIMIZE:
                return max(values)
            else:
                return min(values)
                
        except Exception as e:
            logger.error(f"❌ Error getting best objective value: {e}")
            return 0.0
    
    async def _should_stop_early(self, convergence_history: List[float]) -> bool:
        """Check if optimization should stop early"""
        try:
            if len(convergence_history) < 20:
                return False
            
            # Check if improvement has stalled
            recent_values = convergence_history[-10:]
            improvement = abs(recent_values[-1] - recent_values[0])
            
            # Stop if improvement is less than 1% over last 10 iterations
            if improvement < 0.01:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in early stopping check: {e}")
            return False
    
    async def _estimate_optimal_budget(
        self,
        parameters: List[Parameter],
        objectives: List[Objective]
    ) -> int:
        """Estimate optimal budget based on problem complexity"""
        try:
            # Base budget
            budget = self.default_budget
            
            # Adjust for parameter complexity
            n_params = len(parameters)
            continuous_params = sum(1 for p in parameters if p.param_type == ParameterType.CONTINUOUS)
            categorical_params = sum(1 for p in parameters if p.param_type == ParameterType.CATEGORICAL)
            
            # More budget for more parameters
            budget += n_params * 5
            
            # More budget for continuous parameters (harder to optimize)
            budget += continuous_params * 10
            
            # More budget for multi-objective optimization
            if len(objectives) > 1:
                budget = int(budget * 1.5)
            
            return min(budget, 500)  # Cap at 500 trials
            
        except Exception as e:
            logger.error(f"❌ Error estimating optimal budget: {e}")
            return self.default_budget
    
    async def _generate_grid_points(self, experiment: ExperimentConfiguration) -> List[Dict[str, Any]]:
        """Generate grid points for grid search"""
        try:
            param_grids = []
            
            for param in experiment.parameters:
                if param.param_type == ParameterType.CONTINUOUS:
                    low, high = param.bounds
                    n_points = min(10, int(np.sqrt(experiment.budget)))
                    if param.log_scale:
                        points = np.logspace(np.log10(low), np.log10(high), n_points)
                    else:
                        points = np.linspace(low, high, n_points)
                    param_grids.append(points.tolist())
                
                elif param.param_type == ParameterType.DISCRETE:
                    low, high = param.bounds
                    points = list(range(low, high + 1))
                    param_grids.append(points)
                
                elif param.param_type == ParameterType.CATEGORICAL:
                    param_grids.append(param.bounds)
                
                elif param.param_type == ParameterType.BOOLEAN:
                    param_grids.append([True, False])
            
            # Generate all combinations
            grid_combinations = list(product(*param_grids))
            
            # Convert to parameter dictionaries
            grid_points = []
            for combination in grid_combinations:
                point = {}
                for i, param in enumerate(experiment.parameters):
                    point[param.name] = combination[i]
                grid_points.append(point)
            
            return grid_points
            
        except Exception as e:
            logger.error(f"❌ Error generating grid points: {e}")
            return []
    
    async def _select_parents(
        self,
        population: List[Trial],
        objectives: List[Objective]
    ) -> List[Trial]:
        """Select parents for evolutionary algorithm"""
        try:
            # Tournament selection
            tournament_size = 3
            parents = []
            
            for _ in range(len(population) // 2):
                tournament = random.sample(population, tournament_size)
                best = self._find_best_trial(tournament, objectives)
                parents.append(best)
            
            return parents
            
        except Exception as e:
            logger.error(f"❌ Error selecting parents: {e}")
            return population[:len(population)//2]
    
    async def _crossover_and_mutate(
        self,
        parent1: Trial,
        parent2: Trial,
        experiment: ExperimentConfiguration
    ) -> Trial:
        """Create offspring through crossover and mutation"""
        try:
            child_params = {}
            
            for param in experiment.parameters:
                # Crossover: randomly choose from parents
                if random.random() < 0.5:
                    child_params[param.name] = parent1.parameters[param.name]
                else:
                    child_params[param.name] = parent2.parameters[param.name]
                
                # Mutation
                if random.random() < 0.1:  # 10% mutation rate
                    if param.param_type == ParameterType.CONTINUOUS:
                        # Add Gaussian noise
                        low, high = param.bounds
                        noise_scale = (high - low) * 0.1
                        child_params[param.name] = np.clip(
                            child_params[param.name] + np.random.normal(0, noise_scale),
                            low, high
                        )
                    elif param.param_type == ParameterType.CATEGORICAL:
                        child_params[param.name] = random.choice(param.bounds)
                    elif param.param_type == ParameterType.BOOLEAN:
                        child_params[param.name] = not child_params[param.name]
            
            child = Trial(
                trial_id=str(uuid.uuid4()),
                experiment_id=experiment.experiment_id,
                parameters=child_params
            )
            
            return child
            
        except Exception as e:
            logger.error(f"❌ Error in crossover and mutation: {e}")
            return await self._create_random_trial(experiment)
    
    async def _select_survivors(
        self,
        population: List[Trial],
        target_size: int,
        objectives: List[Objective]
    ) -> List[Trial]:
        """Select survivors for next generation"""
        try:
            # Sort by fitness and select top individuals
            if len(objectives) == 1:
                objective = objectives[0]
                if objective.objective_type == ObjectiveType.MAXIMIZE:
                    population.sort(key=lambda t: t.objectives.get(objective.name, 0), reverse=True)
                else:
                    population.sort(key=lambda t: t.objectives.get(objective.name, float('inf')))
            else:
                # For multi-objective, use non-dominated sorting
                pareto_front = self._find_pareto_front(population, objectives)
                # Return Pareto front + best remaining
                remaining = [t for t in population if t not in pareto_front]
                best_remaining = sorted(
                    remaining,
                    key=lambda t: sum(t.objectives.get(obj.name, 0) * obj.weight for obj in objectives),
                    reverse=True
                )
                population = pareto_front + best_remaining
            
            return population[:target_size]
            
        except Exception as e:
            logger.error(f"❌ Error selecting survivors: {e}")
            return population[:target_size]
    
    async def _calculate_statistical_significance(
        self,
        experiment_id: str,
        result: ExperimentResult
    ) -> Dict[str, float]:
        """Calculate statistical significance of results"""
        try:
            trials = self.trials.get(experiment_id, [])
            if len(trials) < 10:
                return {}
            
            significance = {}
            
            for objective in self.experiments[experiment_id].objectives:
                values = [trial.objectives.get(objective.name, 0) for trial in trials]
                
                if len(values) > 1:
                    # Simple t-test against baseline (mean of first 20% of trials)
                    baseline_size = max(2, len(values) // 5)
                    baseline_values = values[:baseline_size]
                    recent_values = values[-baseline_size:]
                    
                    if len(baseline_values) > 1 and len(recent_values) > 1:
                        baseline_mean = mean(baseline_values)
                        recent_mean = mean(recent_values)
                        
                        # Simplified statistical test
                        improvement = abs(recent_mean - baseline_mean) / abs(baseline_mean) if baseline_mean != 0 else 0
                        significance[objective.name] = min(1.0, improvement * 10)  # Simplified p-value
            
            return significance
            
        except Exception as e:
            logger.error(f"❌ Error calculating statistical significance: {e}")
            return {}
    
    async def _generate_recommendations(
        self,
        experiment: ExperimentConfiguration,
        result: ExperimentResult
    ) -> List[str]:
        """Generate experiment recommendations"""
        try:
            recommendations = []
            
            # Best parameter recommendations
            if result.best_trial:
                recommendations.append(
                    f"Best configuration: {result.best_trial.parameters}"
                )
                
                best_objective = max(result.best_trial.objectives.values())
                recommendations.append(
                    f"Best objective value: {best_objective:.4f}"
                )
            
            # Convergence analysis
            if result.convergence_history:
                final_improvement = (result.convergence_history[-1] - result.convergence_history[0])
                if final_improvement > 0.1:
                    recommendations.append("Good convergence - consider similar experiments")
                else:
                    recommendations.append("Poor convergence - consider different strategy or more budget")
            
            # Multi-objective recommendations
            if len(result.pareto_front) > 1:
                recommendations.append(
                    f"Found {len(result.pareto_front)} Pareto-optimal solutions - consider trade-off analysis"
                )
            
            # Parameter importance
            if len(self.trials.get(experiment.experiment_id, [])) > 20:
                recommendations.append("Sufficient data for parameter importance analysis")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return ["Experiment completed successfully"]
    
    async def _update_optimizer_metrics(self, optimization_time: float, success: bool):
        """Update optimizer metrics"""
        try:
            self.optimizer_metrics['experiments_run'] += 1
            
            if success:
                self.optimizer_metrics['successful_optimizations'] += 1
                
                # Update average convergence time
                total_successful = self.optimizer_metrics['successful_optimizations']
                current_avg = self.optimizer_metrics['average_convergence_time']
                new_avg = (current_avg * (total_successful - 1) + optimization_time) / total_successful
                self.optimizer_metrics['average_convergence_time'] = new_avg
            
            # Update efficiency
            if self.optimizer_metrics['experiments_run'] > 0:
                self.optimizer_metrics['optimization_efficiency'] = (
                    self.optimizer_metrics['successful_optimizations'] / 
                    self.optimizer_metrics['experiments_run']
                )
            
        except Exception as e:
            logger.error(f"❌ Error updating optimizer metrics: {e}")
    
    async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment status and progress"""
        try:
            if experiment_id not in self.experiments:
                return {}
            
            experiment = self.experiments[experiment_id]
            trials = self.trials.get(experiment_id, [])
            
            completed_trials = [t for t in trials if t.status == "completed"]
            
            status = {
                'experiment_id': experiment_id,
                'name': experiment.name,
                'type': experiment.experiment_type.value,
                'strategy': experiment.optimization_strategy.value,
                'total_budget': experiment.budget,
                'completed_trials': len(completed_trials),
                'progress': len(completed_trials) / experiment.budget if experiment.budget > 0 else 0,
                'best_result': None
            }
            
            if completed_trials:
                best_trial = self._find_best_trial(completed_trials, experiment.objectives)
                status['best_result'] = {
                    'parameters': best_trial.parameters,
                    'objectives': best_trial.objectives
                }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting experiment status: {e}")
            return {}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get optimizer metrics"""
        return {
            **self.optimizer_metrics,
            'active_experiments': len(self.experiments),
            'total_trials': sum(len(trials) for trials in self.trials.values())
        }


# Global instance
experiment_optimizer = ExperimentalDesignOptimizer()


async def main():
    """Test the Experimental Design Optimizer"""
    optimizer = ExperimentalDesignOptimizer()
    
    print("🧬 Testing Experimental Design Optimizer...")
    
    # Define parameters
    parameters = [
        Parameter(
            name="learning_rate",
            param_type=ParameterType.CONTINUOUS,
            bounds=(0.001, 0.1),
            log_scale=True,
            description="Learning rate for model training"
        ),
        Parameter(
            name="batch_size",
            param_type=ParameterType.DISCRETE,
            bounds=(16, 128),
            description="Training batch size"
        ),
        Parameter(
            name="optimizer",
            param_type=ParameterType.CATEGORICAL,
            bounds=["adam", "sgd", "rmsprop"],
            description="Optimization algorithm"
        )
    ]
    
    # Define objectives
    objectives = [
        Objective(
            name="accuracy",
            objective_type=ObjectiveType.MAXIMIZE,
            weight=0.7
        ),
        Objective(
            name="training_time",
            objective_type=ObjectiveType.MINIMIZE,
            weight=0.3
        )
    ]
    
    # Create experiment
    experiment_id = await optimizer.create_experiment(
        name="Hyperparameter Optimization",
        experiment_type=ExperimentType.HYPERPARAMETER_TUNING,
        parameters=parameters,
        objectives=objectives,
        strategy=OptimizationStrategy.BAYESIAN_OPTIMIZATION,
        budget=20
    )
    
    print(f"✅ Created experiment: {experiment_id}")
    
    # Define evaluation function
    async def evaluate_model(params):
        # Simulate model training and evaluation
        lr = params["learning_rate"]
        batch_size = params["batch_size"]
        optimizer_type = params["optimizer"]
        
        # Simulate accuracy (higher learning rate = higher accuracy up to a point)
        base_accuracy = 0.8
        lr_bonus = min(0.15, lr * 100)  # Bonus for higher LR
        batch_bonus = 0.05 * (batch_size / 128)  # Bonus for larger batches
        optimizer_bonus = {"adam": 0.05, "sgd": 0.02, "rmsprop": 0.03}[optimizer_type]
        
        accuracy = base_accuracy + lr_bonus + batch_bonus + optimizer_bonus
        accuracy += np.random.normal(0, 0.02)  # Add noise
        accuracy = np.clip(accuracy, 0, 1)
        
        # Simulate training time (larger batches = faster training)
        base_time = 3600  # 1 hour base
        batch_speedup = 1 - (batch_size - 16) / (128 - 16) * 0.3
        training_time = base_time * batch_speedup
        training_time += np.random.normal(0, 180)  # Add noise
        
        await asyncio.sleep(0.01)  # Simulate evaluation time
        
        return {
            "accuracy": accuracy,
            "training_time": training_time
        }
    
    # Run experiment
    result = await optimizer.run_experiment(experiment_id, evaluate_model)
    
    print(f"🎯 Experiment completed!")
    print(f"   Best trial parameters: {result.best_trial.parameters}")
    print(f"   Best trial objectives: {result.best_trial.objectives}")
    print(f"   Pareto front size: {len(result.pareto_front)}")
    print(f"   Convergence history length: {len(result.convergence_history)}")
    
    # Get experiment status
    status = await optimizer.get_experiment_status(experiment_id)
    print(f"\nExperiment status: {status['progress']*100:.1f}% complete")
    
    # Get optimizer metrics
    metrics = await optimizer.get_metrics()
    print(f"Optimizer metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())