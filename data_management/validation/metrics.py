"""🚀 Validation Metrics & Analytics - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/validation/metrics.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE MÉTRIQUES ET ANALYTICS DE VALIDATION
Analytics avancées pour monitoring et optimisation
- Métriques de performance de validation
- Analytics temps réel
- Reporting et dashboards
- Optimisation automatique des règles
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter

# Analytics libraries
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """
Types de métriques"""

    PERFORMANCE = "performance"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    USAGE = "usage"
    ERROR = "error"

class AggregationType(Enum):
    """Types d'agrégation"""

    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std"

@dataclass
class ValidationMetric:
    """Métrique de validation individuelle"""
    id: str
    name: str
    metric_type: MetricType
    value: Union[int, float, str]
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class ValidationEvent:
    """Événement de validation"""
    event_id: str
    event_type: str
    timestamp: datetime
    file_path: str
    creator_type: str
    content_type: str
    validation_result: Dict[str, Any]
    metrics: List[ValidationMetric] = field(default_factory=list)
    duration_ms: float = 0.0
    errors: List[str] = field(default_factory=list)

@dataclass
class MetricSummary:
    """
Résumé de métriques"""
    metric_name: str
    metric_type: MetricType
    total_count: int
    average_value: float
    min_value: float
    max_value: float
    median_value: float
    std_deviation: float
    percentiles: Dict[str, float]
    trend_direction: str  # 'up', 'down', 'stable'
    time_range: Tuple[datetime, datetime]

class MetricsCollector:
    """
Collecteur de métriques de validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.metrics_buffer: List[ValidationMetric] = []
        self.events_buffer: List[ValidationEvent] = []
        self.buffer_size = 1000
    
    def record_validation_event(self, event: ValidationEvent):
        """Enregistre un événement de validation"""
        try:
            # Génération automatique de métriques à partir de l'événement
            auto_metrics = self._generate_auto_metrics(event)
            event.metrics.extend(auto_metrics)
            
            # Ajout au buffer
            self.events_buffer.append(event)
            self.metrics_buffer.extend(event.metrics)
            
            # Nettoyage du buffer si nécessaire
            if len(self.events_buffer) > self.buffer_size:
                self.events_buffer = self.events_buffer[-self.buffer_size:]
            
            if len(self.metrics_buffer) > self.buffer_size * 10:
                self.metrics_buffer = self.metrics_buffer[-self.buffer_size * 10:]
            
            self.logger.debug(f"Recorded validation event {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement événement: {e}")
    
    def record_metric(self, metric: ValidationMetric):
        """Enregistre une métrique individuelle"""
        try:
            self.metrics_buffer.append(metric)
            
            if len(self.metrics_buffer) > self.buffer_size * 10:
                self.metrics_buffer = self.metrics_buffer[-self.buffer_size * 10:]
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement métrique: {e}")
    
    def get_metrics_by_type(self, metric_type: MetricType, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[ValidationMetric]:
        """Récupère les métriques par type et période"""
        filtered_metrics = []
        
        for metric in self.metrics_buffer:
            # Filtrage par type
            if metric.metric_type != metric_type:
                continue
            
            # Filtrage par période
            if start_time and metric.timestamp < start_time:
                continue
            if end_time and metric.timestamp > end_time:
                continue
            
            filtered_metrics.append(metric)
        
        return filtered_metrics
    
    def get_events_by_criteria(
        self,
        creator_type: Optional[str] = None,
        content_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ValidationEvent]:
        """
Récupère les événements selon des critères"""
        filtered_events = []
        
        for event in self.events_buffer:
            # Filtrage par type de créateur
            if creator_type and event.creator_type != creator_type:
                continue
            
            # Filtrage par type de contenu
            if content_type and event.content_type != content_type:
                continue
            
            # Filtrage par période
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def _generate_auto_metrics(self, event: ValidationEvent) -> List[ValidationMetric]:
        """
Génère automatiquement des métriques depuis un événement"""
        auto_metrics = []
        base_timestamp = event.timestamp
        
        # Métrique de performance - durée
        auto_metrics.append(ValidationMetric(
            id=f"{event.event_id}_duration",
            name="validation_duration",
            metric_type=MetricType.PERFORMANCE,
            value=event.duration_ms,
            unit="milliseconds",
            timestamp=base_timestamp,
            context={'event_id': event.event_id, 'creator_type': event.creator_type},
            tags=['performance', 'duration']
        ))
        
        # Métrique de qualité - succès/échec
        is_valid = event.validation_result.get('is_valid', False)
        auto_metrics.append(ValidationMetric(
            id=f"{event.event_id}_success",
            name="validation_success",
            metric_type=MetricType.QUALITY,
            value=1 if is_valid else 0,
            unit="boolean",
            timestamp=base_timestamp,
            context={'event_id': event.event_id, 'creator_type': event.creator_type},
            tags=['quality', 'success']
        ))
        
        # Métrique de compliance - score
        compliance_score = event.validation_result.get('compliance_score', 0.0)
        auto_metrics.append(ValidationMetric(
            id=f"{event.event_id}_compliance",
            name="compliance_score",
            metric_type=MetricType.COMPLIANCE,
            value=compliance_score,
            unit="score",
            timestamp=base_timestamp,
            context={'event_id': event.event_id, 'creator_type': event.creator_type},
            tags=['compliance', 'score']
        ))
        
        # Métrique de sécurité - niveau de menace
        security_data = event.validation_result.get('security', {})
        threat_level = security_data.get('threat_level', 'safe')
        threat_score = {'safe': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}.get(threat_level, 0)
        
        auto_metrics.append(ValidationMetric(
            id=f"{event.event_id}_security",
            name="security_threat_level",
            metric_type=MetricType.SECURITY,
            value=threat_score,
            unit="level",
            timestamp=base_timestamp,
            context={'event_id': event.event_id, 'threat_level': threat_level},
            tags=['security', 'threat']
        ))
        
        # Métrique d'erreur - nombre d'erreurs
        error_count = len(event.errors)
        auto_metrics.append(ValidationMetric(
            id=f"{event.event_id}_errors",
            name="error_count",
            metric_type=MetricType.ERROR,
            value=error_count,
            unit="count",
            timestamp=base_timestamp,
            context={'event_id': event.event_id, 'creator_type': event.creator_type},
            tags=['error', 'count']
        ))
        
        return auto_metrics

class MetricsAnalyzer:
    """Analyseur de métriques avancé"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(f"{__name__}.MetricsAnalyzer")
    
    def analyze_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Récupération des métriques de performance
        performance_metrics = self.collector.get_metrics_by_type(
            MetricType.PERFORMANCE, start_time, end_time
        )
        
        if not performance_metrics:
            return {'status': 'no_data', 'message': 'Insufficient performance data'}
        
        # Analyse par nom de métrique
        analysis = {}
        metrics_by_name = defaultdict(list)
        
        for metric in performance_metrics:
            metrics_by_name[metric.name].append(metric)
        
        for metric_name, metrics in metrics_by_name.items():
            values = [float(m.value) for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # Statistiques de base
            summary = MetricSummary(
                metric_name=metric_name,
                metric_type=MetricType.PERFORMANCE,
                total_count=len(values),
                average_value=statistics.mean(values),
                min_value=min(values),
                max_value=max(values),
                median_value=statistics.median(values),
                std_deviation=statistics.stdev(values) if len(values) > 1 else 0,
                percentiles={
                    'p50': np.percentile(values, 50),
                    'p90': np.percentile(values, 90),
                    'p95': np.percentile(values, 95),
                    'p99': np.percentile(values, 99)
                },
                trend_direction=self._calculate_trend(values, timestamps),
                time_range=(start_time, end_time)
            )
            
            analysis[metric_name] = {
                'summary': summary,
                'anomalies': self._detect_anomalies(values),
                'seasonal_patterns': self._detect_seasonal_patterns(values, timestamps)
            }
        
        return analysis
    
    def analyze_quality_metrics(self, creator_type: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
Analyse les métriques de qualité"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Récupération des événements
        events = self.collector.get_events_by_criteria(
            creator_type=creator_type,
            start_time=start_time,
            end_time=end_time
        )
        
        if not events:
            return {'status': 'no_data', 'message': 'Insufficient quality data'}
        
        analysis = {
            'total_validations': len(events),
            'success_rate': 0,
            'average_compliance_score': 0,
            'common_issues': [],
            'creator_type_breakdown': {},
            'content_type_breakdown': {},
            'trend_analysis': {}
        }
        
        # Calcul du taux de succès
        successful_validations = sum(1 for e in events if e.validation_result.get('is_valid', False))
        analysis['success_rate'] = (successful_validations / len(events)) * 100
        
        # Score de compliance moyen
        compliance_scores = [e.validation_result.get('compliance_score', 0) for e in events]
        analysis['average_compliance_score'] = statistics.mean(compliance_scores)
        
        # Analyse par type de créateur
        creator_stats = defaultdict(lambda: {'total': 0, 'success': 0})
        for event in events:
            creator_stats[event.creator_type]['total'] += 1
            if event.validation_result.get('is_valid', False):
                creator_stats[event.creator_type]['success'] += 1
        
        for creator, stats in creator_stats.items():
            analysis['creator_type_breakdown'][creator] = {
                'total_validations': stats['total'],
                'success_rate': (stats['success'] / stats['total']) * 100,
                'compliance_score': statistics.mean([
                    e.validation_result.get('compliance_score', 0)
                    for e in events if e.creator_type == creator
                ])
            }
        
        # Analyse par type de contenu
        content_stats = defaultdict(lambda: {'total': 0, 'success': 0})
        for event in events:
            content_stats[event.content_type]['total'] += 1
            if event.validation_result.get('is_valid', False):
                content_stats[event.content_type]['success'] += 1
        
        for content, stats in content_stats.items():
            analysis['content_type_breakdown'][content] = {
                'total_validations': stats['total'],
                'success_rate': (stats['success'] / stats['total']) * 100
            }
        
        # Problèmes communs
        all_errors = []
        for event in events:
            all_errors.extend(event.errors)
        
        error_counts = Counter(all_errors)
        analysis['common_issues'] = [
            {'error': error, 'count': count, 'percentage': (count / len(events)) * 100}
            for error, count in error_counts.most_common(10)
        ]
        
        return analysis
    
    def analyze_security_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
Analyse les métriques de sécurité"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Récupération des métriques de sécurité
        security_metrics = self.collector.get_metrics_by_type(
            MetricType.SECURITY, start_time, end_time
        )
        
        if not security_metrics:
            return {'status': 'no_data', 'message': 'Insufficient security data'}
        
        analysis = {
            'total_security_scans': len(security_metrics),
            'threat_level_distribution': {},
            'security_score_average': 0,
            'high_risk_files': 0,
            'security_trends': {}
        }
        
        # Distribution des niveaux de menace
        threat_levels = [m.context.get('threat_level', 'safe') for m in security_metrics]
        threat_distribution = Counter(threat_levels)
        
        for level, count in threat_distribution.items():
            analysis['threat_level_distribution'][level] = {
                'count': count,
                'percentage': (count / len(security_metrics)) * 100
            }
        
        # Fichiers à haut risque
        high_risk_count = sum(1 for m in security_metrics if float(m.value) >= 3)  # High/Critical
        analysis['high_risk_files'] = high_risk_count
        analysis['risk_percentage'] = (high_risk_count / len(security_metrics)) * 100
        
        return analysis
    
    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
Génère un rapport de performance complet"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        report = {
            'report_period': {'start': start_time.isoformat(), 'end': end_time.isoformat()},
            'summary': {},
            'performance_trends': {},
            'quality_analysis': {},
            'security_analysis': {},
            'recommendations': []
        }
        
        # Analyse des tendances de performance
        performance_analysis = self.analyze_performance_trends(days)
        report['performance_trends'] = performance_analysis
        
        # Analyse de qualité
        quality_analysis = self.analyze_quality_metrics(days=days)
        report['quality_analysis'] = quality_analysis
        
        # Analyse de sécurité
        security_analysis = self.analyze_security_metrics(days)
        report['security_analysis'] = security_analysis
        
        # Résumé global
        if quality_analysis.get('status') != 'no_data':
            report['summary'] = {
                'total_validations': quality_analysis.get('total_validations', 0),
                'overall_success_rate': quality_analysis.get('success_rate', 0),
                'average_compliance': quality_analysis.get('average_compliance_score', 0),
                'security_risk_level': self._calculate_overall_risk_level(security_analysis)
            }
        
        # Génération de recommandations
        report['recommendations'] = self._generate_recommendations(
            performance_analysis, quality_analysis, security_analysis
        )
        
        return report
    
    def _calculate_trend(self, values: List[float], timestamps: List[datetime]) -> str:
        """
Calcule la tendance d'une série de valeurs"""
        if len(values) < 2:
            return 'stable'
        
        try:
            # Conversion timestamps en nombres pour régression
            timestamp_numbers = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
            
            # Régression linéaire simple
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamp_numbers, values)
            
            # Seuil de significativité
            if abs(slope) < 0.01 or p_value > 0.05:
                return 'stable'
            elif slope > 0:
                return 'up'
            else:
                return 'down'
                
        except Exception as e:
            self.logger.debug(f"Erreur calcul tendance: {e}")
            return 'stable'
    
    def _detect_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans une série de valeurs"""
        anomalies = []
        
        if len(values) < 5:
            return anomalies
        
        try:
            # Utilisation de l'écart-type pour détecter les outliers
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            threshold = 2 * std_val  # 2 écarts-types
            
            for i, value in enumerate(values):
                if abs(value - mean_val) > threshold:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'deviation': abs(value - mean_val),
                        'type': 'high' if value > mean_val else 'low'
                    })
        
        except Exception as e:
            self.logger.debug(f"Erreur détection anomalies: {e}")
        
        return anomalies
    
    def _detect_seasonal_patterns(self, values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Détecte les patterns saisonniers"""
        patterns = {'hourly': {}, 'daily': {}, 'weekly': {}}
        
        try:
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                # Pattern horaire
                hour = timestamp.hour
                if hour not in patterns['hourly']:
                    patterns['hourly'][hour] = []
                patterns['hourly'][hour].append(value)
                
                # Pattern journalier
                day = timestamp.weekday()
                if day not in patterns['daily']:
                    patterns['daily'][day] = []
                patterns['daily'][day].append(value)
            
            # Calcul des moyennes
            for pattern_type in patterns:
                for key, values_list in patterns[pattern_type].items():
                    if values_list:
                        patterns[pattern_type][key] = {
                            'average': statistics.mean(values_list),
                            'count': len(values_list)
                        }
        
        except Exception as e:
            self.logger.debug(f"Erreur détection patterns: {e}")
        
        return patterns
    
    def _calculate_overall_risk_level(self, security_analysis: Dict[str, Any]) -> str:
        """Calcule le niveau de risque global"""
        if security_analysis.get('status') == 'no_data':
            return 'unknown'
        
        risk_percentage = security_analysis.get('risk_percentage', 0)
        
        if risk_percentage >= 20:
            return 'high'
        elif risk_percentage >= 10:
            return 'medium'
        elif risk_percentage >= 5:
            return 'low'
        else:
            return 'minimal'
    
    def _generate_recommendations(
        self,
        performance_analysis: Dict[str, Any],
        quality_analysis: Dict[str, Any],
        security_analysis: Dict[str, Any]
    ) -> List[str]:
        """
Génère des recommandations basées sur les analyses"""
        recommendations = []
        
        # Recommandations performance
        if performance_analysis:
            for metric_name, analysis in performance_analysis.items():
                if isinstance(analysis, dict) and 'summary' in analysis:
                    summary = analysis['summary']
                    if hasattr(summary, 'trend_direction') and summary.trend_direction == 'down':
                        recommendations.append(f"Performance declining for {metric_name} - investigate bottlenecks")
                    
                    if hasattr(summary, 'std_deviation') and summary.std_deviation > summary.average_value * 0.5:
                        recommendations.append(f"High variability in {metric_name} - check system stability")
        
        # Recommandations qualité
        if quality_analysis.get('status') != 'no_data':
            success_rate = quality_analysis.get('success_rate', 100)
            if success_rate < 80:
                recommendations.append("Validation success rate below 80% - review validation rules")
            
            compliance_score = quality_analysis.get('average_compliance_score', 1.0)
            if compliance_score < 0.7:
                recommendations.append("Low compliance scores - provide user guidance")
        
        # Recommandations sécurité
        if security_analysis.get('status') != 'no_data':
            risk_percentage = security_analysis.get('risk_percentage', 0)
            if risk_percentage > 15:
                recommendations.append("High security risk detected - strengthen security policies")
        
        return recommendations

class MetricsDashboard:
    """Dashboard de métriques en temps réel"""
    
    def __init__(self, analyzer: MetricsAnalyzer):
        self.analyzer = analyzer
        self.logger = logging.getLogger(f"{__name__}.MetricsDashboard")
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques temps réel"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        stats = {
            'timestamp': now.isoformat(),
            'last_hour': {},
            'last_24h': {},
            'status_indicators': {}
        }
        
        # Statistiques dernière heure
        recent_events = self.analyzer.collector.get_events_by_criteria(start_time=last_hour)
        stats['last_hour'] = {
            'total_validations': len(recent_events),
            'success_rate': (sum(1 for e in recent_events if e.validation_result.get('is_valid', False)) / len(recent_events) * 100) if recent_events else 0,
            'average_duration': statistics.mean([e.duration_ms for e in recent_events]) if recent_events else 0
        }
        
        # Statistiques dernières 24h
        daily_events = self.analyzer.collector.get_events_by_criteria(start_time=last_day)
        stats['last_24h'] = {
            'total_validations': len(daily_events),
            'success_rate': (sum(1 for e in daily_events if e.validation_result.get('is_valid', False)) / len(daily_events) * 100) if daily_events else 0,
            'unique_creators': len(set(e.creator_type for e in daily_events)),
            'content_types': len(set(e.content_type for e in daily_events))
        }
        
        # Indicateurs de statut
        stats['status_indicators'] = {
            'system_health': self._calculate_system_health(daily_events),
            'performance_status': self._calculate_performance_status(recent_events),
            'security_status': self._calculate_security_status(daily_events)
        }
        
        return stats
    
    def get_creator_type_dashboard(self, creator_type: str) -> Dict[str, Any]:
        """
Dashboard spécifique à un type de créateur"""
        now = datetime.now()
        last_week = now - timedelta(days=7)
        
        events = self.analyzer.collector.get_events_by_criteria(
            creator_type=creator_type,
            start_time=last_week
        )
        
        dashboard = {
            'creator_type': creator_type,
            'period': 'last_7_days',
            'summary': {},
            'trends': {},
            'top_issues': [],
            'recommendations': []
        }
        
        if not events:
            dashboard['summary'] = {'status': 'no_data'}
            return dashboard
        
        # Résumé
        dashboard['summary'] = {
            'total_validations': len(events),
            'success_rate': (sum(1 for e in events if e.validation_result.get('is_valid', False)) / len(events)) * 100,
            'average_compliance': statistics.mean([e.validation_result.get('compliance_score', 0) for e in events]),
            'content_types': list(set(e.content_type for e in events))
        }
        
        # Tendances par jour
        daily_stats = defaultdict(lambda: {'total': 0, 'success': 0})
        for event in events:
            day = event.timestamp.date()
            daily_stats[day]['total'] += 1
            if event.validation_result.get('is_valid', False):
                daily_stats[day]['success'] += 1
        
        dashboard['trends'] = {
            str(day): {
                'validations': stats['total'],
                'success_rate': (stats['success'] / stats['total']) * 100
            }
            for day, stats in daily_stats.items()
        }
        
        # Top problèmes
        all_errors = []
        for event in events:
            all_errors.extend(event.errors)
        
        error_counts = Counter(all_errors)
        dashboard['top_issues'] = [
            {'error': error, 'count': count}
            for error, count in error_counts.most_common(5)
        ]
        
        return dashboard
    
    def _calculate_system_health(self, events: List[ValidationEvent]) -> str:
        """
Calcule l'état de santé du système"""
        if not events:
            return 'unknown'
        
        success_rate = sum(1 for e in events if e.validation_result.get('is_valid', False)) / len(events)
        avg_duration = statistics.mean([e.duration_ms for e in events])
        error_rate = sum(1 for e in events if e.errors) / len(events)
        
        if success_rate > 0.95 and avg_duration < 1000 and error_rate < 0.05:
            return 'excellent'
        elif success_rate > 0.90 and avg_duration < 2000 and error_rate < 0.10:
            return 'good'
        elif success_rate > 0.80 and avg_duration < 5000 and error_rate < 0.20:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_performance_status(self, events: List[ValidationEvent]) -> str:
        """
Calcule le statut de performance"""
        if not events:
            return 'unknown'
        
        avg_duration = statistics.mean([e.duration_ms for e in events])
        
        if avg_duration < 500:
            return 'excellent'
        elif avg_duration < 1000:
            return 'good'
        elif avg_duration < 2000:
            return 'fair'
        else:
            return 'slow'
    
    def _calculate_security_status(self, events: List[ValidationEvent]) -> str:
        """
Calcule le statut de sécurité"""
        if not events:
            return 'unknown'
        
        high_risk_events = []
        for event in events:
            security_data = event.validation_result.get('security', {})
            threat_level = security_data.get('threat_level', 'safe')
            if threat_level in ['high', 'critical']:
                high_risk_events.append(event)
        
        risk_percentage = len(high_risk_events) / len(events) * 100
        
        if risk_percentage == 0:
            return 'secure'
        elif risk_percentage < 5:
            return 'low_risk'
        elif risk_percentage < 15:
            return 'medium_risk'
        else:
            return 'high_risk'

class ValidationMetrics:
    """
Système principal de métriques de validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ValidationMetrics")
        self.collector = MetricsCollector()
        self.analyzer = MetricsAnalyzer(self.collector)
        self.dashboard = MetricsDashboard(self.analyzer)
    
    def record_validation(
        self,
        file_path: str,
        creator_type: str,
        content_type: str,
        validation_result: Dict[str, Any],
        duration_ms: float,
        errors: List[str] = None
    ):
        """Enregistre une validation complète"""
        event = ValidationEvent(
            event_id=f"val_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            event_type='file_validation',
            timestamp=datetime.now(),
            file_path=file_path,
            creator_type=creator_type,
            content_type=content_type,
            validation_result=validation_result,
            duration_ms=duration_ms,
            errors=errors or []
        )
        
        self.collector.record_validation_event(event)
    
    def get_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Récupère un rapport de performance"""
        return self.analyzer.generate_performance_report(days)
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """
Récupère le dashboard temps réel"""
        return self.dashboard.get_real_time_stats()
    
    def get_creator_dashboard(self, creator_type: str) -> Dict[str, Any]:
        """
Récupère le dashboard d'un type de créateur"""
        return self.dashboard.get_creator_type_dashboard(creator_type)
    
    def export_metrics(self, start_time: datetime, end_time: datetime, format: str = 'json') -> str:
        """
Exporte les métriques dans un format spécifique"""
        events = self.collector.get_events_by_criteria(start_time=start_time, end_time=end_time)
        
        if format == 'json':
            export_data = {
                'export_info': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'total_events': len(events)
                },
                'events': [
                    {
                        'event_id': e.event_id,
                        'timestamp': e.timestamp.isoformat(),
                        'creator_type': e.creator_type,
                        'content_type': e.content_type,
                        'validation_result': e.validation_result,
                        'duration_ms': e.duration_ms,
                        'errors': e.errors
                    }
                    for e in events
                ]
            }
            return json.dumps(export_data, indent=2)
        
        else:
            raise ValueError(f"Format d'export non supporté: {format}")

# Instance globale pour usage facile
validation_metrics = ValidationMetrics()

# Export des classes principales
__all__ = [
    'ValidationMetrics',
    'MetricsCollector',
    'MetricsAnalyzer',
    'MetricsDashboard',
    'ValidationMetric',
    'ValidationEvent',
    'MetricSummary',
    'MetricType',
    'AggregationType',
    'validation_metrics'
]
