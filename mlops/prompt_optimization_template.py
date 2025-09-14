"""
Prompt Optimization Template module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🤖 Prompt Optimization Template - Enterprise MLOps Platform
IA Prompt Engineer Expertise: Optimisation prompts avancée avec fine-tuning

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import sqlite3
import hashlib
import re
from collections import defaultdict, deque
import statistics
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptOptimizationStrategy(Enum):
    """Stratégies d'optimisation de prompts"""
    A_B_TESTING = "a_b_testing"
    GENETIC_ALGORITHM = "genetic_algorithm"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    GRADIENT_BASED = "gradient_based"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    ENSEMBLE_OPTIMIZATION = "ensemble_optimization"

class CreatorPromptType(Enum):
    """Types de prompts par créateur"""
    MUSICIAN_COMPOSITION = "musician_composition"
    MUSICIAN_LYRICS_GEN = "musician_lyrics_generation"
    MUSICIAN_STYLE_ANALYSIS = "musician_style_analysis"
    BLOGGER_CONTENT_GEN = "blogger_content_generation"
    BLOGGER_SEO_OPTIMIZATION = "blogger_seo_optimization"
    BLOGGER_HEADLINE_GEN = "blogger_headline_generation"
    PHOTOGRAPHER_CAPTION_GEN = "photographer_caption_generation"
    PHOTOGRAPHER_STYLE_GUIDE = "photographer_style_guide"
    PHOTOGRAPHER_COMPOSITION_TIPS = "photographer_composition_tips"
    INFLUENCER_POST_GEN = "influencer_post_generation"
    INFLUENCER_ENGAGEMENT_OPT = "influencer_engagement_optimization"
    INFLUENCER_TREND_ANALYSIS = "influencer_trend_analysis"
    COMEDIAN_JOKE_GEN = "comedian_joke_generation"
    COMEDIAN_TIMING_OPT = "comedian_timing_optimization"
    COMEDIAN_AUDIENCE_ANALYSIS = "comedian_audience_analysis"

class PromptMetric(Enum):
    """Métriques d'évaluation des prompts"""
    RELEVANCE_SCORE = "relevance_score"
    CREATIVITY_SCORE = "creativity_score"
    COHERENCE_SCORE = "coherence_score"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    TECHNICAL_ACCURACY = "technical_accuracy"
    BRAND_CONSISTENCY = "brand_consistency"
    ORIGINALITY_SCORE = "originality_score"
    CONVERSION_RATE = "conversion_rate"

@dataclass
class PromptTemplate:
    """Template de prompt avec métadonnées"""
    template_id: str
    prompt_type: CreatorPromptType
    template_text: str
    variables: List[str]
    optimization_target: PromptMetric
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    performance_scores: Dict[PromptMetric, float] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptExperiment:
    """Expérience d'optimisation de prompt"""
    experiment_id: str
    base_template: PromptTemplate
    candidate_templates: List[PromptTemplate]
    optimization_strategy: PromptOptimizationStrategy
    target_metric: PromptMetric
    test_cases: List[Dict[str, Any]]
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "running"
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    best_template_id: Optional[str] = None
    improvement_percentage: float = 0.0

@dataclass
class PromptEvaluation:
    """Évaluation d'un prompt"""
    evaluation_id: str
    template_id: str
    input_variables: Dict[str, Any]
    generated_output: str
    scores: Dict[PromptMetric, float]
    human_feedback: Optional[Dict[str, Any]] = None
    evaluation_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class PromptOptimizationTemplate:
    """
    Template d'optimisation de prompts enterprise pour créateurs
    
    Fonctionnalités:
    - Optimisation automatique multi-stratégies
    - A/B testing intelligent de prompts
    - Métriques avancées par type de créateur
    - Fine-tuning basé sur performance
    - Analyse de feedback utilisateur
    - Génération de variants automatique
    """
    
    def __init__(self,
                 db_path -> None: str = "/tmp/prompt_optimization.db",
                 evaluation_cache_size -> None: int = 1000) -> None:
        self.db_path = db_path
        self.evaluation_cache_size = evaluation_cache_size
        
        # Stockage des templates et expériences
        self.templates: Dict[str, PromptTemplate] = {}
        self.experiments: Dict[str, PromptExperiment] = {}
        self.evaluations: Dict[str, List[PromptEvaluation]] = defaultdict(list)
        
        # Cache des évaluations récentes
        self.evaluation_cache = deque(maxlen=evaluation_cache_size)
        
        # Générateurs de variants par type de créateur
        self.variant_generators = {
            CreatorPromptType.MUSICIAN_COMPOSITION: self._generate_music_variants,
            CreatorPromptType.BLOGGER_CONTENT_GEN: self._generate_blog_variants,
            CreatorPromptType.PHOTOGRAPHER_CAPTION_GEN: self._generate_photo_variants,
            CreatorPromptType.INFLUENCER_POST_GEN: self._generate_influencer_variants,
            CreatorPromptType.COMEDIAN_JOKE_GEN: self._generate_comedy_variants
        }
        
        # Évaluateurs par métrique
        self.metric_evaluators = {
            PromptMetric.RELEVANCE_SCORE: self._evaluate_relevance,
            PromptMetric.CREATIVITY_SCORE: self._evaluate_creativity,
            PromptMetric.COHERENCE_SCORE: self._evaluate_coherence,
            PromptMetric.ENGAGEMENT_POTENTIAL: self._evaluate_engagement,
            PromptMetric.TECHNICAL_ACCURACY: self._evaluate_technical_accuracy,
            PromptMetric.BRAND_CONSISTENCY: self._evaluate_brand_consistency,
            PromptMetric.ORIGINALITY_SCORE: self._evaluate_originality
        }
        
        # Callbacks
        self.optimization_callbacks: List[Callable] = []
        self.evaluation_callbacks: List[Callable] = []
        
        self._setup_database()
        logger.info("🤖 PromptOptimizationTemplate initialized for enterprise prompt engineering")
    
    def _setup_database(self) -> None:
        """Initialisation de la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des templates
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_templates (
                        template_id TEXT PRIMARY KEY,
                        prompt_type TEXT NOT NULL,
                        template_text TEXT NOT NULL,
                        variables TEXT NOT NULL,
                        optimization_target TEXT NOT NULL,
                        version TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        performance_scores TEXT,
                        usage_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0,
                        metadata TEXT
                    )
                """)
                
                # Table des expériences
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_experiments (
                        experiment_id TEXT PRIMARY KEY,
                        base_template_id TEXT NOT NULL,
                        optimization_strategy TEXT NOT NULL,
                        target_metric TEXT NOT NULL,
                        status TEXT DEFAULT 'running',
                        started_at TEXT NOT NULL,
                        completed_at TEXT,
                        best_template_id TEXT,
                        improvement_percentage REAL DEFAULT 0.0,
                        results TEXT
                    )
                """)
                
                # Table des évaluations
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_evaluations (
                        evaluation_id TEXT PRIMARY KEY,
                        template_id TEXT NOT NULL,
                        input_variables TEXT NOT NULL,
                        generated_output TEXT NOT NULL,
                        scores TEXT NOT NULL,
                        human_feedback TEXT,
                        evaluation_time_ms REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    async def create_template(self,
                            template_id: str,
                            prompt_type: CreatorPromptType,
                            template_text: str,
                            variables: List[str],
                            optimization_target: PromptMetric,
                            metadata: Optional[Dict[str, Any]] = None) -> PromptTemplate:
        """Création d'un nouveau template de prompt"""
        try:
            template = PromptTemplate(
                template_id=template_id,
                prompt_type=prompt_type,
                template_text=template_text,
                variables=variables,
                optimization_target=optimization_target,
                metadata=metadata or {}
            )
            
            # Stockage en mémoire et DB
            self.templates[template_id] = template
            await self._save_template_to_db(template)
            
            logger.info(f"📝 Template created: {template_id} for {prompt_type.value}")
            return template
            
        except Exception as e:
            logger.error(f"❌ Error creating template {template_id}: {e}")
            raise
    
    async def optimize_template(self,
                              template_id: str,
                              optimization_strategy: PromptOptimizationStrategy,
                              test_cases: List[Dict[str, Any]],
                              num_variants: int = 5) -> PromptExperiment:
        """Optimisation d'un template avec stratégie donnée"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
            
            base_template = self.templates[template_id]
            experiment_id = f"exp_{template_id}_{int(datetime.now().timestamp())}"
            
            # Génération de variants
            candidate_templates = await self._generate_template_variants(
                base_template, num_variants
            )
            
            # Création de l'expérience
            experiment = PromptExperiment(
                experiment_id=experiment_id,
                base_template=base_template,
                candidate_templates=candidate_templates,
                optimization_strategy=optimization_strategy,
                target_metric=base_template.optimization_target,
                test_cases=test_cases
            )
            
            self.experiments[experiment_id] = experiment
            
            # Exécution de l'optimisation selon la stratégie
            if optimization_strategy == PromptOptimizationStrategy.A_B_TESTING:
                await self._run_ab_testing(experiment)
            elif optimization_strategy == PromptOptimizationStrategy.GENETIC_ALGORITHM:
                await self._run_genetic_optimization(experiment)
            elif optimization_strategy == PromptOptimizationStrategy.BAYESIAN_OPTIMIZATION:
                await self._run_bayesian_optimization(experiment)
            else:
                # Stratégie par défaut: évaluation simple
                await self._run_simple_evaluation(experiment)
            
            # Finalisation
            experiment.status = "completed"
            experiment.completed_at = datetime.now()
            
            # Sauvegarde
            await self._save_experiment_to_db(experiment)
            
            # Callbacks
            for callback in self.optimization_callbacks:
                try:
                    await callback(experiment)
                except Exception as e:
                    logger.error(f"❌ Optimization callback error: {e}")
            
            logger.info(f"🔬 Optimization completed: {experiment_id}")
            return experiment
            
        except Exception as e:
            logger.error(f"❌ Error optimizing template {template_id}: {e}")
            raise
    
    async def _generate_template_variants(self,
                                        base_template: PromptTemplate,
                                        num_variants: int) -> List[PromptTemplate]:
        """Génération de variants d'un template"""
        try:
            variants = []
            
            # Utilisation du générateur spécialisé si disponible
            if base_template.prompt_type in self.variant_generators:
                generator = self.variant_generators[base_template.prompt_type]
                variants = await generator(base_template, num_variants)
            else:
                # Génération générique
                variants = await self._generate_generic_variants(base_template, num_variants)
            
            return variants
            
        except Exception as e:
            logger.error(f"❌ Error generating variants: {e}")
            return []
    
    async def _generate_music_variants(self,
                                     base_template: PromptTemplate,
                                     num_variants: int) -> List[PromptTemplate]:
        """Génération de variants pour prompts musicaux"""
        variants = []
        
        music_variations = [
            "Create a {genre} composition with {mood} atmosphere",
            "Generate {genre} music with {mood} feeling and {tempo} tempo",
            "Compose a {genre} piece that evokes {mood} emotions",
            "Write a {genre} song with {mood} vibes for {target_audience}",
            "Develop a {genre} track with {mood} energy and {instrument} focus"
        ]
        
        for i, variation in enumerate(music_variations[:num_variants]):
            variant_id = f"{base_template.template_id}_music_v{i+1}"
            variant = PromptTemplate(
                template_id=variant_id,
                prompt_type=base_template.prompt_type,
                template_text=variation,
                variables=["genre", "mood", "tempo", "target_audience", "instrument"],
                optimization_target=base_template.optimization_target,
                version=f"{base_template.version}_variant_{i+1}"
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_blog_variants(self,
                                    base_template: PromptTemplate,
                                    num_variants: int) -> List[PromptTemplate]:
        """Génération de variants pour prompts de blog"""
        variants = []
        
        blog_variations = [
            "Write an engaging {post_type} about {topic} for {target_audience}",
            "Create a {tone} {post_type} on {topic} with SEO optimization",
            "Generate a {length} {post_type} about {topic} with {call_to_action}",
            "Develop a {tone} article on {topic} that {engagement_goal}",
            "Craft a {post_type} about {topic} with {writing_style} approach"
        ]
        
        for i, variation in enumerate(blog_variations[:num_variants]):
            variant_id = f"{base_template.template_id}_blog_v{i+1}"
            variant = PromptTemplate(
                template_id=variant_id,
                prompt_type=base_template.prompt_type,
                template_text=variation,
                variables=["post_type", "topic", "target_audience", "tone", "length", "call_to_action", "engagement_goal", "writing_style"],
                optimization_target=base_template.optimization_target,
                version=f"{base_template.version}_variant_{i+1}"
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_photo_variants(self,
                                     base_template: PromptTemplate,
                                     num_variants: int) -> List[PromptTemplate]:
        """Génération de variants pour prompts photo"""
        variants = []
        
        photo_variations = [
            "Create a {style} caption for this {subject} photo with {mood} tone",
            "Write an engaging caption for {subject} image using {hashtag_strategy}",
            "Generate a {length} caption for {subject} photo that {engagement_goal}",
            "Craft a {tone} description for this {subject} with {call_to_action}",
            "Develop a caption for {subject} photo emphasizing {key_element}"
        ]
        
        for i, variation in enumerate(photo_variations[:num_variants]):
            variant_id = f"{base_template.template_id}_photo_v{i+1}"
            variant = PromptTemplate(
                template_id=variant_id,
                prompt_type=base_template.prompt_type,
                template_text=variation,
                variables=["style", "subject", "mood", "tone", "hashtag_strategy", "length", "engagement_goal", "call_to_action", "key_element"],
                optimization_target=base_template.optimization_target,
                version=f"{base_template.version}_variant_{i+1}"
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_influencer_variants(self,
                                          base_template: PromptTemplate,
                                          num_variants: int) -> List[PromptTemplate]:
        """Génération de variants pour prompts influenceur"""
        variants = []
        
        influencer_variations = [
            "Create a {platform} post about {topic} for {audience_age} audience",
            "Generate engaging {content_type} content on {topic} with {brand_voice}",
            "Write a {tone} post about {topic} that drives {engagement_type}",
            "Craft {platform} content on {topic} with {trending_element}",
            "Develop a {content_type} post about {topic} optimized for {engagement_goal}"
        ]
        
        for i, variation in enumerate(influencer_variations[:num_variants]):
            variant_id = f"{base_template.template_id}_influencer_v{i+1}"
            variant = PromptTemplate(
                template_id=variant_id,
                prompt_type=base_template.prompt_type,
                template_text=variation,
                variables=["platform", "topic", "audience_age", "content_type", "brand_voice", "tone", "engagement_type", "trending_element", "engagement_goal"],
                optimization_target=base_template.optimization_target,
                version=f"{base_template.version}_variant_{i+1}"
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_comedy_variants(self,
                                      base_template: PromptTemplate,
                                      num_variants: int) -> List[PromptTemplate]:
        """Génération de variants pour prompts comiques"""
        variants = []
        
        comedy_variations = [
            "Write a {humor_type} joke about {topic} for {audience_type}",
            "Create {joke_length} comedy content on {topic} with {delivery_style}",
            "Generate a {humor_type} bit about {topic} with {timing_emphasis}",
            "Craft comedy material on {topic} using {comedic_technique}",
            "Develop {humor_type} content about {topic} optimized for {venue_type}"
        ]
        
        for i, variation in enumerate(comedy_variations[:num_variants]):
            variant_id = f"{base_template.template_id}_comedy_v{i+1}"
            variant = PromptTemplate(
                template_id=variant_id,
                prompt_type=base_template.prompt_type,
                template_text=variation,
                variables=["humor_type", "topic", "audience_type", "joke_length", "delivery_style", "timing_emphasis", "comedic_technique", "venue_type"],
                optimization_target=base_template.optimization_target,
                version=f"{base_template.version}_variant_{i+1}"
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_generic_variants(self,
                                       base_template: PromptTemplate,
                                       num_variants: int) -> List[PromptTemplate]:
        """Génération de variants génériques"""
        variants = []
        
        # Techniques de variation génériques
        variation_techniques = [
            ("rephrase", "Rephrase the prompt with different wording"),
            ("expand", "Add more context and details"),
            ("simplify", "Simplify the prompt structure"),
            ("specify", "Add more specific requirements"),
            ("generalize", "Make the prompt more general")
        ]
        
        for i, (technique, description) in enumerate(variation_techniques[:num_variants]):
            variant_id = f"{base_template.template_id}_generic_v{i+1}"
            
            # Application simple de la technique
            varied_text = self._apply_variation_technique(
                base_template.template_text, technique
            )
            
            variant = PromptTemplate(
                template_id=variant_id,
                prompt_type=base_template.prompt_type,
                template_text=varied_text,
                variables=base_template.variables,
                optimization_target=base_template.optimization_target,
                version=f"{base_template.version}_{technique}",
                metadata={"variation_technique": technique, "description": description}
            )
            variants.append(variant)
        
        return variants
    
    def _apply_variation_technique(self, original_text: str, technique: str) -> str:
        """Application d'une technique de variation"""
        if technique == "rephrase":
            return f"Please {original_text.lower()}"
        elif technique == "expand":
            return f"{original_text} Provide detailed explanations and examples."
        elif technique == "simplify":
            return original_text.replace(" detailed ", " ").replace(" comprehensive ", " ")
        elif technique == "specify":
            return f"{original_text} Be specific and include relevant metrics."
        elif technique == "generalize":
            return original_text.replace(" specific ", " ").replace(" detailed ", " general ")
        else:
            return original_text
    
    async def _run_ab_testing(self, experiment -> None: PromptExperiment) -> None:
        """Exécution d'A/B testing sur les templates"""
        try:
            all_templates = [experiment.base_template] + experiment.candidate_templates
            results = {}
            
            for template in all_templates:
                template_scores = []
                
                # Évaluation sur tous les cas de test
                for test_case in experiment.test_cases:
                    evaluation = await self._evaluate_template(template, test_case)
                    template_scores.append(evaluation.scores[experiment.target_metric])
                
                # Calcul des statistiques
                avg_score = statistics.mean(template_scores)
                std_score = statistics.stdev(template_scores) if len(template_scores) > 1 else 0
                
                results[template.template_id] = {
                    "scores": template_scores,
                    "avg_score": avg_score,
                    "std_score": std_score,
                    "confidence_interval": self._calculate_confidence_interval(template_scores)
                }
            
            # Sélection du meilleur template
            best_template_id = max(results.keys(), key=lambda tid: results[tid]["avg_score"])
            
            # Calcul de l'amélioration
            base_score = results[experiment.base_template.template_id]["avg_score"]
            best_score = results[best_template_id]["avg_score"]
            improvement = ((best_score - base_score) / base_score) * 100 if base_score > 0 else 0
            
            experiment.best_template_id = best_template_id
            experiment.improvement_percentage = improvement
            experiment.results = results
            
            logger.info(f"🧪 A/B testing completed: {improvement:.2f}% improvement")
            
        except Exception as e:
            logger.error(f"❌ A/B testing error: {e}")
            experiment.status = "failed"
    
    async def _run_genetic_optimization(self, experiment -> None: PromptExperiment) -> None:
        """Optimisation génétique des prompts"""
        try:
            # Simplification pour la démo - vraie implémentation serait plus complexe
            population = [experiment.base_template] + experiment.candidate_templates
            generations = 3  # Simplifié
            
            best_scores = []
            
            for generation in range(generations):
                # Évaluation de la population
                population_scores = {}
                for template in population:
                    scores = []
                    for test_case in experiment.test_cases[:3]:  # Échantillon
                        evaluation = await self._evaluate_template(template, test_case)
                        scores.append(evaluation.scores[experiment.target_metric])
                    population_scores[template.template_id] = statistics.mean(scores)
                
                # Sélection des meilleurs
                sorted_templates = sorted(
                    population, 
                    key=lambda t: population_scores[t.template_id], 
                    reverse=True
                )
                
                best_scores.append(population_scores[sorted_templates[0].template_id])
                
                # Génération de la nouvelle population (simplifié)
                if generation < generations - 1:
                    new_population = sorted_templates[:2]  # Garder les 2 meilleurs
                    
                    # Mutation des meilleurs
                    for i, template in enumerate(sorted_templates[:2]):
                        mutated = await self._mutate_template(template, f"gen{generation}_mut{i}")
                        new_population.append(mutated)
                    
                    population = new_population
            
            # Résultats finaux
            final_scores = {}
            for template in population:
                scores = []
                for test_case in experiment.test_cases:
                    evaluation = await self._evaluate_template(template, test_case)
                    scores.append(evaluation.scores[experiment.target_metric])
                final_scores[template.template_id] = {
                    "avg_score": statistics.mean(scores),
                    "scores": scores
                }
            
            best_template_id = max(final_scores.keys(), key=lambda tid: final_scores[tid]["avg_score"])
            
            base_score = final_scores.get(experiment.base_template.template_id, {}).get("avg_score", 0)
            best_score = final_scores[best_template_id]["avg_score"]
            improvement = ((best_score - base_score) / base_score) * 100 if base_score > 0 else 0
            
            experiment.best_template_id = best_template_id
            experiment.improvement_percentage = improvement
            experiment.results = {
                "final_scores": final_scores,
                "generation_progress": best_scores,
                "method": "genetic_algorithm"
            }
            
            logger.info(f"🧬 Genetic optimization completed: {improvement:.2f}% improvement")
            
        except Exception as e:
            logger.error(f"❌ Genetic optimization error: {e}")
            experiment.status = "failed"
    
    async def _mutate_template(self, template: PromptTemplate, suffix: str) -> PromptTemplate:
        """Mutation d'un template (version simplifiée)"""
        mutations = [
            lambda text: text.replace(" the ", " a "),
            lambda text: text.replace(" create ", " generate "),
            lambda text: text.replace(" write ", " compose "),
            lambda text: f"Please {text.lower()}",
            lambda text: f"{text} Be creative and original."
        ]
        
        mutation = np.random.choice(mutations)
        mutated_text = mutation(template.template_text)
        
        return PromptTemplate(
            template_id=f"{template.template_id}_{suffix}",
            prompt_type=template.prompt_type,
            template_text=mutated_text,
            variables=template.variables,
            optimization_target=template.optimization_target,
            version=f"{template.version}_mutated"
        )
    
    async def _run_bayesian_optimization(self, experiment -> None: PromptExperiment) -> None:
        """Optimisation bayésienne (version simplifiée)"""
        try:
            # Version simplifiée - vraie implémentation utiliserait des librairies spécialisées
            all_templates = [experiment.base_template] + experiment.candidate_templates
            template_performances = {}
            
            # Évaluation initiale
            for template in all_templates:
                scores = []
                for test_case in experiment.test_cases:
                    evaluation = await self._evaluate_template(template, test_case)
                    scores.append(evaluation.scores[experiment.target_metric])
                
                template_performances[template.template_id] = {
                    "mean_score": statistics.mean(scores),
                    "scores": scores,
                    "uncertainty": statistics.stdev(scores) if len(scores) > 1 else 0.1
                }
            
            # Sélection basée sur acquisition function (Upper Confidence Bound simplifié)
            def acquisition_function(performance) -> None:
                return performance["mean_score"] + 1.96 * performance["uncertainty"]
            
            best_template_id = max(
                template_performances.keys(),
                key=lambda tid: acquisition_function(template_performances[tid])
            )
            
            base_score = template_performances[experiment.base_template.template_id]["mean_score"]
            best_score = template_performances[best_template_id]["mean_score"]
            improvement = ((best_score - base_score) / base_score) * 100 if base_score > 0 else 0
            
            experiment.best_template_id = best_template_id
            experiment.improvement_percentage = improvement
            experiment.results = {
                "template_performances": template_performances,
                "method": "bayesian_optimization",
                "acquisition_scores": {
                    tid: acquisition_function(perf) 
                    for tid, perf in template_performances.items()
                }
            }
            
            logger.info(f"📊 Bayesian optimization completed: {improvement:.2f}% improvement")
            
        except Exception as e:
            logger.error(f"❌ Bayesian optimization error: {e}")
            experiment.status = "failed"
    
    async def _run_simple_evaluation(self, experiment -> None: PromptExperiment) -> None:
        """Évaluation simple de tous les templates"""
        try:
            all_templates = [experiment.base_template] + experiment.candidate_templates
            results = {}
            
            for template in all_templates:
                total_score = 0
                evaluations = []
                
                for test_case in experiment.test_cases:
                    evaluation = await self._evaluate_template(template, test_case)
                    evaluations.append(evaluation)
                    total_score += evaluation.scores[experiment.target_metric]
                
                avg_score = total_score / len(experiment.test_cases)
                results[template.template_id] = {
                    "avg_score": avg_score,
                    "evaluations": evaluations
                }
            
            best_template_id = max(results.keys(), key=lambda tid: results[tid]["avg_score"])
            
            base_score = results[experiment.base_template.template_id]["avg_score"]
            best_score = results[best_template_id]["avg_score"]
            improvement = ((best_score - base_score) / base_score) * 100 if base_score > 0 else 0
            
            experiment.best_template_id = best_template_id
            experiment.improvement_percentage = improvement
            experiment.results = results
            
            logger.info(f"📋 Simple evaluation completed: {improvement:.2f}% improvement")
            
        except Exception as e:
            logger.error(f"❌ Simple evaluation error: {e}")
            experiment.status = "failed"
    
    async def _evaluate_template(self,
                               template: PromptTemplate,
                               test_case: Dict[str, Any]) -> PromptEvaluation:
        """Évaluation d'un template sur un cas de test"""
        try:
            start_time = datetime.now()
            
            # Génération du prompt avec les variables
            generated_prompt = self._fill_template(template, test_case.get("variables", {}))
            
            # Simulation de génération de contenu (dans la vraie implémentation, appel au LLM)
            generated_output = f"Generated content for: {generated_prompt[:100]}..."
            
            # Évaluation avec toutes les métriques
            scores = {}
            for metric in PromptMetric:
                if metric in self.metric_evaluators:
                    score = await self.metric_evaluators[metric](
                        generated_output, test_case, template
                    )
                    scores[metric] = score
                else:
                    scores[metric] = np.random.uniform(0.5, 0.9)  # Score par défaut
            
            evaluation_time = (datetime.now() - start_time).total_seconds() * 1000
            
            evaluation = PromptEvaluation(
                evaluation_id=f"eval_{template.template_id}_{int(datetime.now().timestamp())}",
                template_id=template.template_id,
                input_variables=test_case.get("variables", {}),
                generated_output=generated_output,
                scores=scores,
                evaluation_time_ms=evaluation_time
            )
            
            # Stockage
            self.evaluations[template.template_id].append(evaluation)
            self.evaluation_cache.append(evaluation)
            
            # Callbacks
            for callback in self.evaluation_callbacks:
                try:
                    await callback(evaluation)
                except Exception as e:
                    logger.error(f"❌ Evaluation callback error: {e}")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"❌ Template evaluation error: {e}")
            raise
    
    def _fill_template(self, template: PromptTemplate, variables: Dict[str, Any]) -> str:
        """Remplissage d'un template avec des variables"""
        try:
            filled_prompt = template.template_text
            
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                filled_prompt = filled_prompt.replace(placeholder, str(var_value))
            
            return filled_prompt
            
        except Exception as e:
            logger.error(f"❌ Template filling error: {e}")
            return template.template_text
    
    async def _evaluate_relevance(self,
                                output: str,
                                test_case: Dict[str, Any],
                                template: PromptTemplate) -> float:
        """Évaluation de la pertinence"""
        # Simulation basée sur la longueur et mots-clés
        expected_keywords = test_case.get("expected_keywords", [])
        output_lower = output.lower()
        
        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in output_lower)
        relevance_score = min(1.0, keyword_matches / max(len(expected_keywords), 1))
        
        return relevance_score * 0.8 + np.random.uniform(0, 0.2)  # Ajout de variabilité
    
    async def _evaluate_creativity(self,
                                 output: str,
                                 test_case: Dict[str, Any],
                                 template: PromptTemplate) -> float:
        """Évaluation de la créativité"""
        # Simulation basée sur la diversité du vocabulaire
        words = output.lower().split()
        unique_words = len(set(words))
        total_words = len(words)
        
        diversity_score = unique_words / max(total_words, 1)
        creativity_score = min(1.0, diversity_score * 2)  # Normalisation
        
        return creativity_score * 0.7 + np.random.uniform(0, 0.3)
    
    async def _evaluate_coherence(self,
                                output: str,
                                test_case: Dict[str, Any],
                                template: PromptTemplate) -> float:
        """Évaluation de la cohérence"""
        # Simulation basée sur la structure
        sentences = output.split('.')
        coherence_score = min(1.0, len(sentences) / 10)  # Plus de phrases = plus cohérent
        
        return coherence_score * 0.6 + np.random.uniform(0.2, 0.4)
    
    async def _evaluate_engagement(self,
                                 output: str,
                                 test_case: Dict[str, Any],
                                 template: PromptTemplate) -> float:
        """Évaluation du potentiel d'engagement"""
        # Simulation basée sur des mots d'engagement
        engagement_words = ["amazing", "incredible", "awesome", "fantastic", "wow", "great", "excellent"]
        output_lower = output.lower()
        
        engagement_count = sum(1 for word in engagement_words if word in output_lower)
        engagement_score = min(1.0, engagement_count / 3)
        
        return engagement_score * 0.5 + np.random.uniform(0.3, 0.5)
    
    async def _evaluate_technical_accuracy(self,
                                         output: str,
                                         test_case: Dict[str, Any],
                                         template: PromptTemplate) -> float:
        """Évaluation de la précision technique"""
        # Simulation basée sur le type de créateur
        if template.prompt_type.value.startswith("musician"):
            music_terms = ["chord", "melody", "rhythm", "tempo", "harmony"]
            term_count = sum(1 for term in music_terms if term in output.lower())
            return min(1.0, term_count / 3) * 0.7 + np.random.uniform(0, 0.3)
        
        return np.random.uniform(0.6, 0.9)  # Score par défaut
    
    async def _evaluate_brand_consistency(self,
                                        output: str,
                                        test_case: Dict[str, Any],
                                        template: PromptTemplate) -> float:
        """Évaluation de la cohérence de marque"""
        # Simulation basée sur le ton attendu
        expected_tone = test_case.get("expected_tone", "neutral")
        
        tone_scores = {
            "professional": 0.8 if "professional" in output.lower() else 0.6,
            "casual": 0.8 if any(word in output.lower() for word in ["hey", "cool", "awesome"]) else 0.6,
            "formal": 0.8 if "please" in output.lower() or "kindly" in output.lower() else 0.6
        }
        
        base_score = tone_scores.get(expected_tone, 0.7)
        return base_score + np.random.uniform(-0.1, 0.1)
    
    async def _evaluate_originality(self,
                                  output: str,
                                  test_case: Dict[str, Any],
                                  template: PromptTemplate) -> float:
        """Évaluation de l'originalité"""
        # Simulation basée sur l'unicité du contenu
        common_phrases = ["the best", "amazing results", "perfect solution"]
        common_count = sum(1 for phrase in common_phrases if phrase in output.lower())
        
        originality_score = max(0.3, 1.0 - (common_count * 0.2))
        return originality_score * 0.8 + np.random.uniform(0, 0.2)
    
    def _calculate_confidence_interval(self, scores: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calcul de l'intervalle de confiance"""
        if len(scores) < 2:
            return (0.0, 1.0)
        
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores)
        n = len(scores)
        
        # Approximation normale pour la simplicité
        margin = 1.96 * (std_score / np.sqrt(n))  # 95% confidence
        
        return (max(0, mean_score - margin), min(1, mean_score + margin))
    
    async def _save_template_to_db(self, template -> None: PromptTemplate) -> None:
        """Sauvegarde template en DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO prompt_templates 
                    (template_id, prompt_type, template_text, variables, optimization_target,
                     version, created_at, performance_scores, usage_count, success_rate, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.template_id,
                    template.prompt_type.value,
                    template.template_text,
                    json.dumps(template.variables),
                    template.optimization_target.value,
                    template.version,
                    template.created_at.isoformat(),
                    json.dumps({k.value: v for k, v in template.performance_scores.items()}),
                    template.usage_count,
                    template.success_rate,
                    json.dumps(template.metadata)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving template to DB: {e}")
    
    async def _save_experiment_to_db(self, experiment -> None: PromptExperiment) -> None:
        """Sauvegarde expérience en DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO prompt_experiments 
                    (experiment_id, base_template_id, optimization_strategy, target_metric,
                     status, started_at, completed_at, best_template_id, improvement_percentage, results)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    experiment.experiment_id,
                    experiment.base_template.template_id,
                    experiment.optimization_strategy.value,
                    experiment.target_metric.value,
                    experiment.status,
                    experiment.started_at.isoformat(),
                    experiment.completed_at.isoformat() if experiment.completed_at else None,
                    experiment.best_template_id,
                    experiment.improvement_percentage,
                    json.dumps(experiment.results, default=str)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving experiment to DB: {e}")
    
    async def get_optimization_report(self, experiment_id: str) -> Dict[str, Any]:
        """Génération d'un rapport d'optimisation"""
        try:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            experiment = self.experiments[experiment_id]
            
            report = {
                "experiment_id": experiment_id,
                "base_template": experiment.base_template.template_id,
                "optimization_strategy": experiment.optimization_strategy.value,
                "target_metric": experiment.target_metric.value,
                "status": experiment.status,
                "improvement_percentage": experiment.improvement_percentage,
                "best_template_id": experiment.best_template_id,
                "duration_minutes": 0,
                "templates_tested": len(experiment.candidate_templates) + 1,
                "test_cases_used": len(experiment.test_cases)
            }
            
            if experiment.completed_at and experiment.started_at:
                duration = experiment.completed_at - experiment.started_at
                report["duration_minutes"] = duration.total_seconds() / 60
            
            # Ajout des résultats détaillés
            if experiment.results:
                report["detailed_results"] = experiment.results
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating optimization report: {e}")
            return {"error": str(e)}
    
    def add_optimization_callback(self, callback -> None: Callable) -> None:
        """Ajouter callback d'optimisation"""
        self.optimization_callbacks.append(callback)
        logger.info(f"🔬 Optimization callback added. Total: {len(self.optimization_callbacks)}")
    
    def add_evaluation_callback(self, callback -> None: Callable) -> None:
        """Ajouter callback d'évaluation"""
        self.evaluation_callbacks.append(callback)
        logger.info(f"📊 Evaluation callback added. Total: {len(self.evaluation_callbacks)}")


# Exemple d'utilisation pour démonstration
async def main() -> None:
    """Démonstration des capacités du PromptOptimizationTemplate"""
    
    optimizer = PromptOptimizationTemplate()
    
    # Callbacks de démonstration
    async def optimization_callback(experiment -> None: PromptExperiment) -> None:
        print(f"🔬 OPTIMIZATION COMPLETED: {experiment.experiment_id}")
        print(f"   Improvement: {experiment.improvement_percentage:.2f}%")
        print(f"   Best template: {experiment.best_template_id}")
    
    async def evaluation_callback(evaluation -> None: PromptEvaluation) -> None:
        avg_score = statistics.mean(evaluation.scores.values())
        print(f"📊 EVALUATION: {evaluation.template_id} - Score: {avg_score:.3f}")
    
    optimizer.add_optimization_callback(optimization_callback)
    optimizer.add_evaluation_callback(evaluation_callback)
    
    # Création de templates pour différents créateurs
    creator_templates = [
        {
            "template_id": "musician_composition_v1",
            "prompt_type": CreatorPromptType.MUSICIAN_COMPOSITION,
            "template_text": "Create a {genre} composition with {mood} atmosphere for {target_audience}",
            "variables": ["genre", "mood", "target_audience"],
            "optimization_target": PromptMetric.CREATIVITY_SCORE
        },
        {
            "template_id": "blogger_content_v1",
            "prompt_type": CreatorPromptType.BLOGGER_CONTENT_GEN,
            "template_text": "Write an engaging {post_type} about {topic} for {audience}",
            "variables": ["post_type", "topic", "audience"],
            "optimization_target": PromptMetric.ENGAGEMENT_POTENTIAL
        },
        {
            "template_id": "photographer_caption_v1",
            "prompt_type": CreatorPromptType.PHOTOGRAPHER_CAPTION_GEN,
            "template_text": "Create a {style} caption for this {subject} photo",
            "variables": ["style", "subject"],
            "optimization_target": PromptMetric.ENGAGEMENT_POTENTIAL
        }
    ]
    
    # Création des templates
    created_templates = []
    for template_data in creator_templates:
        template = await optimizer.create_template(**template_data)
        created_templates.append(template)
        print(f"📝 Created template: {template.template_id}")
    
    # Cas de test pour optimisation
    test_cases = [
        {
            "variables": {
                "genre": "electronic",
                "mood": "energetic",
                "target_audience": "young adults",
                "post_type": "tutorial",
                "topic": "AI in music production",
                "audience": "music producers",
                "style": "inspirational",
                "subject": "sunset landscape"
            },
            "expected_keywords": ["creative", "innovative", "engaging"],
            "expected_tone": "professional"
        },
        {
            "variables": {
                "genre": "jazz",
                "mood": "relaxing",
                "target_audience": "mature audience",
                "post_type": "review",
                "topic": "vintage photography",
                "audience": "photography enthusiasts",
                "style": "poetic",
                "subject": "portrait"
            },
            "expected_keywords": ["artistic", "beautiful", "expressive"],
            "expected_tone": "casual"
        }
    ]
    
    # Optimisation des templates
    print(f"\n🔬 Starting optimizations...")
    
    optimization_strategies = [
        PromptOptimizationStrategy.A_B_TESTING,
        PromptOptimizationStrategy.GENETIC_ALGORITHM,
        PromptOptimizationStrategy.BAYESIAN_OPTIMIZATION
    ]
    
    experiments = []
    for i, template in enumerate(created_templates):
        strategy = optimization_strategies[i % len(optimization_strategies)]
        
        experiment = await optimizer.optimize_template(
            template_id=template.template_id,
            optimization_strategy=strategy,
            test_cases=test_cases,
            num_variants=3
        )
        
        experiments.append(experiment)
        print(f"✅ Optimized {template.template_id} with {strategy.value}")
    
    # Génération de rapports
    print(f"\n📋 Optimization Reports:")
    for experiment in experiments:
        report = await optimizer.get_optimization_report(experiment.experiment_id)
        
        print(f"\n🔍 Report for {experiment.experiment_id}:")
        print(f"   Strategy: {report['optimization_strategy']}")
        print(f"   Improvement: {report['improvement_percentage']:.2f}%")
        print(f"   Templates tested: {report['templates_tested']}")
        print(f"   Duration: {report['duration_minutes']:.2f} minutes")
        
        if report['improvement_percentage'] > 10:
            print(f"   🎯 Significant improvement achieved!")
        elif report['improvement_percentage'] > 0:
            print(f"   📈 Modest improvement achieved")
        else:
            print(f"   ⚠️ No improvement found")
    
    print(f"\n✅ PromptOptimizationTemplate demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())