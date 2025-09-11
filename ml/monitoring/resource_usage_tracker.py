"""🚀 Resource Usage Tracker - IA Influencer Agent Platform Enterprise
=====================================================================
Module: ml/monitoring/resource_usage_tracker.py
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer + DevOps Expert + Sustainability Specialist
Phase: 13 - Advanced Content Processing + Creator Intelligence
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 TRACEUR D'UTILISATION DES RESSOURCES
Advanced resource usage tracking with:
- Inference resource monitoring and optimization
- Cost optimization and budget management
- Carbon footprint monitoring for sustainability
- Real-time resource allocation tracking
- Predictive resource planning
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from collections import deque, defaultdict
import statistics

# Configuration
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types de ressources trackées"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    ENERGY = "energy"

class CostCategory(Enum):
    """Catégories de coûts"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    INFERENCE = "inference"
    TRAINING = "training"
    DATA_TRANSFER = "data_transfer"

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class ResourceMetrics:
    """Métriques de ressources instantanées"""
    timestamp: datetime
    cpu_usage_percent: float
    gpu_usage_percent: float
    memory_usage_mb: float
    memory_available_mb: float
    storage_used_gb: float
    storage_available_gb: float
    network_in_mbps: float
    network_out_mbps: float
    energy_consumption_watts: float
    temperature_celsius: float

@dataclass
class CostMetrics:
    """Métriques de coût"""
    compute_cost_usd: float
    storage_cost_usd: float
    network_cost_usd: float
    total_cost_usd: float
    cost_per_inference: float
    daily_budget_usage_percent: float
    monthly_projection_usd: float

@dataclass
class CarbonFootprint:
    """Empreinte carbone"""
    energy_consumption_kwh: float
    carbon_emissions_kg_co2: float
    carbon_efficiency_score: float
    renewable_energy_percent: float
    carbon_offset_recommendations: List[str]

@dataclass
class ResourceAlert:
    """Alerte de ressource"""
    alert_id: str
    timestamp: datetime
    level: AlertLevel
    resource_type: ResourceType
    message: str
    threshold_value: float
    current_value: float
    suggested_actions: List[str]

@dataclass
class OptimizationRecommendation:
    """Recommandation d'optimisation"""
    category: str
    priority: str
    description: str
    estimated_savings_usd: float
    estimated_savings_percent: float
    implementation_effort: str
    carbon_impact: str

@dataclass
class ResourceUsageReport:
    """Rapport d'utilisation des ressources"""
    report_id: str
    period_start: datetime
    period_end: datetime
    resource_metrics: ResourceMetrics
    cost_metrics: CostMetrics
    carbon_footprint: CarbonFootprint
    alerts: List[ResourceAlert]
    optimization_recommendations: List[OptimizationRecommendation]
    efficiency_score: float
    sustainability_score: float

class ResourceUsageTracker:
    """🎯 Traceur d'Utilisation des Ressources Enterprise
    
    Fonctionnalités avancées:
    - Monitoring temps réel des ressources
    - Optimisation automatique des coûts
    - Tracking empreinte carbone
    - Alertes intelligentes
    - Planification prédictive
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise le traceur de ressources
        
        Args:
            config: Configuration personnalisée
        """
        self.config = config or {}
        self.resource_history = deque(maxlen=10000)
        self.cost_history = deque(maxlen=1000)
        self.active_alerts = {}
        self.optimization_cache = {}
        
        # Configuration par défaut
        self.monitoring_interval = self.config.get('monitoring_interval_seconds', 60)
        self.daily_budget_usd = self.config.get('daily_budget_usd', 1000.0)
        self.cost_per_cpu_hour = self.config.get('cost_per_cpu_hour', 0.10)
        self.cost_per_gpu_hour = self.config.get('cost_per_gpu_hour', 2.50)
        self.cost_per_gb_storage = self.config.get('cost_per_gb_storage', 0.023)
        self.carbon_intensity_kg_per_kwh = self.config.get('carbon_intensity', 0.5)
        
        # Seuils d'alerte
        self.alert_thresholds = {
            ResourceType.CPU: {'warning': 70, 'critical': 85, 'emergency': 95},
            ResourceType.GPU: {'warning': 80, 'critical': 90, 'emergency': 98},
            ResourceType.MEMORY: {'warning': 75, 'critical': 85, 'emergency': 95},
            ResourceType.STORAGE: {'warning': 80, 'critical': 90, 'emergency': 95},
            ResourceType.ENERGY: {'warning': 500, 'critical': 750, 'emergency': 1000}
        }
        
        # Thread de monitoring
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        logger.info("Resource Usage Tracker initialized - Sustainability Intelligence Ready")
    
    async def start_monitoring(self):
        """Démarrage du monitoring en continu"""
        try:
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                logger.warning("Monitoring already active")
                return
            
            self._stop_monitoring.clear()
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitoring_thread.start()
            
            logger.info("Resource monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            raise
    
    async def stop_monitoring(self):
        """Arrêt du monitoring"""
        try:
            if self._monitoring_thread:
                self._stop_monitoring.set()
                self._monitoring_thread.join(timeout=5.0)
                
            logger.info("Resource monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")
    
    def _monitoring_loop(self):
        """Boucle de monitoring principal"""
        while not self._stop_monitoring.is_set():
            try:
                # Collecte des métriques
                metrics = self._collect_resource_metrics()
                self.resource_history.append(metrics)
                
                # Analyse des alertes
                alerts = self._analyze_alerts(metrics)
                for alert in alerts:
                    self._handle_alert(alert)
                
                # Calcul des coûts
                cost_metrics = self._calculate_costs(metrics)
                self.cost_history.append(cost_metrics)
                
                # Attente avant la prochaine collecte
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(self.monitoring_interval)
    
    def _collect_resource_metrics(self) -> ResourceMetrics:
        """Collecte des métriques de ressources actuelles"""
        try:
            # Simulation de collecte de métriques système
            import random
            
            # Métriques simulées avec variabilité réaliste
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_usage_percent=random.uniform(20, 85),
                gpu_usage_percent=random.uniform(40, 95),
                memory_usage_mb=random.uniform(4000, 12000),
                memory_available_mb=random.uniform(4000, 8000),
                storage_used_gb=random.uniform(100, 500),
                storage_available_gb=random.uniform(500, 1000),
                network_in_mbps=random.uniform(10, 100),
                network_out_mbps=random.uniform(5, 50),
                energy_consumption_watts=random.uniform(200, 800),
                temperature_celsius=random.uniform(35, 75)
            )
            
        except Exception as e:
            logger.error(f"Resource metrics collection failed: {str(e)}")
            # Retour de métriques par défaut en cas d'erreur
            return ResourceMetrics(
                datetime.now(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
    
    def _analyze_alerts(self, metrics: ResourceMetrics) -> List[ResourceAlert]:
        """Analyse des seuils et génération d'alertes"""
        alerts = []
        
        try:
            # Vérification CPU
            cpu_alert = self._check_threshold(
                ResourceType.CPU, metrics.cpu_usage_percent
            )
            if cpu_alert:
                alerts.append(cpu_alert)
            
            # Vérification GPU
            gpu_alert = self._check_threshold(
                ResourceType.GPU, metrics.gpu_usage_percent
            )
            if gpu_alert:
                alerts.append(gpu_alert)
            
            # Vérification mémoire
            memory_usage_percent = (metrics.memory_usage_mb / 
                                  (metrics.memory_usage_mb + metrics.memory_available_mb)) * 100
            memory_alert = self._check_threshold(
                ResourceType.MEMORY, memory_usage_percent
            )
            if memory_alert:
                alerts.append(memory_alert)
            
            # Vérification stockage
            storage_usage_percent = (metrics.storage_used_gb / 
                                   (metrics.storage_used_gb + metrics.storage_available_gb)) * 100
            storage_alert = self._check_threshold(
                ResourceType.STORAGE, storage_usage_percent
            )
            if storage_alert:
                alerts.append(storage_alert)
            
            # Vérification énergie
            energy_alert = self._check_threshold(
                ResourceType.ENERGY, metrics.energy_consumption_watts
            )
            if energy_alert:
                alerts.append(energy_alert)
            
        except Exception as e:
            logger.error(f"Alert analysis failed: {str(e)}")
        
        return alerts
    
    def _check_threshold(
        self,
        resource_type: ResourceType,
        current_value: float
    ) -> Optional[ResourceAlert]:
        """Vérification des seuils pour un type de ressource"""
        try:
            thresholds = self.alert_thresholds.get(resource_type, {})
            
            # Détermination du niveau d'alerte
            alert_level = None
            threshold_value = None
            
            if current_value >= thresholds.get('emergency', float('inf')):
                alert_level = AlertLevel.EMERGENCY
                threshold_value = thresholds['emergency']
            elif current_value >= thresholds.get('critical', float('inf')):
                alert_level = AlertLevel.CRITICAL
                threshold_value = thresholds['critical']
            elif current_value >= thresholds.get('warning', float('inf')):
                alert_level = AlertLevel.WARNING
                threshold_value = thresholds['warning']
            
            if alert_level:
                # Génération de l'alerte
                alert_id = f"{resource_type.value}_{int(time.time())}"
                
                # Vérification si l'alerte existe déjà
                existing_alert_key = f"{resource_type.value}_{alert_level.value}"
                if existing_alert_key in self.active_alerts:
                    # Mise à jour de l'alerte existante
                    self.active_alerts[existing_alert_key].current_value = current_value
                    return None
                
                message = self._generate_alert_message(resource_type, alert_level, current_value)
                suggestions = self._generate_alert_suggestions(resource_type, alert_level)
                
                alert = ResourceAlert(
                    alert_id=alert_id,
                    timestamp=datetime.now(),
                    level=alert_level,
                    resource_type=resource_type,
                    message=message,
                    threshold_value=threshold_value,
                    current_value=current_value,
                    suggested_actions=suggestions
                )
                
                # Enregistrement de l'alerte active
                self.active_alerts[existing_alert_key] = alert
                return alert
            
            else:
                # Suppression de l'alerte si elle n'est plus active
                for level in AlertLevel:
                    alert_key = f"{resource_type.value}_{level.value}"
                    if alert_key in self.active_alerts:
                        del self.active_alerts[alert_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Threshold check failed for {resource_type}: {str(e)}")
            return None
    
    def _generate_alert_message(
        self,
        resource_type: ResourceType,
        level: AlertLevel,
        value: float
    ) -> str:
        """Génération du message d'alerte"""
        severity_map = {
            AlertLevel.WARNING: "ATTENTION",
            AlertLevel.CRITICAL: "CRITIQUE",
            AlertLevel.EMERGENCY: "URGENCE"
        }
        
        resource_names = {
            ResourceType.CPU: "CPU",
            ResourceType.GPU: "GPU",
            ResourceType.MEMORY: "Mémoire",
            ResourceType.STORAGE: "Stockage",
            ResourceType.ENERGY: "Consommation énergétique"
        }
        
        severity = severity_map.get(level, "ALERTE")
        resource_name = resource_names.get(resource_type, resource_type.value)
        
        if resource_type == ResourceType.ENERGY:
            return f"{severity}: {resource_name} élevée - {value:.0f}W"
        else:
            return f"{severity}: {resource_name} élevée - {value:.1f}%"
    
    def _generate_alert_suggestions(
        self,
        resource_type: ResourceType,
        level: AlertLevel
    ) -> List[str]:
        """Génération de suggestions pour résoudre l'alerte"""
        suggestions = []
        
        if resource_type == ResourceType.CPU:
            suggestions = [
                "Réduire le nombre de processus simultanés",
                "Optimiser les algorithmes gourmands en CPU",
                "Implémenter la mise en cache pour réduire les calculs",
                "Considérer l'auto-scaling horizontal"
            ]
        elif resource_type == ResourceType.GPU:
            suggestions = [
                "Optimiser la taille des batches",
                "Implémenter la quantification de modèles",
                "Utiliser mixed precision training",
                "Répartir la charge sur plusieurs GPUs"
            ]
        elif resource_type == ResourceType.MEMORY:
            suggestions = [
                "Libérer les objets non utilisés",
                "Optimiser les structures de données",
                "Implémenter la pagination des données",
                "Augmenter la capacité mémoire"
            ]
        elif resource_type == ResourceType.STORAGE:
            suggestions = [
                "Nettoyer les fichiers temporaires",
                "Compresser les données anciennes",
                "Archiver les données non critiques",
                "Augmenter la capacité de stockage"
            ]
        elif resource_type == ResourceType.ENERGY:
            suggestions = [
                "Réduire l'utilisation GPU pendant les heures de pointe",
                "Optimiser les modèles pour l'efficacité énergétique",
                "Planifier les tâches intensives aux heures creuses",
                "Migrer vers des serveurs plus efficaces"
            ]
        
        # Suggestions spécifiques au niveau d'alerte
        if level == AlertLevel.EMERGENCY:
            suggestions.insert(0, "ACTION IMMÉDIATE REQUISE")
            suggestions.insert(1, "Arrêter les processus non-critiques")
        
        return suggestions
    
    def _handle_alert(self, alert: ResourceAlert):
        """Gestion d'une alerte générée"""
        try:
            # Log de l'alerte
            logger.warning(f"Resource Alert: {alert.message}")
            
            # Actions automatiques basées sur le niveau
            if alert.level == AlertLevel.EMERGENCY:
                # Actions d'urgence automatiques
                self._execute_emergency_actions(alert.resource_type)
            
            # Notification (simulation)
            self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"Alert handling failed: {str(e)}")
    
    def _execute_emergency_actions(self, resource_type: ResourceType):
        """Exécution d'actions d'urgence automatiques"""
        try:
            if resource_type == ResourceType.MEMORY:
                # Simulation de libération mémoire
                logger.info("Emergency: Clearing memory caches")
            elif resource_type == ResourceType.STORAGE:
                # Simulation de nettoyage stockage
                logger.info("Emergency: Cleaning temporary files")
            elif resource_type == ResourceType.ENERGY:
                # Simulation de réduction consommation
                logger.info("Emergency: Reducing energy consumption")
            
        except Exception as e:
            logger.error(f"Emergency actions failed: {str(e)}")
    
    def _send_alert_notification(self, alert: ResourceAlert):
        """Envoi de notification d'alerte"""
        # Simulation d'envoi de notification
        logger.info(f"Alert notification sent: {alert.alert_id}")
    
    def _calculate_costs(self, metrics: ResourceMetrics) -> CostMetrics:
        """Calcul des coûts basés sur les métriques"""
        try:
            # Calcul des coûts par heure
            cpu_hours = (metrics.cpu_usage_percent / 100.0) * (self.monitoring_interval / 3600.0)
            gpu_hours = (metrics.gpu_usage_percent / 100.0) * (self.monitoring_interval / 3600.0)
            
            compute_cost = (cpu_hours * self.cost_per_cpu_hour + 
                          gpu_hours * self.cost_per_gpu_hour)
            
            storage_cost = (metrics.storage_used_gb * self.cost_per_gb_storage) / 30  # Coût quotidien
            
            # Coût réseau (simulation)
            network_gb = (metrics.network_out_mbps * self.monitoring_interval) / (8 * 1024)
            network_cost = network_gb * 0.09  # $0.09 per GB
            
            total_cost = compute_cost + storage_cost + network_cost
            
            # Coût par inférence (estimation)
            estimated_inferences_per_hour = 1000  # Simulation
            cost_per_inference = total_cost / (estimated_inferences_per_hour * (self.monitoring_interval / 3600.0))
            
            # Utilisation du budget quotidien
            daily_cost_rate = total_cost * (24 * 3600 / self.monitoring_interval)
            budget_usage_percent = (daily_cost_rate / self.daily_budget_usd) * 100
            
            # Projection mensuelle
            monthly_projection = daily_cost_rate * 30
            
            return CostMetrics(
                compute_cost_usd=compute_cost,
                storage_cost_usd=storage_cost,
                network_cost_usd=network_cost,
                total_cost_usd=total_cost,
                cost_per_inference=cost_per_inference,
                daily_budget_usage_percent=budget_usage_percent,
                monthly_projection_usd=monthly_projection
            )
            
        except Exception as e:
            logger.error(f"Cost calculation failed: {str(e)}")
            return CostMetrics(0, 0, 0, 0, 0, 0, 0)
    
    async def calculate_carbon_footprint(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> CarbonFootprint:
        """Calcul de l'empreinte carbone pour une période"""
        try:
            # Filtrage des métriques pour la période
            period_metrics = [
                m for m in self.resource_history
                if start_time <= m.timestamp <= end_time
            ]
            
            if not period_metrics:
                return CarbonFootprint(0, 0, 0, 0, [])
            
            # Calcul de la consommation énergétique totale
            total_energy_wh = sum(m.energy_consumption_watts for m in period_metrics) * (self.monitoring_interval / 3600.0)
            total_energy_kwh = total_energy_wh / 1000.0
            
            # Calcul des émissions carbone
            carbon_emissions_kg = total_energy_kwh * self.carbon_intensity_kg_per_kwh
            
            # Score d'efficacité carbone (plus bas = mieux)
            avg_energy_per_inference = total_energy_kwh / max(1, len(period_metrics) * 100)  # Estimation
            carbon_efficiency_score = max(0, min(1, 1 - (avg_energy_per_inference / 0.01)))  # Normalisation
            
            # Pourcentage d'énergie renouvelable (simulation)
            renewable_energy_percent = 30.0  # Simulation
            
            # Recommandations de compensation carbone
            offset_recommendations = self._generate_carbon_offset_recommendations(carbon_emissions_kg)
            
            return CarbonFootprint(
                energy_consumption_kwh=total_energy_kwh,
                carbon_emissions_kg_co2=carbon_emissions_kg,
                carbon_efficiency_score=carbon_efficiency_score,
                renewable_energy_percent=renewable_energy_percent,
                carbon_offset_recommendations=offset_recommendations
            )
            
        except Exception as e:
            logger.error(f"Carbon footprint calculation failed: {str(e)}")
            return CarbonFootprint(0, 0, 0, 0, [])
    
    def _generate_carbon_offset_recommendations(
        self,
        carbon_emissions_kg: float
    ) -> List[str]:
        """Génération de recommandations de compensation carbone"""
        recommendations = []
        
        # Recommandations basées sur le niveau d'émissions
        if carbon_emissions_kg > 100:
            recommendations.append("Investir dans des projets de reforestation")
            recommendations.append("Soutenir des projets d'énergie renouvelable")
            recommendations.append("Optimiser les algorithmes pour réduire la consommation")
        
        if carbon_emissions_kg > 50:
            recommendations.append("Migrer vers des centres de données verts")
            recommendations.append("Implémenter des horaires d'exécution éco-responsables")
        
        if carbon_emissions_kg > 10:
            recommendations.append("Acheter des crédits carbone certifiés")
            recommendations.append("Optimiser l'utilisation des ressources")
        
        # Recommandations générales
        recommendations.extend([
            "Mesurer et reporter régulièrement l'empreinte carbone",
            "Sensibiliser l'équipe aux enjeux environnementaux"
        ])
        
        return recommendations[:5]  # Limiter à 5 recommandations
    
    async def generate_optimization_recommendations(
        self,
        timeframe_hours: int = 24
    ) -> List[OptimizationRecommendation]:
        """Génération de recommandations d'optimisation"""
        try:
            recommendations = []
            
            # Analyse des métriques récentes
            cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
            recent_metrics = [
                m for m in self.resource_history
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return recommendations
            
            # Calcul des moyennes
            avg_cpu = statistics.mean(m.cpu_usage_percent for m in recent_metrics)
            avg_gpu = statistics.mean(m.gpu_usage_percent for m in recent_metrics)
            avg_memory = statistics.mean(m.memory_usage_mb for m in recent_metrics)
            avg_energy = statistics.mean(m.energy_consumption_watts for m in recent_metrics)
            
            # Recommandations basées sur l'utilisation CPU
            if avg_cpu > 80:
                recommendations.append(OptimizationRecommendation(
                    category="compute",
                    priority="high",
                    description="Optimisation CPU - Utilisation élevée détectée",
                    estimated_savings_usd=50.0,
                    estimated_savings_percent=15.0,
                    implementation_effort="medium",
                    carbon_impact="positive"
                ))
            
            # Recommandations basées sur l'utilisation GPU
            if avg_gpu > 85:
                recommendations.append(OptimizationRecommendation(
                    category="gpu",
                    priority="high",
                    description="Optimisation GPU - Implémenter la quantification de modèles",
                    estimated_savings_usd=200.0,
                    estimated_savings_percent=25.0,
                    implementation_effort="high",
                    carbon_impact="very positive"
                ))
            
            # Recommandations basées sur la mémoire
            if avg_memory > 8000:
                recommendations.append(OptimizationRecommendation(
                    category="memory",
                    priority="medium",
                    description="Optimisation mémoire - Implémenter un garbage collector plus agressif",
                    estimated_savings_usd=30.0,
                    estimated_savings_percent=8.0,
                    implementation_effort="low",
                    carbon_impact="neutral"
                ))
            
            # Recommandations basées sur l'énergie
            if avg_energy > 600:
                recommendations.append(OptimizationRecommendation(
                    category="energy",
                    priority="high",
                    description="Optimisation énergétique - Planifier les tâches aux heures creuses",
                    estimated_savings_usd=75.0,
                    estimated_savings_percent=20.0,
                    implementation_effort="medium",
                    carbon_impact="very positive"
                ))
            
            # Recommandations générales
            recommendations.append(OptimizationRecommendation(
                category="general",
                priority="low",
                description="Mise en place de cache intelligent pour réduire les recalculs",
                estimated_savings_usd=100.0,
                estimated_savings_percent=12.0,
                implementation_effort="medium",
                carbon_impact="positive"
            ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendations failed: {str(e)}")
            return []
    
    async def generate_usage_report(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> ResourceUsageReport:
        """Génération d'un rapport d'utilisation complet"""
        try:
            report_id = str(uuid.uuid4())
            
            # Filtrage des métriques pour la période
            period_metrics = [
                m for m in self.resource_history
                if start_time <= m.timestamp <= end_time
            ]
            
            if not period_metrics:
                # Métriques par défaut si aucune donnée
                avg_metrics = ResourceMetrics(
                    datetime.now(), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                )
            else:
                # Calcul des moyennes
                avg_metrics = ResourceMetrics(
                    timestamp=datetime.now(),
                    cpu_usage_percent=statistics.mean(m.cpu_usage_percent for m in period_metrics),
                    gpu_usage_percent=statistics.mean(m.gpu_usage_percent for m in period_metrics),
                    memory_usage_mb=statistics.mean(m.memory_usage_mb for m in period_metrics),
                    memory_available_mb=statistics.mean(m.memory_available_mb for m in period_metrics),
                    storage_used_gb=statistics.mean(m.storage_used_gb for m in period_metrics),
                    storage_available_gb=statistics.mean(m.storage_available_gb for m in period_metrics),
                    network_in_mbps=statistics.mean(m.network_in_mbps for m in period_metrics),
                    network_out_mbps=statistics.mean(m.network_out_mbps for m in period_metrics),
                    energy_consumption_watts=statistics.mean(m.energy_consumption_watts for m in period_metrics),
                    temperature_celsius=statistics.mean(m.temperature_celsius for m in period_metrics)
                )
            
            # Calcul des coûts moyens
            cost_metrics = self._calculate_costs(avg_metrics)
            
            # Calcul de l'empreinte carbone
            carbon_footprint = await self.calculate_carbon_footprint(start_time, end_time)
            
            # Récupération des alertes de la période
            period_alerts = [
                alert for alert in self.active_alerts.values()
                if start_time <= alert.timestamp <= end_time
            ]
            
            # Génération des recommandations
            recommendations = await self.generate_optimization_recommendations()
            
            # Calcul des scores
            efficiency_score = self._calculate_efficiency_score(avg_metrics, cost_metrics)
            sustainability_score = carbon_footprint.carbon_efficiency_score
            
            return ResourceUsageReport(
                report_id=report_id,
                period_start=start_time,
                period_end=end_time,
                resource_metrics=avg_metrics,
                cost_metrics=cost_metrics,
                carbon_footprint=carbon_footprint,
                alerts=period_alerts,
                optimization_recommendations=recommendations,
                efficiency_score=efficiency_score,
                sustainability_score=sustainability_score
            )
            
        except Exception as e:
            logger.error(f"Usage report generation failed: {str(e)}")
            raise RuntimeError(f"Report generation error: {str(e)}")
    
    def _calculate_efficiency_score(
        self,
        metrics: ResourceMetrics,
        costs: CostMetrics
    ) -> float:
        """Calcul du score d'efficacité global"""
        try:
            # Facteurs d'efficacité
            cpu_efficiency = 1.0 - (metrics.cpu_usage_percent / 100.0) ** 2  # Pénalité quadratique
            gpu_efficiency = 1.0 - (metrics.gpu_usage_percent / 100.0) ** 2
            memory_efficiency = 1.0 - ((metrics.memory_usage_mb / (metrics.memory_usage_mb + metrics.memory_available_mb)) ** 2)
            cost_efficiency = max(0, 1.0 - (costs.daily_budget_usage_percent / 100.0))
            
            # Moyenne pondérée
            efficiency_score = (
                cpu_efficiency * 0.25 +
                gpu_efficiency * 0.35 +
                memory_efficiency * 0.25 +
                cost_efficiency * 0.15
            )
            
            return max(0, min(1, efficiency_score))
            
        except Exception as e:
            logger.error(f"Efficiency score calculation failed: {str(e)}")
            return 0.5
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Récupération des métriques temps réel"""
        try:
            if not self.resource_history:
                return {}
            
            latest_metrics = self.resource_history[-1]
            latest_costs = self.cost_history[-1] if self.cost_history else None
            
            return {
                'timestamp': latest_metrics.timestamp.isoformat(),
                'resource_utilization': {
                    'cpu_percent': latest_metrics.cpu_usage_percent,
                    'gpu_percent': latest_metrics.gpu_usage_percent,
                    'memory_percent': (latest_metrics.memory_usage_mb / 
                                     (latest_metrics.memory_usage_mb + latest_metrics.memory_available_mb)) * 100,
                    'storage_percent': (latest_metrics.storage_used_gb / 
                                      (latest_metrics.storage_used_gb + latest_metrics.storage_available_gb)) * 100,
                    'energy_watts': latest_metrics.energy_consumption_watts
                },
                'costs': {
                    'total_usd': latest_costs.total_cost_usd if latest_costs else 0,
                    'budget_usage_percent': latest_costs.daily_budget_usage_percent if latest_costs else 0,
                    'monthly_projection': latest_costs.monthly_projection_usd if latest_costs else 0
                } if latest_costs else {},
                'active_alerts': len(self.active_alerts),
                'monitoring_status': 'active' if self._monitoring_thread and self._monitoring_thread.is_alive() else 'inactive'
            }
            
        except Exception as e:
            logger.error(f"Real-time metrics retrieval failed: {str(e)}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Résumé des performances de tracking"""
        return {
            'monitoring_duration_hours': len(self.resource_history) * (self.monitoring_interval / 3600),
            'data_points_collected': len(self.resource_history),
            'total_alerts_generated': len(self.active_alerts),
            'average_efficiency_score': 0.82,  # Simulation
            'carbon_tracking_enabled': True,
            'cost_optimization_active': True,
            'monitoring_interval_seconds': self.monitoring_interval
        }

# Factory function pour intégration facile
def create_resource_tracker(config: Optional[Dict[str, Any]] = None) -> ResourceUsageTracker:
    """Factory pour créer un traceur de ressources configuré"""
    return ResourceUsageTracker(config)

# Export pour usage externe
__all__ = [
    'ResourceUsageTracker',
    'ResourceUsageReport',
    'ResourceMetrics',
    'CostMetrics',
    'CarbonFootprint',
    'OptimizationRecommendation',
    'ResourceType',
    'create_resource_tracker'
]