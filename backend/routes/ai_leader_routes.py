"""
🎯 AI LEADER DASHBOARD - Interface de Monitoring de l'Agent IA Autonome

Visualise en temps réel:
- Phase actuelle de l'agent (Learning, Backup, Autonomous, Evolution)
- Capacités internes développées
- APIs externes observées et remplacées
- Pourcentage d'autonomie
- Performance comparée aux APIs externes

Author: Fahed Mlaiel
Date: October 2025
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging

from backend.ai_leader_agent import (
    ai_leader_agent,
    get_ai_leader_status,
    AgentPhase,
    APIType
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/ai-leader/status")
async def get_agent_status():
    """
    Récupère le statut complet de l'AI Leader Agent
    """
    try:
        status = get_ai_leader_status()
        return {
            "success": True,
            "agent": status
        }
    except Exception as e:
        logger.error(f"Erreur récupération status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-leader/capabilities")
async def get_capabilities():
    """
    Liste toutes les capacités internes de l'agent
    """
    try:
        capabilities = []
        
        for name, cap in ai_leader_agent.internal_capabilities.items():
            capabilities.append({
                "name": name,
                "type": cap.capability_type.value,
                "accuracy": cap.accuracy,
                "quality": cap.quality,
                "speed": cap.speed,
                "training_progress": cap.training_progress,
                "ready_for_production": cap.ready_for_production,
                "matches_api_quality": cap.matches_api_quality,
                "better_than_api": cap.better_than_api
            })

        
        return {
            "success": True,
            "total": len(capabilities),
            "ready": sum(1 for c in capabilities if c["ready_for_production"]),
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Erreur récupération capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-leader/learning-data")
async def get_learning_data():
    """
    Récupère les données d'apprentissage pour toutes les APIs
    """
    try:
        learning_data = []
        
        for name, data in ai_leader_agent.api_learning_data.items():
            learning_data.append({
                "api_name": data.api_name,
                "api_type": data.api_type.value,
                "training_samples": data.training_samples,
                "success_rate": data.success_rate,
                "model_accuracy": data.model_accuracy,
                "is_available": data.is_available,
                "consecutive_failures": data.consecutive_failures,
                "avg_latency": sum(data.latency_history[-100:]) / len(data.latency_history[-100:]) if data.latency_history else 0,
                "avg_quality": sum(data.quality_scores[-100:]) / len(data.quality_scores[-100:]) if data.quality_scores else 0,
                "cost_per_request": data.cost_per_request
            })

        
        return {
            "success": True,
            "total_apis": len(learning_data),
            "learning_data": learning_data
        }
    except Exception as e:
        logger.error(f"Erreur récupération learning data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-leader/autonomy-metrics")
async def get_autonomy_metrics():
    """
    Métriques détaillées sur l'autonomie de l'agent
    """
    try:
        status = get_ai_leader_status()
        
        # Calculer des métriques supplémentaires

        total_apis = len(ai_leader_agent.api_learning_data)

        ready_capabilities = status["capabilities_ready"]

        
        coverage = ready_capabilities / total_apis if total_apis > 0 else 0
        
        # Économies estimées (coût APIs externes vs internes)

        total_external_cost = sum(
            data.cost_per_request * data.training_samples
            for data in ai_leader_agent.api_learning_data.values()
        )
        
        # Coût interne estimé (beaucoup moins cher)

        internal_cost_factor = 0.1  # 90% moins cher

        total_internal_cost = total_external_cost * internal_cost_factor

        savings = total_external_cost - total_internal_cost
        
        return {
            "success": True,
            "metrics": {
                "autonomy_percentage": status["autonomy_percentage"],
                "api_coverage": coverage,
                "total_apis_tracked": total_apis,
                "capabilities_ready": ready_capabilities,
                "total_calls_observed": status["total_api_calls_observed"],
                "total_calls_replaced": status["total_api_calls_replaced"],
                "estimated_savings": savings,
                "cost_reduction_percentage": 90,
                "is_fully_autonomous": status["is_fully_autonomous"],
                "current_phase": status["phase"]
            }
        }
    except Exception as e:
        logger.error(f"Erreur calcul métriques: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-leader/force-autonomous")
async def force_autonomous_mode():
    """
    Force le passage en mode autonome (pour test)
    """
    try:
        ai_leader_agent.current_phase = AgentPhase.AUTONOMOUS
        await ai_leader_agent._save_state()

        
        return {
            "success": True,
            "message": "Agent forcé en mode AUTONOMOUS",
            "phase": ai_leader_agent.current_phase.value
        }
    except Exception as e:
        logger.error(f"Erreur force autonomous: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-leader/trigger-training")
async def trigger_training():
    """
    Déclenche l'entraînement de toutes les capacités
    """
    try:
        trained = []
        
        for api_name, data in ai_leader_agent.api_learning_data.items():
            if data.training_samples >= 10:  # Minimum de samples
                await ai_leader_agent._train_capability(api_name, data.api_type)

                trained.append(api_name)

        
        return {
            "success": True,
            "message": f"Entraînement lancé pour {len(trained)} APIs",
            "trained_apis": trained
        }
    except Exception as e:
        logger.error(f"Erreur trigger training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-leader/comparison/{api_name}")
async def compare_with_external(api_name: str):
    """
    Compare les performances de la capacité interne avec l'API externe
    """
    try:
        # Trouver les données d'apprentissage
        if api_name not in ai_leader_agent.api_learning_data:
            raise HTTPException(status_code=404, detail=f"API {api_name} non trouvée")


        
        learning_data = ai_leader_agent.api_learning_data[api_name]
        
        # Trouver la capacité interne

        capability_name = f"internal_{api_name.lower().replace(' ', '_')}"
        if capability_name not in ai_leader_agent.internal_capabilities:
            return {
                "success": True,
                "message": "Capacité interne pas encore développée",
                "internal_ready": False
            }

        
        capability = ai_leader_agent.internal_capabilities[capability_name]
        
        # Calculer les métriques externes

        external_avg_quality = sum(learning_data.quality_scores[-100:]) / len(learning_data.quality_scores[-100:]) if learning_data.quality_scores else 0

        external_avg_latency = sum(learning_data.latency_history[-100:]) / len(learning_data.latency_history[-100:]) if learning_data.latency_history else 0
        
        return {
            "success": True,
            "api_name": api_name,
            "external": {
                "quality": external_avg_quality,
                "latency": external_avg_latency,
                "cost_per_request": learning_data.cost_per_request,
                "success_rate": learning_data.success_rate,
                "is_available": learning_data.is_available
            },
            "internal": {
                "quality": capability.quality,
                "latency": 1.0 / capability.speed if capability.speed > 0 else 0,
                "cost_per_request": learning_data.cost_per_request * 0.1,  # 90% moins cher
                "accuracy": capability.accuracy,
                "ready": capability.ready_for_production
            },
            "comparison": {
                "quality_ratio": capability.quality / external_avg_quality if external_avg_quality > 0 else 0,
                "speed_improvement": (external_avg_latency * capability.speed) if external_avg_latency > 0 else 0,
                "cost_savings": 90,  # 90% moins cher
                "internal_is_better": capability.better_than_api,
                "can_replace": capability.ready_for_production
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur comparaison: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-leader/evolution-timeline")
async def get_evolution_timeline():
    """
    Timeline de l'évolution de l'agent
    """
    try:
        timeline = []
        
        # Créer une timeline basée sur les données d'apprentissage
        for api_name, data in ai_leader_agent.api_learning_data.items():
            capability_name = f"internal_{api_name.lower().replace(' ', '_')}"
            
            if capability_name in ai_leader_agent.internal_capabilities:
                cap = ai_leader_agent.internal_capabilities[capability_name]
                
                timeline.append({
                    "api_name": api_name,
                    "training_samples": data.training_samples,
                    "training_progress": cap.training_progress,
                    "accuracy": cap.accuracy,
                    "quality": cap.quality,
                    "ready": cap.ready_for_production,
                    "last_trained": data.last_trained.isoformat() if data.last_trained else None
                })
        
        # Trier par progression
        timeline.sort(key=lambda x: x["training_progress"], reverse=True)

        
        return {
            "success": True,
            "timeline": timeline,
            "total_capabilities": len(timeline)
        }
    except Exception as e:
        logger.error(f"Erreur evolution timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))
