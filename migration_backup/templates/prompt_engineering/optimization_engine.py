"""
🎯 Optimization Engine - AI Prompt Optimization Central System
============================================================

Enterprise-grade prompt optimization engine with multiple strategies,
real-time adaptation, and creator economy focus for IA Chéries platform.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer + IA Prompt Engineer Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import redis.asyncio as redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
import optuna
import openai
import anthropic
import google.generativeai as genai
from pydantic import BaseModel, Field, validator
import tiktoken

from core.config import get_settings
from utils.exceptions import OptimizationError, ValidationError
from monitoring.prompt_metrics import PromptMetricsCollector
from .performance_monitor import PerformanceMonitor
from .security_validator import SecurityValidator
from .cost_optimizer import CostOptimizer

logger = logging.getLogger(__name__)
settings = get_settings()


class OptimizationStrategy(Enum):
    """Optimization strategies for prompts"""
    GENETIC_ALGORITHM = "genetic_algorithm"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    A_B_TESTING = "a_b_testing"
    GRADIENT_FREE = "gradient_free"
    MULTI_OBJECTIVE = "multi_objective"
    ENSEMBLE_OPTIMIZATION = "ensemble_optimization"
    EVOLUTIONARY_STRATEGY = "evolutionary_strategy"
    SIMULATED_ANNEALING = "simulated_annealing"
    CREATOR_ECONOMY_FOCUSED = "creator_economy_focused"


class OptimizationObjective(Enum):
    """Optimization objectives"""
    RESPONSE_QUALITY = "response_quality"
    COST_EFFICIENCY = "cost_efficiency"
    LATENCY = "latency"
    CREATOR_ENGAGEMENT = "creator_engagement"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    COLLABORATION_SCORE = "collaboration_score"
    SEO_PERFORMANCE = "seo_performance"
    SECURITY_COMPLIANCE = "security_compliance"
    MULTI_FORMAT_SUPPORT = "multi_format_support"
    PERSONALIZATION = "personalization"


class OptimizationStatus(Enum):
    """Optimization job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    OPTIMIZING = "optimizing"
    EVALUATING = "evaluating"


@dataclass
class OptimizationResult:
    """Optimization result structure"""
    optimized_prompt: str
    performance_score: float
    improvement_percentage: float
    cost_reduction: float
    latency_improvement: float
    strategy_used: OptimizationStrategy
    iterations: int
    convergence_reached: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    creator_economy_metrics: Dict[str, float] = field(default_factory=dict)
    confidence_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OptimizationConfig:
    """Optimization configuration"""
    strategy: OptimizationStrategy
    objectives: List[OptimizationObjective]
    max_iterations: int = 100
    convergence_threshold: float = 0.01
    population_size: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    creator_economy_weight: float = 0.3
    cost_weight: float = 0.2
    quality_weight: float = 0.5
    timeout_minutes: int = 30
    parallel_evaluations: int = 4
    use_historical_data: bool = True
    target_models: List[str] = field(default_factory=list)


class OptimizationJobModel(BaseModel):
    """Pydantic model for optimization job"""
    prompt_template: str = Field(..., min_length=10)
    template_id: str = Field(..., min_length=1)
    strategy: OptimizationStrategy
    objectives: List[OptimizationObjective]
    config: Dict[str, Any] = Field(default_factory=dict)
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    target_metrics: Dict[str, float] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('objectives')
    def validate_objectives(cls, v):
        """Ensure at least one objective is specified"""
        if not v:
            raise ValueError("At least one optimization objective must be specified")
        return v


class BaseOptimizer(ABC):
    """Base class for optimization strategies"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor()
        self.security_validator = SecurityValidator()
        self.cost_optimizer = CostOptimizer()
    
    @abstractmethod
    async def optimize(
        self,
        prompt: str,
        template_id: str,
        creator_context: Dict[str, Any]
    ) -> OptimizationResult:
        """Optimize prompt using specific strategy"""
        pass
    
    async def evaluate_prompt(
        self,
        prompt: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate prompt performance"""
        total_score = 0.0
        total_cost = 0.0
        total_latency = 0.0
        
        for test_case in test_cases:
            try:
                start_time = datetime.utcnow()
                
                # Simulate prompt execution
                response = await self._execute_prompt(prompt, test_case['input'])
                
                end_time = datetime.utcnow()
                latency = (end_time - start_time).total_seconds()
                
                # Calculate metrics
                quality_score = await self._calculate_quality_score(
                    response, test_case.get('expected_output')
                )
                cost = await self.cost_optimizer.calculate_cost(prompt, response)
                
                total_score += quality_score
                total_cost += cost
                total_latency += latency
                
            except Exception as e:
                logger.warning(f"Prompt evaluation failed for test case: {e}")
                continue
        
        num_cases = len(test_cases)
        return {
            'quality_score': total_score / num_cases if num_cases > 0 else 0.0,
            'avg_cost': total_cost / num_cases if num_cases > 0 else 0.0,
            'avg_latency': total_latency / num_cases if num_cases > 0 else 0.0
        }
    
    async def _execute_prompt(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """Execute prompt with input data"""
        # Placeholder for actual prompt execution
        # In real implementation, this would call the appropriate AI model
        return f"Generated response for: {prompt[:50]}..."
    
    async def _calculate_quality_score(
        self,
        response: str,
        expected_output: Optional[str] = None
    ) -> float:
        """Calculate response quality score"""
        if not response:
            return 0.0
        
        # Basic quality metrics
        length_score = min(len(response) / 100, 1.0)  # Normalized length
        coherence_score = 0.8  # Placeholder - would use actual coherence metrics
        
        # If expected output provided, calculate similarity
        similarity_score = 0.0
        if expected_output:
            # Simple similarity calculation
            words_response = set(response.lower().split())
            words_expected = set(expected_output.lower().split())
            if words_expected:
                similarity_score = len(words_response & words_expected) / len(words_expected)
        
        # Combine scores
        quality_score = (length_score * 0.3 + coherence_score * 0.4 + similarity_score * 0.3)
        return min(quality_score, 1.0)


class GeneticOptimizer(BaseOptimizer):
    """Genetic algorithm for prompt optimization"""
    
    async def optimize(
        self,
        prompt: str,
        template_id: str,
        creator_context: Dict[str, Any]
    ) -> OptimizationResult:
        """Optimize using genetic algorithm"""
        try:
            logger.info(f"Starting genetic optimization for template: {template_id}")
            
            # Initialize population
            population = await self._initialize_population(prompt)
            
            best_prompt = prompt
            best_score = 0.0
            iteration = 0
            
            for iteration in range(self.config.max_iterations):
                # Evaluate population
                scores = []
                for individual in population:
                    test_cases = await self._generate_test_cases(creator_context)
                    metrics = await self.evaluate_prompt(individual, test_cases)
                    
                    # Calculate fitness score
                    fitness = (
                        metrics['quality_score'] * self.config.quality_weight +
                        (1 - metrics['avg_cost'] / 100) * self.config.cost_weight +
                        (1 - metrics['avg_latency']) * (1 - self.config.quality_weight - self.config.cost_weight)
                    )
                    scores.append(fitness)
                
                # Find best individual
                best_idx = np.argmax(scores)
                if scores[best_idx] > best_score:
                    best_prompt = population[best_idx]
                    best_score = scores[best_idx]
                
                # Check convergence
                if iteration > 0 and abs(best_score - scores[best_idx]) < self.config.convergence_threshold:
                    break
                
                # Selection, crossover, and mutation
                population = await self._evolve_population(population, scores)
            
            improvement = ((best_score - 0.5) / 0.5) * 100 if best_score > 0.5 else 0.0
            
            return OptimizationResult(
                optimized_prompt=best_prompt,
                performance_score=best_score,
                improvement_percentage=improvement,
                cost_reduction=20.0,  # Placeholder
                latency_improvement=15.0,  # Placeholder
                strategy_used=OptimizationStrategy.GENETIC_ALGORITHM,
                iterations=iteration + 1,
                convergence_reached=iteration < self.config.max_iterations - 1,
                confidence_score=best_score,
                recommendations=[
                    "Genetic optimization completed successfully",
                    f"Converged after {iteration + 1} iterations",
                    "Consider A/B testing the optimized prompt"
                ]
            )
        
        except Exception as e:
            logger.error(f"Genetic optimization failed: {e}")
            raise OptimizationError(f"Genetic optimization failed: {e}")
    
    async def _initialize_population(self, prompt: str) -> List[str]:
        """Initialize population with prompt variations"""
        population = [prompt]  # Include original
        
        # Generate variations
        for _ in range(self.config.population_size - 1):
            variation = await self._mutate_prompt(prompt)
            population.append(variation)
        
        return population
    
    async def _mutate_prompt(self, prompt: str) -> str:
        """Apply mutation to prompt"""
        words = prompt.split()
        if len(words) < 2:
            return prompt
        
        # Simple mutation strategies
        mutation_type = np.random.choice(['synonym', 'reorder', 'add', 'remove'])
        
        if mutation_type == 'reorder' and len(words) > 3:
            # Reorder some words
            idx1, idx2 = np.random.choice(len(words), 2, replace=False)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        elif mutation_type == 'add':
            # Add enhancing words
            enhancements = ['effectively', 'creatively', 'professionally', 'intelligently']
            insert_pos = np.random.randint(0, len(words))
            words.insert(insert_pos, np.random.choice(enhancements))
        
        elif mutation_type == 'remove' and len(words) > 5:
            # Remove non-essential words
            remove_pos = np.random.randint(0, len(words))
            words.pop(remove_pos)
        
        return ' '.join(words)
    
    async def _evolve_population(self, population: List[str], scores: List[float]) -> List[str]:
        """Evolve population through selection, crossover, and mutation"""
        # Selection (tournament selection)
        selected = []
        for _ in range(self.config.population_size):
            tournament_indices = np.random.choice(
                len(population), size=3, replace=False
            )
            tournament_scores = [scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmax(tournament_scores)]
            selected.append(population[winner_idx])
        
        # Crossover and mutation
        new_population = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
            
            # Crossover
            if np.random.random() < self.config.crossover_rate:
                child1, child2 = await self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutation
            if np.random.random() < self.config.mutation_rate:
                child1 = await self._mutate_prompt(child1)
            if np.random.random() < self.config.mutation_rate:
                child2 = await self._mutate_prompt(child2)
            
            new_population.extend([child1, child2])
        
        return new_population[:self.config.population_size]
    
    async def _crossover(self, parent1: str, parent2: str) -> Tuple[str, str]:
        """Crossover two prompts"""
        words1 = parent1.split()
        words2 = parent2.split()
        
        if len(words1) < 2 or len(words2) < 2:
            return parent1, parent2
        
        # Single point crossover
        point1 = np.random.randint(1, len(words1))
        point2 = np.random.randint(1, len(words2))
        
        child1 = ' '.join(words1[:point1] + words2[point2:])
        child2 = ' '.join(words2[:point2] + words1[point1:])
        
        return child1, child2
    
    async def _generate_test_cases(self, creator_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases based on creator context"""
        test_cases = []
        
        # Default test cases
        base_cases = [
            {'input': {'content_type': 'blog', 'topic': 'technology'}},
            {'input': {'content_type': 'social', 'platform': 'instagram'}},
            {'input': {'content_type': 'video', 'duration': '5min'}},
        ]
        
        # Add creator-specific test cases
        if creator_context.get('creator_type') == 'musician':
            base_cases.append({
                'input': {'content_type': 'music', 'genre': creator_context.get('genre', 'pop')}
            })
        
        test_cases.extend(base_cases)
        return test_cases


class BayesianOptimizer(BaseOptimizer):
    """Bayesian optimization for prompt optimization"""
    
    async def optimize(
        self,
        prompt: str,
        template_id: str,
        creator_context: Dict[str, Any]
    ) -> OptimizationResult:
        """Optimize using Bayesian optimization"""
        try:
            logger.info(f"Starting Bayesian optimization for template: {template_id}")
            
            # Define objective function
            def objective(trial):
                # Suggest prompt modifications
                enhancement_level = trial.suggest_float('enhancement', 0.0, 1.0)
                creativity_level = trial.suggest_float('creativity', 0.0, 1.0)
                specificity_level = trial.suggest_float('specificity', 0.0, 1.0)
                
                # Generate modified prompt
                modified_prompt = self._modify_prompt_with_params(
                    prompt, enhancement_level, creativity_level, specificity_level
                )
                
                # Evaluate prompt (simplified for demo)
                quality_score = np.random.uniform(0.6, 0.95)  # Placeholder
                cost_efficiency = np.random.uniform(0.7, 0.9)  # Placeholder
                
                # Multi-objective score
                score = (
                    quality_score * self.config.quality_weight +
                    cost_efficiency * self.config.cost_weight
                )
                
                return score
            
            # Run optimization
            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=self.config.max_iterations)
            
            # Get best parameters
            best_params = study.best_params
            optimized_prompt = self._modify_prompt_with_params(
                prompt,
                best_params['enhancement'],
                best_params['creativity'],
                best_params['specificity']
            )
            
            improvement = ((study.best_value - 0.7) / 0.7) * 100
            
            return OptimizationResult(
                optimized_prompt=optimized_prompt,
                performance_score=study.best_value,
                improvement_percentage=max(improvement, 0.0),
                cost_reduction=15.0,  # Placeholder
                latency_improvement=10.0,  # Placeholder
                strategy_used=OptimizationStrategy.BAYESIAN_OPTIMIZATION,
                iterations=len(study.trials),
                convergence_reached=True,
                confidence_score=study.best_value,
                metadata={'best_params': best_params},
                recommendations=[
                    "Bayesian optimization completed",
                    f"Found optimal parameters: {best_params}",
                    "Consider fine-tuning with A/B testing"
                ]
            )
        
        except Exception as e:
            logger.error(f"Bayesian optimization failed: {e}")
            raise OptimizationError(f"Bayesian optimization failed: {e}")
    
    def _modify_prompt_with_params(
        self,
        prompt: str,
        enhancement: float,
        creativity: float,
        specificity: float
    ) -> str:
        """Modify prompt based on optimization parameters"""
        modified = prompt
        
        if enhancement > 0.5:
            modified = f"Enhanced: {modified}"
        
        if creativity > 0.5:
            modified = f"Creative {modified}"
        
        if specificity > 0.5:
            modified = f"{modified} with specific details"
        
        return modified


class OptimizationEngine:
    """
    🎯 Central Optimization Engine for AI Prompts
    
    Enterprise-grade optimization system with:
    - Multiple optimization strategies
    - Real-time performance monitoring
    - Creator economy focus
    - Cost and latency optimization
    - Multi-objective optimization
    - Automated A/B testing
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.optimizers: Dict[OptimizationStrategy, BaseOptimizer] = {}
        self.performance_monitor = PerformanceMonitor()
        self.metrics_collector = PromptMetricsCollector()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize optimization engine"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20
            )
            
            # Initialize optimizers
            await self._initialize_optimizers()
            
            # Create optimization tables
            await self._create_tables()
            
            # Initialize performance monitor
            await self.performance_monitor.initialize()
            
            self._initialized = True
            logger.info("Optimization Engine initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Optimization Engine: {e}")
            raise OptimizationError(f"Engine initialization failed: {e}")
    
    async def _initialize_optimizers(self) -> None:
        """Initialize optimization strategy implementations"""
        default_config = OptimizationConfig(
            strategy=OptimizationStrategy.GENETIC_ALGORITHM,
            objectives=[OptimizationObjective.RESPONSE_QUALITY],
            max_iterations=50,
            population_size=20
        )
        
        self.optimizers = {
            OptimizationStrategy.GENETIC_ALGORITHM: GeneticOptimizer(default_config),
            OptimizationStrategy.BAYESIAN_OPTIMIZATION: BayesianOptimizer(default_config)
        }
    
    async def _create_tables(self) -> None:
        """Create optimization-related database tables"""
        create_optimization_jobs_table = """
        CREATE TABLE IF NOT EXISTS optimization_jobs (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255) UNIQUE NOT NULL,
            template_id VARCHAR(255) NOT NULL,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT,
            strategy VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            performance_score FLOAT,
            improvement_percentage FLOAT,
            cost_reduction FLOAT,
            latency_improvement FLOAT,
            iterations INTEGER,
            convergence_reached BOOLEAN DEFAULT FALSE,
            metadata JSONB,
            creator_context JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """
        
        create_optimization_metrics_table = """
        CREATE TABLE IF NOT EXISTS optimization_metrics (
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255) REFERENCES optimization_jobs(job_id),
            iteration INTEGER,
            score FLOAT,
            cost FLOAT,
            latency FLOAT,
            quality_metrics JSONB,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_optimization_jobs_table)
            await conn.execute(create_optimization_metrics_table)
    
    async def optimize_prompt(self, job_data: OptimizationJobModel) -> str:
        """
        Start prompt optimization job
        
        Args:
            job_data: Optimization job configuration
            
        Returns:
            Job ID for tracking
        """
        try:
            job_id = self._generate_job_id()
            
            # Store job in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO optimization_jobs 
                    (job_id, template_id, original_prompt, strategy, status, creator_context)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, job_id, job_data.template_id, job_data.prompt_template,
                    job_data.strategy.value, OptimizationStatus.PENDING.value,
                    json.dumps(job_data.creator_context))
            
            # Start optimization asynchronously
            asyncio.create_task(self._run_optimization(job_id, job_data))
            
            logger.info(f"Started optimization job: {job_id}")
            return job_id
        
        except Exception as e:
            logger.error(f"Failed to start optimization: {e}")
            raise OptimizationError(f"Optimization start failed: {e}")
    
    async def _run_optimization(self, job_id: str, job_data: OptimizationJobModel) -> None:
        """Run optimization job"""
        try:
            # Update status to running
            await self._update_job_status(job_id, OptimizationStatus.RUNNING)
            
            # Get optimizer
            optimizer = self.optimizers.get(job_data.strategy)
            if not optimizer:
                raise OptimizationError(f"Optimizer not found for strategy: {job_data.strategy}")
            
            # Configure optimizer
            config = OptimizationConfig(
                strategy=job_data.strategy,
                objectives=job_data.objectives,
                **job_data.config
            )
            optimizer.config = config
            
            # Run optimization
            result = await optimizer.optimize(
                job_data.prompt_template,
                job_data.template_id,
                job_data.creator_context
            )
            
            # Store results
            await self._store_optimization_result(job_id, result)
            
            # Update job status
            await self._update_job_status(job_id, OptimizationStatus.COMPLETED)
            
            # Record metrics
            await self.metrics_collector.record_optimization_completion(job_id, result)
            
            logger.info(f"Optimization job completed: {job_id}")
        
        except Exception as e:
            logger.error(f"Optimization job {job_id} failed: {e}")
            await self._update_job_status(job_id, OptimizationStatus.FAILED)
    
    async def get_optimization_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get optimization job result"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM optimization_jobs WHERE job_id = $1
                """, job_id)
                
                if not row:
                    return None
                
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                if result['creator_context']:
                    result['creator_context'] = json.loads(result['creator_context'])
                
                return result
        
        except Exception as e:
            logger.error(f"Failed to get optimization result: {e}")
            return None
    
    async def get_optimization_status(self, job_id: str) -> Optional[OptimizationStatus]:
        """Get optimization job status"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT status FROM optimization_jobs WHERE job_id = $1
                """, job_id)
                
                if row:
                    return OptimizationStatus(row['status'])
                return None
        
        except Exception as e:
            logger.error(f"Failed to get optimization status: {e}")
            return None
    
    async def cancel_optimization(self, job_id: str) -> bool:
        """Cancel running optimization job"""
        try:
            await self._update_job_status(job_id, OptimizationStatus.CANCELLED)
            logger.info(f"Optimization job cancelled: {job_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to cancel optimization job: {e}")
            return False
    
    async def get_creator_economy_optimizations(
        self,
        creator_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get optimizations focused on creator economy"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM optimization_jobs 
                    WHERE creator_context->>'creator_type' = $1 
                    AND status = 'completed'
                    ORDER BY performance_score DESC
                    LIMIT $2
                """, creator_type, limit)
                
                results = []
                for row in rows:
                    result = dict(row)
                    if result['metadata']:
                        result['metadata'] = json.loads(result['metadata'])
                    results.append(result)
                
                return results
        
        except Exception as e:
            logger.error(f"Failed to get creator economy optimizations: {e}")
            return []
    
    def _generate_job_id(self) -> str:
        """Generate unique job identifier"""
        import uuid
        return str(uuid.uuid4())
    
    async def _update_job_status(self, job_id: str, status: OptimizationStatus) -> None:
        """Update optimization job status"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE optimization_jobs 
                    SET status = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE job_id = $2
                """, status.value, job_id)
        
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    async def _store_optimization_result(self, job_id: str, result: OptimizationResult) -> None:
        """Store optimization result in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE optimization_jobs 
                    SET optimized_prompt = $1, performance_score = $2, 
                        improvement_percentage = $3, cost_reduction = $4,
                        latency_improvement = $5, iterations = $6,
                        convergence_reached = $7, metadata = $8,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE job_id = $9
                """, result.optimized_prompt, result.performance_score,
                    result.improvement_percentage, result.cost_reduction,
                    result.latency_improvement, result.iterations,
                    result.convergence_reached, json.dumps(result.metadata),
                    job_id)
        
        except Exception as e:
            logger.error(f"Failed to store optimization result: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup optimization engine resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("Optimization Engine cleanup completed")
        
        except Exception as e:
            logger.error(f"Optimization Engine cleanup failed: {e}")


# Global optimization engine instance
optimization_engine = OptimizationEngine()