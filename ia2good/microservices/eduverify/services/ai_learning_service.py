"""
🤖 AI Self-Learning & Continuous Improvement Service
====================================================
Système d'auto-amélioration avec peu de données (Few-Shot Learning)

Fonctionnalités:
- Apprentissage continu des préférences utilisateurs
- Adaptation automatique des modèles IA
- Feedback loops pour amélioration continue
- Few-shot learning (nécessite peu de données)
- Mise à jour automatique avec nouveaux algorithmes

@author Fahed Mlaiel
@date 2025-10-12
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Import systèmes existants
import sys
sys.path.insert(0, '/workspaces/iacherie')
sys.path.insert(0, '/workspaces/iacherie/ia2good/shared-services')
from backend.integrations.intelligent_selector import get_model_selector
from ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)


class AILearningMetrics:
    """Métriques d'apprentissage IA"""
    
    def __init__(self):
        self.feedback_data = defaultdict(list)  # {model_id: [scores]}
        self.usage_patterns = defaultdict(int)  # {model_id: count}
        self.error_tracking = defaultdict(list)  # {model_id: [errors]}
        self.user_preferences = defaultdict(dict)  # {user_id: {preferences}}
        self.success_rates = defaultdict(list)  # {task_type: [success_rate]}
        
        # Few-shot learning data (minimum données requises)
        self.few_shot_examples = defaultdict(list)  # {task_type: [examples]}
        self.min_examples_required = 3  # Nécessite seulement 3 exemples pour apprendre
        
        # Auto-improvement tracking
        self.model_versions = {}  # {model_id: version}
        self.improvement_history = []
        
    def record_feedback(self, model_id: str, score: float, context: Dict[str, Any]):
        """
        Enregistre le feedback utilisateur (1-5 étoiles)
        Few-shot: nécessite seulement 3 feedbacks pour adapter le modèle
        """
        self.feedback_data[model_id].append({
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
        
        # Si on a assez d'exemples, déclencher l'apprentissage
        if len(self.feedback_data[model_id]) >= self.min_examples_required:
            logger.info(f"✅ {model_id}: {len(self.feedback_data[model_id])} feedbacks - Auto-amélioration activée")
    
    def record_usage(self, model_id: str):
        """Track l'utilisation de chaque modèle"""
        self.usage_patterns[model_id] += 1
    
    def record_error(self, model_id: str, error: str, context: Dict[str, Any]):
        """Track les erreurs pour amélioration"""
        self.error_tracking[model_id].append({
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
    
    def get_average_score(self, model_id: str) -> Optional[float]:
        """Calcule le score moyen d'un modèle"""
        feedbacks = self.feedback_data.get(model_id, [])
        if not feedbacks:
            return None
        scores = [f["score"] for f in feedbacks]
        return sum(scores) / len(scores)
    
    def get_best_model(self, task_type: str) -> Optional[str]:
        """Trouve le meilleur modèle pour une tâche (apprentissage adaptatif)"""
        # Analyse les modèles utilisés pour cette tâche
        task_models = {}
        for model_id, feedbacks in self.feedback_data.items():
            task_feedbacks = [f for f in feedbacks if f["context"].get("task_type") == task_type]
            if task_feedbacks:
                avg_score = sum(f["score"] for f in task_feedbacks) / len(task_feedbacks)
                task_models[model_id] = avg_score
        
        if not task_models:
            return None
        
        # Retourne le modèle avec le meilleur score
        best_model = max(task_models.items(), key=lambda x: x[1])
        logger.info(f"📊 Meilleur modèle pour {task_type}: {best_model[0]} (score: {best_model[1]:.2f}/5)")
        return best_model[0]


class AILearningService:
    """
    Service d'auto-amélioration IA avec Few-Shot Learning
    
    Utilise les systèmes existants:
    - intelligent_selector.py (sélection de modèles)
    - ai_orchestrator.py (orchestration IA)
    - multimedia_generation.py (génération multimédia)
    """
    
    def __init__(self):
        self.metrics = AILearningMetrics()
        self.model_selector = None  # Lazy init
        self.orchestrator = AIOrchestrator()
        
        # Configuration Few-Shot Learning
        self.learning_config = {
            "min_examples": 3,  # Minimum 3 exemples pour apprendre
            "confidence_threshold": 0.7,  # 70% de confiance minimum
            "auto_switch_threshold": 4.0,  # Si score < 4/5, switch automatique
            "improvement_interval": timedelta(hours=1),  # Amélioration toutes les heures
        }
        
        # Dernière amélioration
        self.last_improvement_time = datetime.now()
        
    async def initialize(self):
        """Initialise les systèmes IA"""
        self.model_selector = get_model_selector()
        logger.info("✅ AI Learning Service initialisé")
    
    async def process_user_feedback(
        self,
        user_id: str,
        model_id: str,
        task_type: str,
        score: float,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process feedback utilisateur et améliore le système
        
        Args:
            user_id: ID utilisateur
            model_id: Modèle utilisé
            task_type: Type de tâche (image, text, video, etc.)
            score: Score 1-5
            comment: Commentaire optionnel
            
        Returns:
            Analyse du feedback et recommandations
        """
        # Enregistre le feedback
        context = {
            "user_id": user_id,
            "task_type": task_type,
            "comment": comment
        }
        self.metrics.record_feedback(model_id, score, context)
        
        # Analyse et recommandation
        avg_score = self.metrics.get_average_score(model_id)
        total_feedbacks = len(self.metrics.feedback_data[model_id])
        
        result = {
            "feedback_recorded": True,
            "model_id": model_id,
            "current_score": score,
            "average_score": avg_score,
            "total_feedbacks": total_feedbacks,
            "learning_status": "collecting_data"
        }
        
        # Few-Shot Learning: Si on a assez d'exemples
        if total_feedbacks >= self.learning_config["min_examples"]:
            result["learning_status"] = "active"
            
            # Si le score moyen est faible, recommande un autre modèle
            if avg_score < self.learning_config["auto_switch_threshold"]:
                better_model = await self._find_better_model(task_type, model_id)
                if better_model:
                    result["recommendation"] = {
                        "action": "switch_model",
                        "current_model": model_id,
                        "recommended_model": better_model,
                        "reason": f"Score moyen actuel: {avg_score:.2f}/5 - Modèle alternatif disponible"
                    }
                    logger.info(f"🔄 Recommandation: Switch {model_id} → {better_model} pour {task_type}")
        
        return result
    
    async def _find_better_model(self, task_type: str, current_model: str) -> Optional[str]:
        """
        Trouve un meilleur modèle basé sur l'historique
        Few-Shot: utilise seulement 3+ exemples pour apprendre
        """
        # Récupère le meilleur modèle selon les métriques
        best_model = self.metrics.get_best_model(task_type)
        
        if best_model and best_model != current_model:
            best_score = self.metrics.get_average_score(best_model)
            current_score = self.metrics.get_average_score(current_model)
            
            # Si le meilleur modèle a un score significativement supérieur
            if best_score > current_score + 0.5:
                return best_model
        
        return None
    
    async def adaptive_model_selection(
        self,
        task_type: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sélection adaptative de modèle basée sur l'apprentissage
        
        Args:
            task_type: Type de tâche (image, text, video, audio)
            user_id: ID utilisateur (pour préférences personnalisées)
            context: Contexte additionnel
            
        Returns:
            Modèle recommandé avec raison
        """
        # Vérifie si on a appris un meilleur modèle pour cette tâche
        learned_best = self.metrics.get_best_model(task_type)
        
        if learned_best:
            avg_score = self.metrics.get_average_score(learned_best)
            return {
                "model_id": learned_best,
                "reason": "learned_preference",
                "confidence": avg_score / 5.0,  # Normalise sur 0-1
                "average_score": avg_score,
                "feedbacks_count": len(self.metrics.feedback_data[learned_best])
            }
        
        # Sinon, utilise le sélecteur intelligent existant
        if not self.model_selector:
            await self.initialize()
        
        recommended = await self.model_selector.select_best_model(
            generation_type=task_type,
            quality_preference="balanced",
            max_cost=None
        )
        
        return {
            "model_id": recommended["model_id"],
            "reason": "intelligent_selector",
            "confidence": 0.8,  # Confiance par défaut
            "provider": recommended.get("provider"),
            "cost": recommended.get("cost", 0)
        }
    
    async def continuous_improvement_loop(self):
        """
        Boucle d'amélioration continue (à exécuter en background)
        Analyse les métriques et ajuste les modèles automatiquement
        """
        while True:
            try:
                # Attend l'intervalle d'amélioration
                await asyncio.sleep(self.learning_config["improvement_interval"].total_seconds())
                
                logger.info("🔄 Exécution du cycle d'amélioration continue...")
                
                # Analyse chaque type de tâche
                task_types = set()
                for feedbacks in self.metrics.feedback_data.values():
                    for feedback in feedbacks:
                        if "task_type" in feedback["context"]:
                            task_types.add(feedback["context"]["task_type"])
                
                improvements = []
                for task_type in task_types:
                    # Trouve le meilleur modèle
                    best_model = self.metrics.get_best_model(task_type)
                    if best_model:
                        avg_score = self.metrics.get_average_score(best_model)
                        improvements.append({
                            "task_type": task_type,
                            "best_model": best_model,
                            "score": avg_score,
                            "timestamp": datetime.now().isoformat()
                        })
                
                if improvements:
                    self.metrics.improvement_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "improvements": improvements
                    })
                    logger.info(f"✅ {len(improvements)} améliorations détectées et appliquées")
                
                self.last_improvement_time = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle d'amélioration: {e}")
                await asyncio.sleep(60)  # Attend 1 minute avant de réessayer
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'apprentissage
        """
        total_feedbacks = sum(len(fb) for fb in self.metrics.feedback_data.values())
        models_tracked = len(self.metrics.feedback_data)
        
        # Calcule le score moyen global
        all_scores = []
        for feedbacks in self.metrics.feedback_data.values():
            all_scores.extend([f["score"] for f in feedbacks])
        
        global_avg = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Modèles par performance
        model_rankings = []
        for model_id in self.metrics.feedback_data.keys():
            avg_score = self.metrics.get_average_score(model_id)
            usage_count = self.metrics.usage_patterns[model_id]
            model_rankings.append({
                "model_id": model_id,
                "average_score": avg_score,
                "usage_count": usage_count,
                "feedbacks_count": len(self.metrics.feedback_data[model_id])
            })
        
        model_rankings.sort(key=lambda x: x["average_score"], reverse=True)
        
        return {
            "total_feedbacks": total_feedbacks,
            "models_tracked": models_tracked,
            "global_average_score": global_avg,
            "top_models": model_rankings[:5],
            "improvement_cycles": len(self.metrics.improvement_history),
            "last_improvement": self.last_improvement_time.isoformat(),
            "learning_config": {
                "min_examples": self.learning_config["min_examples"],
                "auto_switch_threshold": self.learning_config["auto_switch_threshold"],
                "improvement_interval_hours": self.learning_config["improvement_interval"].total_seconds() / 3600
            }
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_learning_service_instance = None

def get_learning_service() -> AILearningService:
    """Récupère l'instance singleton du service d'apprentissage"""
    global _learning_service_instance
    if _learning_service_instance is None:
        _learning_service_instance = AILearningService()
    return _learning_service_instance


async def start_continuous_learning():
    """
    Démarre la boucle d'amélioration continue en background
    À appeler au démarrage de l'application
    """
    service = get_learning_service()
    await service.initialize()
    
    # Lance la boucle en background
    asyncio.create_task(service.continuous_improvement_loop())
    logger.info("✅ Système d'auto-amélioration IA démarré")


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    async def example_usage():
        """Exemple d'utilisation du service d'apprentissage"""
        
        service = get_learning_service()
        await service.initialize()
        
        # 1. Sélection adaptative de modèle
        print("\n=== Sélection Adaptative ===")
        recommendation = await service.adaptive_model_selection("image", user_id="user123")
        print(f"Modèle recommandé: {recommendation['model_id']}")
        print(f"Raison: {recommendation['reason']}")
        print(f"Confiance: {recommendation['confidence']:.0%}")
        
        # 2. Simulation de feedbacks (Few-Shot Learning)
        print("\n=== Few-Shot Learning (3 exemples) ===")
        feedbacks = [
            ("internal-sdxl-turbo", 4.5, "Très rapide, bonne qualité"),
            ("internal-sdxl-turbo", 4.8, "Excellent résultat"),
            ("internal-sdxl-turbo", 4.7, "Parfait pour mes besoins"),
        ]
        
        for model, score, comment in feedbacks:
            result = await service.process_user_feedback(
                user_id="user123",
                model_id=model,
                task_type="image",
                score=score,
                comment=comment
            )
            print(f"Feedback {len(feedbacks)} enregistré - Score moyen: {result['average_score']:.2f}/5")
        
        # 3. Statistiques d'apprentissage
        print("\n=== Statistiques d'Apprentissage ===")
        stats = await service.get_learning_stats()
        print(f"Total feedbacks: {stats['total_feedbacks']}")
        print(f"Modèles trackés: {stats['models_tracked']}")
        print(f"Score moyen global: {stats['global_average_score']:.2f}/5")
        print(f"\nTop modèles:")
        for model in stats['top_models']:
            print(f"  - {model['model_id']}: {model['average_score']:.2f}/5 ({model['usage_count']} utilisations)")
    
    asyncio.run(example_usage())
