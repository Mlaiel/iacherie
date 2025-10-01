"""
Intelligent Alert Manager Module
Gestionnaire alertes intelligent ML-powered - IA Chéries Platform

⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️
🔒 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import logging

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status des alertes"""
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"

@dataclass
class Alert:
    """Structure d'une alerte"""
    alert_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    labels: Dict[str, str]
    annotations: Dict[str, str]
    starts_at: datetime
    ends_at: Optional[datetime]
    creator_id: Optional[str]
    business_impact: float
    correlation_group: Optional[str]

@dataclass
class AlertCorrelation:
    """Corrélation entre alertes"""
    correlation_id: str
    alert_ids: List[str]
    correlation_score: float
    root_cause_probability: float
    business_impact_aggregate: float

class IntelligentAlertManager:
    """
    Gestionnaire alertes intelligent ML-powered
    
    Fonctionnalités:
    - ML-based alert correlation
    - Anomaly detection alerting
    - Context-aware notifications
    - Alert fatigue prevention
    - Predictive alerting system
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.alerts_cache: Dict[str, Alert] = {}
        self.correlations: Dict[str, AlertCorrelation] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        self.ml_models = self._initialize_ml_models()
        self.processing_active = False
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialise les métriques Prometheus"""
        
        # Métriques des alertes
        self.alert_count = Gauge(
            'ainflue_alerts_active_count',
            'Number of active alerts',
            labelnames=['severity', 'rule_name', 'creator_tier'],
            registry=self.registry
        )
        
        self.alert_processing_time = Histogram(
            'ainflue_alerts_processing_time_seconds',
            'Alert processing time in seconds',
            labelnames=['processing_stage', 'alert_type'],
            registry=self.registry
        )
        
        self.alert_correlation_count = Gauge(
            'ainflue_alerts_correlation_groups_count',
            'Number of alert correlation groups',
            labelnames=['correlation_type', 'severity'],
            registry=self.registry
        )
        
        # Métriques de machine learning
        self.ml_prediction_accuracy = Gauge(
            'ainflue_alerts_ml_prediction_accuracy',
            'ML model prediction accuracy for alerts',
            labelnames=['model_type', 'prediction_type'],
            registry=self.registry
        )
        
        self.anomaly_detection_rate = Gauge(
            'ainflue_alerts_anomaly_detection_rate',
            'Anomaly detection success rate',
            labelnames=['anomaly_type', 'detection_method'],
            registry=self.registry
        )
        
        self.alert_fatigue_score = Gauge(
            'ainflue_alerts_fatigue_score',
            'Alert fatigue score for operators',
            labelnames=['operator_id', 'alert_category'],
            registry=self.registry
        )
        
        # Métriques de notification
        self.notification_delivery_rate = Gauge(
            'ainflue_alerts_notification_delivery_rate',
            'Notification delivery success rate',
            labelnames=['channel', 'notification_type'],
            registry=self.registry
        )
        
        self.notification_response_time = Histogram(
            'ainflue_alerts_notification_response_time_seconds',
            'Notification response time in seconds',
            labelnames=['channel', 'priority'],
            registry=self.registry
        )
        
        # Métriques business
        self.business_impact_score = Gauge(
            'ainflue_alerts_business_impact_score',
            'Business impact score of alerts',
            labelnames=['impact_category', 'creator_tier'],
            registry=self.registry
        )
        
        self.alert_resolution_efficiency = Gauge(
            'ainflue_alerts_resolution_efficiency',
            'Alert resolution efficiency score',
            labelnames=['alert_category', 'resolution_method'],
            registry=self.registry
        )
        
        logger.info("Intelligent alert manager metrics initialized")
    
    def _initialize_ml_models(self) -> Dict[str, Any]:
        """Initialise les modèles ML pour l'analyse des alertes"""
        return {
            'correlation_clusterer': DBSCAN(eps=0.3, min_samples=2),
            'anomaly_detector': None,  # À implémenter avec un modèle plus sophistiqué
            'fatigue_predictor': None,  # Modèle de prédiction de fatigue
            'impact_calculator': None,  # Modèle de calcul d'impact business
            'scaler': StandardScaler()
        }
    
    async def start_processing(self, interval: int = 10):
        """Démarre le traitement intelligent des alertes"""
        if self.processing_active:
            logger.warning("Alert processing already active")
            return
            
        self.processing_active = True
        asyncio.create_task(self._processing_loop(interval))
        logger.info(f"Started intelligent alert processing with {interval}s interval")
    
    async def stop_processing(self):
        """Arrête le traitement des alertes"""
        self.processing_active = False
        logger.info("Stopped intelligent alert processing")
    
    async def _processing_loop(self, interval: int):
        """Boucle principale de traitement des alertes"""
        while self.processing_active:
            try:
                await self._process_alerts()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(interval)
    
    async def _process_alerts(self):
        """Traite toutes les alertes actives"""
        start_time = time.time()
        
        try:
            # Collecte des nouvelles alertes
            new_alerts = await self._fetch_new_alerts()
            
            # Traitement des alertes
            await asyncio.gather(
                self._correlate_alerts(),
                self._detect_anomalies(),
                self._calculate_business_impact(),
                self._prevent_alert_fatigue(),
                self._send_intelligent_notifications(),
                return_exceptions=True
            )
            
            processing_time = time.time() - start_time
            self.alert_processing_time.labels(
                processing_stage='full_cycle',
                alert_type='all'
            ).observe(processing_time)
            
            logger.debug(f"Alert processing cycle completed in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error in alert processing: {e}")
    
    async def _fetch_new_alerts(self) -> List[Alert]:
        """Récupère les nouvelles alertes depuis Prometheus"""
        # Simulation de récupération d'alertes
        # Dans un environnement réel, cela ferait une requête à l'API Prometheus
        import random
        
        new_alerts = []
        for _ in range(random.randint(1, 8)):
            alert_id = f"alert_{int(time.time())}_{random.randint(1000, 9999)}"
            
            alert = Alert(
                alert_id=alert_id,
                rule_name=random.choice([
                    'HighCPUUsage', 'LowDiskSpace', 'CreatorRevenueDrop',
                    'AIModelLatency', 'SecurityViolation', 'CollaborationFailure'
                ]),
                severity=AlertSeverity(random.choice(['info', 'warning', 'error', 'critical'])),
                status=AlertStatus.FIRING,
                labels={
                    'instance': f'creator-api-{random.randint(1, 10)}',
                    'creator_tier': random.choice(['bronze', 'silver', 'gold', 'platinum']),
                    'service': random.choice(['api', 'analytics', 'ai-engine', 'payment'])
                },
                annotations={
                    'description': f'Alert generated at {datetime.now()}',
                    'runbook': 'https://runbooks.ainflue.com/alerts/',
                    'dashboard': 'https://grafana.ainflue.com/dashboards/'
                },
                starts_at=datetime.now(),
                ends_at=None,
                creator_id=f'creator_{random.randint(1, 100)}' if random.random() > 0.3 else None,
                business_impact=random.uniform(0.1, 1.0),
                correlation_group=None
            )
            
            self.alerts_cache[alert_id] = alert
            new_alerts.append(alert)
        
        return new_alerts
    
    async def _correlate_alerts(self):
        """Corrèle les alertes en utilisant ML"""
        try:
            active_alerts = [alert for alert in self.alerts_cache.values() 
                           if alert.status == AlertStatus.FIRING]
            
            if len(active_alerts) < 2:
                return
            
            # Préparation des features pour le clustering
            features = self._extract_alert_features(active_alerts)
            
            if len(features) > 0:
                # Normalisation des features
                features_scaled = self.ml_models['scaler'].fit_transform(features)
                
                # Clustering pour trouver les corrélations
                clusters = self.ml_models['correlation_clusterer'].fit_predict(features_scaled)
                
                # Création des groupes de corrélation
                correlation_groups = self._create_correlation_groups(active_alerts, clusters)
                
                # Mise à jour des métriques
                for severity in AlertSeverity:
                    count = sum(1 for group in correlation_groups.values() 
                              if any(self.alerts_cache[aid].severity == severity 
                                   for aid in group.alert_ids))
                    
                    self.alert_correlation_count.labels(
                        correlation_type='ml_clustered',
                        severity=severity.value
                    ).set(count)
                
                logger.debug(f"Created {len(correlation_groups)} correlation groups")
                
        except Exception as e:
            logger.error(f"Error in alert correlation: {e}")
    
    def _extract_alert_features(self, alerts: List[Alert]) -> np.ndarray:
        """Extrait les features des alertes pour le ML"""
        features = []
        
        for alert in alerts:
            # Features temporelles
            hour_of_day = alert.starts_at.hour
            day_of_week = alert.starts_at.weekday()
            
            # Features de sévérité (encodage numérique)
            severity_mapping = {'info': 1, 'warning': 2, 'error': 3, 'critical': 4}
            severity_score = severity_mapping.get(alert.severity.value, 1)
            
            # Features de service (encodage one-hot simple)
            service = alert.labels.get('service', 'unknown')
            service_mapping = {'api': 1, 'analytics': 2, 'ai-engine': 3, 'payment': 4}
            service_score = service_mapping.get(service, 0)
            
            # Features business
            business_impact = alert.business_impact
            
            # Features tier créateur
            tier = alert.labels.get('creator_tier', 'bronze')
            tier_mapping = {'bronze': 1, 'silver': 2, 'gold': 3, 'platinum': 4}
            tier_score = tier_mapping.get(tier, 1)
            
            feature_vector = [
                hour_of_day, day_of_week, severity_score, 
                service_score, business_impact, tier_score
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _create_correlation_groups(self, 
                                 alerts: List[Alert], 
                                 clusters: np.ndarray) -> Dict[str, AlertCorrelation]:
        """Crée les groupes de corrélation basés sur le clustering"""
        correlation_groups = {}
        
        # Groupement par cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id == -1:  # Outliers
                continue
                
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(alerts[i])
        
        # Création des objets AlertCorrelation
        for cluster_id, cluster_alerts in cluster_groups.items():
            if len(cluster_alerts) < 2:
                continue
                
            correlation_id = f"corr_{cluster_id}_{int(time.time())}"
            alert_ids = [alert.alert_id for alert in cluster_alerts]
            
            # Calcul du score de corrélation
            correlation_score = self._calculate_correlation_score(cluster_alerts)
            
            # Calcul de la probabilité de cause racine
            root_cause_prob = self._calculate_root_cause_probability(cluster_alerts)
            
            # Impact business agrégé
            business_impact_agg = sum(alert.business_impact for alert in cluster_alerts)
            
            correlation = AlertCorrelation(
                correlation_id=correlation_id,
                alert_ids=alert_ids,
                correlation_score=correlation_score,
                root_cause_probability=root_cause_prob,
                business_impact_aggregate=business_impact_agg
            )
            
            correlation_groups[correlation_id] = correlation
            
            # Mise à jour du groupe de corrélation dans les alertes
            for alert in cluster_alerts:
                alert.correlation_group = correlation_id
        
        self.correlations.update(correlation_groups)
        return correlation_groups
    
    def _calculate_correlation_score(self, alerts: List[Alert]) -> float:
        """Calcule le score de corrélation pour un groupe d'alertes"""
        if len(alerts) < 2:
            return 0.0
        
        # Facteurs de corrélation
        time_correlation = self._calculate_temporal_correlation(alerts)
        service_correlation = self._calculate_service_correlation(alerts)
        severity_correlation = self._calculate_severity_correlation(alerts)
        creator_correlation = self._calculate_creator_correlation(alerts)
        
        # Score pondéré
        score = (
            time_correlation * 0.3 +
            service_correlation * 0.25 +
            severity_correlation * 0.2 +
            creator_correlation * 0.25
        )
        
        return min(1.0, max(0.0, score))
    
    def _calculate_temporal_correlation(self, alerts: List[Alert]) -> float:
        """Calcule la corrélation temporelle"""
        if len(alerts) < 2:
            return 0.0
        
        timestamps = [alert.starts_at.timestamp() for alert in alerts]
        time_span = max(timestamps) - min(timestamps)
        
        # Plus les alertes sont proches temporellement, plus la corrélation est élevée
        if time_span < 300:  # 5 minutes
            return 1.0
        elif time_span < 1800:  # 30 minutes
            return 0.8
        elif time_span < 3600:  # 1 heure
            return 0.5
        else:
            return 0.2
    
    def _calculate_service_correlation(self, alerts: List[Alert]) -> float:
        """Calcule la corrélation entre services"""
        services = [alert.labels.get('service', 'unknown') for alert in alerts]
        unique_services = set(services)
        
        if len(unique_services) == 1:
            return 1.0  # Même service
        elif len(unique_services) == 2:
            return 0.7  # Services potentiellement liés
        else:
            return 0.3  # Services multiples
    
    def _calculate_severity_correlation(self, alerts: List[Alert]) -> float:
        """Calcule la corrélation de sévérité"""
        severities = [alert.severity for alert in alerts]
        unique_severities = set(severities)
        
        if len(unique_severities) == 1:
            return 1.0
        elif len(unique_severities) == 2:
            return 0.6
        else:
            return 0.3
    
    def _calculate_creator_correlation(self, alerts: List[Alert]) -> float:
        """Calcule la corrélation par créateur"""
        creator_ids = [alert.creator_id for alert in alerts if alert.creator_id]
        
        if not creator_ids:
            return 0.5  # Pas d'info créateur
        
        unique_creators = set(creator_ids)
        if len(unique_creators) == 1:
            return 1.0  # Même créateur
        else:
            return 0.4  # Créateurs différents
    
    def _calculate_root_cause_probability(self, alerts: List[Alert]) -> float:
        """Calcule la probabilité qu'une alerte soit la cause racine"""
        if not alerts:
            return 0.0
        
        # L'alerte la plus ancienne avec la plus haute sévérité a plus de chances d'être la cause racine
        sorted_alerts = sorted(alerts, key=lambda a: (a.starts_at, -['info', 'warning', 'error', 'critical'].index(a.severity.value)))
        
        # Score basé sur l'ordre temporel et la sévérité
        root_cause_alert = sorted_alerts[0]
        severity_weight = {'info': 0.2, 'warning': 0.4, 'error': 0.7, 'critical': 1.0}
        
        probability = severity_weight.get(root_cause_alert.severity.value, 0.5)
        return probability
    
    async def _detect_anomalies(self):
        """Détecte les anomalies dans les patterns d'alertes"""
        try:
            # Simulation de détection d'anomalies
            # Dans un environnement réel, utiliser un modèle d'anomaly detection plus sophistiqué
            
            current_hour = datetime.now().hour
            active_alerts_count = len([a for a in self.alerts_cache.values() if a.status == AlertStatus.FIRING])
            
            # Seuils basés sur l'heure
            expected_alerts = self._get_expected_alert_count(current_hour)
            
            anomaly_score = abs(active_alerts_count - expected_alerts) / max(expected_alerts, 1)
            
            if anomaly_score > 2.0:  # Anomalie détectée
                self.anomaly_detection_rate.labels(
                    anomaly_type='alert_volume',
                    detection_method='statistical_threshold'
                ).set(1.0)
                
                logger.warning(f"Alert volume anomaly detected: {active_alerts_count} alerts (expected: {expected_alerts})")
            else:
                self.anomaly_detection_rate.labels(
                    anomaly_type='alert_volume',
                    detection_method='statistical_threshold'
                ).set(0.0)
                
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
    
    def _get_expected_alert_count(self, hour: int) -> float:
        """Retourne le nombre d'alertes attendu pour une heure donnée"""
        # Pattern typique: plus d'alertes pendant les heures de travail
        if 9 <= hour <= 17:  # Heures de bureau
            return 5.0
        elif 18 <= hour <= 22:  # Soirée
            return 3.0
        else:  # Nuit
            return 1.0
    
    async def _calculate_business_impact(self):
        """Calcule l'impact business des alertes"""
        try:
            for alert in self.alerts_cache.values():
                if alert.status != AlertStatus.FIRING:
                    continue
                
                # Facteurs d'impact business
                severity_impact = {'info': 0.1, 'warning': 0.3, 'error': 0.7, 'critical': 1.0}
                tier_impact = {'bronze': 0.2, 'silver': 0.4, 'gold': 0.7, 'platinum': 1.0}
                service_impact = {'api': 0.9, 'payment': 1.0, 'ai-engine': 0.8, 'analytics': 0.5}
                
                impact_score = (
                    severity_impact.get(alert.severity.value, 0.5) * 0.4 +
                    tier_impact.get(alert.labels.get('creator_tier', 'bronze'), 0.2) * 0.3 +
                    service_impact.get(alert.labels.get('service', 'unknown'), 0.5) * 0.3
                )
                
                alert.business_impact = impact_score
                
                # Mise à jour des métriques
                impact_category = 'high' if impact_score > 0.7 else 'medium' if impact_score > 0.4 else 'low'
                
                self.business_impact_score.labels(
                    impact_category=impact_category,
                    creator_tier=alert.labels.get('creator_tier', 'unknown')
                ).set(impact_score)
                
        except Exception as e:
            logger.error(f"Error calculating business impact: {e}")
    
    async def _prevent_alert_fatigue(self):
        """Prévient la fatigue des alertes"""
        try:
            # Simulation de calcul de fatigue
            # Dans un environnement réel, analyser les patterns de réponse des opérateurs
            
            alert_categories = {}
            for alert in self.alerts_cache.values():
                category = alert.rule_name
                if category not in alert_categories:
                    alert_categories[category] = 0
                alert_categories[category] += 1
            
            # Calcul du score de fatigue par catégorie
            for category, count in alert_categories.items():
                fatigue_score = min(1.0, count / 10.0)  # Seuil à 10 alertes
                
                self.alert_fatigue_score.labels(
                    operator_id='default_operator',
                    alert_category=category
                ).set(fatigue_score)
                
                # Suppression d'alertes si fatigue élevée
                if fatigue_score > 0.8:
                    await self._suppress_redundant_alerts(category)
                    
        except Exception as e:
            logger.error(f"Error in alert fatigue prevention: {e}")
    
    async def _suppress_redundant_alerts(self, category: str):
        """Supprime les alertes redondantes pour réduire la fatigue"""
        try:
            category_alerts = [alert for alert in self.alerts_cache.values() 
                             if alert.rule_name == category and alert.status == AlertStatus.FIRING]
            
            if len(category_alerts) > 5:  # Seuil de suppression
                # Garde les 3 alertes les plus importantes
                sorted_alerts = sorted(category_alerts, 
                                     key=lambda a: a.business_impact, reverse=True)
                
                for alert in sorted_alerts[3:]:
                    alert.status = AlertStatus.SUPPRESSED
                    logger.info(f"Suppressed redundant alert: {alert.alert_id}")
                    
        except Exception as e:
            logger.error(f"Error suppressing redundant alerts: {e}")
    
    async def _send_intelligent_notifications(self):
        """Envoie des notifications intelligentes"""
        try:
            high_priority_alerts = [
                alert for alert in self.alerts_cache.values()
                if alert.status == AlertStatus.FIRING and alert.business_impact > 0.7
            ]
            
            for alert in high_priority_alerts:
                # Sélection du canal de notification basé sur l'impact et la sévérité
                channels = self._select_notification_channels(alert)
                
                for channel in channels:
                    success = await self._send_notification(channel, alert)
                    
                    # Mise à jour des métriques
                    self.notification_delivery_rate.labels(
                        channel=channel,
                        notification_type='intelligent_alert'
                    ).set(1.0 if success else 0.0)
                    
        except Exception as e:
            logger.error(f"Error sending intelligent notifications: {e}")
    
    def _select_notification_channels(self, alert: Alert) -> List[str]:
        """Sélectionne les canaux de notification appropriés"""
        channels = []
        
        if alert.severity == AlertSeverity.CRITICAL:
            channels.extend(['pagerduty', 'slack', 'email'])
        elif alert.severity == AlertSeverity.ERROR:
            channels.extend(['slack', 'email'])
        elif alert.business_impact > 0.8:
            channels.extend(['slack', 'email'])
        else:
            channels.append('email')
        
        return list(set(channels))  # Déduplique
    
    async def _send_notification(self, channel: str, alert: Alert) -> bool:
        """Envoie une notification sur le canal spécifié"""
        try:
            start_time = time.time()
            
            # Simulation d'envoi de notification
            # Dans un environnement réel, intégrer avec les APIs des services
            await asyncio.sleep(0.1)  # Simulation du délai d'envoi
            
            response_time = time.time() - start_time
            
            priority = 'high' if alert.business_impact > 0.7 else 'normal'
            self.notification_response_time.labels(
                channel=channel,
                priority=priority
            ).observe(response_time)
            
            logger.debug(f"Notification sent via {channel} for alert {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification via {channel}: {e}")
            return False
    
    def register_notification_handler(self, channel: str, handler: Callable):
        """Enregistre un gestionnaire de notification personnalisé"""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for channel: {channel}")
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Récupère une alerte par son ID"""
        return self.alerts_cache.get(alert_id)
    
    def get_active_alerts(self) -> List[Alert]:
        """Récupère toutes les alertes actives"""
        return [alert for alert in self.alerts_cache.values() if alert.status == AlertStatus.FIRING]
    
    def get_correlation_groups(self) -> List[AlertCorrelation]:
        """Récupère tous les groupes de corrélation"""
        return list(self.correlations.values())
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acquitte une alerte"""
        try:
            if alert_id in self.alerts_cache:
                self.alerts_cache[alert_id].status = AlertStatus.ACKNOWLEDGED
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Résout une alerte"""
        try:
            if alert_id in self.alerts_cache:
                alert = self.alerts_cache[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.ends_at = datetime.now()
                logger.info(f"Alert resolved: {alert_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    def export_registry(self) -> CollectorRegistry:
        """Exporte le registry Prometheus"""
        return self.registry