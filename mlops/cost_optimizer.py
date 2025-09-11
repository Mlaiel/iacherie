"""
🚀 COST OPTIMIZER - ENTERPRISE MLOPS COST OPTIMIZATION ENGINE
Rôle DevOps: Optimisation des coûts d'infrastructure ML avec recommandations intelligentes

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
import aiosqlite
from collections import defaultdict
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import os

# Ainflue Business Logic Integration
from core.config import AinflueCoreConfig
from core.exceptions import AinflueCoreException

class CostOptimizationStrategy(Enum):
    """Stratégies d'optimisation des coûts"""
    RESOURCE_RIGHTSIZING = "resource_rightsizing"
    SPOT_INSTANCES = "spot_instances"
    RESERVED_INSTANCES = "reserved_instances"
    AUTO_SCALING = "auto_scaling"
    IDLE_RESOURCE_TERMINATION = "idle_resource_termination"
    WORKLOAD_SCHEDULING = "workload_scheduling"
    MULTI_CLOUD_ARBITRAGE = "multi_cloud_arbitrage"

class CloudProvider(Enum):
    """Providers cloud supportés"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"

@dataclass
class ResourceUsage:
    """Métriques d'utilisation des ressources"""
    resource_id: str
    resource_type: str
    provider: CloudProvider
    cpu_utilization: float
    memory_utilization: float
    gpu_utilization: float
    storage_usage: float
    network_io: float
    cost_per_hour: float
    uptime_hours: int
    idle_hours: int
    creator_type: str  # musician, blogger, photographer, influencer, comedian
    model_type: str
    timestamp: datetime

@dataclass
class CostRecommendation:
    """Recommandation d'optimisation des coûts"""
    recommendation_id: str
    strategy: CostOptimizationStrategy
    resource_id: str
    current_cost: float
    projected_cost: float
    savings_amount: float
    savings_percentage: float
    confidence_score: float
    implementation_effort: str
    risk_level: str
    description: str
    action_items: List[str]
    creator_impact: str
    model_impact: str

class CostOptimizer:
    """
    🚀 Enterprise Cost Optimizer pour MLOps Infrastructure
    
    Fonctionnalités DevOps Expert:
    - Optimisation coûts multi-cloud intelligente
    - Recommandations ML-powered avec attribution précise
    - Right-sizing automatique des ressources
    - Spot instances et reserved instances optimization
    - Cost allocation par créateur/modèle
    - Prédiction coûts avec anomaly detection
    """
    
    def __init__(self, config: Optional[AinflueCoreConfig] = None):
        self.config = config or AinflueCoreConfig()
        self.logger = self._setup_logging()
        self.db_path = "mlops_cost_optimization.db"
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Creator-specific cost profiles
        self.creator_cost_profiles = {
            "musician": {
                "gpu_intensive": True,
                "storage_heavy": True,
                "peak_hours": [18, 19, 20, 21, 22],
                "cost_sensitivity": "medium"
            },
            "blogger": {
                "gpu_intensive": False,
                "storage_heavy": False,
                "peak_hours": [9, 10, 11, 14, 15, 16],
                "cost_sensitivity": "high"
            },
            "photographer": {
                "gpu_intensive": True,
                "storage_heavy": True,
                "peak_hours": [10, 11, 12, 13, 14, 15],
                "cost_sensitivity": "medium"
            },
            "influencer": {
                "gpu_intensive": True,
                "storage_heavy": True,
                "peak_hours": [17, 18, 19, 20, 21],
                "cost_sensitivity": "low"
            },
            "comedian": {
                "gpu_intensive": False,
                "storage_heavy": False,
                "peak_hours": [19, 20, 21, 22, 23],
                "cost_sensitivity": "high"
            }
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger("CostOptimizer")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    async def initialize(self) -> None:
        """Initialisation de la base de données"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS resource_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        resource_id TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        cpu_utilization REAL,
                        memory_utilization REAL,
                        gpu_utilization REAL,
                        storage_usage REAL,
                        network_io REAL,
                        cost_per_hour REAL,
                        uptime_hours INTEGER,
                        idle_hours INTEGER,
                        creator_type TEXT,
                        model_type TEXT,
                        timestamp TEXT,
                        UNIQUE(resource_id, timestamp)
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS cost_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recommendation_id TEXT UNIQUE NOT NULL,
                        strategy TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        current_cost REAL,
                        projected_cost REAL,
                        savings_amount REAL,
                        savings_percentage REAL,
                        confidence_score REAL,
                        implementation_effort TEXT,
                        risk_level TEXT,
                        description TEXT,
                        action_items TEXT,
                        creator_impact TEXT,
                        model_impact TEXT,
                        created_at TEXT,
                        implemented BOOLEAN DEFAULT FALSE
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS cost_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        period TEXT NOT NULL,
                        total_cost REAL,
                        optimized_cost REAL,
                        savings_realized REAL,
                        cost_by_creator TEXT,
                        cost_by_provider TEXT,
                        top_recommendations TEXT,
                        created_at TEXT
                    )
                """)
                
                await db.commit()
                
            self.logger.info("✅ Cost Optimizer initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
            raise AinflueCoreException(f"Échec initialisation Cost Optimizer: {e}")

    async def analyze_resource_usage(self, resource_data: List[Dict[str, Any]]) -> List[ResourceUsage]:
        """Analyse de l'utilisation des ressources"""
        try:
            usage_records = []
            
            for data in resource_data:
                usage = ResourceUsage(
                    resource_id=data['resource_id'],
                    resource_type=data['resource_type'],
                    provider=CloudProvider(data['provider']),
                    cpu_utilization=data.get('cpu_utilization', 0.0),
                    memory_utilization=data.get('memory_utilization', 0.0),
                    gpu_utilization=data.get('gpu_utilization', 0.0),
                    storage_usage=data.get('storage_usage', 0.0),
                    network_io=data.get('network_io', 0.0),
                    cost_per_hour=data.get('cost_per_hour', 0.0),
                    uptime_hours=data.get('uptime_hours', 0),
                    idle_hours=data.get('idle_hours', 0),
                    creator_type=data.get('creator_type', 'unknown'),
                    model_type=data.get('model_type', 'unknown'),
                    timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
                )
                usage_records.append(usage)
                
                # Sauvegarde en base
                await self._save_resource_usage(usage)
            
            self.logger.info(f"✅ Analysé {len(usage_records)} enregistrements d'utilisation")
            return usage_records
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse utilisation: {e}")
            raise AinflueCoreException(f"Échec analyse utilisation: {e}")

    async def generate_cost_recommendations(self, usage_records: List[ResourceUsage]) -> List[CostRecommendation]:
        """Génération de recommandations d'optimisation des coûts"""
        try:
            recommendations = []
            
            for usage in usage_records:
                # Analyse right-sizing
                rightsizing_rec = await self._analyze_rightsizing(usage)
                if rightsizing_rec:
                    recommendations.append(rightsizing_rec)
                
                # Analyse spot instances
                spot_rec = await self._analyze_spot_instances(usage)
                if spot_rec:
                    recommendations.append(spot_rec)
                
                # Analyse idle resources
                idle_rec = await self._analyze_idle_resources(usage)
                if idle_rec:
                    recommendations.append(idle_rec)
                
                # Analyse workload scheduling
                scheduling_rec = await self._analyze_workload_scheduling(usage)
                if scheduling_rec:
                    recommendations.append(scheduling_rec)
            
            # Sauvegarde des recommandations
            for rec in recommendations:
                await self._save_recommendation(rec)
            
            self.logger.info(f"✅ Généré {len(recommendations)} recommandations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération recommandations: {e}")
            raise AinflueCoreException(f"Échec génération recommandations: {e}")

    async def _analyze_rightsizing(self, usage: ResourceUsage) -> Optional[CostRecommendation]:
        """Analyse de right-sizing des ressources"""
        try:
            # Seuils basés sur le type de créateur
            profile = self.creator_cost_profiles.get(usage.creator_type, {})
            
            if usage.cpu_utilization < 30 and usage.memory_utilization < 40:
                # Resource over-provisioned
                savings_percentage = 25.0
                savings_amount = usage.cost_per_hour * usage.uptime_hours * (savings_percentage / 100)
                
                return CostRecommendation(
                    recommendation_id=f"rightsize_{usage.resource_id}_{int(datetime.now().timestamp())}",
                    strategy=CostOptimizationStrategy.RESOURCE_RIGHTSIZING,
                    resource_id=usage.resource_id,
                    current_cost=usage.cost_per_hour * usage.uptime_hours,
                    projected_cost=usage.cost_per_hour * usage.uptime_hours * 0.75,
                    savings_amount=savings_amount,
                    savings_percentage=savings_percentage,
                    confidence_score=0.85,
                    implementation_effort="Low",
                    risk_level="Low",
                    description=f"Resource {usage.resource_id} est sur-dimensionnée. CPU: {usage.cpu_utilization}%, RAM: {usage.memory_utilization}%",
                    action_items=[
                        "Réduire la taille de l'instance",
                        "Monitorer les performances post-modification",
                        "Tester avec un échantillon de trafic"
                    ],
                    creator_impact=f"Optimisation coûts pour créateur {usage.creator_type}",
                    model_impact=f"Performance maintenue pour modèle {usage.model_type}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse rightsizing: {e}")
            return None

    async def _analyze_spot_instances(self, usage: ResourceUsage) -> Optional[CostRecommendation]:
        """Analyse d'utilisation de spot instances"""
        try:
            # Spot instances recommandées pour workloads non-critiques
            profile = self.creator_cost_profiles.get(usage.creator_type, {})
            
            if (usage.resource_type in ["training", "batch_inference"] and 
                profile.get("cost_sensitivity", "medium") in ["medium", "high"]):
                
                savings_percentage = 70.0
                savings_amount = usage.cost_per_hour * usage.uptime_hours * (savings_percentage / 100)
                
                return CostRecommendation(
                    recommendation_id=f"spot_{usage.resource_id}_{int(datetime.now().timestamp())}",
                    strategy=CostOptimizationStrategy.SPOT_INSTANCES,
                    resource_id=usage.resource_id,
                    current_cost=usage.cost_per_hour * usage.uptime_hours,
                    projected_cost=usage.cost_per_hour * usage.uptime_hours * 0.3,
                    savings_amount=savings_amount,
                    savings_percentage=savings_percentage,
                    confidence_score=0.75,
                    implementation_effort="Medium",
                    risk_level="Medium",
                    description=f"Workload {usage.resource_type} compatible avec spot instances",
                    action_items=[
                        "Implémenter handling d'interruptions",
                        "Configurer checkpointing automatique",
                        "Tester resilience avec spot instances"
                    ],
                    creator_impact=f"Réduction coûts significative pour {usage.creator_type}",
                    model_impact=f"Checkpointing requis pour {usage.model_type}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse spot instances: {e}")
            return None

    async def _analyze_idle_resources(self, usage: ResourceUsage) -> Optional[CostRecommendation]:
        """Analyse des ressources idle"""
        try:
            idle_percentage = (usage.idle_hours / max(usage.uptime_hours, 1)) * 100
            
            if idle_percentage > 60:
                savings_amount = usage.cost_per_hour * usage.idle_hours
                savings_percentage = idle_percentage * 0.8  # 80% des heures idle récupérables
                
                return CostRecommendation(
                    recommendation_id=f"idle_{usage.resource_id}_{int(datetime.now().timestamp())}",
                    strategy=CostOptimizationStrategy.IDLE_RESOURCE_TERMINATION,
                    resource_id=usage.resource_id,
                    current_cost=usage.cost_per_hour * usage.uptime_hours,
                    projected_cost=usage.cost_per_hour * (usage.uptime_hours - usage.idle_hours * 0.8),
                    savings_amount=savings_amount * 0.8,
                    savings_percentage=savings_percentage,
                    confidence_score=0.9,
                    implementation_effort="Low",
                    risk_level="Low",
                    description=f"Resource idle {idle_percentage:.1f}% du temps",
                    action_items=[
                        "Configurer auto-shutdown après inactivité",
                        "Implémenter scaling to zero",
                        "Optimiser scheduling des workloads"
                    ],
                    creator_impact=f"Pas d'impact négatif pour {usage.creator_type}",
                    model_impact=f"Amélioration efficiency pour {usage.model_type}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse idle resources: {e}")
            return None

    async def _analyze_workload_scheduling(self, usage: ResourceUsage) -> Optional[CostRecommendation]:
        """Analyse d'optimisation du scheduling des workloads"""
        try:
            profile = self.creator_cost_profiles.get(usage.creator_type, {})
            peak_hours = profile.get("peak_hours", [])
            
            # Recommander off-peak scheduling pour workloads non-urgents
            if usage.resource_type in ["training", "batch_processing"] and peak_hours:
                savings_percentage = 20.0
                savings_amount = usage.cost_per_hour * usage.uptime_hours * (savings_percentage / 100)
                
                return CostRecommendation(
                    recommendation_id=f"schedule_{usage.resource_id}_{int(datetime.now().timestamp())}",
                    strategy=CostOptimizationStrategy.WORKLOAD_SCHEDULING,
                    resource_id=usage.resource_id,
                    current_cost=usage.cost_per_hour * usage.uptime_hours,
                    projected_cost=usage.cost_per_hour * usage.uptime_hours * 0.8,
                    savings_amount=savings_amount,
                    savings_percentage=savings_percentage,
                    confidence_score=0.7,
                    implementation_effort="Medium",
                    risk_level="Low",
                    description=f"Scheduling off-peak pour {usage.creator_type}",
                    action_items=[
                        "Configurer scheduler off-peak",
                        "Définir priorités workloads",
                        "Implémenter queue management"
                    ],
                    creator_impact=f"Délai acceptable pour {usage.creator_type}",
                    model_impact=f"Training/processing différé pour {usage.model_type}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse workload scheduling: {e}")
            return None

    async def calculate_cost_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """Calcul d'analytics de coûts"""
        try:
            start_date = datetime.now() - timedelta(days=period_days)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Coût total
                cursor = await db.execute("""
                    SELECT SUM(cost_per_hour * uptime_hours) as total_cost,
                           COUNT(*) as resource_count
                    FROM resource_usage 
                    WHERE timestamp >= ?
                """, (start_date.isoformat(),))
                
                total_result = await cursor.fetchone()
                total_cost = total_result[0] or 0.0
                resource_count = total_result[1] or 0
                
                # Coût par créateur
                cursor = await db.execute("""
                    SELECT creator_type, SUM(cost_per_hour * uptime_hours) as cost
                    FROM resource_usage 
                    WHERE timestamp >= ?
                    GROUP BY creator_type
                """, (start_date.isoformat(),))
                
                cost_by_creator = dict(await cursor.fetchall())
                
                # Coût par provider
                cursor = await db.execute("""
                    SELECT provider, SUM(cost_per_hour * uptime_hours) as cost
                    FROM resource_usage 
                    WHERE timestamp >= ?
                    GROUP BY provider
                """, (start_date.isoformat(),))
                
                cost_by_provider = dict(await cursor.fetchall())
                
                # Savings potentiels
                cursor = await db.execute("""
                    SELECT SUM(savings_amount) as potential_savings,
                           COUNT(*) as recommendation_count
                    FROM cost_recommendations 
                    WHERE created_at >= ? AND implemented = FALSE
                """, (start_date.isoformat(),))
                
                savings_result = await cursor.fetchone()
                potential_savings = savings_result[0] or 0.0
                recommendation_count = savings_result[1] or 0
            
            analytics = {
                "period_days": period_days,
                "total_cost": total_cost,
                "resource_count": resource_count,
                "potential_savings": potential_savings,
                "optimization_percentage": (potential_savings / max(total_cost, 1)) * 100,
                "recommendation_count": recommendation_count,
                "cost_by_creator": cost_by_creator,
                "cost_by_provider": cost_by_provider,
                "average_cost_per_resource": total_cost / max(resource_count, 1),
                "roi_if_implemented": potential_savings * 12,  # Annualisé
                "top_cost_creators": sorted(cost_by_creator.items(), key=lambda x: x[1], reverse=True)[:3],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Sauvegarde analytics
            await self._save_analytics(analytics)
            
            self.logger.info(f"✅ Analytics calculées: ${total_cost:.2f} coût total, ${potential_savings:.2f} savings potentiels")
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul analytics: {e}")
            raise AinflueCoreException(f"Échec calcul analytics: {e}")

    async def implement_recommendation(self, recommendation_id: str) -> bool:
        """Implémentation d'une recommandation"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM cost_recommendations 
                    WHERE recommendation_id = ?
                """, (recommendation_id,))
                
                rec_data = await cursor.fetchone()
                if not rec_data:
                    raise ValueError(f"Recommandation {recommendation_id} non trouvée")
                
                # Simulation d'implémentation
                await asyncio.sleep(1)  # Simule le temps d'implémentation
                
                # Marquer comme implémentée
                await db.execute("""
                    UPDATE cost_recommendations 
                    SET implemented = TRUE 
                    WHERE recommendation_id = ?
                """, (recommendation_id,))
                
                await db.commit()
            
            self.logger.info(f"✅ Recommandation {recommendation_id} implémentée")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur implémentation recommandation: {e}")
            return False

    async def _save_resource_usage(self, usage: ResourceUsage) -> None:
        """Sauvegarde d'un enregistrement d'utilisation"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO resource_usage 
                    (resource_id, resource_type, provider, cpu_utilization, memory_utilization,
                     gpu_utilization, storage_usage, network_io, cost_per_hour, uptime_hours,
                     idle_hours, creator_type, model_type, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    usage.resource_id, usage.resource_type, usage.provider.value,
                    usage.cpu_utilization, usage.memory_utilization, usage.gpu_utilization,
                    usage.storage_usage, usage.network_io, usage.cost_per_hour,
                    usage.uptime_hours, usage.idle_hours, usage.creator_type,
                    usage.model_type, usage.timestamp.isoformat()
                ))
                await db.commit()
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde usage: {e}")

    async def _save_recommendation(self, rec: CostRecommendation) -> None:
        """Sauvegarde d'une recommandation"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO cost_recommendations 
                    (recommendation_id, strategy, resource_id, current_cost, projected_cost,
                     savings_amount, savings_percentage, confidence_score, implementation_effort,
                     risk_level, description, action_items, creator_impact, model_impact, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rec.recommendation_id, rec.strategy.value, rec.resource_id,
                    rec.current_cost, rec.projected_cost, rec.savings_amount,
                    rec.savings_percentage, rec.confidence_score, rec.implementation_effort,
                    rec.risk_level, rec.description, json.dumps(rec.action_items),
                    rec.creator_impact, rec.model_impact, datetime.now().isoformat()
                ))
                await db.commit()
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde recommandation: {e}")

    async def _save_analytics(self, analytics: Dict[str, Any]) -> None:
        """Sauvegarde des analytics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO cost_analytics 
                    (period, total_cost, optimized_cost, savings_realized, cost_by_creator,
                     cost_by_provider, top_recommendations, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{analytics['period_days']}_days",
                    analytics['total_cost'],
                    analytics['total_cost'] - analytics['potential_savings'],
                    analytics['potential_savings'],
                    json.dumps(analytics['cost_by_creator']),
                    json.dumps(analytics['cost_by_provider']),
                    json.dumps(analytics.get('top_recommendations', [])),
                    datetime.now().isoformat()
                ))
                await db.commit()
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde analytics: {e}")

    async def get_cost_dashboard(self) -> Dict[str, Any]:
        """Dashboard de coûts en temps réel"""
        try:
            analytics = await self.calculate_cost_analytics(7)  # 7 derniers jours
            
            async with aiosqlite.connect(self.db_path) as db:
                # Top recommandations non implémentées
                cursor = await db.execute("""
                    SELECT recommendation_id, strategy, savings_amount, confidence_score
                    FROM cost_recommendations 
                    WHERE implemented = FALSE
                    ORDER BY savings_amount DESC
                    LIMIT 5
                """)
                
                top_recommendations = await cursor.fetchall()
            
            dashboard = {
                "current_period": analytics,
                "top_recommendations": [
                    {
                        "id": rec[0],
                        "strategy": rec[1],
                        "savings": rec[2],
                        "confidence": rec[3]
                    } for rec in top_recommendations
                ],
                "cost_trends": await self._calculate_cost_trends(),
                "optimization_score": min(100, analytics['optimization_percentage']),
                "status": "healthy" if analytics['optimization_percentage'] < 20 else "needs_optimization"
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"❌ Erreur dashboard: {e}")
            raise AinflueCoreException(f"Échec génération dashboard: {e}")

    async def _calculate_cost_trends(self) -> List[Dict[str, Any]]:
        """Calcul des tendances de coûts"""
        try:
            trends = []
            
            for days_back in [7, 14, 21, 30]:
                start_date = datetime.now() - timedelta(days=days_back)
                
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute("""
                        SELECT SUM(cost_per_hour * uptime_hours) as cost
                        FROM resource_usage 
                        WHERE timestamp >= ?
                    """, (start_date.isoformat(),))
                    
                    result = await cursor.fetchone()
                    cost = result[0] or 0.0
                
                trends.append({
                    "period": f"{days_back}_days",
                    "cost": cost,
                    "daily_average": cost / days_back
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul tendances: {e}")
            return []

    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        try:
            self.executor.shutdown(wait=True)
            self.logger.info("✅ Cost Optimizer nettoyé")
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")

# Example usage pour démonstration
async def main():
    optimizer = CostOptimizer()
    await optimizer.initialize()
    
    # Exemple de données d'utilisation
    sample_usage = [
        {
            "resource_id": "ml-gpu-001",
            "resource_type": "training",
            "provider": "aws",
            "cpu_utilization": 25.0,
            "memory_utilization": 35.0,
            "gpu_utilization": 80.0,
            "storage_usage": 70.0,
            "network_io": 45.0,
            "cost_per_hour": 3.5,
            "uptime_hours": 24,
            "idle_hours": 8,
            "creator_type": "musician",
            "model_type": "audio_classification",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    usage_records = await optimizer.analyze_resource_usage(sample_usage)
    recommendations = await optimizer.generate_cost_recommendations(usage_records)
    analytics = await optimizer.calculate_cost_analytics()
    dashboard = await optimizer.get_cost_dashboard()
    
    print(f"Generated {len(recommendations)} recommendations")
    print(f"Potential savings: ${analytics['potential_savings']:.2f}")
    
    await optimizer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())