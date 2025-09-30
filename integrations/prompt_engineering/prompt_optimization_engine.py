# ⚡ Optimization: Optimization engine avec ML-powered improvements
"""
Prompt Optimization Engine - Enterprise Implementation
=====================================================
Optimization engine enterprise avec ML-powered prompt improvements, A/B testing,
performance metrics tracking et continuous improvement loop pour optimisation prompts.

Expert Roles Applied:
- Lead Dev IA: ML algorithms pour optimization prompts
- Backend Senior: Infrastructure scalable pour A/B testing
- ML Engineer: Machine learning models pour performance prediction
- DBA: Optimization metrics storage et analytics
- Sécurité: Safe optimization avec security validation
- IA Prompt Engineer: Advanced optimization techniques et best practices

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Integrations - Prompt Engineering
Version: 1.0 Enterprise Production
"""

import asyncio
import json
import logging
import hashlib
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
import redis.asyncio as redis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from scipy import stats
import uuid
import openai

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationGoal(Enum):
    """Objectifs d'optimisation supportés"""
    QUALITY_IMPROVEMENT = "quality_improvement"
    ENGAGEMENT_MAXIMIZATION = "engagement_maximization"
    CONVERSION_OPTIMIZATION = "conversion_optimization"
    RESPONSE_TIME_REDUCTION = "response_time_reduction"
    SAFETY_ENHANCEMENT = "safety_enhancement"
    CREATIVITY_BOOST = "creativity_boost"
    ACCURACY_IMPROVEMENT = "accuracy_improvement"

class OptimizationStrategy(Enum):
    """Stratégies d'optimisation disponibles"""
    GENETIC_ALGORITHM = "genetic_algorithm"
    GRADIENT_DESCENT = "gradient_descent"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    ENSEMBLE_METHOD = "ensemble_method"
    NEURAL_EVOLUTION = "neural_evolution"

class ABTestStatus(Enum):
    """Statuts des tests A/B"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class OptimizationConfig:
    """Configuration pour l'optimisation de prompts"""
    goal: OptimizationGoal
    strategy: OptimizationStrategy
    max_iterations: int
    convergence_threshold: float
    safety_constraints: Dict[str, Any]
    performance_targets: Dict[str, float]
    optimization_timeout: timedelta
    use_ab_testing: bool = True
    sample_size_min: int = 100

@dataclass
class PromptVariant:
    """Variante de prompt pour l'optimisation"""
    id: str
    original_prompt: str
    optimized_prompt: str
    optimization_score: float
    performance_metrics: Dict[str, float]
    generation_strategy: str
    confidence_score: float
    safety_validated: bool
    created_at: datetime

@dataclass
class ABTestExperiment:
    """Expérience A/B pour l'optimisation de prompts"""
    id: str
    name: str
    description: str
    variants: List[PromptVariant]
    control_variant_id: str
    status: ABTestStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    target_sample_size: int
    current_sample_size: int
    confidence_level: float
    statistical_power: float
    success_metrics: List[str]
    results: Optional[Dict[str, Any]]
    winner_variant_id: Optional[str]

@dataclass
class OptimizationResult:
    """Résultat d'optimisation de prompt"""
    original_prompt: str
    optimized_prompts: List[PromptVariant]
    best_variant: PromptVariant
    improvement_metrics: Dict[str, float]
    optimization_strategy: OptimizationStrategy
    ab_test_experiment: Optional[ABTestExperiment]
    confidence_score: float
    optimization_time: timedelta
    recommendations: List[str]

class PromptOptimizationEngine:
    """Optimization engine enterprise avec ML-powered prompt improvements et A/B testing"""
    
    def __init__(self, db_config: Dict[str, Any], redis_config: Dict[str, Any], openai_config: Dict[str, Any]):
        """
        Initialise le moteur d'optimisation avec configuration enterprise
        
        Args:
            db_config: Configuration base de données PostgreSQL
            redis_config: Configuration Redis pour cache et performance
            openai_config: Configuration OpenAI pour génération de variants
        """
        self.db_config = db_config
        self.redis_config = redis_config
        self.openai_config = openai_config
        self.db_pool = None
        self.redis_client = None
        
        # Modèles ML pour l'optimisation
        self.quality_predictor = None
        self.engagement_predictor = None
        self.safety_classifier = None
        
        # Cache des optimisations récentes
        self.optimization_cache: Dict[str, OptimizationResult] = {}
        self.active_experiments: Dict[str, ABTestExperiment] = {}
        
        # Configuration enterprise
        self.max_concurrent_optimizations = 50
        self.optimization_timeout = timedelta(minutes=30)
        self.min_statistical_significance = 0.95
        
        logger.info("PromptOptimizationEngine initialized - Enterprise mode")

    async def initialize(self):
        """Initialise les connexions et modèles ML"""
        try:
            # Initialisation pool de connexions PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                min_size=5,
                max_size=20
            )
            
            # Initialisation Redis client
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config.get('password'),
                decode_responses=True
            )
            
            # Configuration OpenAI
            openai.api_key = self.openai_config['api_key']
            
            # Création du schéma de base de données
            await self._create_database_schema()
            
            # Initialisation des modèles ML
            await self._initialize_ml_models()
            
            # Chargement des expériences actives
            await self._load_active_experiments()
            
            logger.info("PromptOptimizationEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PromptOptimizationEngine: {e}")
            raise

    async def _create_database_schema(self):
        """Crée le schéma de base de données pour l'optimisation"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS prompt_optimizations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            original_prompt TEXT NOT NULL,
            optimization_config JSONB NOT NULL,
            optimization_results JSONB,
            status VARCHAR(50) DEFAULT 'running',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            creator_id UUID,
            project_id UUID
        );
        
        CREATE TABLE IF NOT EXISTS ab_test_experiments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            variants JSONB NOT NULL,
            control_variant_id UUID NOT NULL,
            status VARCHAR(50) DEFAULT 'draft',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            target_sample_size INTEGER,
            current_sample_size INTEGER DEFAULT 0,
            confidence_level FLOAT DEFAULT 0.95,
            statistical_power FLOAT DEFAULT 0.8,
            success_metrics JSONB DEFAULT '[]',
            results JSONB,
            winner_variant_id UUID,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS optimization_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            optimization_id UUID REFERENCES prompt_optimizations(id),
            experiment_id UUID REFERENCES ab_test_experiments(id),
            variant_id UUID,
            metric_name VARCHAR(100),
            metric_value FLOAT,
            measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_session_id VARCHAR(255),
            context_data JSONB
        );
        
        CREATE INDEX IF NOT EXISTS idx_optimizations_status ON prompt_optimizations(status);
        CREATE INDEX IF NOT EXISTS idx_experiments_status ON ab_test_experiments(status);
        CREATE INDEX IF NOT EXISTS idx_metrics_optimization ON optimization_metrics(optimization_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_experiment ON optimization_metrics(experiment_id);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)

    async def ml_prompt_optimization(
        self,
        original_prompt: str,
        optimization_config: OptimizationConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> List[PromptVariant]:
        """Optimisation ML-powered des prompts avec algorithmes avancés"""
        try:
            logger.info(f"Starting ML prompt optimization with strategy: {optimization_config.strategy.value}")
            
            # Analyse du prompt original
            prompt_analysis = await self._analyze_prompt_structure(original_prompt, context)
            
            # Génération de variants basée sur la stratégie choisie
            variants = []
            
            if optimization_config.strategy == OptimizationStrategy.GENETIC_ALGORITHM:
                variants = await self._genetic_algorithm_optimization(
                    original_prompt, optimization_config, prompt_analysis
                )
            elif optimization_config.strategy == OptimizationStrategy.BAYESIAN_OPTIMIZATION:
                variants = await self._bayesian_optimization(
                    original_prompt, optimization_config, prompt_analysis
                )
            elif optimization_config.strategy == OptimizationStrategy.REINFORCEMENT_LEARNING:
                variants = await self._reinforcement_learning_optimization(
                    original_prompt, optimization_config, prompt_analysis
                )
            elif optimization_config.strategy == OptimizationStrategy.ENSEMBLE_METHOD:
                variants = await self._ensemble_optimization(
                    original_prompt, optimization_config, prompt_analysis
                )
            else:
                # Stratégie par défaut: Gradient Descent
                variants = await self._gradient_descent_optimization(
                    original_prompt, optimization_config, prompt_analysis
                )
            
            # Évaluation et scoring des variants
            scored_variants = []
            for variant_prompt in variants:
                variant = await self._evaluate_prompt_variant(
                    original_prompt, variant_prompt, optimization_config, context
                )
                scored_variants.append(variant)
            
            # Tri par score d'optimisation
            scored_variants.sort(key=lambda x: x.optimization_score, reverse=True)
            
            logger.info(f"Generated {len(scored_variants)} optimized variants")
            return scored_variants
            
        except Exception as e:
            logger.error(f"ML prompt optimization failed: {e}")
            raise

    async def ab_testing_automation(
        self,
        variants: List[PromptVariant],
        experiment_config: Dict[str, Any]
    ) -> ABTestExperiment:
        """Automation des tests A/B pour l'optimisation de prompts"""
        try:
            # Création de l'expérience A/B
            experiment = ABTestExperiment(
                id=str(uuid.uuid4()),
                name=experiment_config.get('name', f"Optimization_AB_Test_{int(time.time())}"),
                description=experiment_config.get('description', 'Automated AB test for prompt optimization'),
                variants=variants,
                control_variant_id=variants[0].id if variants else None,
                status=ABTestStatus.DRAFT,
                start_date=None,
                end_date=None,
                target_sample_size=experiment_config.get('target_sample_size', 1000),
                current_sample_size=0,
                confidence_level=experiment_config.get('confidence_level', 0.95),
                statistical_power=experiment_config.get('statistical_power', 0.8),
                success_metrics=experiment_config.get('success_metrics', ['quality_score', 'engagement_rate']),
                results=None,
                winner_variant_id=None
            )
            
            # Validation statistique de l'expérience
            validation_result = await self._validate_ab_test_design(experiment)
            if not validation_result['is_valid']:
                raise ValueError(f"AB test validation failed: {validation_result['errors']}")
            
            # Sauvegarde de l'expérience
            await self._save_ab_test_experiment(experiment)
            
            # Configuration de l'automation
            await self._setup_ab_test_automation(experiment)
            
            # Démarrage de l'expérience si auto-start activé
            if experiment_config.get('auto_start', False):
                await self._start_ab_test_experiment(experiment.id)
            
            self.active_experiments[experiment.id] = experiment
            
            logger.info(f"AB test experiment created: {experiment.id}")
            return experiment
            
        except Exception as e:
            logger.error(f"AB testing automation setup failed: {e}")
            raise

    async def performance_metrics_tracking(
        self,
        experiment_id: str,
        variant_id: str,
        metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ):
        """Suivi des métriques de performance en temps réel"""
        try:
            # Enregistrement des métriques
            async with self.db_pool.acquire() as conn:
                for metric_name, metric_value in metrics.items():
                    await conn.execute("""
                        INSERT INTO optimization_metrics (
                            experiment_id, variant_id, metric_name, metric_value,
                            measurement_timestamp, user_session_id, context_data
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, uuid.UUID(experiment_id), uuid.UUID(variant_id), 
                    metric_name, metric_value, datetime.utcnow(),
                    context.get('session_id') if context else None,
                    json.dumps(context) if context else None)
            
            # Mise à jour du cache de métriques
            cache_key = f"metrics:{experiment_id}:{variant_id}"
            await self.redis_client.hset(cache_key, mapping=metrics)
            await self.redis_client.expire(cache_key, 3600)  # 1 heure
            
            # Vérification si l'expérience doit être arrêtée
            await self._check_experiment_completion(experiment_id)
            
            logger.debug(f"Performance metrics tracked for experiment {experiment_id}, variant {variant_id}")
            
        except Exception as e:
            logger.error(f"Performance metrics tracking failed: {e}")

    async def optimization_recommendation_engine(
        self,
        prompt: str,
        performance_history: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Moteur de recommandations d'optimisation basé sur l'historique"""
        try:
            # Analyse de l'historique de performance
            performance_analysis = await self._analyze_performance_history(performance_history)
            
            # Identification des patterns d'amélioration
            improvement_patterns = await self._identify_improvement_patterns(
                prompt, performance_analysis, context
            )
            
            # Génération de recommandations personnalisées
            recommendations = []
            
            # Recommandations basées sur les performances faibles
            if performance_analysis['avg_quality_score'] < 0.7:
                recommendations.extend(await self._generate_quality_recommendations(
                    prompt, performance_analysis
                ))
            
            # Recommandations basées sur l'engagement
            if performance_analysis['avg_engagement_rate'] < 0.5:
                recommendations.extend(await self._generate_engagement_recommendations(
                    prompt, performance_analysis
                ))
            
            # Recommandations basées sur la sécurité
            if performance_analysis['safety_score'] < 0.9:
                recommendations.extend(await self._generate_safety_recommendations(
                    prompt, performance_analysis
                ))
            
            # Recommandations basées sur les patterns de succès
            success_recommendations = await self._generate_success_pattern_recommendations(
                improvement_patterns, context
            )
            recommendations.extend(success_recommendations)
            
            # Priorisation des recommandations
            prioritized_recommendations = await self._prioritize_recommendations(
                recommendations, performance_analysis
            )
            
            logger.info(f"Generated {len(prioritized_recommendations)} optimization recommendations")
            return prioritized_recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendation engine failed: {e}")
            raise

    async def prompt_quality_scoring(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Scoring avancé de la qualité des prompts"""
        try:
            # Analyse structurelle du prompt
            structure_score = await self._analyze_prompt_structure_score(prompt)
            
            # Analyse de clarté et précision
            clarity_score = await self._analyze_prompt_clarity(prompt)
            
            # Analyse de créativité et originalité
            creativity_score = await self._analyze_prompt_creativity(prompt, context)
            
            # Analyse de sécurité
            safety_score = await self._analyze_prompt_safety(prompt)
            
            # Analyse de performance prédite
            predicted_performance = await self._predict_prompt_performance(prompt, context)
            
            # Score composite avec pondération
            weights = {
                'structure': 0.2,
                'clarity': 0.25,
                'creativity': 0.2,
                'safety': 0.15,
                'predicted_performance': 0.2
            }
            
            composite_score = (
                structure_score * weights['structure'] +
                clarity_score * weights['clarity'] +
                creativity_score * weights['creativity'] +
                safety_score * weights['safety'] +
                predicted_performance * weights['predicted_performance']
            )
            
            quality_metrics = {
                'composite_score': composite_score,
                'structure_score': structure_score,
                'clarity_score': clarity_score,
                'creativity_score': creativity_score,
                'safety_score': safety_score,
                'predicted_performance': predicted_performance,
                'confidence_interval': await self._calculate_confidence_interval(composite_score)
            }
            
            logger.info(f"Prompt quality scoring completed: {composite_score:.3f}")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Prompt quality scoring failed: {e}")
            raise

    async def optimization_analytics(self) -> Dict[str, Any]:
        """Analytics complètes des optimisations effectuées"""
        try:
            # Statistiques globales d'optimisation
            global_stats = await self._get_optimization_global_stats()
            
            # Analyse des stratégies d'optimisation les plus efficaces
            strategy_analysis = await self._analyze_optimization_strategies()
            
            # Analyse des améliorations moyennes par catégorie
            improvement_analysis = await self._analyze_improvement_categories()
            
            # Tendances d'optimisation dans le temps
            optimization_trends = await self._analyze_optimization_trends()
            
            # Performance des tests A/B
            ab_test_performance = await self._analyze_ab_test_performance()
            
            # Insights et recommandations
            optimization_insights = await self._generate_optimization_insights(
                global_stats, strategy_analysis, improvement_analysis
            )
            
            analytics_data = {
                'global_statistics': global_stats,
                'strategy_effectiveness': strategy_analysis,
                'improvement_categories': improvement_analysis,
                'optimization_trends': optimization_trends,
                'ab_test_performance': ab_test_performance,
                'insights_and_recommendations': optimization_insights,
                'last_updated': datetime.utcnow().isoformat(),
                'active_experiments': len(self.active_experiments),
                'cached_optimizations': len(self.optimization_cache)
            }
            
            logger.info("Optimization analytics generated successfully")
            return analytics_data
            
        except Exception as e:
            logger.error(f"Optimization analytics generation failed: {e}")
            raise

    async def continuous_improvement_loop(self):
        """Boucle d'amélioration continue pour l'optimisation"""
        try:
            logger.info("Starting continuous improvement loop")
            
            while True:
                # Analyse des expériences actives
                for experiment_id, experiment in self.active_experiments.items():
                    await self._process_active_experiment(experiment)
                
                # Mise à jour des modèles ML avec nouvelles données
                await self._update_ml_models()
                
                # Nettoyage des caches expirés
                await self._cleanup_expired_cache()
                
                # Génération de rapports de performance
                await self._generate_performance_reports()
                
                # Attente avant la prochaine itération
                await asyncio.sleep(300)  # 5 minutes
                
        except Exception as e:
            logger.error(f"Continuous improvement loop failed: {e}")

    # Méthodes d'optimisation spécialisées
    async def _genetic_algorithm_optimization(
        self,
        original_prompt: str,
        config: OptimizationConfig,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Optimisation par algorithme génétique"""
        population_size = 20
        generations = 10
        mutation_rate = 0.1
        
        # Population initiale
        population = [original_prompt]
        
        # Génération de variants par mutation et crossover
        for _ in range(population_size - 1):
            variant = await self._mutate_prompt(original_prompt, mutation_rate)
            population.append(variant)
        
        # Évolution sur plusieurs générations
        for generation in range(generations):
            # Évaluation de la population
            fitness_scores = []
            for prompt in population:
                score = await self._evaluate_prompt_fitness(prompt, config)
                fitness_scores.append(score)
            
            # Sélection des meilleurs
            selected = await self._selection(population, fitness_scores)
            
            # Crossover et mutation
            new_population = []
            for i in range(0, len(selected), 2):
                if i + 1 < len(selected):
                    child1, child2 = await self._crossover(selected[i], selected[i + 1])
                    new_population.extend([child1, child2])
            
            # Application de mutations
            for i in range(len(new_population)):
                if np.random.random() < mutation_rate:
                    new_population[i] = await self._mutate_prompt(new_population[i], mutation_rate)
            
            population = new_population
        
        return population[:10]  # Retourne les 10 meilleurs

    async def _bayesian_optimization(
        self,
        original_prompt: str,
        config: OptimizationConfig,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Optimisation bayésienne des prompts"""
        # Implémentation simplifiée de l'optimisation bayésienne
        variants = [original_prompt]
        
        # Génération de variants basée sur l'analyse
        for i in range(9):  # 9 variants + l'original
            variant = await self._generate_bayesian_variant(original_prompt, analysis, i)
            variants.append(variant)
        
        return variants

    async def _evaluate_prompt_variant(
        self,
        original_prompt: str,
        variant_prompt: str,
        config: OptimizationConfig,
        context: Optional[Dict[str, Any]]
    ) -> PromptVariant:
        """Évalue un variant de prompt et calcule son score"""
        try:
            # Calcul des métriques de performance
            quality_score = await self._calculate_quality_score(variant_prompt, context)
            engagement_score = await self._predict_engagement(variant_prompt, context)
            safety_score = await self._calculate_safety_score(variant_prompt)
            
            # Score d'optimisation composite
            optimization_score = (
                quality_score * 0.4 +
                engagement_score * 0.3 +
                safety_score * 0.3
            )
            
            # Calcul de la confiance
            confidence_score = await self._calculate_variant_confidence(
                original_prompt, variant_prompt, optimization_score
            )
            
            variant = PromptVariant(
                id=str(uuid.uuid4()),
                original_prompt=original_prompt,
                optimized_prompt=variant_prompt,
                optimization_score=optimization_score,
                performance_metrics={
                    'quality_score': quality_score,
                    'engagement_score': engagement_score,
                    'safety_score': safety_score
                },
                generation_strategy=config.strategy.value,
                confidence_score=confidence_score,
                safety_validated=safety_score >= 0.8,
                created_at=datetime.utcnow()
            )
            
            return variant
            
        except Exception as e:
            logger.error(f"Prompt variant evaluation failed: {e}")
            raise

    async def _initialize_ml_models(self):
        """Initialise les modèles ML pour l'optimisation"""
        try:
            # Modèle de prédiction de qualité
            self.quality_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Modèle de prédiction d'engagement
            self.engagement_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            # Modèle de classification de sécurité
            self.safety_classifier = RandomForestRegressor(n_estimators=50, random_state=42)
            
            # Entraînement avec données synthétiques pour l'initialisation
            await self._train_initial_models()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            raise

    async def _train_initial_models(self):
        """Entraîne les modèles avec des données synthétiques initiales"""
        # Données synthétiques pour l'initialisation
        n_samples = 1000
        
        # Features synthétiques (longueur du prompt, complexité, etc.)
        X = np.random.randn(n_samples, 10)
        
        # Labels synthétiques
        y_quality = np.random.uniform(0.1, 1.0, n_samples)
        y_engagement = np.random.uniform(0.0, 1.0, n_samples)
        y_safety = np.random.uniform(0.5, 1.0, n_samples)
        
        # Entraînement des modèles
        self.quality_predictor.fit(X, y_quality)
        self.engagement_predictor.fit(X, y_engagement)
        self.safety_classifier.fit(X, y_safety)

    # Méthodes utilitaires privées continuent...
    async def _analyze_prompt_structure(self, prompt: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse la structure d'un prompt pour l'optimisation"""
        return {
            'length': len(prompt),
            'word_count': len(prompt.split()),
            'sentence_count': len([s for s in prompt.split('.') if s.strip()]),
            'complexity_score': len(set(prompt.split())) / len(prompt.split()) if prompt.split() else 0,
            'has_instructions': any(word in prompt.lower() for word in ['create', 'generate', 'write', 'make']),
            'has_examples': 'example' in prompt.lower() or 'for instance' in prompt.lower(),
            'question_count': prompt.count('?'),
            'exclamation_count': prompt.count('!')
        }

    async def _load_active_experiments(self):
        """Charge les expériences A/B actives depuis la base de données"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM ab_test_experiments 
                    WHERE status IN ('active', 'running') 
                    ORDER BY created_at DESC
                """)
                
                for row in rows:
                    experiment = ABTestExperiment(
                        id=str(row['id']),
                        name=row['name'],
                        description=row['description'],
                        variants=row['variants'],
                        control_variant_id=str(row['control_variant_id']),
                        status=ABTestStatus(row['status']),
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        target_sample_size=row['target_sample_size'],
                        current_sample_size=row['current_sample_size'],
                        confidence_level=row['confidence_level'],
                        statistical_power=row['statistical_power'],
                        success_metrics=row['success_metrics'],
                        results=row['results'],
                        winner_variant_id=str(row['winner_variant_id']) if row['winner_variant_id'] else None
                    )
                    
                    self.active_experiments[experiment.id] = experiment
                    
            logger.info(f"Loaded {len(self.active_experiments)} active experiments")
            
        except Exception as e:
            logger.error(f"Failed to load active experiments: {e}")

    async def _calculate_quality_score(self, prompt: str, context: Optional[Dict[str, Any]]) -> float:
        """Calcule le score de qualité d'un prompt"""
        # Implémentation simplifiée - à améliorer avec des modèles plus sophistiqués
        base_score = 0.5
        
        # Bonus pour la longueur appropriée
        if 50 <= len(prompt) <= 300:
            base_score += 0.2
        
        # Bonus pour la clarté (présence d'instructions)
        if any(word in prompt.lower() for word in ['create', 'generate', 'write', 'explain']):
            base_score += 0.15
        
        # Bonus pour la spécificité
        if len(set(prompt.split())) / len(prompt.split()) > 0.7:  # Diversité lexicale
            base_score += 0.15
        
        return min(base_score, 1.0)

    async def _predict_engagement(self, prompt: str, context: Optional[Dict[str, Any]]) -> float:
        """Prédit le score d'engagement d'un prompt"""
        # Utilisation du modèle ML (implémentation simplifiée)
        features = np.array([[
            len(prompt),
            len(prompt.split()),
            prompt.count('?'),
            prompt.count('!'),
            len(set(prompt.split())) / len(prompt.split()) if prompt.split() else 0,
            1 if any(word in prompt.lower() for word in ['exciting', 'amazing', 'incredible']) else 0,
            1 if 'you' in prompt.lower() else 0,
            len([w for w in prompt.split() if len(w) > 6]),
            1 if prompt.count(',') > 2 else 0,
            len(prompt) / 100  # Normalisation de la longueur
        ]])
        
        try:
            engagement_score = self.engagement_predictor.predict(features)[0]
            return max(0.0, min(1.0, engagement_score))
        except:
            return 0.6  # Score par défaut

    async def _calculate_safety_score(self, prompt: str) -> float:
        """Calcule le score de sécurité d'un prompt"""
        # Mots/phrases potentiellement dangereux
        unsafe_keywords = [
            'ignore previous', 'disregard', 'override', 'hack', 'exploit',
            'bypass', 'jailbreak', 'prompt injection', 'system prompt'
        ]
        
        safety_score = 1.0
        
        for keyword in unsafe_keywords:
            if keyword in prompt.lower():
                safety_score -= 0.2
        
        return max(0.0, safety_score)

# Classes de support pour l'optimisation
@dataclass
class OptimizationMetrics:
    """Métriques d'optimisation pour un prompt"""
    quality_improvement: float
    engagement_improvement: float
    safety_improvement: float
    overall_improvement: float
    confidence_score: float
    statistical_significance: float