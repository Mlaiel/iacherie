"""
⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

PERFORMANCE ALERTS ENGINE - ANALYTICS NOTIFICATIONS
=====================================================

🎯 RÔLE ENTERPRISE:
- Alertes performance temps réel pour creators Ainflue
- Monitoring KPIs critiques et métriques business
- Détection anomalies et régressions performance
- Alertes prédictives basées IA/ML

🚀 FONCTIONNALITÉS AINFLUE:
- Performance content tracking (vues, engagement, reach)
- Revenue performance alerts (CPM, CPC, conversions)
- Audio quality performance monitoring
- Cross-platform performance comparison
- Audience engagement degradation alerts
- Viral potential performance indicators
- Creator portfolio performance tracking
- ROI performance optimization alerts
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import json

class PerformanceMetricType(Enum):
    """Types de métriques de performance"""
    CONTENT_VIEWS = "content_views"
    ENGAGEMENT_RATE = "engagement_rate"
    REVENUE_CPM = "revenue_cpm"
    AUDIO_QUALITY = "audio_quality"
    LOAD_TIME = "load_time"
    CONVERSION_RATE = "conversion_rate"
    REACH = "reach"
    VIRAL_SCORE = "viral_score"
    USER_RETENTION = "user_retention"
    COLLABORATION_SUCCESS = "collaboration_success"

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class TrendDirection(Enum):
    """Direction des tendances"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class PerformanceThreshold:
    """Seuils de performance"""
    metric_type: PerformanceMetricType
    critical_threshold: float
    warning_threshold: float
    target_value: float
    comparison_period_hours: int = 24

@dataclass
class PerformanceAlert:
    """Structure d'une alerte performance"""
    alert_id: str
    user_id: str
    content_id: Optional[str]
    metric_type: PerformanceMetricType
    severity: AlertSeverity
    current_value: float
    threshold_value: float
    trend_direction: TrendDirection
    impact_assessment: str
    recommended_actions: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class PerformanceAlertsEngine:
    """
    Engine principal pour les alertes de performance
    Monitoring intelligent et alertes prédictives pour Ainflue
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise l'engine d'alertes performance"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration des seuils par défaut
        self._initialize_default_thresholds()
        
        # Configuration IA/ML
        self.ai_prediction_enabled = self.config.get('ai_prediction', True)
        self.anomaly_detection_enabled = self.config.get('anomaly_detection', True)
        
        # Cache pour optimiser les performances
        self.metrics_cache = {}
        self.alerts_sent = {}
        
        # Métriques de l'engine
        self.engine_metrics = {
            'alerts_generated': 0,
            'critical_alerts': 0,
            'false_positives': 0,
            'prediction_accuracy': 0.0
        }
        
        self.logger.info("PerformanceAlertsEngine initialisé avec succès")

    def _initialize_default_thresholds(self):
        """Initialise les seuils de performance par défaut"""
        self.default_thresholds = {
            PerformanceMetricType.CONTENT_VIEWS: PerformanceThreshold(
                metric_type=PerformanceMetricType.CONTENT_VIEWS,
                critical_threshold=50.0,  # 50% baisse critique
                warning_threshold=25.0,   # 25% baisse warning
                target_value=1000.0,      # 1000 vues objectif
                comparison_period_hours=24
            ),
            PerformanceMetricType.ENGAGEMENT_RATE: PerformanceThreshold(
                metric_type=PerformanceMetricType.ENGAGEMENT_RATE,
                critical_threshold=40.0,  # 40% baisse engagement
                warning_threshold=20.0,   # 20% baisse warning
                target_value=5.0,         # 5% engagement target
                comparison_period_hours=24
            ),
            PerformanceMetricType.REVENUE_CPM: PerformanceThreshold(
                metric_type=PerformanceMetricType.REVENUE_CPM,
                critical_threshold=30.0,  # 30% baisse CPM
                warning_threshold=15.0,   # 15% baisse warning
                target_value=2.50,        # $2.50 CPM target
                comparison_period_hours=24
            ),
            PerformanceMetricType.AUDIO_QUALITY: PerformanceThreshold(
                metric_type=PerformanceMetricType.AUDIO_QUALITY,
                critical_threshold=70.0,  # Quality score < 70
                warning_threshold=80.0,   # Quality score < 80
                target_value=95.0,        # Quality score target 95
                comparison_period_hours=6
            ),
            PerformanceMetricType.LOAD_TIME: PerformanceThreshold(
                metric_type=PerformanceMetricType.LOAD_TIME,
                critical_threshold=5000.0,  # > 5 seconds critical
                warning_threshold=3000.0,   # > 3 seconds warning
                target_value=1000.0,        # < 1 second target
                comparison_period_hours=1
            ),
            PerformanceMetricType.CONVERSION_RATE: PerformanceThreshold(
                metric_type=PerformanceMetricType.CONVERSION_RATE,
                critical_threshold=50.0,  # 50% baisse conversion
                warning_threshold=25.0,   # 25% baisse warning
                target_value=3.0,         # 3% conversion target
                comparison_period_hours=24
            )
        }

    async def generate_alert(self, context: Any) -> Dict[str, Any]:
        """
        Génère une alerte de performance selon le contexte
        
        Args:
            context: Contexte de notification analytics
            
        Returns:
            Données de l'alerte générée
        """
        try:
            # Extraction des métriques actuelles
            current_metrics = await self._extract_performance_metrics(context)
            
            # Analyse comparative avec historique
            comparison_data = await self._analyze_performance_trends(
                context.user_id,
                context.content_id,
                current_metrics
            )
            
            # Détection d'anomalies IA
            anomalies = await self._detect_anomalies(current_metrics, comparison_data)
            
            # Génération des alertes selon les seuils
            alerts = await self._generate_threshold_alerts(
                context,
                current_metrics,
                comparison_data,
                anomalies
            )
            
            # Prédictions IA si activées
            predictions = []
            if self.ai_prediction_enabled:
                predictions = await self._generate_performance_predictions(
                    context,
                    current_metrics,
                    comparison_data
                )
            
            # Construction de la notification
            notification_data = await self._build_performance_notification(
                context,
                alerts,
                predictions,
                current_metrics
            )
            
            # Mise à jour des métriques engine
            await self._update_engine_metrics(alerts)
            
            return notification_data
            
        except Exception as e:
            self.logger.error(f"Erreur génération alerte performance: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'notification_type': 'performance_alert'
            }

    async def _extract_performance_metrics(
        self,
        context: Any
    ) -> Dict[PerformanceMetricType, float]:
        """Extrait les métriques de performance actuelles"""
        
        # Simulation de données - à remplacer par vraies métriques
        base_metrics = {
            PerformanceMetricType.CONTENT_VIEWS: 850.0,
            PerformanceMetricType.ENGAGEMENT_RATE: 4.2,
            PerformanceMetricType.REVENUE_CPM: 2.15,
            PerformanceMetricType.AUDIO_QUALITY: 92.5,
            PerformanceMetricType.LOAD_TIME: 1250.0,
            PerformanceMetricType.CONVERSION_RATE: 2.8,
            PerformanceMetricType.REACH: 15500.0,
            PerformanceMetricType.VIRAL_SCORE: 7.3,
            PerformanceMetricType.USER_RETENTION: 78.5,
            PerformanceMetricType.COLLABORATION_SUCCESS: 85.0
        }
        
        # Variation selon le contexte utilisateur
        user_factor = hash(context.user_id) % 100 / 100.0
        content_factor = hash(context.content_id or 'default') % 100 / 100.0 if context.content_id else 0.5
        
        adjusted_metrics = {}
        for metric_type, base_value in base_metrics.items():
            # Application de variations réalistes
            variation = (user_factor + content_factor) / 2
            if variation < 0.3:  # Performance faible
                multiplier = 0.6 + (variation * 0.4)
            elif variation > 0.7:  # Performance élevée
                multiplier = 1.0 + ((variation - 0.7) * 0.5)
            else:  # Performance normale
                multiplier = 0.8 + (variation * 0.4)
            
            adjusted_metrics[metric_type] = base_value * multiplier
        
        return adjusted_metrics

    async def _analyze_performance_trends(
        self,
        user_id: str,
        content_id: Optional[str],
        current_metrics: Dict[PerformanceMetricType, float]
    ) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        
        # Simulation de données historiques
        historical_data = {}
        comparison_results = {}
        
        for metric_type, current_value in current_metrics.items():
            # Génération de données historiques simulées
            historical_values = await self._get_historical_metrics(
                user_id,
                content_id,
                metric_type,
                self.default_thresholds[metric_type].comparison_period_hours
            )
            
            # Calcul des statistiques comparatives
            if historical_values:
                avg_historical = statistics.mean(historical_values)
                change_percentage = ((current_value - avg_historical) / avg_historical) * 100
                
                # Détermination de la tendance
                if abs(change_percentage) < 5:
                    trend = TrendDirection.STABLE
                elif change_percentage > 15:
                    trend = TrendDirection.INCREASING
                elif change_percentage < -15:
                    trend = TrendDirection.DECREASING
                else:
                    trend = TrendDirection.VOLATILE
                
                comparison_results[metric_type] = {
                    'current_value': current_value,
                    'historical_average': avg_historical,
                    'change_percentage': change_percentage,
                    'trend_direction': trend,
                    'historical_values': historical_values[-10:],  # Dernières 10 valeurs
                    'volatility': statistics.stdev(historical_values) if len(historical_values) > 1 else 0
                }
        
        return comparison_results

    async def _get_historical_metrics(
        self,
        user_id: str,
        content_id: Optional[str],
        metric_type: PerformanceMetricType,
        hours_back: int
    ) -> List[float]:
        """Récupère les données historiques pour une métrique"""
        
        # Simulation de données historiques - à remplacer par vraie DB
        base_value = {
            PerformanceMetricType.CONTENT_VIEWS: 900.0,
            PerformanceMetricType.ENGAGEMENT_RATE: 4.5,
            PerformanceMetricType.REVENUE_CPM: 2.30,
            PerformanceMetricType.AUDIO_QUALITY: 94.0,
            PerformanceMetricType.LOAD_TIME: 1100.0,
            PerformanceMetricType.CONVERSION_RATE: 3.1
        }.get(metric_type, 100.0)
        
        # Génération de 24 points de données simulés
        historical_values = []
        for i in range(24):
            # Variation réaliste autour de la valeur de base
            variation = (hash(f"{user_id}_{content_id}_{metric_type}_{i}") % 100 - 50) / 100.0
            value = base_value * (1 + variation * 0.2)  # ±20% variation
            historical_values.append(max(0, value))
        
        return historical_values

    async def _detect_anomalies(
        self,
        current_metrics: Dict[PerformanceMetricType, float],
        comparison_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans les métriques"""
        
        if not self.anomaly_detection_enabled:
            return []
        
        anomalies = []
        
        for metric_type, comparison in comparison_data.items():
            current_value = comparison['current_value']
            historical_avg = comparison['historical_average']
            volatility = comparison['volatility']
            
            # Détection d'anomalie basée sur l'écart type
            if volatility > 0:
                z_score = abs(current_value - historical_avg) / volatility
                
                if z_score > 3:  # Anomalie forte (3 sigma)
                    anomalies.append({
                        'metric_type': metric_type,
                        'anomaly_type': 'statistical_outlier',
                        'severity': 'high',
                        'z_score': z_score,
                        'description': f"Valeur exceptionnellement éloignée de la moyenne historique",
                        'current_value': current_value,
                        'expected_range': (
                            historical_avg - 2 * volatility,
                            historical_avg + 2 * volatility
                        )
                    })
                elif z_score > 2:  # Anomalie modérée (2 sigma)
                    anomalies.append({
                        'metric_type': metric_type,
                        'anomaly_type': 'statistical_deviation',
                        'severity': 'medium',
                        'z_score': z_score,
                        'description': f"Valeur significativement différente de la normale",
                        'current_value': current_value,
                        'expected_range': (
                            historical_avg - volatility,
                            historical_avg + volatility
                        )
                    })
            
            # Détection d'anomalie basée sur les changements brusques
            change_percentage = comparison['change_percentage']
            if abs(change_percentage) > 50:  # Changement > 50%
                anomalies.append({
                    'metric_type': metric_type,
                    'anomaly_type': 'sudden_change',
                    'severity': 'high' if abs(change_percentage) > 75 else 'medium',
                    'change_percentage': change_percentage,
                    'description': f"Changement brusque de {change_percentage:.1f}%",
                    'current_value': current_value,
                    'previous_average': historical_avg
                })
        
        return anomalies

    async def _generate_threshold_alerts(
        self,
        context: Any,
        current_metrics: Dict[PerformanceMetricType, float],
        comparison_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> List[PerformanceAlert]:
        """Génère les alertes basées sur les seuils"""
        
        alerts = []
        
        for metric_type, current_value in current_metrics.items():
            threshold = self.default_thresholds.get(metric_type)
            if not threshold:
                continue
            
            comparison = comparison_data.get(metric_type, {})
            change_percentage = comparison.get('change_percentage', 0)
            trend_direction = comparison.get('trend_direction', TrendDirection.STABLE)
            
            # Vérification des seuils critiques
            alert_severity = None
            threshold_value = None
            
            # Pour les métriques où une baisse est mauvaise
            if metric_type in [
                PerformanceMetricType.CONTENT_VIEWS,
                PerformanceMetricType.ENGAGEMENT_RATE,
                PerformanceMetricType.REVENUE_CPM,
                PerformanceMetricType.CONVERSION_RATE
            ]:
                if change_percentage <= -threshold.critical_threshold:
                    alert_severity = AlertSeverity.CRITICAL
                    threshold_value = threshold.critical_threshold
                elif change_percentage <= -threshold.warning_threshold:
                    alert_severity = AlertSeverity.HIGH
                    threshold_value = threshold.warning_threshold
            
            # Pour les métriques où une hausse est mauvaise (ex: temps de chargement)
            elif metric_type in [PerformanceMetricType.LOAD_TIME]:
                if current_value >= threshold.critical_threshold:
                    alert_severity = AlertSeverity.CRITICAL
                    threshold_value = threshold.critical_threshold
                elif current_value >= threshold.warning_threshold:
                    alert_severity = AlertSeverity.HIGH
                    threshold_value = threshold.warning_threshold
            
            # Pour les métriques de qualité
            elif metric_type in [PerformanceMetricType.AUDIO_QUALITY]:
                if current_value <= threshold.critical_threshold:
                    alert_severity = AlertSeverity.CRITICAL
                    threshold_value = threshold.critical_threshold
                elif current_value <= threshold.warning_threshold:
                    alert_severity = AlertSeverity.HIGH
                    threshold_value = threshold.warning_threshold
            
            # Génération de l'alerte si seuil dépassé
            if alert_severity:
                alert = PerformanceAlert(
                    alert_id=f"perf_{metric_type.value}_{context.user_id}_{int(datetime.now().timestamp())}",
                    user_id=context.user_id,
                    content_id=context.content_id,
                    metric_type=metric_type,
                    severity=alert_severity,
                    current_value=current_value,
                    threshold_value=threshold_value,
                    trend_direction=trend_direction,
                    impact_assessment=await self._assess_impact(metric_type, current_value, change_percentage),
                    recommended_actions=await self._generate_recommendations(metric_type, alert_severity, trend_direction),
                    timestamp=datetime.now(),
                    metadata={
                        'change_percentage': change_percentage,
                        'historical_average': comparison.get('historical_average', 0),
                        'target_value': threshold.target_value,
                        'anomalies': [a for a in anomalies if a['metric_type'] == metric_type]
                    }
                )
                alerts.append(alert)
        
        return alerts

    async def _assess_impact(
        self,
        metric_type: PerformanceMetricType,
        current_value: float,
        change_percentage: float
    ) -> str:
        """Évalue l'impact business de la métrique"""
        
        impact_templates = {
            PerformanceMetricType.CONTENT_VIEWS: {
                'critical': f"Perte massive de visibilité ({change_percentage:.1f}%). Impact revenue estimé élevé.",
                'high': f"Baisse significative engagement ({change_percentage:.1f}%). Revenus affectés.",
                'medium': f"Diminution notable audience ({change_percentage:.1f}%). Surveillance requise."
            },
            PerformanceMetricType.ENGAGEMENT_RATE: {
                'critical': f"Effondrement engagement ({change_percentage:.1f}%). Algorithmes défavorables.",
                'high': f"Chute engagement importante ({change_percentage:.1f}%). Reach organique réduit.",
                'medium': f"Engagement en baisse ({change_percentage:.1f}%). Optimisation contenu requise."
            },
            PerformanceMetricType.REVENUE_CPM: {
                'critical': f"Effondrement CPM ({change_percentage:.1f}%). Revenus gravement impactés.",
                'high': f"Baisse CPM significative ({change_percentage:.1f}%). Rentabilité réduite.",
                'medium': f"CPM en diminution ({change_percentage:.1f}%). Optimisation monétisation nécessaire."
            },
            PerformanceMetricType.AUDIO_QUALITY: {
                'critical': f"Qualité audio dégradée ({current_value:.1f}/100). Expérience utilisateur compromise.",
                'high': f"Problèmes qualité audio ({current_value:.1f}/100). Satisfaction utilisateur affectée.",
                'medium': f"Qualité audio sous-optimale ({current_value:.1f}/100). Amélioration recommandée."
            }
        }
        
        # Détermination du niveau d'impact
        if abs(change_percentage) > 40 or current_value < 70:
            level = 'critical'
        elif abs(change_percentage) > 20 or current_value < 80:
            level = 'high'
        else:
            level = 'medium'
        
        return impact_templates.get(metric_type, {}).get(
            level,
            f"Impact {level} détecté pour {metric_type.value}"
        )

    async def _generate_recommendations(
        self,
        metric_type: PerformanceMetricType,
        severity: AlertSeverity,
        trend_direction: TrendDirection
    ) -> List[str]:
        """Génère des recommandations d'action"""
        
        base_recommendations = {
            PerformanceMetricType.CONTENT_VIEWS: [
                "Analyser l'algorithme de recommandation actuel",
                "Optimiser les tags et métadonnées SEO",
                "Programmer contenu aux heures de peak audience",
                "Améliorer thumbnails et titres accrocheurs",
                "Augmenter fréquence de publication",
                "Analyser performance contenu similaire concurrent"
            ],
            PerformanceMetricType.ENGAGEMENT_RATE: [
                "Analyser feedback audience et commentaires",
                "Tester différents formats de contenu",
                "Améliorer call-to-action dans le contenu",
                "Optimiser longueur et structure du contenu",
                "Augmenter interaction directe avec audience",
                "A/B tester différents styles de présentation"
            ],
            PerformanceMetricType.REVENUE_CPM: [
                "Revoir stratégie de placement publicitaire",
                "Optimiser audience targeting demographics",
                "Négocier avec réseaux publicitaires premium",
                "Diversifier sources de monétisation",
                "Améliorer contenu brand-safe",
                "Analyser concurrence pricing strategies"
            ],
            PerformanceMetricType.AUDIO_QUALITY: [
                "Vérifier équipement enregistrement audio",
                "Optimiser post-production et mastering",
                "Corriger problèmes acoustiques studio",
                "Upgrader codec et qualité d'export",
                "Réenregistrer segments problématiques",
                "Consulter ingénieur son professionnel"
            ],
            PerformanceMetricType.LOAD_TIME: [
                "Optimiser compression et taille fichiers",
                "Implémenter CDN pour distribution globale",
                "Optimiser code et ressources frontend",
                "Compresser images et médias",
                "Mettre en cache contenu statique",
                "Upgrader infrastructure serveur"
            ],
            PerformanceMetricType.CONVERSION_RATE: [
                "Optimiser funnel de conversion utilisateur",
                "A/B tester call-to-action placements",
                "Simplifier processus d'inscription/achat",
                "Améliorer UX/UI des pages critiques",
                "Analyser points de friction utilisateur",
                "Personnaliser expérience selon segments"
            ]
        }
        
        recommendations = base_recommendations.get(metric_type, [
            "Analyser les causes de la dégradation",
            "Implémenter monitoring renforcé",
            "Consulter expert domaine spécialisé"
        ])
        
        # Priorité selon la sévérité
        if severity == AlertSeverity.CRITICAL:
            return recommendations[:3]  # Actions urgentes
        elif severity == AlertSeverity.HIGH:
            return recommendations[:4]  # Actions importantes
        else:
            return recommendations[:2]  # Actions recommandées

    async def _generate_performance_predictions(
        self,
        context: Any,
        current_metrics: Dict[PerformanceMetricType, float],
        comparison_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des prédictions de performance IA"""
        
        predictions = []
        
        for metric_type, comparison in comparison_data.items():
            trend_direction = comparison.get('trend_direction', TrendDirection.STABLE)
            change_percentage = comparison.get('change_percentage', 0)
            volatility = comparison.get('volatility', 0)
            
            # Prédiction simple basée sur la tendance
            current_value = comparison['current_value']
            
            if trend_direction == TrendDirection.DECREASING:
                # Prédiction de continuation de la baisse
                predicted_change = min(-5, change_percentage * 0.7)  # Atténuation de 30%
                confidence = 0.8 if abs(change_percentage) > 20 else 0.6
                
                predictions.append({
                    'metric_type': metric_type,
                    'prediction_type': 'trend_continuation',
                    'timeframe_hours': 24,
                    'predicted_value': current_value * (1 + predicted_change / 100),
                    'predicted_change_percentage': predicted_change,
                    'confidence_score': confidence,
                    'risk_level': 'high' if predicted_change < -15 else 'medium',
                    'description': f"Continuation probable de la baisse ({predicted_change:.1f}%)"
                })
            
            elif trend_direction == TrendDirection.INCREASING:
                # Prédiction de continuation de la hausse
                predicted_change = max(2, change_percentage * 0.6)  # Atténuation de 40%
                confidence = 0.7 if change_percentage > 15 else 0.5
                
                predictions.append({
                    'metric_type': metric_type,
                    'prediction_type': 'growth_continuation',
                    'timeframe_hours': 24,
                    'predicted_value': current_value * (1 + predicted_change / 100),
                    'predicted_change_percentage': predicted_change,
                    'confidence_score': confidence,
                    'risk_level': 'low',
                    'description': f"Croissance probable maintenue ({predicted_change:.1f}%)"
                })
            
            elif trend_direction == TrendDirection.VOLATILE:
                # Prédiction de stabilisation
                predictions.append({
                    'metric_type': metric_type,
                    'prediction_type': 'volatility_stabilization',
                    'timeframe_hours': 24,
                    'predicted_value': comparison['historical_average'],
                    'predicted_change_percentage': 0,
                    'confidence_score': 0.6,
                    'risk_level': 'medium',
                    'description': "Stabilisation probable vers moyenne historique"
                })
        
        return predictions

    async def _build_performance_notification(
        self,
        context: Any,
        alerts: List[PerformanceAlert],
        predictions: List[Dict[str, Any]],
        current_metrics: Dict[PerformanceMetricType, float]
    ) -> Dict[str, Any]:
        """Construit la notification de performance finale"""
        
        # Priorité selon les alertes
        max_severity = AlertSeverity.INFO
        if alerts:
            severity_order = [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM, AlertSeverity.LOW]
            for severity in severity_order:
                if any(alert.severity == severity for alert in alerts):
                    max_severity = severity
                    break
        
        # Construction du contenu principal
        if alerts:
            primary_alert = alerts[0]  # Alerte la plus importante
            
            title = f"🚨 Performance Alert: {primary_alert.metric_type.value.replace('_', ' ').title()}"
            
            if max_severity == AlertSeverity.CRITICAL:
                title = f"🔴 CRITICAL: {title}"
            elif max_severity == AlertSeverity.HIGH:
                title = f"🟡 HIGH: {title}"
            
            message = f"""
Performance issue détectée pour votre contenu:

📊 Métrique: {primary_alert.metric_type.value.replace('_', ' ').title()}
📈 Valeur actuelle: {primary_alert.current_value:.1f}
⚠️ Seuil dépassé: {primary_alert.threshold_value:.1f}
📉 Tendance: {primary_alert.trend_direction.value}

🎯 Impact: {primary_alert.impact_assessment}

🔧 Actions recommandées:
{chr(10).join([f"• {action}" for action in primary_alert.recommended_actions])}
"""
        else:
            title = "📊 Performance Report"
            message = "Rapport de performance disponible pour votre contenu."
        
        # Ajout des prédictions si disponibles
        if predictions:
            high_risk_predictions = [p for p in predictions if p.get('risk_level') == 'high']
            if high_risk_predictions:
                prediction = high_risk_predictions[0]
                message += f"\n\n🔮 Prédiction IA (24h): {prediction['description']}"
        
        # Construction des données complètes
        notification_data = {
            'notification_id': f"perf_alert_{context.user_id}_{int(datetime.now().timestamp())}",
            'notification_type': 'performance_alert',
            'priority': max_severity.value,
            'content': {
                'title': title,
                'message': message,
                'icon': '📊',
                'color': self._get_severity_color(max_severity)
            },
            'data': {
                'alerts': [self._serialize_alert(alert) for alert in alerts],
                'predictions': predictions,
                'current_metrics': {k.value: v for k, v in current_metrics.items()},
                'summary': {
                    'total_alerts': len(alerts),
                    'critical_alerts': len([a for a in alerts if a.severity == AlertSeverity.CRITICAL]),
                    'high_risk_predictions': len([p for p in predictions if p.get('risk_level') == 'high'])
                }
            },
            'actions': self._generate_notification_actions(alerts),
            'engagement_score': self._calculate_engagement_score(max_severity, alerts, predictions)
        }
        
        return notification_data

    def _serialize_alert(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Sérialise une alerte pour la notification"""
        return {
            'alert_id': alert.alert_id,
            'metric_type': alert.metric_type.value,
            'severity': alert.severity.value,
            'current_value': alert.current_value,
            'threshold_value': alert.threshold_value,
            'trend_direction': alert.trend_direction.value,
            'impact_assessment': alert.impact_assessment,
            'recommended_actions': alert.recommended_actions,
            'timestamp': alert.timestamp.isoformat(),
            'metadata': alert.metadata
        }

    def _get_severity_color(self, severity: AlertSeverity) -> str:
        """Retourne la couleur selon la sévérité"""
        color_map = {
            AlertSeverity.CRITICAL: '#FF0000',
            AlertSeverity.HIGH: '#FF8C00',
            AlertSeverity.MEDIUM: '#FFD700',
            AlertSeverity.LOW: '#90EE90',
            AlertSeverity.INFO: '#87CEEB'
        }
        return color_map.get(severity, '#87CEEB')

    def _generate_notification_actions(self, alerts: List[PerformanceAlert]) -> List[Dict[str, str]]:
        """Génère les actions possibles pour la notification"""
        actions = [
            {
                'action_id': 'view_detailed_analytics',
                'label': 'Voir Analytics Détaillées',
                'type': 'navigation',
                'url': '/analytics/performance'
            },
            {
                'action_id': 'dismiss_alert',
                'label': 'Marquer comme Lu',
                'type': 'action'
            }
        ]
        
        if alerts:
            actions.append({
                'action_id': 'get_optimization_tips',
                'label': 'Conseils d\'Optimisation',
                'type': 'navigation',
                'url': '/optimization/recommendations'
            })
        
        return actions

    def _calculate_engagement_score(
        self,
        severity: AlertSeverity,
        alerts: List[PerformanceAlert],
        predictions: List[Dict[str, Any]]
    ) -> float:
        """Calcule le score d'engagement de la notification"""
        
        base_score = 0.5
        
        # Bonus selon la sévérité
        severity_bonus = {
            AlertSeverity.CRITICAL: 0.4,
            AlertSeverity.HIGH: 0.3,
            AlertSeverity.MEDIUM: 0.2,
            AlertSeverity.LOW: 0.1,
            AlertSeverity.INFO: 0.0
        }
        
        score = base_score + severity_bonus.get(severity, 0.0)
        
        # Bonus pour multiple alertes
        if len(alerts) > 1:
            score += min(0.2, len(alerts) * 0.05)
        
        # Bonus pour prédictions à haut risque
        high_risk_predictions = len([p for p in predictions if p.get('risk_level') == 'high'])
        if high_risk_predictions > 0:
            score += min(0.2, high_risk_predictions * 0.1)
        
        return min(1.0, score)

    async def _update_engine_metrics(self, alerts: List[PerformanceAlert]):
        """Met à jour les métriques de l'engine"""
        self.engine_metrics['alerts_generated'] += len(alerts)
        
        critical_count = len([a for a in alerts if a.severity == AlertSeverity.CRITICAL])
        self.engine_metrics['critical_alerts'] += critical_count
        
        # Simulation de mise à jour accuracy - à remplacer par vraie logique
        self.engine_metrics['prediction_accuracy'] = 0.87

    async def get_engine_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'engine"""
        return {
            'engine_name': 'PerformanceAlertsEngine',
            'status': 'active',
            'metrics': self.engine_metrics,
            'thresholds_configured': len(self.default_thresholds),
            'ai_features': {
                'prediction_enabled': self.ai_prediction_enabled,
                'anomaly_detection_enabled': self.anomaly_detection_enabled
            }
        }

# Export principal
__all__ = [
    'PerformanceAlertsEngine',
    'PerformanceAlert',
    'PerformanceMetricType',
    'AlertSeverity',
    'TrendDirection'
]