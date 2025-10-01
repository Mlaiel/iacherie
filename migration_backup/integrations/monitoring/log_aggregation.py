#!/usr/bin/env python3

"""
📝 LOG AGGREGATION ENGINE - ENTERPRISE IMPLEMENTATION
=====================================================

Log aggregation enterprise avec structured logging et intelligent analysis.
Infrastructure robuste d'agrégation de logs pour monitoring des applications IA Chéries.

© 2025 Fahed Mlaiel - Propriété intellectuelle exclusive
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from collections import defaultdict, Counter
import gzip

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Niveaux de log standardisés"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogSource(Enum):
    """Sources de logs"""
    APPLICATION = "application"
    SYSTEM = "system"
    DATABASE = "database"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"

@dataclass
class StructuredLogEntry:
    """Entrée de log structurée"""
    timestamp: datetime
    level: LogLevel
    source: LogSource
    service: str
    message: str
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    creator_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    context: Dict[str, Any] = field(default_factory=dict)
    fingerprint: Optional[str] = None

@dataclass
class LogPattern:
    """Pattern de log détecté"""
    pattern_id: str
    pattern_regex: str
    description: str
    severity: str
    occurrence_count: int
    first_seen: datetime
    last_seen: datetime
    services: Set[str] = field(default_factory=set)
    sample_messages: List[str] = field(default_factory=list)

@dataclass
class LogAnalysisResult:
    """Résultat d'analyse de logs"""
    analysis_id: str
    time_range: tuple[datetime, datetime]
    total_entries: int
    entries_by_level: Dict[LogLevel, int]
    entries_by_service: Dict[str, int]
    detected_patterns: List[LogPattern]
    anomalies: List[Dict[str, Any]]
    error_trends: Dict[str, List[tuple[datetime, int]]]
    recommendations: List[str]
    correlation_insights: Dict[str, Any]

class StructuredLoggingFramework:
    """Framework de logging structuré enterprise"""
    
    def __init__(self):
        self.log_buffer: List[StructuredLogEntry] = []
        self.structured_formatters: Dict[str, Any] = {}
        self.correlation_tracker: Dict[str, List[str]] = defaultdict(list)
        logger.info("📝 Structured Logging Framework initialisé")
    
    def create_structured_entry(
        self,
        message: str,
        level: LogLevel,
        source: LogSource,
        service: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Crée une entrée de log structurée"""
        
        entry = StructuredLogEntry(
            timestamp=datetime.now(),
            level=level,
            source=source,
            service=service,
            message=message,
            correlation_id=correlation_id,
            trace_id=trace_id,
            context=context or {}
        )
        
        # Génération fingerprint pour déduplication
        entry.fingerprint = self._generate_fingerprint(entry)
        
        # Ajout à la corrélation
        if correlation_id:
            self.correlation_tracker[correlation_id].append(entry.fingerprint)
        
        # Tags automatiques basés sur le contenu
        entry.tags = self._extract_auto_tags(message, context or {})
        
        self.log_buffer.append(entry)
        
        # Nettoyage automatique du buffer
        if len(self.log_buffer) > 100000:
            self.log_buffer = self.log_buffer[-50000:]
        
        return entry
    
    def _generate_fingerprint(self, entry: StructuredLogEntry) -> str:
        """Génère une empreinte unique pour l'entrée"""
        # Normalisation du message pour grouper les erreurs similaires
        normalized_message = re.sub(r'\d+', 'N', entry.message)
        normalized_message = re.sub(r'[0-9a-f-]{36}', 'UUID', normalized_message)
        
        fingerprint_data = f"{entry.service}:{entry.level.value}:{normalized_message}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
    
    def _extract_auto_tags(self, message: str, context: Dict[str, Any]) -> Set[str]:
        """Extrait automatiquement des tags du message et contexte"""
        tags = set()
        
        # Tags basés sur mots-clés
        if any(word in message.lower() for word in ['error', 'exception', 'failed', 'timeout']):
            tags.add('error_related')
        
        if any(word in message.lower() for word in ['slow', 'performance', 'latency']):
            tags.add('performance_related')
        
        if any(word in message.lower() for word in ['security', 'auth', 'permission', 'unauthorized']):
            tags.add('security_related')
        
        if any(word in message.lower() for word in ['creator', 'content', 'upload']):
            tags.add('creator_activity')
        
        # Tags basés sur contexte
        if 'user_id' in context:
            tags.add('user_activity')
        
        if 'api_endpoint' in context:
            tags.add('api_call')
        
        return tags
    
    def format_json_log(self, entry: StructuredLogEntry) -> str:
        """Formate l'entrée en JSON structuré"""
        log_dict = {
            'timestamp': entry.timestamp.isoformat(),
            'level': entry.level.value,
            'source': entry.source.value,
            'service': entry.service,
            'message': entry.message,
            'fingerprint': entry.fingerprint,
            'tags': list(entry.tags)
        }
        
        # Ajout des IDs de corrélation s'ils existent
        for field in ['correlation_id', 'trace_id', 'span_id', 'session_id', 'user_id', 'creator_id']:
            value = getattr(entry, field)
            if value:
                log_dict[field] = value
        
        # Ajout métadonnées et contexte
        if entry.metadata:
            log_dict['metadata'] = entry.metadata
        
        if entry.context:
            log_dict['context'] = entry.context
        
        return json.dumps(log_dict, ensure_ascii=False)

class LogCorrelationEngine:
    """Moteur de corrélation de logs"""
    
    def __init__(self):
        self.correlation_cache: Dict[str, List[StructuredLogEntry]] = {}
        self.session_logs: Dict[str, List[StructuredLogEntry]] = defaultdict(list)
        self.trace_logs: Dict[str, List[StructuredLogEntry]] = defaultdict(list)
        logger.info("🔗 Log Correlation Engine initialisé")
    
    async def correlate_logs_by_trace(
        self,
        trace_id: str,
        time_window: timedelta = timedelta(minutes=10)
    ) -> List[StructuredLogEntry]:
        """Corrèle les logs par trace ID"""
        
        correlated_logs = []
        cutoff_time = datetime.now() - time_window
        
        # Recherche dans le cache de trace
        if trace_id in self.trace_logs:
            correlated_logs.extend([
                log for log in self.trace_logs[trace_id]
                if log.timestamp > cutoff_time
            ])
        
        # Tri chronologique
        correlated_logs.sort(key=lambda x: x.timestamp)
        
        logger.info(f"🔗 {len(correlated_logs)} logs corrélés pour trace {trace_id[:8]}")
        return correlated_logs
    
    async def correlate_logs_by_session(
        self,
        session_id: str,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[StructuredLogEntry]:
        """Corrèle les logs par session utilisateur"""
        
        correlated_logs = []
        cutoff_time = datetime.now() - time_window
        
        if session_id in self.session_logs:
            correlated_logs.extend([
                log for log in self.session_logs[session_id]
                if log.timestamp > cutoff_time
            ])
        
        correlated_logs.sort(key=lambda x: x.timestamp)
        
        logger.info(f"🔗 {len(correlated_logs)} logs corrélés pour session {session_id[:8]}")
        return correlated_logs
    
    async def add_log_to_correlation(self, log_entry: StructuredLogEntry):
        """Ajoute un log aux structures de corrélation"""
        
        # Corrélation par trace
        if log_entry.trace_id:
            self.trace_logs[log_entry.trace_id].append(log_entry)
        
        # Corrélation par session
        if log_entry.session_id:
            self.session_logs[log_entry.session_id].append(log_entry)
        
        # Nettoyage automatique des anciens logs
        await self._cleanup_old_correlations()
    
    async def _cleanup_old_correlations(self):
        """Nettoie les corrélations anciennes"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Nettoyage traces
        for trace_id in list(self.trace_logs.keys()):
            self.trace_logs[trace_id] = [
                log for log in self.trace_logs[trace_id]
                if log.timestamp > cutoff_time
            ]
            if not self.trace_logs[trace_id]:
                del self.trace_logs[trace_id]
        
        # Nettoyage sessions
        for session_id in list(self.session_logs.keys()):
            self.session_logs[session_id] = [
                log for log in self.session_logs[session_id]
                if log.timestamp > cutoff_time
            ]
            if not self.session_logs[session_id]:
                del self.session_logs[session_id]

class IntelligentLogAnalysis:
    """Analyse intelligente de logs avec ML"""
    
    def __init__(self):
        self.known_patterns: Dict[str, LogPattern] = {}
        self.error_signatures: Dict[str, int] = Counter()
        self.anomaly_baseline: Dict[str, Dict[str, float]] = {}
        logger.info("🧠 Intelligent Log Analysis initialisé")
    
    async def analyze_log_patterns(
        self,
        logs: List[StructuredLogEntry],
        time_window: timedelta = timedelta(hours=1)
    ) -> List[LogPattern]:
        """Analyse et détecte les patterns dans les logs"""
        
        patterns_found = []
        message_groups = defaultdict(list)
        
        # Groupement des messages par fingerprint
        for log in logs:
            if log.fingerprint:
                message_groups[log.fingerprint].append(log)
        
        # Détection de nouveaux patterns
        for fingerprint, group_logs in message_groups.items():
            if len(group_logs) < 3:  # Seuil minimum pour un pattern
                continue
            
            # Création ou mise à jour du pattern
            if fingerprint in self.known_patterns:
                pattern = self.known_patterns[fingerprint]
                pattern.occurrence_count += len(group_logs)
                pattern.last_seen = max(log.timestamp for log in group_logs)
                pattern.services.update(log.service for log in group_logs)
            else:
                # Nouveau pattern détecté
                sample_messages = [log.message for log in group_logs[:3]]
                pattern = LogPattern(
                    pattern_id=fingerprint,
                    pattern_pattern=self._generate_pattern_regex(group_logs[0].message),
                    description=self._generate_pattern_description(group_logs),
                    severity=self._calculate_pattern_severity(group_logs),
                    occurrence_count=len(group_logs),
                    first_seen=min(log.timestamp for log in group_logs),
                    last_seen=max(log.timestamp for log in group_logs),
                    services=set(log.service for log in group_logs),
                    sample_messages=sample_messages
                )
                self.known_patterns[fingerprint] = pattern
            
            patterns_found.append(self.known_patterns[fingerprint])
        
        # Tri par sévérité et fréquence
        patterns_found.sort(
            key=lambda p: (p.severity == 'critical', p.occurrence_count),
            reverse=True
        )
        
        logger.info(f"🧠 {len(patterns_found)} patterns détectés dans {len(logs)} logs")
        return patterns_found
    
    def _generate_pattern_regex(self, sample_message: str) -> str:
        """Génère une regex pour matcher le pattern"""
        # Normalisation basique - remplace nombres et UUIDs
        pattern = re.escape(sample_message)
        pattern = re.sub(r'\\d+', r'\\d+', pattern)
        pattern = re.sub(r'[0-9a-f\\-]{36}', r'[0-9a-f\\-]{36}', pattern)
        return pattern
    
    def _generate_pattern_description(self, logs: List[StructuredLogEntry]) -> str:
        """Génère une description du pattern"""
        service_names = set(log.service for log in logs)
        level = logs[0].level.value
        
        if len(service_names) == 1:
            return f"{level} récurrent dans {list(service_names)[0]}"
        else:
            return f"{level} récurrent dans {len(service_names)} services"
    
    def _calculate_pattern_severity(self, logs: List[StructuredLogEntry]) -> str:
        """Calcule la sévérité du pattern"""
        level_counts = Counter(log.level for log in logs)
        
        if LogLevel.CRITICAL in level_counts:
            return 'critical'
        elif LogLevel.ERROR in level_counts:
            return 'high'
        elif LogLevel.WARNING in level_counts:
            return 'medium'
        else:
            return 'low'
    
    async def detect_anomalies(
        self,
        logs: List[StructuredLogEntry],
        baseline_window: timedelta = timedelta(days=7)
    ) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans les patterns de logs"""
        
        anomalies = []
        current_time = datetime.now()
        
        # Analyse volume par service
        service_counts = Counter(log.service for log in logs)
        
        for service, count in service_counts.items():
            if service not in self.anomaly_baseline:
                self.anomaly_baseline[service] = {'avg_volume': count, 'std_volume': 0}
                continue
            
            baseline = self.anomaly_baseline[service]
            
            # Détection volume anormal (> 3 écarts-types)
            if baseline['std_volume'] > 0:
                z_score = abs(count - baseline['avg_volume']) / baseline['std_volume']
                if z_score > 3:
                    anomalies.append({
                        'type': 'volume_anomaly',
                        'service': service,
                        'current_volume': count,
                        'expected_volume': baseline['avg_volume'],
                        'z_score': z_score,
                        'severity': 'high' if z_score > 5 else 'medium'
                    })
        
        # Analyse taux d'erreur
        error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        error_rate = len(error_logs) / len(logs) if logs else 0
        
        if error_rate > 0.1:  # Seuil 10%
            anomalies.append({
                'type': 'high_error_rate',
                'error_rate': error_rate,
                'total_errors': len(error_logs),
                'total_logs': len(logs),
                'severity': 'critical' if error_rate > 0.2 else 'high'
            })
        
        logger.info(f"🚨 {len(anomalies)} anomalies détectées")
        return anomalies

class LogRetentionManagement:
    """Gestion de la rétention des logs"""
    
    def __init__(self):
        self.retention_policies: Dict[LogSource, timedelta] = {
            LogSource.SECURITY: timedelta(days=365),    # 1 an pour sécurité
            LogSource.AUDIT: timedelta(days=2555),      # 7 ans pour audit
            LogSource.APPLICATION: timedelta(days=90),   # 3 mois pour application
            LogSource.PERFORMANCE: timedelta(days=30),   # 1 mois pour performance
            LogSource.SYSTEM: timedelta(days=60),       # 2 mois pour système
            LogSource.DATABASE: timedelta(days=180)     # 6 mois pour base de données
        }
        self.archived_logs: Dict[str, bytes] = {}
        logger.info("📦 Log Retention Management initialisé")
    
    async def apply_retention_policy(
        self,
        logs: List[StructuredLogEntry]
    ) -> tuple[List[StructuredLogEntry], List[StructuredLogEntry]]:
        """Applique les politiques de rétention"""
        
        active_logs = []
        logs_to_archive = []
        current_time = datetime.now()
        
        for log in logs:
            retention_period = self.retention_policies.get(
                log.source,
                timedelta(days=30)  # Défaut
            )
            
            log_age = current_time - log.timestamp
            
            if log_age <= retention_period:
                active_logs.append(log)
            else:
                logs_to_archive.append(log)
        
        # Archivage des logs expirés
        if logs_to_archive:
            await self._archive_logs(logs_to_archive)
        
        logger.info(f"📦 Rétention appliquée: {len(active_logs)} actifs, {len(logs_to_archive)} archivés")
        return active_logs, logs_to_archive
    
    async def _archive_logs(self, logs: List[StructuredLogEntry]):
        """Archive les logs expirés avec compression"""
        
        # Groupement par mois pour archivage
        monthly_groups = defaultdict(list)
        
        for log in logs:
            month_key = log.timestamp.strftime('%Y-%m')
            monthly_groups[month_key].append(log)
        
        # Compression et stockage
        for month_key, month_logs in monthly_groups.items():
            archive_data = []
            
            for log in month_logs:
                log_dict = {
                    'timestamp': log.timestamp.isoformat(),
                    'level': log.level.value,
                    'source': log.source.value,
                    'service': log.service,
                    'message': log.message,
                    'fingerprint': log.fingerprint
                }
                archive_data.append(log_dict)
            
            # Compression gzip
            json_data = json.dumps(archive_data, ensure_ascii=False)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            archive_key = f"logs_archive_{month_key}"
            self.archived_logs[archive_key] = compressed_data
            
            logger.info(f"📦 Archivé {len(month_logs)} logs pour {month_key}")

class LogAggregation:
    """
    📝 LOG AGGREGATION ENGINE ENTERPRISE
    
    Infrastructure robuste d'agrégation de logs avec:
    - Structured logging framework complet
    - Log correlation engine intelligent
    - Intelligent log analysis avec ML
    - Log pattern detection avancé
    - Error pattern recognition automatique
    - Log retention management enterprise
    - Log search optimization
    """
    
    def __init__(self):
        self.structured_framework = StructuredLoggingFramework()
        self.correlation_engine = LogCorrelationEngine()
        self.intelligent_analysis = IntelligentLogAnalysis()
        self.retention_manager = LogRetentionManagement()
        self.log_storage: List[StructuredLogEntry] = []
        self.search_index: Dict[str, List[int]] = defaultdict(list)
        logger.info("📝 Log Aggregation Engine enterprise initialisé")
    
    async def ingest_log(
        self,
        message: str,
        level: LogLevel,
        source: LogSource,
        service: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> StructuredLogEntry:
        """Ingère un nouveau log dans le système"""
        
        # Création entrée structurée
        log_entry = self.structured_framework.create_structured_entry(
            message=message,
            level=level,
            source=source,
            service=service,
            context=context,
            correlation_id=correlation_id,
            trace_id=trace_id
        )
        
        # Ajout au stockage
        self.log_storage.append(log_entry)
        
        # Ajout à la corrélation
        await self.correlation_engine.add_log_to_correlation(log_entry)
        
        # Indexation pour recherche
        await self._index_log_for_search(log_entry, len(self.log_storage) - 1)
        
        # Nettoyage automatique si trop de logs
        if len(self.log_storage) > 1000000:  # 1M logs max en mémoire
            await self._cleanup_old_logs()
        
        logger.debug(f"📝 Log ingéré: {service} - {level.value}")
        return log_entry
    
    async def analyze_logs(
        self,
        time_window: timedelta = timedelta(hours=1),
        service_filter: Optional[str] = None
    ) -> LogAnalysisResult:
        """Analyse complète des logs sur une période"""
        
        end_time = datetime.now()
        start_time = end_time - time_window
        
        # Filtrage des logs par période et service
        filtered_logs = [
            log for log in self.log_storage
            if start_time <= log.timestamp <= end_time
            and (not service_filter or log.service == service_filter)
        ]
        
        if not filtered_logs:
            return LogAnalysisResult(
                analysis_id=f"analysis_{int(datetime.now().timestamp())}",
                time_range=(start_time, end_time),
                total_entries=0,
                entries_by_level={},
                entries_by_service={},
                detected_patterns=[],
                anomalies=[],
                error_trends={},
                recommendations=[],
                correlation_insights={}
            )
        
        # Analyse des patterns
        patterns = await self.intelligent_analysis.analyze_log_patterns(filtered_logs)
        
        # Détection d'anomalies
        anomalies = await self.intelligent_analysis.detect_anomalies(filtered_logs)
        
        # Statistiques par niveau
        entries_by_level = Counter(log.level for log in filtered_logs)
        
        # Statistiques par service
        entries_by_service = Counter(log.service for log in filtered_logs)
        
        # Tendances d'erreurs
        error_trends = await self._calculate_error_trends(filtered_logs, time_window)
        
        # Insights de corrélation
        correlation_insights = await self._generate_correlation_insights(filtered_logs)
        
        # Recommandations
        recommendations = await self._generate_recommendations(
            patterns, anomalies, entries_by_level
        )
        
        analysis_result = LogAnalysisResult(
            analysis_id=f"analysis_{int(datetime.now().timestamp())}",
            time_range=(start_time, end_time),
            total_entries=len(filtered_logs),
            entries_by_level=entries_by_level,
            entries_by_service=entries_by_service,
            detected_patterns=patterns,
            anomalies=anomalies,
            error_trends=error_trends,
            recommendations=recommendations,
            correlation_insights=correlation_insights
        )
        
        logger.info(f"📊 Analyse logs complétée: {len(filtered_logs)} entrées analysées")
        return analysis_result
    
    async def search_logs(
        self,
        query: str,
        limit: int = 100,
        service_filter: Optional[str] = None,
        level_filter: Optional[LogLevel] = None,
        time_range: Optional[tuple[datetime, datetime]] = None
    ) -> List[StructuredLogEntry]:
        """Recherche optimisée dans les logs"""
        
        results = []
        query_lower = query.lower()
        
        for i, log in enumerate(self.log_storage):
            # Filtres
            if service_filter and log.service != service_filter:
                continue
            
            if level_filter and log.level != level_filter:
                continue
            
            if time_range:
                start_time, end_time = time_range
                if not (start_time <= log.timestamp <= end_time):
                    continue
            
            # Recherche textuelle
            if (query_lower in log.message.lower() or
                query_lower in log.service.lower() or
                any(query_lower in tag.lower() for tag in log.tags)):
                results.append(log)
                
                if len(results) >= limit:
                    break
        
        logger.info(f"🔍 Recherche '{query}': {len(results)} résultats trouvés")
        return results
    
    async def get_correlated_logs(
        self,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[StructuredLogEntry]:
        """Récupère les logs corrélés"""
        
        if trace_id:
            return await self.correlation_engine.correlate_logs_by_trace(trace_id)
        elif session_id:
            return await self.correlation_engine.correlate_logs_by_session(session_id)
        else:
            return []
    
    async def _index_log_for_search(self, log_entry: StructuredLogEntry, index: int):
        """Indexe un log pour la recherche rapide"""
        
        # Indexation par mots-clés du message
        words = re.findall(r'\w+', log_entry.message.lower())
        for word in words:
            if len(word) > 2:  # Ignorer mots très courts
                self.search_index[word].append(index)
        
        # Indexation par service
        self.search_index[f"service:{log_entry.service}"].append(index)
        
        # Indexation par niveau
        self.search_index[f"level:{log_entry.level.value}"].append(index)
        
        # Indexation par tags
        for tag in log_entry.tags:
            self.search_index[f"tag:{tag}"].append(index)
    
    async def _cleanup_old_logs(self):
        """Nettoie les anciens logs selon les politiques de rétention"""
        
        active_logs, archived_logs = await self.retention_manager.apply_retention_policy(
            self.log_storage
        )
        
        # Remplacement du stockage par les logs actifs
        self.log_storage = active_logs
        
        # Reconstruction de l'index de recherche
        self.search_index.clear()
        for i, log in enumerate(self.log_storage):
            await self._index_log_for_search(log, i)
        
        logger.info(f"🧹 Nettoyage effectué: {len(active_logs)} logs conservés")
    
    async def _calculate_error_trends(
        self,
        logs: List[StructuredLogEntry],
        time_window: timedelta
    ) -> Dict[str, List[tuple[datetime, int]]]:
        """Calcule les tendances d'erreurs par service"""
        
        trends = {}
        error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        
        # Groupement par service et par heure
        service_hourly_errors = defaultdict(lambda: defaultdict(int))
        
        for log in error_logs:
            hour_key = log.timestamp.replace(minute=0, second=0, microsecond=0)
            service_hourly_errors[log.service][hour_key] += 1
        
        # Conversion en format de tendance
        for service, hourly_counts in service_hourly_errors.items():
            trends[service] = [(hour, count) for hour, count in sorted(hourly_counts.items())]
        
        return trends
    
    async def _generate_correlation_insights(
        self,
        logs: List[StructuredLogEntry]
    ) -> Dict[str, Any]:
        """Génère des insights de corrélation"""
        
        insights = {}
        
        # Corrélations trace_id
        trace_correlations = defaultdict(list)
        for log in logs:
            if log.trace_id:
                trace_correlations[log.trace_id].append(log)
        
        insights['traces_with_multiple_services'] = len([
            trace_logs for trace_logs in trace_correlations.values()
            if len(set(log.service for log in trace_logs)) > 1
        ])
        
        # Corrélations session
        session_correlations = defaultdict(list)
        for log in logs:
            if log.session_id:
                session_correlations[log.session_id].append(log)
        
        insights['active_sessions'] = len(session_correlations)
        
        # Services les plus actifs
        service_activity = Counter(log.service for log in logs)
        insights['most_active_services'] = service_activity.most_common(5)
        
        return insights
    
    async def _generate_recommendations(
        self,
        patterns: List[LogPattern],
        anomalies: List[Dict[str, Any]],
        entries_by_level: Counter
    ) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        
        recommendations = []
        
        # Recommandations basées sur les patterns
        critical_patterns = [p for p in patterns if p.severity == 'critical']
        if critical_patterns:
            recommendations.append(
                f"🚨 {len(critical_patterns)} patterns critiques détectés - "
                "Investigation immédiate recommandée"
            )
        
        # Recommandations basées sur les anomalies
        volume_anomalies = [a for a in anomalies if a['type'] == 'volume_anomaly']
        if volume_anomalies:
            recommendations.append(
                f"📈 {len(volume_anomalies)} anomalies de volume - "
                "Vérifier la charge système"
            )
        
        # Recommandations basées sur les niveaux
        error_count = entries_by_level.get(LogLevel.ERROR, 0)
        critical_count = entries_by_level.get(LogLevel.CRITICAL, 0)
        total_count = sum(entries_by_level.values())
        
        if total_count > 0:
            error_rate = (error_count + critical_count) / total_count
            if error_rate > 0.1:
                recommendations.append(
                    f"⚠️ Taux d'erreur élevé ({error_rate:.1%}) - "
                    "Audit de la stabilité système recommandé"
                )
        
        # Recommandation performance
        if total_count > 10000:
            recommendations.append(
                "⚡ Volume de logs élevé - "
                "Considérer l'optimisation du niveau de logging"
            )
        
        return recommendations

# Instance globale pour import facilité
_log_aggregation = LogAggregation()

async def get_log_aggregation() -> LogAggregation:
    """Retourne l'instance du moteur d'agrégation de logs"""
    return _log_aggregation

async def log_structured(
    message: str,
    level: LogLevel,
    source: LogSource,
    service: str,
    context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    trace_id: Optional[str] = None
) -> StructuredLogEntry:
    """Helper pour logger de manière structurée"""
    return await _log_aggregation.ingest_log(
        message, level, source, service, context, correlation_id, trace_id
    )

# Export des classes principales
__all__ = [
    'LogAggregation',
    'StructuredLogEntry',
    'LogPattern',
    'LogAnalysisResult',
    'LogLevel',
    'LogSource',
    'get_log_aggregation',
    'log_structured'
]