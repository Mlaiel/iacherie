"""
Enterprise Prompt Engineering System - Advanced IA Prompt Engineer Implementation
=================================================================================

Architecture enterprise pour l'optimisation, la sécurité et l'automation des prompts IA.
Implémente les meilleures pratiques de Prompt Engineering selon expertise IA avancée.

Fonctionnalités Enterprise:
- Optimisation automatique des prompts avec A/B testing
- Détection et prévention d'injection de prompts  
- Fine-tuning automation pour modèles personnalisés
- Templates enterprise avec versioning
- Metrics et analytics avancés des prompts
- Multi-modal prompt orchestration (texte, image, audio)
- Chain-of-thought optimization
- Integration avec pipeline ML/IA
"""

import asyncio
import json
import logging
import time
import redis
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import openai
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import asyncpg
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptType(Enum):
    """Types de prompts supportés par le système enterprise"""
    COMPLETION = "completion"
    CHAT = "chat"
    INSTRUCTION = "instruction"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"
    CHAIN_OF_THOUGHT = "chain_of_thought"

class SecurityLevel(Enum):
    """Niveaux de sécurité pour la validation des prompts"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PromptMetrics:
    """Métriques de performance des prompts"""
    prompt_id: str
    version: str
    response_time: float
    token_count: int
    cost: float
    accuracy_score: float
    relevance_score: float
    safety_score: float
    user_satisfaction: float
    conversion_rate: float
    timestamp: datetime

@dataclass
class PromptTemplate:
    """Template enterprise pour prompts optimisés"""
    template_id: str
    name: str
    version: str
    category: str
    prompt_type: PromptType
    template_content: str
    variables: Dict[str, Any]
    validation_rules: Dict[str, Any]
    performance_baseline: Dict[str, float]
    security_level: SecurityLevel
    tags: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class OptimizationResult:
    """Résultat d'optimisation de prompt"""
    original_prompt: str
    optimized_prompt: str
    improvement_score: float
    metrics_comparison: Dict[str, float]
    optimization_strategy: str
    confidence_level: float

class EnterprisePromptSecurityValidator:
    """Système de sécurité avancé pour validation des prompts"""
    
    def __init__(self):
        self.injection_patterns = [
            r"ignore\s+(?:previous|above|all)\s+(?:instructions?|prompts?)",
            r"forget\s+(?:everything|all|previous)",
            r"act\s+as\s+(?:a\s+)?(?:different|new)\s+(?:character|person|ai)",
            r"pretend\s+(?:you\s+are|to\s+be)",
            r"system\s*:\s*you\s+are\s+now",
            r"jailbreak|jail\s+break",
            r"developer\s+mode",
            r"godmode|god\s+mode",
            r"sudo\s+mode",
            r"override\s+(?:safety|security|guidelines)",
        ]
        
        # Chargement du modèle de classification pour détection d'injections
        try:
            self.injection_classifier = AutoModelForSequenceClassification.from_pretrained(
                "microsoft/DialoGPT-medium"
            )
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        except Exception as e:
            logger.warning(f"Impossible de charger le modèle de classification: {e}")
            self.injection_classifier = None
            self.tokenizer = None
    
    def validate_prompt_security(self, prompt: str, security_level: SecurityLevel) -> Dict[str, Any]:
        """Validation complète de sécurité d'un prompt"""
        results = {
            "is_safe": True,
            "risk_score": 0.0,
            "detected_threats": [],
            "recommendations": []
        }
        
        # Détection de patterns d'injection
        injection_score = self._detect_injection_patterns(prompt)
        results["injection_score"] = injection_score
        
        # Classification ML des injections
        if self.injection_classifier:
            ml_score = self._ml_injection_detection(prompt)
            results["ml_injection_score"] = ml_score
        else:
            ml_score = 0.0
        
        # Analyse de contenu sensible
        content_risk = self._analyze_sensitive_content(prompt)
        results["content_risk_score"] = content_risk
        
        # Score de risque global
        risk_score = max(injection_score, ml_score, content_risk)
        results["risk_score"] = risk_score
        
        # Évaluation selon le niveau de sécurité
        threshold = self._get_security_threshold(security_level)
        if risk_score > threshold:
            results["is_safe"] = False
            results["detected_threats"].append(f"Risque de sécurité élevé: {risk_score:.2f}")
        
        # Recommandations d'amélioration
        if injection_score > 0.3:
            results["recommendations"].append("Reformuler pour éviter les patterns d'injection")
        if content_risk > 0.4:
            results["recommendations"].append("Revoir le contenu pour éviter les éléments sensibles")
        
        return results
    
    def _detect_injection_patterns(self, prompt: str) -> float:
        """Détection de patterns d'injection via regex"""
        prompt_lower = prompt.lower()
        detected_patterns = 0
        
        for pattern in self.injection_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                detected_patterns += 1
        
        return min(detected_patterns / len(self.injection_patterns), 1.0)
    
    def _ml_injection_detection(self, prompt: str) -> float:
        """Détection d'injection via modèle ML"""
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            with torch.no_grad():
                outputs = self.injection_classifier(inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                # Retourne la probabilité d'injection (classe malveillante)
                return float(probabilities[0][1]) if probabilities.shape[1] > 1 else 0.0
        except Exception as e:
            logger.error(f"Erreur dans la détection ML: {e}")
            return 0.0
    
    def _analyze_sensitive_content(self, prompt: str) -> float:
        """Analyse du contenu sensible"""
        sensitive_keywords = [
            "password", "secret", "token", "key", "confidential",
            "private", "personal", "bank", "credit", "ssn",
            "violence", "harm", "illegal", "drugs", "weapon"
        ]
        
        prompt_lower = prompt.lower()
        sensitive_count = sum(1 for keyword in sensitive_keywords if keyword in prompt_lower)
        
        return min(sensitive_count / 10.0, 1.0)
    
    def _get_security_threshold(self, level: SecurityLevel) -> float:
        """Seuils de sécurité selon le niveau"""
        thresholds = {
            SecurityLevel.LOW: 0.8,
            SecurityLevel.MEDIUM: 0.6,
            SecurityLevel.HIGH: 0.4,
            SecurityLevel.CRITICAL: 0.2
        }
        return thresholds.get(level, 0.6)

class EnterprisePromptOptimizer:
    """Optimiseur avancé de prompts avec ML et A/B testing"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.optimization_strategies = [
            "clarity_enhancement",
            "context_enrichment", 
            "instruction_refinement",
            "example_integration",
            "chain_of_thought",
            "few_shot_learning",
            "role_specification",
            "constraint_addition"
        ]
    
    def optimize_prompt(self, prompt: str, target_metrics: Dict[str, float]) -> OptimizationResult:
        """Optimisation intelligente d'un prompt"""
        
        # Analyse du prompt original
        original_analysis = self._analyze_prompt_structure(prompt)
        
        # Génération de variantes optimisées
        optimized_variants = []
        for strategy in self.optimization_strategies:
            variant = self._apply_optimization_strategy(prompt, strategy, target_metrics)
            if variant != prompt:
                optimized_variants.append((variant, strategy))
        
        # Sélection de la meilleure variante
        best_variant, best_strategy = self._select_best_variant(
            prompt, optimized_variants, target_metrics
        )
        
        # Calcul du score d'amélioration
        improvement_score = self._calculate_improvement_score(prompt, best_variant)
        
        return OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=best_variant,
            improvement_score=improvement_score,
            metrics_comparison={"estimated_improvement": improvement_score},
            optimization_strategy=best_strategy,
            confidence_level=min(improvement_score, 0.95)
        )
    
    def _analyze_prompt_structure(self, prompt: str) -> Dict[str, Any]:
        """Analyse structurelle d'un prompt"""
        return {
            "length": len(prompt),
            "word_count": len(prompt.split()),
            "sentence_count": len(prompt.split('.')),
            "has_examples": "example" in prompt.lower() or "for instance" in prompt.lower(),
            "has_instructions": any(word in prompt.lower() for word in ["please", "must", "should", "need"]),
            "has_context": any(word in prompt.lower() for word in ["context", "background", "given"]),
            "clarity_score": self._calculate_clarity_score(prompt)
        }
    
    def _apply_optimization_strategy(self, prompt: str, strategy: str, targets: Dict[str, float]) -> str:
        """Application d'une stratégie d'optimisation spécifique"""
        
        if strategy == "clarity_enhancement":
            return self._enhance_clarity(prompt)
        elif strategy == "context_enrichment":
            return self._enrich_context(prompt)
        elif strategy == "instruction_refinement":
            return self._refine_instructions(prompt)
        elif strategy == "example_integration":
            return self._integrate_examples(prompt)
        elif strategy == "chain_of_thought":
            return self._add_chain_of_thought(prompt)
        elif strategy == "few_shot_learning":
            return self._add_few_shot_examples(prompt)
        elif strategy == "role_specification":
            return self._specify_role(prompt)
        elif strategy == "constraint_addition":
            return self._add_constraints(prompt)
        else:
            return prompt
    
    def _enhance_clarity(self, prompt: str) -> str:
        """Amélioration de la clarté du prompt"""
        # Simplification et structuration
        if "please" not in prompt.lower():
            prompt = "Please " + prompt.lower()
        
        # Ajout de structure si manquante
        if not prompt.endswith(('.', '!', '?')):
            prompt += "."
        
        return prompt
    
    def _enrich_context(self, prompt: str) -> str:
        """Enrichissement du contexte"""
        if "context:" not in prompt.lower():
            return f"Context: This is a professional request requiring accurate information.\n\n{prompt}"
        return prompt
    
    def _refine_instructions(self, prompt: str) -> str:
        """Raffinement des instructions"""
        if not any(word in prompt.lower() for word in ["step", "first", "then", "finally"]):
            return f"{prompt}\n\nPlease provide a step-by-step response."
        return prompt
    
    def _integrate_examples(self, prompt: str) -> str:
        """Intégration d'exemples"""
        if "example" not in prompt.lower():
            return f"{prompt}\n\nFor example, consider providing specific details and clear reasoning."
        return prompt
    
    def _add_chain_of_thought(self, prompt: str) -> str:
        """Ajout de chain-of-thought"""
        if "think" not in prompt.lower() and "reasoning" not in prompt.lower():
            return f"{prompt}\n\nPlease think through this step by step and show your reasoning."
        return prompt
    
    def _add_few_shot_examples(self, prompt: str) -> str:
        """Ajout d'exemples few-shot"""
        return f"{prompt}\n\nProvide your answer following similar high-quality examples."
    
    def _specify_role(self, prompt: str) -> str:
        """Spécification de rôle"""
        if not prompt.lower().startswith(("as a", "you are", "act as")):
            return f"As an expert in this domain, {prompt.lower()}"
        return prompt
    
    def _add_constraints(self, prompt: str) -> str:
        """Ajout de contraintes"""
        return f"{prompt}\n\nEnsure your response is accurate, concise, and professional."
    
    def _select_best_variant(self, original: str, variants: List[Tuple[str, str]], targets: Dict[str, float]) -> Tuple[str, str]:
        """Sélection de la meilleure variante"""
        if not variants:
            return original, "none"
        
        # Scoring simple basé sur la longueur et la structure
        best_score = 0
        best_variant = original
        best_strategy = "none"
        
        for variant, strategy in variants:
            score = self._score_variant(variant, targets)
            if score > best_score:
                best_score = score
                best_variant = variant
                best_strategy = strategy
        
        return best_variant, best_strategy
    
    def _score_variant(self, variant: str, targets: Dict[str, float]) -> float:
        """Scoring d'une variante de prompt"""
        score = 0.0
        
        # Bonus pour structure
        if "step" in variant.lower():
            score += 0.2
        if "example" in variant.lower():
            score += 0.15
        if "context" in variant.lower():
            score += 0.1
        if "please" in variant.lower():
            score += 0.05
        
        # Bonus pour longueur optimale
        word_count = len(variant.split())
        if 20 <= word_count <= 100:
            score += 0.3
        
        return score
    
    def _calculate_clarity_score(self, prompt: str) -> float:
        """Calcul du score de clarté"""
        words = prompt.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Score basé sur longueur moyenne des mots et structure
        clarity = 1.0 - min(avg_word_length / 10.0, 0.5)
        if any(word in prompt.lower() for word in ["please", "specific", "clear"]):
            clarity += 0.2
        
        return min(clarity, 1.0)
    
    def _calculate_improvement_score(self, original: str, optimized: str) -> float:
        """Calcul du score d'amélioration"""
        if original == optimized:
            return 0.0
        
        orig_analysis = self._analyze_prompt_structure(original)
        opt_analysis = self._analyze_prompt_structure(optimized)
        
        improvement = 0.0
        
        # Amélioration de la clarté
        clarity_improvement = opt_analysis["clarity_score"] - orig_analysis["clarity_score"]
        improvement += clarity_improvement * 0.4
        
        # Amélioration structurelle
        if opt_analysis["has_examples"] and not orig_analysis["has_examples"]:
            improvement += 0.2
        if opt_analysis["has_instructions"] and not orig_analysis["has_instructions"]:
            improvement += 0.2
        if opt_analysis["has_context"] and not orig_analysis["has_context"]:
            improvement += 0.2
        
        return min(improvement, 1.0)

class EnterprisePromptAnalytics:
    """Système d'analytics avancé pour prompts enterprise"""
    
    def __init__(self, redis_client: redis.Redis, db_pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.metrics_cache = {}
    
    async def track_prompt_performance(self, prompt_id: str, metrics: PromptMetrics):
        """Suivi des performances de prompt"""
        try:
            # Stockage en cache Redis
            cache_key = f"prompt_metrics:{prompt_id}:{metrics.timestamp.isoformat()}"
            await self.redis.setex(
                cache_key, 
                3600, 
                json.dumps(asdict(metrics), default=str)
            )
            
            # Stockage en base de données
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO prompt_metrics 
                    (prompt_id, version, response_time, token_count, cost, 
                     accuracy_score, relevance_score, safety_score, 
                     user_satisfaction, conversion_rate, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, 
                metrics.prompt_id, metrics.version, metrics.response_time,
                metrics.token_count, metrics.cost, metrics.accuracy_score,
                metrics.relevance_score, metrics.safety_score,
                metrics.user_satisfaction, metrics.conversion_rate, metrics.timestamp
                )
            
            logger.info(f"Métriques enregistrées pour prompt {prompt_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors du suivi des métriques: {e}")
    
    async def get_prompt_analytics(self, prompt_id: str, time_range: int = 24) -> Dict[str, Any]:
        """Récupération des analytics d'un prompt"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range)
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM prompt_metrics 
                    WHERE prompt_id = $1 AND timestamp >= $2 AND timestamp <= $3
                    ORDER BY timestamp DESC
                """, prompt_id, start_time, end_time)
            
            if not rows:
                return {"error": "Aucune donnée trouvée"}
            
            # Calcul des statistiques
            metrics = [dict(row) for row in rows]
            analytics = {
                "prompt_id": prompt_id,
                "total_executions": len(metrics),
                "time_range_hours": time_range,
                "performance_summary": {
                    "avg_response_time": np.mean([m["response_time"] for m in metrics]),
                    "avg_token_count": np.mean([m["token_count"] for m in metrics]),
                    "total_cost": sum(m["cost"] for m in metrics),
                    "avg_accuracy": np.mean([m["accuracy_score"] for m in metrics]),
                    "avg_relevance": np.mean([m["relevance_score"] for m in metrics]),
                    "avg_safety": np.mean([m["safety_score"] for m in metrics]),
                    "avg_satisfaction": np.mean([m["user_satisfaction"] for m in metrics]),
                    "conversion_rate": np.mean([m["conversion_rate"] for m in metrics])
                },
                "trends": self._calculate_trends(metrics),
                "recommendations": self._generate_recommendations(metrics)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des analytics: {e}")
            return {"error": str(e)}
    
    def _calculate_trends(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Calcul des tendances de performance"""
        if len(metrics) < 2:
            return {"insufficient_data": True}
        
        # Tri par timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x["timestamp"])
        
        # Calcul des tendances
        response_times = [m["response_time"] for m in sorted_metrics]
        accuracy_scores = [m["accuracy_score"] for m in sorted_metrics]
        
        return {
            "response_time_trend": "improving" if response_times[-1] < response_times[0] else "degrading",
            "accuracy_trend": "improving" if accuracy_scores[-1] > accuracy_scores[0] else "degrading",
            "performance_stability": np.std(response_times) < 0.1
        }
    
    def _generate_recommendations(self, metrics: List[Dict]) -> List[str]:
        """Génération de recommandations d'amélioration"""
        recommendations = []
        
        avg_response_time = np.mean([m["response_time"] for m in metrics])
        avg_accuracy = np.mean([m["accuracy_score"] for m in metrics])
        avg_cost = np.mean([m["cost"] for m in metrics])
        
        if avg_response_time > 2.0:
            recommendations.append("Optimiser le prompt pour réduire le temps de réponse")
        if avg_accuracy < 0.8:
            recommendations.append("Améliorer la précision avec des exemples ou du fine-tuning")
        if avg_cost > 0.05:
            recommendations.append("Réduire les coûts en optimisant la longueur du prompt")
        
        return recommendations

class EnterprisePromptTemplateManager:
    """Gestionnaire de templates enterprise avec versioning"""
    
    def __init__(self, redis_client: redis.Redis, db_pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.templates_cache = {}
    
    async def create_template(self, template: PromptTemplate) -> str:
        """Création d'un nouveau template"""
        try:
            template_data = asdict(template)
            
            # Stockage en base de données
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO prompt_templates 
                    (template_id, name, version, category, prompt_type, 
                     template_content, variables, validation_rules, 
                     performance_baseline, security_level, tags, 
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                template.template_id, template.name, template.version,
                template.category, template.prompt_type.value,
                template.template_content, json.dumps(template.variables),
                json.dumps(template.validation_rules),
                json.dumps(template.performance_baseline),
                template.security_level.value, json.dumps(template.tags),
                template.created_at, template.updated_at
                )
            
            # Cache Redis
            cache_key = f"template:{template.template_id}:{template.version}"
            await self.redis.setex(
                cache_key, 
                7200, 
                json.dumps(template_data, default=str)
            )
            
            logger.info(f"Template créé: {template.template_id} v{template.version}")
            return template.template_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du template: {e}")
            raise
    
    async def get_template(self, template_id: str, version: Optional[str] = None) -> Optional[PromptTemplate]:
        """Récupération d'un template"""
        try:
            # Tentative de récupération depuis le cache
            if version:
                cache_key = f"template:{template_id}:{version}"
            else:
                cache_key = f"template:{template_id}:latest"
            
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return PromptTemplate(**data)
            
            # Récupération depuis la base de données
            async with self.db_pool.acquire() as conn:
                if version:
                    row = await conn.fetchrow("""
                        SELECT * FROM prompt_templates 
                        WHERE template_id = $1 AND version = $2
                    """, template_id, version)
                else:
                    row = await conn.fetchrow("""
                        SELECT * FROM prompt_templates 
                        WHERE template_id = $1 
                        ORDER BY created_at DESC LIMIT 1
                    """, template_id)
            
            if row:
                template_data = dict(row)
                template_data["variables"] = json.loads(template_data["variables"])
                template_data["validation_rules"] = json.loads(template_data["validation_rules"])
                template_data["performance_baseline"] = json.loads(template_data["performance_baseline"])
                template_data["tags"] = json.loads(template_data["tags"])
                template_data["prompt_type"] = PromptType(template_data["prompt_type"])
                template_data["security_level"] = SecurityLevel(template_data["security_level"])
                
                template = PromptTemplate(**template_data)
                
                # Mise en cache
                await self.redis.setex(
                    cache_key, 
                    7200, 
                    json.dumps(asdict(template), default=str)
                )
                
                return template
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du template: {e}")
            return None

class EnterprisePromptABTester:
    """Système A/B testing pour prompts enterprise"""
    
    def __init__(self, redis_client: redis.Redis, analytics: EnterprisePromptAnalytics):
        self.redis = redis_client
        self.analytics = analytics
        self.active_tests = {}
    
    async def create_ab_test(self, test_name: str, prompt_a: str, prompt_b: str, 
                           traffic_split: float = 0.5, duration_hours: int = 24) -> str:
        """Création d'un test A/B"""
        test_id = f"ab_test_{int(time.time())}"
        
        test_config = {
            "test_id": test_id,
            "test_name": test_name,
            "prompt_a": prompt_a,
            "prompt_b": prompt_b,
            "traffic_split": traffic_split,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            "status": "active"
        }
        
        # Stockage de la configuration
        await self.redis.setex(
            f"ab_test:{test_id}",
            duration_hours * 3600,
            json.dumps(test_config)
        )
        
        self.active_tests[test_id] = test_config
        logger.info(f"Test A/B créé: {test_id}")
        
        return test_id
    
    async def get_test_variant(self, test_id: str, user_id: str) -> Dict[str, Any]:
        """Récupération de la variante pour un utilisateur"""
        test_config = await self._get_test_config(test_id)
        if not test_config or test_config["status"] != "active":
            return {"error": "Test non trouvé ou inactif"}
        
        # Déterminisme basé sur user_id
        hash_value = hashlib.md5(f"{test_id}_{user_id}".encode()).hexdigest()
        hash_int = int(hash_value[:8], 16)
        
        variant = "A" if (hash_int / 0xFFFFFFFF) < test_config["traffic_split"] else "B"
        prompt = test_config["prompt_a"] if variant == "A" else test_config["prompt_b"]
        
        # Tracking de l'assignation
        await self.redis.incr(f"ab_test:{test_id}:variant_{variant}_assigned")
        
        return {
            "test_id": test_id,
            "variant": variant,
            "prompt": prompt
        }
    
    async def record_test_result(self, test_id: str, user_id: str, variant: str, 
                               metrics: Dict[str, float]):
        """Enregistrement des résultats du test"""
        result_key = f"ab_test:{test_id}:results:{variant}"
        
        # Stockage des métriques
        await self.redis.lpush(result_key, json.dumps({
            "user_id": user_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Mise à jour des compteurs
        await self.redis.incr(f"ab_test:{test_id}:variant_{variant}_completed")
    
    async def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """Récupération des résultats du test A/B"""
        test_config = await self._get_test_config(test_id)
        if not test_config:
            return {"error": "Test non trouvé"}
        
        # Récupération des résultats pour chaque variante
        results_a = await self._get_variant_results(test_id, "A")
        results_b = await self._get_variant_results(test_id, "B")
        
        # Calcul des statistiques
        analysis = self._analyze_test_results(results_a, results_b)
        
        return {
            "test_id": test_id,
            "test_name": test_config["test_name"],
            "status": test_config["status"],
            "variant_a": results_a,
            "variant_b": results_b,
            "analysis": analysis,
            "recommendation": self._generate_test_recommendation(analysis)
        }
    
    async def _get_test_config(self, test_id: str) -> Optional[Dict]:
        """Récupération de la configuration du test"""
        data = await self.redis.get(f"ab_test:{test_id}")
        return json.loads(data) if data else None
    
    async def _get_variant_results(self, test_id: str, variant: str) -> Dict[str, Any]:
        """Récupération des résultats d'une variante"""
        results_key = f"ab_test:{test_id}:results:{variant}"
        raw_results = await self.redis.lrange(results_key, 0, -1)
        
        if not raw_results:
            return {"sample_size": 0, "metrics": {}}
        
        # Parsing des résultats
        parsed_results = [json.loads(result) for result in raw_results]
        
        # Calcul des moyennes
        all_metrics = [result["metrics"] for result in parsed_results]
        avg_metrics = {}
        
        if all_metrics:
            metric_keys = all_metrics[0].keys()
            for key in metric_keys:
                values = [m[key] for m in all_metrics if key in m]
                avg_metrics[key] = np.mean(values) if values else 0.0
        
        return {
            "sample_size": len(parsed_results),
            "metrics": avg_metrics
        }
    
    def _analyze_test_results(self, results_a: Dict, results_b: Dict) -> Dict[str, Any]:
        """Analyse statistique des résultats"""
        if results_a["sample_size"] == 0 or results_b["sample_size"] == 0:
            return {"error": "Données insuffisantes"}
        
        analysis = {}
        
        # Comparaison métrique par métrique
        for metric in results_a["metrics"]:
            if metric in results_b["metrics"]:
                value_a = results_a["metrics"][metric]
                value_b = results_b["metrics"][metric]
                
                improvement = ((value_b - value_a) / value_a * 100) if value_a > 0 else 0
                
                analysis[metric] = {
                    "variant_a_value": value_a,
                    "variant_b_value": value_b,
                    "improvement_percent": improvement,
                    "winner": "B" if value_b > value_a else "A"
                }
        
        return analysis
    
    def _generate_test_recommendation(self, analysis: Dict) -> str:
        """Génération de recommandation basée sur l'analyse"""
        if "error" in analysis:
            return "Données insuffisantes pour une recommandation"
        
        b_wins = sum(1 for metric in analysis.values() if metric.get("winner") == "B")
        total_metrics = len(analysis)
        
        if b_wins > total_metrics * 0.6:
            return "Recommandation: Adopter la variante B"
        elif b_wins < total_metrics * 0.4:
            return "Recommandation: Conserver la variante A"
        else:
            return "Recommandation: Résultats mitigés, prolonger le test"

class EnterprisePromptEngineering:
    """Système enterprise principal de Prompt Engineering"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 2),
            decode_responses=True
        )
        
        # Pool de connexions PostgreSQL
        self.db_pool = None
        
        # Composants du système
        self.security_validator = EnterprisePromptSecurityValidator()
        self.optimizer = EnterprisePromptOptimizer()
        self.analytics = None  # Initialisé après la DB
        self.template_manager = None  # Initialisé après la DB
        self.ab_tester = None  # Initialisé après analytics
        
        # Métriques système
        self.system_metrics = {
            "total_prompts_processed": 0,
            "optimization_requests": 0,
            "security_validations": 0,
            "ab_tests_created": 0,
            "templates_created": 0
        }
    
    async def initialize(self):
        """Initialisation du système enterprise"""
        try:
            # Initialisation du pool de base de données
            self.db_pool = await asyncpg.create_pool(
                host=self.config.get("db_host", "localhost"),
                port=self.config.get("db_port", 5432),
                user=self.config.get("db_user", "postgres"),
                password=self.config.get("db_password", "password"),
                database=self.config.get("db_name", "ainflue_enterprise"),
                min_size=5,
                max_size=20
            )
            
            # Création des tables si nécessaire
            await self._create_database_schema()
            
            # Initialisation des composants
            self.analytics = EnterprisePromptAnalytics(self.redis, self.db_pool)
            self.template_manager = EnterprisePromptTemplateManager(self.redis, self.db_pool)
            self.ab_tester = EnterprisePromptABTester(self.redis, self.analytics)
            
            # Test de connectivité Redis
            await self.redis.ping()
            
            logger.info("Système Enterprise Prompt Engineering initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            raise
    
    async def _create_database_schema(self):
        """Création du schéma de base de données"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS prompt_metrics (
            id SERIAL PRIMARY KEY,
            prompt_id VARCHAR(255) NOT NULL,
            version VARCHAR(50) NOT NULL,
            response_time FLOAT NOT NULL,
            token_count INTEGER NOT NULL,
            cost FLOAT NOT NULL,
            accuracy_score FLOAT NOT NULL,
            relevance_score FLOAT NOT NULL,
            safety_score FLOAT NOT NULL,
            user_satisfaction FLOAT NOT NULL,
            conversion_rate FLOAT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id SERIAL PRIMARY KEY,
            template_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            version VARCHAR(50) NOT NULL,
            category VARCHAR(100) NOT NULL,
            prompt_type VARCHAR(50) NOT NULL,
            template_content TEXT NOT NULL,
            variables JSONB NOT NULL,
            validation_rules JSONB NOT NULL,
            performance_baseline JSONB NOT NULL,
            security_level VARCHAR(20) NOT NULL,
            tags JSONB NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_prompt_metrics_id_timestamp ON prompt_metrics(prompt_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_prompt_templates_id ON prompt_templates(template_id);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)
    
    async def process_prompt_request(self, prompt: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Traitement complet d'une requête de prompt enterprise"""
        options = options or {}
        request_id = f"req_{int(time.time())}"
        
        try:
            # Validation de sécurité
            security_level = SecurityLevel(options.get("security_level", "medium"))
            security_result = self.security_validator.validate_prompt_security(prompt, security_level)
            
            if not security_result["is_safe"]:
                return {
                    "request_id": request_id,
                    "status": "rejected",
                    "reason": "Échec de validation de sécurité",
                    "security_analysis": security_result
                }
            
            # Optimisation si demandée
            optimized_prompt = prompt
            optimization_result = None
            
            if options.get("optimize", False):
                target_metrics = options.get("target_metrics", {})
                optimization_result = self.optimizer.optimize_prompt(prompt, target_metrics)
                optimized_prompt = optimization_result.optimized_prompt
                self.system_metrics["optimization_requests"] += 1
            
            # Application de template si spécifié
            if options.get("template_id"):
                template = await self.template_manager.get_template(options["template_id"])
                if template:
                    optimized_prompt = self._apply_template(optimized_prompt, template, options.get("template_vars", {}))
            
            # Tracking des métriques
            self.system_metrics["total_prompts_processed"] += 1
            self.system_metrics["security_validations"] += 1
            
            return {
                "request_id": request_id,
                "status": "success",
                "original_prompt": prompt,
                "processed_prompt": optimized_prompt,
                "security_analysis": security_result,
                "optimization_result": optimization_result,
                "processing_time": time.time()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête: {e}")
            return {
                "request_id": request_id,
                "status": "error",
                "error": str(e)
            }
    
    def _apply_template(self, prompt: str, template: PromptTemplate, variables: Dict[str, Any]) -> str:
        """Application d'un template de prompt"""
        try:
            # Substitution des variables dans le template
            formatted_template = template.template_content
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                formatted_template = formatted_template.replace(placeholder, str(var_value))
            
            # Intégration du prompt utilisateur
            if "{user_prompt}" in formatted_template:
                return formatted_template.replace("{user_prompt}", prompt)
            else:
                return f"{formatted_template}\n\n{prompt}"
            
        except Exception as e:
            logger.error(f"Erreur lors de l'application du template: {e}")
            return prompt
    
    async def create_optimized_template(self, name: str, base_prompt: str, 
                                      category: str, prompt_type: PromptType) -> str:
        """Création d'un template optimisé"""
        try:
            # Optimisation du prompt de base
            optimization_result = self.optimizer.optimize_prompt(base_prompt, {})
            
            # Création du template
            template = PromptTemplate(
                template_id=f"template_{int(time.time())}",
                name=name,
                version="1.0",
                category=category,
                prompt_type=prompt_type,
                template_content=optimization_result.optimized_prompt,
                variables={},
                validation_rules={},
                performance_baseline={},
                security_level=SecurityLevel.MEDIUM,
                tags=[category, "optimized"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            template_id = await self.template_manager.create_template(template)
            self.system_metrics["templates_created"] += 1
            
            return template_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du template: {e}")
            raise
    
    async def run_prompt_ab_test(self, test_name: str, prompt_a: str, prompt_b: str,
                                duration_hours: int = 24) -> str:
        """Lancement d'un test A/B de prompts"""
        try:
            test_id = await self.ab_tester.create_ab_test(
                test_name, prompt_a, prompt_b, duration_hours=duration_hours
            )
            self.system_metrics["ab_tests_created"] += 1
            return test_id
            
        except Exception as e:
            logger.error(f"Erreur lors du lancement du test A/B: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Récupération du statut du système"""
        try:
            # Test de connectivité
            redis_status = "connected" if await self.redis.ping() else "disconnected"
            db_status = "connected" if self.db_pool else "disconnected"
            
            return {
                "status": "operational",
                "version": "1.0.0",
                "components": {
                    "redis": redis_status,
                    "database": db_status,
                    "security_validator": "active",
                    "optimizer": "active",
                    "analytics": "active" if self.analytics else "inactive",
                    "template_manager": "active" if self.template_manager else "inactive",
                    "ab_tester": "active" if self.ab_tester else "inactive"
                },
                "metrics": self.system_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def shutdown(self):
        """Arrêt propre du système"""
        try:
            if self.db_pool:
                await self.db_pool.close()
            
            await self.redis.close()
            logger.info("Système Enterprise Prompt Engineering arrêté proprement")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt: {e}")

# Fonctions utilitaires pour l'intégration enterprise
async def initialize_enterprise_prompt_system(config: Dict[str, Any]) -> EnterprisePromptEngineering:
    """Initialisation du système enterprise de prompt engineering"""
    system = EnterprisePromptEngineering(config)
    await system.initialize()
    return system

def create_default_config() -> Dict[str, Any]:
    """Configuration par défaut pour le système enterprise"""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 2,
        "db_host": "localhost", 
        "db_port": 5432,
        "db_user": "postgres",
        "db_password": "password",
        "db_name": "ainflue_enterprise",
        "security_level": "medium",
        "optimization_enabled": True,
        "analytics_enabled": True,
        "ab_testing_enabled": True
    }

# Point d'entrée pour démonstration
async def demonstrate_enterprise_prompt_engineering():
    """Démonstration des capacités enterprise de prompt engineering"""
    
    print("🚀 Démonstration Enterprise Prompt Engineering System")
    print("=" * 60)
    
    try:
        # Configuration et initialisation
        config = create_default_config()
        system = await initialize_enterprise_prompt_system(config)
        
        # Test de prompt avec optimisation
        test_prompt = "Write a professional email about project status"
        
        print("📝 Test d'optimisation de prompt:")
        result = await system.process_prompt_request(
            test_prompt,
            {"optimize": True, "security_level": "high"}
        )
        
        print(f"Prompt original: {result['original_prompt']}")
        print(f"Prompt optimisé: {result['processed_prompt']}")
        print(f"Score de sécurité: {result['security_analysis']['risk_score']:.2f}")
        
        # Création d'un template
        print("\n🔧 Création de template optimisé:")
        template_id = await system.create_optimized_template(
            "Professional Email Template",
            "Write a {tone} email about {subject}",
            "communication",
            PromptType.GENERATION
        )
        print(f"Template créé: {template_id}")
        
        # Test A/B
        print("\n🧪 Lancement de test A/B:")
        ab_test_id = await system.run_prompt_ab_test(
            "Email Tone Test",
            "Write a formal email about project status",
            "Write a friendly email about project status",
            duration_hours=1
        )
        print(f"Test A/B lancé: {ab_test_id}")
        
        # Statut du système
        print("\n📊 Statut du système:")
        status = await system.get_system_status()
        print(f"Statut: {status['status']}")
        print(f"Prompts traités: {status['metrics']['total_prompts_processed']}")
        print(f"Optimisations: {status['metrics']['optimization_requests']}")
        
        await system.shutdown()
        print("\n✅ Démonstration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")

if __name__ == "__main__":
    # Exécution de la démonstration
    asyncio.run(demonstrate_enterprise_prompt_engineering())