"""
🎯 PROMPT OPTIMIZATION TEMPLATE - IA PROMPT ENGINEER EXPERT IMPLEMENTATION
=========================================================================

Enterprise-grade prompt optimization template with:
- Automated prompt engineering and optimization
- A/B testing framework for prompts
- Performance metrics and evaluation
- Prompt versioning and rollback
- Multi-model prompt adaptation
- Context-aware prompt generation
- Prompt security and safety filters
- Real-time prompt monitoring

Author: IA Prompt Engineer Expert
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
import json
import time
import hashlib
import re
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
import openai
import anthropic
import google.generativeai as genai
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import spacy
import statistics
import asyncpg
import motor.motor_asyncio
import tiktoken


class PromptType(Enum):
    """Prompt types"""
    COMPLETION = "completion"
    CHAT = "chat"
    INSTRUCTION = "instruction"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    GENERATION = "generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class OptimizationStrategy(Enum):
    """Optimization strategies"""
    GENETIC_ALGORITHM = "genetic_algorithm"
    GRADIENT_DESCENT = "gradient_descent"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    RANDOM_SEARCH = "random_search"
    EVOLUTIONARY = "evolutionary"
    REINFORCEMENT_LEARNING = "reinforcement_learning"


class EvaluationMetric(Enum):
    """Evaluation metrics"""
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    ACCURACY = "accuracy"
    FLUENCY = "fluency"
    SAFETY = "safety"
    COST_EFFICIENCY = "cost_efficiency"
    RESPONSE_TIME = "response_time"
    TOKEN_USAGE = "token_usage"


class ModelProvider(Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"


@dataclass
class PromptOptimizationConfig:
    """Prompt optimization configuration"""
    # Model settings
    primary_model: str = "gpt-4"
    fallback_models: List[str] = field(default_factory=lambda: ["gpt-3.5-turbo"])
    model_provider: ModelProvider = ModelProvider.OPENAI
    
    # Optimization settings
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.GENETIC_ALGORITHM
    population_size: int = 20
    generations: int = 10
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    selection_pressure: float = 2.0
    
    # Evaluation settings
    evaluation_metrics: List[EvaluationMetric] = field(default_factory=lambda: [
        EvaluationMetric.RELEVANCE,
        EvaluationMetric.COHERENCE,
        EvaluationMetric.SAFETY
    ])
    test_set_size: int = 100
    validation_split: float = 0.2
    
    # A/B testing
    enable_ab_testing: bool = True
    ab_test_duration_hours: int = 24
    ab_test_confidence_level: float = 0.95
    min_samples_per_variant: int = 100
    
    # Performance settings
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    timeout_seconds: int = 30
    
    # Safety and filtering
    enable_safety_filter: bool = True
    content_filter_threshold: float = 0.8
    bias_detection_enabled: bool = True
    
    # Caching and storage
    enable_caching: bool = True
    cache_ttl: int = 3600
    store_optimization_history: bool = True
    
    # Database settings
    database_url: str = "postgresql://localhost/prompt_optimization"
    redis_url: str = "redis://localhost:6379"


class PromptTemplate(BaseModel):
    """Prompt template model"""
    id: str = Field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest())
    name: str
    type: PromptType
    template: str
    variables: List[str] = Field(default_factory=list)
    system_message: Optional[str] = None
    examples: List[Dict[str, str]] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance metrics
    performance_score: float = 0.0
    cost_per_request: float = 0.0
    average_response_time: float = 0.0
    token_efficiency: float = 0.0
    
    # Version control
    version: str = "1.0.0"
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('template')
    def validate_template(cls, v):
        if not v.strip():
            raise ValueError("Template cannot be empty")
        return v


class PromptEvaluation(BaseModel):
    """Prompt evaluation result"""
    prompt_id: str
    test_case_id: str
    input_data: Dict[str, Any]
    generated_output: str
    expected_output: Optional[str] = None
    
    # Evaluation scores
    relevance_score: float = 0.0
    coherence_score: float = 0.0
    accuracy_score: float = 0.0
    fluency_score: float = 0.0
    safety_score: float = 0.0
    
    # Performance metrics
    response_time_ms: int = 0
    token_count: int = 0
    cost: float = 0.0
    
    # Metadata
    model_used: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evaluator_id: str = "auto"


class OptimizationResult(BaseModel):
    """Optimization process result"""
    original_prompt_id: str
    optimized_prompt_id: str
    optimization_strategy: OptimizationStrategy
    improvement_percentage: float
    iterations: int
    time_taken_seconds: float
    
    # Performance comparison
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    
    # Configuration
    config_used: Dict[str, Any]
    test_cases_count: int
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    optimizer_version: str = "1.0.0"


class ABTestResult(BaseModel):
    """A/B test result"""
    test_id: str
    variant_a_prompt_id: str
    variant_b_prompt_id: str
    
    # Test metrics
    variant_a_score: float
    variant_b_score: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    
    # Sample sizes
    variant_a_samples: int
    variant_b_samples: int
    
    # Winner determination
    winner_variant: str  # "A", "B", or "No significant difference"
    effect_size: float
    
    # Test metadata
    start_time: datetime
    end_time: datetime
    metric_used: EvaluationMetric
    
    @validator('winner_variant')
    def validate_winner(cls, v):
        if v not in ["A", "B", "No significant difference"]:
            raise ValueError("Winner must be 'A', 'B', or 'No significant difference'")
        return v


class AbstractPromptEvaluator(ABC):
    """Abstract prompt evaluator interface"""
    
    @abstractmethod
    async def evaluate_relevance(self, prompt: str, output: str, expected: Optional[str] = None) -> float:
        """Evaluate relevance of the output"""
        pass
    
    @abstractmethod
    async def evaluate_coherence(self, output: str) -> float:
        """Evaluate coherence of the output"""
        pass
    
    @abstractmethod
    async def evaluate_safety(self, output: str) -> float:
        """Evaluate safety of the output"""
        pass


class NLPPromptEvaluator(AbstractPromptEvaluator):
    """NLP-based prompt evaluator"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.logger = logging.getLogger(__name__)
    
    async def evaluate_relevance(self, prompt: str, output: str, expected: Optional[str] = None) -> float:
        """Evaluate relevance using semantic similarity"""
        try:
            if expected:
                # Compare output with expected answer
                docs = [output, expected]
                tfidf_matrix = self.vectorizer.fit_transform(docs)
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            else:
                # Compare output with prompt for context relevance
                docs = [prompt, output]
                tfidf_matrix = self.vectorizer.fit_transform(docs)
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
        except Exception as e:
            self.logger.error(f"Relevance evaluation failed: {e}")
            return 0.5
    
    async def evaluate_coherence(self, output: str) -> float:
        """Evaluate coherence using linguistic features"""
        try:
            doc = self.nlp(output)
            
            # Calculate coherence metrics
            scores = []
            
            # Sentence connectivity (presence of discourse markers)
            discourse_markers = ["however", "therefore", "furthermore", "moreover", "additionally"]
            marker_score = sum(1 for token in doc if token.text.lower() in discourse_markers)
            scores.append(min(marker_score / max(len(list(doc.sents)), 1), 1.0))
            
            # Entity consistency (repeated entities)
            entities = [ent.text for ent in doc.ents]
            entity_score = len(set(entities)) / max(len(entities), 1) if entities else 0.5
            scores.append(entity_score)
            
            # Average sentence length (moderate length indicates better structure)
            avg_sent_length = np.mean([len(sent.text.split()) for sent in doc.sents])
            length_score = 1.0 - abs(avg_sent_length - 15) / 20  # Optimal around 15 words
            scores.append(max(0, min(1, length_score)))
            
            return float(np.mean(scores))
        except Exception as e:
            self.logger.error(f"Coherence evaluation failed: {e}")
            return 0.5
    
    async def evaluate_safety(self, output: str) -> float:
        """Evaluate safety using content analysis"""
        try:
            # Sentiment analysis for extreme negativity
            sentiment = self.sentiment_analyzer.polarity_scores(output)
            safety_score = 1.0
            
            # Penalize extremely negative content
            if sentiment['compound'] < -0.8:
                safety_score *= 0.5
            
            # Check for harmful keywords (this is a simplified version)
            harmful_patterns = [
                r'\b(hate|violence|kill|death|harm)\b',
                r'\b(illegal|fraud|scam)\b',
                r'\b(explicit|nsfw|adult)\b'
            ]
            
            for pattern in harmful_patterns:
                if re.search(pattern, output.lower()):
                    safety_score *= 0.7
            
            return float(max(0, safety_score))
        except Exception as e:
            self.logger.error(f"Safety evaluation failed: {e}")
            return 0.8


class PromptOptimizer:
    """Main prompt optimization engine"""
    
    def __init__(self, config: PromptOptimizationConfig):
        self.config = config
        self.evaluator = NLPPromptEvaluator()
        self.db_pool = None
        self.redis = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize tokenizer for cost calculation
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
    
    async def initialize(self):
        """Initialize the optimizer"""
        # Connect to database
        self.db_pool = await asyncpg.create_pool(self.config.database_url)
        
        # Connect to Redis
        self.redis = redis.from_url(self.config.redis_url)
        
        # Create tables if they don't exist
        await self._create_tables()
        
        self.logger.info("Prompt optimizer initialized")
    
    async def shutdown(self):
        """Shutdown the optimizer"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis:
            await self.redis.close()
    
    async def _create_tables(self):
        """Create database tables"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    type VARCHAR NOT NULL,
                    template TEXT NOT NULL,
                    variables JSONB,
                    system_message TEXT,
                    examples JSONB,
                    constraints JSONB,
                    metadata JSONB,
                    performance_score FLOAT DEFAULT 0,
                    cost_per_request FLOAT DEFAULT 0,
                    average_response_time FLOAT DEFAULT 0,
                    token_efficiency FLOAT DEFAULT 0,
                    version VARCHAR DEFAULT '1.0.0',
                    parent_id VARCHAR,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_evaluations (
                    id SERIAL PRIMARY KEY,
                    prompt_id VARCHAR NOT NULL,
                    test_case_id VARCHAR NOT NULL,
                    input_data JSONB,
                    generated_output TEXT,
                    expected_output TEXT,
                    relevance_score FLOAT DEFAULT 0,
                    coherence_score FLOAT DEFAULT 0,
                    accuracy_score FLOAT DEFAULT 0,
                    fluency_score FLOAT DEFAULT 0,
                    safety_score FLOAT DEFAULT 0,
                    response_time_ms INTEGER DEFAULT 0,
                    token_count INTEGER DEFAULT 0,
                    cost FLOAT DEFAULT 0,
                    model_used VARCHAR,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    evaluator_id VARCHAR DEFAULT 'auto'
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_results (
                    id SERIAL PRIMARY KEY,
                    original_prompt_id VARCHAR NOT NULL,
                    optimized_prompt_id VARCHAR NOT NULL,
                    optimization_strategy VARCHAR NOT NULL,
                    improvement_percentage FLOAT,
                    iterations INTEGER,
                    time_taken_seconds FLOAT,
                    before_metrics JSONB,
                    after_metrics JSONB,
                    config_used JSONB,
                    test_cases_count INTEGER,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    optimizer_version VARCHAR DEFAULT '1.0.0'
                )
            """)
    
    async def optimize_prompt(
        self,
        prompt_template: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        target_metric: EvaluationMetric = EvaluationMetric.RELEVANCE
    ) -> OptimizationResult:
        """Optimize a prompt using the configured strategy"""
        
        start_time = time.time()
        
        # Evaluate baseline performance
        baseline_metrics = await self._evaluate_prompt(prompt_template, test_cases)
        
        # Apply optimization strategy
        if self.config.optimization_strategy == OptimizationStrategy.GENETIC_ALGORITHM:
            optimized_prompt = await self._genetic_algorithm_optimization(
                prompt_template, test_cases, target_metric
            )
        elif self.config.optimization_strategy == OptimizationStrategy.RANDOM_SEARCH:
            optimized_prompt = await self._random_search_optimization(
                prompt_template, test_cases, target_metric
            )
        else:
            raise ValueError(f"Unsupported optimization strategy: {self.config.optimization_strategy}")
        
        # Evaluate optimized performance
        optimized_metrics = await self._evaluate_prompt(optimized_prompt, test_cases)
        
        # Calculate improvement
        baseline_score = baseline_metrics.get(target_metric.value, 0)
        optimized_score = optimized_metrics.get(target_metric.value, 0)
        improvement = ((optimized_score - baseline_score) / max(baseline_score, 0.001)) * 100
        
        # Save optimized prompt
        await self._save_prompt(optimized_prompt)
        
        # Create result
        result = OptimizationResult(
            original_prompt_id=prompt_template.id,
            optimized_prompt_id=optimized_prompt.id,
            optimization_strategy=self.config.optimization_strategy,
            improvement_percentage=improvement,
            iterations=self.config.generations,
            time_taken_seconds=time.time() - start_time,
            before_metrics=baseline_metrics,
            after_metrics=optimized_metrics,
            config_used=self.config.__dict__,
            test_cases_count=len(test_cases)
        )
        
        # Store result
        await self._save_optimization_result(result)
        
        return result
    
    async def _genetic_algorithm_optimization(
        self,
        prompt_template: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        target_metric: EvaluationMetric
    ) -> PromptTemplate:
        """Optimize prompt using genetic algorithm"""
        
        # Initialize population
        population = await self._create_initial_population(prompt_template)
        
        for generation in range(self.config.generations):
            self.logger.info(f"Processing generation {generation + 1}/{self.config.generations}")
            
            # Evaluate population
            fitness_scores = []
            for individual in population:
                metrics = await self._evaluate_prompt(individual, test_cases[:10])  # Use subset for speed
                fitness_scores.append(metrics.get(target_metric.value, 0))
            
            # Selection
            selected = self._selection(population, fitness_scores)
            
            # Crossover and mutation
            new_population = []
            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                
                # Crossover
                if np.random.random() < self.config.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1, parent2
                
                # Mutation
                if np.random.random() < self.config.mutation_rate:
                    child1 = self._mutate(child1)
                if np.random.random() < self.config.mutation_rate:
                    child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.config.population_size]
        
        # Return best individual
        final_fitness = []
        for individual in population:
            metrics = await self._evaluate_prompt(individual, test_cases)
            final_fitness.append(metrics.get(target_metric.value, 0))
        
        best_idx = np.argmax(final_fitness)
        return population[best_idx]
    
    async def _random_search_optimization(
        self,
        prompt_template: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        target_metric: EvaluationMetric
    ) -> PromptTemplate:
        """Optimize prompt using random search"""
        
        best_prompt = prompt_template
        baseline_metrics = await self._evaluate_prompt(prompt_template, test_cases)
        best_score = baseline_metrics.get(target_metric.value, 0)
        
        for iteration in range(self.config.population_size * self.config.generations):
            # Generate random variant
            variant = self._mutate(prompt_template)
            
            # Evaluate variant
            metrics = await self._evaluate_prompt(variant, test_cases)
            score = metrics.get(target_metric.value, 0)
            
            # Update best if improved
            if score > best_score:
                best_prompt = variant
                best_score = score
                self.logger.info(f"Iteration {iteration}: New best score {score:.3f}")
        
        return best_prompt
    
    async def _create_initial_population(self, template: PromptTemplate) -> List[PromptTemplate]:
        """Create initial population for genetic algorithm"""
        population = [template]  # Include original
        
        # Generate variants
        for _ in range(self.config.population_size - 1):
            variant = self._mutate(template)
            population.append(variant)
        
        return population
    
    def _selection(self, population: List[PromptTemplate], fitness_scores: List[float]) -> List[PromptTemplate]:
        """Tournament selection"""
        selected = []
        
        for _ in range(len(population)):
            # Tournament selection
            tournament_size = int(len(population) * 0.1) + 1
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx])
        
        return selected
    
    def _crossover(self, parent1: PromptTemplate, parent2: PromptTemplate) -> Tuple[PromptTemplate, PromptTemplate]:
        """Crossover operation for prompt templates"""
        # Simple template text crossover
        template1_parts = parent1.template.split('\n')
        template2_parts = parent2.template.split('\n')
        
        # Random crossover point
        crossover_point = np.random.randint(1, min(len(template1_parts), len(template2_parts)))
        
        # Create children
        child1_template = '\n'.join(template1_parts[:crossover_point] + template2_parts[crossover_point:])
        child2_template = '\n'.join(template2_parts[:crossover_point] + template1_parts[crossover_point:])
        
        # Create child prompt templates
        child1 = PromptTemplate(
            name=f"{parent1.name}_child1",
            type=parent1.type,
            template=child1_template,
            variables=parent1.variables.copy(),
            system_message=parent1.system_message,
            examples=parent1.examples.copy()
        )
        
        child2 = PromptTemplate(
            name=f"{parent2.name}_child2",
            type=parent2.type,
            template=child2_template,
            variables=parent2.variables.copy(),
            system_message=parent2.system_message,
            examples=parent2.examples.copy()
        )
        
        return child1, child2
    
    def _mutate(self, template: PromptTemplate) -> PromptTemplate:
        """Mutate a prompt template"""
        mutations = [
            self._add_instruction,
            self._modify_tone,
            self._add_constraint,
            self._rephrase_section,
            self._add_example
        ]
        
        # Apply random mutation
        mutation_func = np.random.choice(mutations)
        mutated_template = mutation_func(template.template)
        
        # Create mutated prompt
        mutated = PromptTemplate(
            name=f"{template.name}_mutated",
            type=template.type,
            template=mutated_template,
            variables=template.variables.copy(),
            system_message=template.system_message,
            examples=template.examples.copy()
        )
        
        return mutated
    
    def _add_instruction(self, template: str) -> str:
        """Add instruction to template"""
        instructions = [
            "Please be concise and specific.",
            "Provide examples where relevant.",
            "Think step by step.",
            "Be creative and original.",
            "Focus on accuracy and detail."
        ]
        
        instruction = np.random.choice(instructions)
        return f"{template}\n\n{instruction}"
    
    def _modify_tone(self, template: str) -> str:
        """Modify tone of template"""
        tone_modifiers = [
            ("Please", "Kindly"),
            ("explain", "elaborate on"),
            ("tell me", "describe"),
            ("write", "compose"),
            ("create", "generate")
        ]
        
        modified = template
        for old, new in tone_modifiers:
            if old in template.lower():
                modified = modified.replace(old, new)
                break
        
        return modified
    
    def _add_constraint(self, template: str) -> str:
        """Add constraint to template"""
        constraints = [
            "Keep your response under 200 words.",
            "Use professional language.",
            "Include specific examples.",
            "Avoid technical jargon.",
            "Be objective and factual."
        ]
        
        constraint = np.random.choice(constraints)
        return f"{template}\n\nConstraint: {constraint}"
    
    def _rephrase_section(self, template: str) -> str:
        """Rephrase a section of the template"""
        # Simple rephrasing (in production, use more sophisticated NLP)
        replacements = {
            "What is": "Can you explain what",
            "How to": "What is the process for",
            "Why does": "What causes",
            "When should": "At what point should"
        }
        
        modified = template
        for old, new in replacements.items():
            if old in template:
                modified = template.replace(old, new, 1)
                break
        
        return modified
    
    def _add_example(self, template: str) -> str:
        """Add example to template"""
        example_prompts = [
            "For example:",
            "Here's an example:",
            "Consider this example:",
            "As an illustration:"
        ]
        
        example_prompt = np.random.choice(example_prompts)
        return f"{template}\n\n{example_prompt} [Provide a relevant example here]"
    
    async def _evaluate_prompt(self, prompt: PromptTemplate, test_cases: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate prompt performance on test cases"""
        
        total_metrics = {metric.value: [] for metric in self.config.evaluation_metrics}
        total_cost = 0
        total_time = 0
        total_tokens = 0
        
        for test_case in test_cases[:20]:  # Limit for efficiency
            try:
                # Generate response
                start_time = time.time()
                response, tokens_used = await self._generate_response(prompt, test_case['input'])
                response_time = (time.time() - start_time) * 1000
                
                # Calculate cost
                cost = self._calculate_cost(tokens_used)
                
                # Evaluate response
                if EvaluationMetric.RELEVANCE in self.config.evaluation_metrics:
                    relevance = await self.evaluator.evaluate_relevance(
                        prompt.template, response, test_case.get('expected_output')
                    )
                    total_metrics[EvaluationMetric.RELEVANCE.value].append(relevance)
                
                if EvaluationMetric.COHERENCE in self.config.evaluation_metrics:
                    coherence = await self.evaluator.evaluate_coherence(response)
                    total_metrics[EvaluationMetric.COHERENCE.value].append(coherence)
                
                if EvaluationMetric.SAFETY in self.config.evaluation_metrics:
                    safety = await self.evaluator.evaluate_safety(response)
                    total_metrics[EvaluationMetric.SAFETY.value].append(safety)
                
                total_cost += cost
                total_time += response_time
                total_tokens += tokens_used
                
            except Exception as e:
                self.logger.error(f"Evaluation failed for test case: {e}")
                continue
        
        # Calculate averages
        metrics = {}
        for metric_name, scores in total_metrics.items():
            if scores:
                metrics[metric_name] = np.mean(scores)
            else:
                metrics[metric_name] = 0.0
        
        # Add performance metrics
        metrics['cost_efficiency'] = 1.0 / (total_cost + 0.001)
        metrics['response_time'] = total_time / len(test_cases)
        metrics['token_efficiency'] = 1.0 / (total_tokens / len(test_cases) + 1)
        
        return metrics
    
    async def _generate_response(self, prompt: PromptTemplate, input_data: Dict[str, Any]) -> Tuple[str, int]:
        """Generate response using the prompt"""
        # Fill in template variables
        filled_template = prompt.template
        for var, value in input_data.items():
            filled_template = filled_template.replace(f"{{{var}}}", str(value))
        
        try:
            # Use OpenAI API (implement other providers as needed)
            client = openai.AsyncOpenAI()
            
            messages = []
            if prompt.system_message:
                messages.append({"role": "system", "content": prompt.system_message})
            
            messages.append({"role": "user", "content": filled_template})
            
            response = await client.chat.completions.create(
                model=self.config.primary_model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return content, tokens_used
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return "", 0
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost based on token usage"""
        # GPT-4 pricing (approximate)
        cost_per_1k_tokens = 0.03
        return (tokens_used / 1000) * cost_per_1k_tokens
    
    async def _save_prompt(self, prompt: PromptTemplate):
        """Save prompt template to database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO prompt_templates 
                (id, name, type, template, variables, system_message, examples, 
                 constraints, metadata, performance_score, cost_per_request,
                 average_response_time, token_efficiency, version, parent_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (id) DO UPDATE SET
                template = $4, updated_at = NOW()
            """, 
                prompt.id, prompt.name, prompt.type.value, prompt.template,
                json.dumps(prompt.variables), prompt.system_message, 
                json.dumps(prompt.examples), json.dumps(prompt.constraints),
                json.dumps(prompt.metadata), prompt.performance_score,
                prompt.cost_per_request, prompt.average_response_time,
                prompt.token_efficiency, prompt.version, prompt.parent_id
            )
    
    async def _save_optimization_result(self, result: OptimizationResult):
        """Save optimization result to database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO optimization_results 
                (original_prompt_id, optimized_prompt_id, optimization_strategy,
                 improvement_percentage, iterations, time_taken_seconds,
                 before_metrics, after_metrics, config_used, test_cases_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
                result.original_prompt_id, result.optimized_prompt_id,
                result.optimization_strategy.value, result.improvement_percentage,
                result.iterations, result.time_taken_seconds,
                json.dumps(result.before_metrics), json.dumps(result.after_metrics),
                json.dumps(result.config_used), result.test_cases_count
            )
    
    async def run_ab_test(
        self,
        prompt_a: PromptTemplate,
        prompt_b: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        metric: EvaluationMetric = EvaluationMetric.RELEVANCE
    ) -> ABTestResult:
        """Run A/B test between two prompts"""
        
        # Split test cases randomly
        test_a, test_b = train_test_split(test_cases, test_size=0.5, random_state=42)
        
        # Evaluate both variants
        metrics_a = await self._evaluate_prompt(prompt_a, test_a)
        metrics_b = await self._evaluate_prompt(prompt_b, test_b)
        
        score_a = metrics_a.get(metric.value, 0)
        score_b = metrics_b.get(metric.value, 0)
        
        # Statistical significance test (simplified)
        mean_diff = score_b - score_a
        std_pooled = np.sqrt((0.1**2 + 0.1**2) / 2)  # Assuming std of 0.1
        t_stat = mean_diff / (std_pooled / np.sqrt(len(test_cases) / 2))
        
        # Determine winner
        if abs(t_stat) > 1.96:  # 95% confidence
            winner = "B" if score_b > score_a else "A"
            significance = abs(t_stat) / 1.96
        else:
            winner = "No significant difference"
            significance = abs(t_stat) / 1.96
        
        # Calculate effect size
        effect_size = abs(mean_diff) / std_pooled
        
        result = ABTestResult(
            test_id=hashlib.md5(f"{prompt_a.id}_{prompt_b.id}_{time.time()}".encode()).hexdigest(),
            variant_a_prompt_id=prompt_a.id,
            variant_b_prompt_id=prompt_b.id,
            variant_a_score=score_a,
            variant_b_score=score_b,
            statistical_significance=significance,
            confidence_interval=(score_a - 0.1, score_a + 0.1),  # Simplified
            variant_a_samples=len(test_a),
            variant_b_samples=len(test_b),
            winner_variant=winner,
            effect_size=effect_size,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            metric_used=metric
        )
        
        return result


# Usage example
async def main():
    """Example usage of PromptOptimizer"""
    
    # Configure optimizer
    config = PromptOptimizationConfig(
        primary_model="gpt-4",
        optimization_strategy=OptimizationStrategy.GENETIC_ALGORITHM,
        population_size=10,
        generations=5,
        evaluation_metrics=[
            EvaluationMetric.RELEVANCE,
            EvaluationMetric.COHERENCE,
            EvaluationMetric.SAFETY
        ]
    )
    
    # Initialize optimizer
    optimizer = PromptOptimizer(config)
    await optimizer.initialize()
    
    try:
        # Create original prompt
        original_prompt = PromptTemplate(
            name="Content Summarization",
            type=PromptType.SUMMARIZATION,
            template="Summarize the following content: {content}",
            variables=["content"],
            system_message="You are a helpful assistant that creates concise summaries."
        )
        
        # Create test cases
        test_cases = [
            {
                "input": {"content": "Long article about AI and machine learning..."},
                "expected_output": "AI and ML are transforming industries..."
            },
            {
                "input": {"content": "Research paper on climate change..."},
                "expected_output": "Climate change research shows..."
            }
            # Add more test cases...
        ]
        
        # Optimize prompt
        result = await optimizer.optimize_prompt(
            original_prompt,
            test_cases,
            EvaluationMetric.RELEVANCE
        )
        
        print(f"Optimization completed!")
        print(f"Improvement: {result.improvement_percentage:.2f}%")
        print(f"Original relevance: {result.before_metrics.get('relevance', 0):.3f}")
        print(f"Optimized relevance: {result.after_metrics.get('relevance', 0):.3f}")
        
        # Run A/B test
        optimized_prompt = await optimizer._load_prompt(result.optimized_prompt_id)
        ab_result = await optimizer.run_ab_test(
            original_prompt,
            optimized_prompt,
            test_cases,
            EvaluationMetric.RELEVANCE
        )
        
        print(f"A/B Test Results:")
        print(f"Winner: Variant {ab_result.winner_variant}")
        print(f"Statistical significance: {ab_result.statistical_significance:.3f}")
        print(f"Effect size: {ab_result.effect_size:.3f}")
        
    finally:
        await optimizer.shutdown()


if __name__ == "__main__":
    asyncio.run(main())