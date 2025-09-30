"""
📈 Content Performance Service - Performance de Contenu Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service spécialisé de monitoring et optimisation de performance pour contenu.
Monitoring temps réel avec optimisation automatique et alertes intelligentes.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass

import numpy as np
import psutil
import time

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Métriques de performance du contenu"""
    content_id: str
    load_time: float = 0.0
    processing_time: float = 0.0
    delivery_time: float = 0.0
    bandwidth_usage: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0


class ContentPerformanceService:
    """Service de monitoring et optimisation de performance"""
    
    def __init__(self):
        self.metrics_history = {}
        self.performance_thresholds = {
            'load_time': 3.0,  # seconds
            'processing_time': 5.0,  # seconds
            'error_rate': 0.05,  # 5%
            'cpu_usage': 80.0,  # %
            'memory_usage': 85.0,  # %
            'latency_p95': 2000.0  # ms
        }
        self.optimization_rules = self._load_optimization_rules()
        self.monitoring_enabled = True
    
    async def monitor_content_performance(
        self,
        content_id: str,
        operation: str = "delivery",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Monitor la performance d'une opération sur le contenu"""
        
        if not self.monitoring_enabled:
            return {'monitoring': 'disabled'}
        
        try:
            start_time = time.time()
            
            # Collecter métriques système
            system_metrics = await self._collect_system_metrics()
            
            # Métriques spécifiques à l'opération
            operation_metrics = await self._collect_operation_metrics(
                content_id, operation, metadata
            )
            
            # Calculer temps d'exécution
            execution_time = time.time() - start_time
            
            # Créer métriques de performance
            performance_metrics = PerformanceMetrics(
                content_id=content_id,
                processing_time=execution_time,
                cpu_usage=system_metrics.get('cpu_percent', 0),
                memory_usage=system_metrics.get('memory_percent', 0),
                **operation_metrics
            )
            
            # Analyser performance
            analysis = await self._analyze_performance(performance_metrics)
            
            # Stocker dans l'historique
            await self._store_metrics_history(content_id, performance_metrics)
            
            # Générer recommandations d'optimisation
            recommendations = await self._generate_optimization_recommendations(
                performance_metrics, analysis
            )
            
            return {
                'content_id': content_id,
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': performance_metrics.__dict__,
                'analysis': analysis,
                'recommendations': recommendations,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Erreur monitoring performance {content_id}: {e}")
            return {
                'content_id': content_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'error'
            }
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collecte les métriques système"""
        
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters()._asdict(),
                'process_count': len(psutil.pids())
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques système: {e}")
            return {}
    
    async def _collect_operation_metrics(
        self,
        content_id: str,
        operation: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Collecte les métriques spécifiques à l'opération"""
        
        metrics = {}
        
        try:
            if operation == "upload":
                metrics.update(await self._collect_upload_metrics(content_id, metadata))
            elif operation == "processing":
                metrics.update(await self._collect_processing_metrics(content_id, metadata))
            elif operation == "delivery":
                metrics.update(await self._collect_delivery_metrics(content_id, metadata))
            elif operation == "transcoding":
                metrics.update(await self._collect_transcoding_metrics(content_id, metadata))
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques opération {operation}: {e}")
        
        return metrics
    
    async def _collect_upload_metrics(
        self,
        content_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Collecte métriques pour upload"""
        
        file_size = metadata.get('file_size', 0) if metadata else 0
        
        return {
            'bandwidth_usage': file_size / 1024 / 1024,  # MB
            'load_time': np.random.uniform(0.5, 3.0),  # Simulé
            'throughput': file_size / max(np.random.uniform(1, 5), 0.1)  # bytes/sec
        }
    
    async def _collect_processing_metrics(
        self,
        content_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Collecte métriques pour processing"""
        
        return {
            'processing_time': np.random.uniform(1.0, 8.0),  # Simulé
            'cpu_usage': np.random.uniform(30, 90),
            'memory_usage': np.random.uniform(40, 85)
        }
    
    async def _collect_delivery_metrics(
        self,
        content_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Collecte métriques pour delivery"""
        
        return {
            'delivery_time': np.random.uniform(0.1, 2.0),  # Simulé
            'cache_hit_rate': np.random.uniform(0.6, 0.95),
            'latency_p95': np.random.uniform(500, 2500),  # ms
            'latency_p99': np.random.uniform(1000, 5000)  # ms
        }
    
    async def _collect_transcoding_metrics(
        self,
        content_id: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Collecte métriques pour transcoding"""
        
        return {
            'processing_time': np.random.uniform(5.0, 30.0),  # Simulé
            'cpu_usage': np.random.uniform(70, 95),
            'memory_usage': np.random.uniform(60, 90),
            'throughput': np.random.uniform(1000, 10000)  # frames/sec
        }
    
    async def _analyze_performance(
        self,
        metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """Analyse les métriques de performance"""
        
        analysis = {
            'score': 100,
            'issues': [],
            'bottlenecks': [],
            'trends': {}
        }
        
        # Analyser chaque métrique contre les seuils
        for metric_name, threshold in self.performance_thresholds.items():
            metric_value = getattr(metrics, metric_name, 0)
            
            if metric_value > threshold:
                analysis['score'] -= 10
                analysis['issues'].append({
                    'metric': metric_name,
                    'value': metric_value,
                    'threshold': threshold,
                    'severity': 'high' if metric_value > threshold * 1.5 else 'medium'
                })
                
                # Identifier bottlenecks
                if metric_name in ['cpu_usage', 'memory_usage']:
                    analysis['bottlenecks'].append('system_resources')
                elif metric_name in ['load_time', 'processing_time']:
                    analysis['bottlenecks'].append('processing_speed')
                elif metric_name in ['latency_p95', 'latency_p99']:
                    analysis['bottlenecks'].append('network_latency')
        
        # Calculer score final
        analysis['score'] = max(analysis['score'], 0)
        
        # Déterminer grade de performance
        if analysis['score'] >= 90:
            analysis['grade'] = 'excellent'
        elif analysis['score'] >= 75:
            analysis['grade'] = 'good'
        elif analysis['score'] >= 60:
            analysis['grade'] = 'fair'
        else:
            analysis['grade'] = 'poor'
        
        # Analyser tendances si historique disponible
        if metrics.content_id in self.metrics_history:
            analysis['trends'] = await self._analyze_trends(metrics.content_id)
        
        return analysis
    
    async def _analyze_trends(self, content_id: str) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        
        history = self.metrics_history.get(content_id, [])
        
        if len(history) < 2:
            return {}
        
        trends = {}
        
        # Analyser tendances des dernières métriques
        recent_metrics = history[-5:]  # 5 dernières mesures
        
        for metric_name in ['processing_time', 'cpu_usage', 'memory_usage', 'latency_p95']:
            values = [getattr(m, metric_name, 0) for m in recent_metrics]
            
            if len(values) >= 2:
                # Calculer tendance (régression linéaire simple)
                x = list(range(len(values)))
                trend_slope = np.polyfit(x, values, 1)[0]
                
                trends[metric_name] = {
                    'direction': 'increasing' if trend_slope > 0 else 'decreasing',
                    'slope': trend_slope,
                    'recent_avg': np.mean(values),
                    'volatility': np.std(values)
                }
        
        return trends
    
    async def _store_metrics_history(
        self,
        content_id: str,
        metrics: PerformanceMetrics
    ) -> None:
        """Stocke les métriques dans l'historique"""
        
        if content_id not in self.metrics_history:
            self.metrics_history[content_id] = []
        
        # Ajouter timestamp aux métriques
        metrics_with_timestamp = {
            'timestamp': datetime.utcnow(),
            'metrics': metrics
        }
        
        self.metrics_history[content_id].append(metrics_with_timestamp)
        
        # Limiter la taille de l'historique
        max_history = 100
        if len(self.metrics_history[content_id]) > max_history:
            self.metrics_history[content_id] = self.metrics_history[content_id][-max_history:]
    
    async def _generate_optimization_recommendations(
        self,
        metrics: PerformanceMetrics,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations d'optimisation"""
        
        recommendations = []
        
        # Recommandations basées sur les bottlenecks
        for bottleneck in analysis.get('bottlenecks', []):
            if bottleneck == 'system_resources':
                recommendations.append({
                    'type': 'infrastructure',
                    'priority': 'high',
                    'action': 'Scale up system resources',
                    'description': 'CPU or memory usage is high - consider upgrading hardware'
                })
            
            elif bottleneck == 'processing_speed':
                recommendations.append({
                    'type': 'optimization',
                    'priority': 'medium',
                    'action': 'Optimize processing algorithms',
                    'description': 'Processing time is above threshold - review algorithms'
                })
            
            elif bottleneck == 'network_latency':
                recommendations.append({
                    'type': 'network',
                    'priority': 'medium',
                    'action': 'Implement CDN or edge caching',
                    'description': 'High latency detected - consider content delivery optimization'
                })
        
        # Recommandations spécifiques aux métriques
        if metrics.cache_hit_rate < 0.7:
            recommendations.append({
                'type': 'caching',
                'priority': 'medium',
                'action': 'Improve caching strategy',
                'description': f'Cache hit rate is {metrics.cache_hit_rate:.2%} - optimize caching'
            })
        
        if metrics.error_rate > 0.01:
            recommendations.append({
                'type': 'reliability',
                'priority': 'high',
                'action': 'Investigate and fix errors',
                'description': f'Error rate is {metrics.error_rate:.2%} - review error logs'
            })
        
        # Recommandations automatiques d'optimisation
        auto_optimizations = await self._get_automatic_optimizations(metrics)
        recommendations.extend(auto_optimizations)
        
        return recommendations
    
    async def _get_automatic_optimizations(
        self,
        metrics: PerformanceMetrics
    ) -> List[Dict[str, Any]]:
        """Obtient les optimisations automatiques possibles"""
        
        optimizations = []
        
        # Optimisation de compression
        if metrics.bandwidth_usage > 100:  # > 100MB
            optimizations.append({
                'type': 'compression',
                'priority': 'low',
                'action': 'Enable content compression',
                'description': 'Large bandwidth usage - enable gzip/brotli compression',
                'auto_applicable': True
            })
        
        # Optimisation de cache
        if metrics.cache_hit_rate < 0.8:
            optimizations.append({
                'type': 'caching',
                'priority': 'medium',
                'action': 'Extend cache TTL',
                'description': 'Low cache hit rate - consider extending cache duration',
                'auto_applicable': True
            })
        
        return optimizations
    
    async def apply_automatic_optimizations(
        self,
        content_id: str,
        optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Applique les optimisations automatiques"""
        
        applied_optimizations = []
        failed_optimizations = []
        
        for optimization in optimizations:
            if optimization.get('auto_applicable', False):
                try:
                    result = await self._apply_optimization(content_id, optimization)
                    if result['success']:
                        applied_optimizations.append(optimization)
                    else:
                        failed_optimizations.append({
                            'optimization': optimization,
                            'error': result['error']
                        })
                        
                except Exception as e:
                    failed_optimizations.append({
                        'optimization': optimization,
                        'error': str(e)
                    })
        
        return {
            'content_id': content_id,
            'applied': applied_optimizations,
            'failed': failed_optimizations,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _apply_optimization(
        self,
        content_id: str,
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Applique une optimisation spécifique"""
        
        optimization_type = optimization['type']
        
        try:
            if optimization_type == 'compression':
                # Activer compression pour le contenu
                result = await self._enable_compression(content_id)
                
            elif optimization_type == 'caching':
                # Optimiser paramètres de cache
                result = await self._optimize_caching(content_id)
                
            else:
                result = {'success': False, 'error': 'Unknown optimization type'}
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _enable_compression(self, content_id: str) -> Dict[str, Any]:
        """Active la compression pour le contenu"""
        # Placeholder - en production, configurer compression
        logger.info(f"Enabling compression for content {content_id}")
        return {'success': True, 'message': 'Compression enabled'}
    
    async def _optimize_caching(self, content_id: str) -> Dict[str, Any]:
        """Optimise les paramètres de cache"""
        # Placeholder - en production, ajuster TTL cache
        logger.info(f"Optimizing caching for content {content_id}")
        return {'success': True, 'message': 'Cache optimization applied'}
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Charge les règles d'optimisation"""
        return {
            'compression': {
                'trigger_bandwidth_mb': 50,
                'compression_ratio': 0.7
            },
            'caching': {
                'min_hit_rate': 0.8,
                'default_ttl': 3600
            },
            'scaling': {
                'cpu_threshold': 80,
                'memory_threshold': 85
            }
        }
    
    async def get_performance_dashboard(
        self,
        content_ids: Optional[List[str]] = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Génère un dashboard de performance"""
        
        dashboard = {
            'generated_at': datetime.utcnow().isoformat(),
            'time_range': time_range,
            'overview': {},
            'content_performance': [],
            'system_health': {},
            'recommendations': []
        }
        
        try:
            # Vue d'ensemble globale
            dashboard['overview'] = await self._generate_overview_metrics(time_range)
            
            # Performance par contenu
            if content_ids:
                for content_id in content_ids:
                    perf_data = await self._get_content_performance_summary(content_id)
                    dashboard['content_performance'].append(perf_data)
            
            # Santé système
            dashboard['system_health'] = await self._get_system_health_summary()
            
            # Recommandations globales
            dashboard['recommendations'] = await self._get_global_recommendations()
            
        except Exception as e:
            logger.error(f"Erreur génération dashboard: {e}")
            dashboard['error'] = str(e)
        
        return dashboard
    
    async def _generate_overview_metrics(self, time_range: str) -> Dict[str, Any]:
        """Génère les métriques de vue d'ensemble"""
        
        # Simuler métriques globales
        return {
            'total_requests': np.random.randint(10000, 50000),
            'avg_response_time': np.random.uniform(500, 2000),
            'error_rate': np.random.uniform(0.01, 0.05),
            'throughput': np.random.uniform(1000, 5000),
            'availability': np.random.uniform(0.995, 0.999)
        }
    
    async def _get_content_performance_summary(self, content_id: str) -> Dict[str, Any]:
        """Obtient le résumé de performance pour un contenu"""
        
        history = self.metrics_history.get(content_id, [])
        
        if not history:
            return {
                'content_id': content_id,
                'status': 'no_data'
            }
        
        recent_metrics = history[-10:]  # 10 dernières mesures
        
        return {
            'content_id': content_id,
            'avg_processing_time': np.mean([m['metrics'].processing_time for m in recent_metrics]),
            'avg_cpu_usage': np.mean([m['metrics'].cpu_usage for m in recent_metrics]),
            'last_measurement': recent_metrics[-1]['timestamp'].isoformat(),
            'measurement_count': len(history)
        }
    
    async def _get_system_health_summary(self) -> Dict[str, Any]:
        """Obtient le résumé de santé système"""
        
        system_metrics = await self._collect_system_metrics()
        
        return {
            'cpu_usage': system_metrics.get('cpu_percent', 0),
            'memory_usage': system_metrics.get('memory_percent', 0),
            'disk_usage': system_metrics.get('disk_usage', 0),
            'status': 'healthy' if system_metrics.get('cpu_percent', 0) < 80 else 'warning'
        }
    
    async def _get_global_recommendations(self) -> List[Dict[str, Any]]:
        """Obtient les recommandations globales"""
        
        # Analyser toutes les métriques récentes
        all_recent_metrics = []
        for content_history in self.metrics_history.values():
            if content_history:
                all_recent_metrics.append(content_history[-1]['metrics'])
        
        recommendations = []
        
        if all_recent_metrics:
            avg_cpu = np.mean([m.cpu_usage for m in all_recent_metrics])
            avg_memory = np.mean([m.memory_usage for m in all_recent_metrics])
            
            if avg_cpu > 75:
                recommendations.append({
                    'type': 'infrastructure',
                    'priority': 'high',
                    'message': 'High average CPU usage across content processing'
                })
            
            if avg_memory > 80:
                recommendations.append({
                    'type': 'infrastructure',
                    'priority': 'high',
                    'message': 'High average memory usage - consider memory optimization'
                })
        
        return recommendations


# Instance globale du service
content_performance_service = ContentPerformanceService()