"""
Creator Metrics Configuration Module
Configuration métriques spécialisées Creator Economy - IA Chérie Platform

⚠️ CONFIDENTIEL - IA Chérie Creator Platform ⚠️
🔒 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

import os
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import logging

logger = logging.getLogger(__name__)

@dataclass
class CreatorMetricDefinition:
    """Définition d'une métrique créateur"""
    name: str
    type: str  # gauge, counter, histogram
    description: str
    labels: List[str]
    business_context: str
    thresholds: Dict[str, float]

class CreatorMetricsConfig:
    """
    Configuration métriques spécialisées Creator Economy
    
    Fonctionnalités:
    - Creator workflow metrics definition
    - Business KPI mapping configuration  
    - Custom metric exporters setup
    - Creator-specific service discovery
    - Multi-tenant metrics configuration
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "creator_metrics.yml"
        self.registry = CollectorRegistry()
        self.metrics_definitions = {}
        self.exporters = {}
        self._load_configuration()
        self._initialize_metrics()
    
    def _load_configuration(self):
        """Charge la configuration des métriques créateur"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self._process_config(config)
            else:
                self._create_default_config()
                logger.warning(f"Configuration file not found, created default: {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading creator metrics config: {e}")
            self._create_default_config()
    
    def _process_config(self, config: Dict[str, Any]):
        """Traite la configuration chargée"""
        creator_workflows = config.get('creator_workflows', {})
        business_kpis = config.get('business_kpis', {})
        service_discovery = config.get('service_discovery', {})
        
        self.workflow_metrics = self._parse_workflow_metrics(creator_workflows)
        self.business_metrics = self._parse_business_metrics(business_kpis)
        self.service_config = service_discovery
    
    def _parse_workflow_metrics(self, workflows: Dict) -> Dict[str, CreatorMetricDefinition]:
        """Parse les métriques de workflow créateur"""
        metrics = {}
        
        for workflow_name, workflow_config in workflows.items():
            for metric_name, metric_config in workflow_config.get('metrics', {}).items():
                full_name = f"ainflue_creator_{workflow_name}_{metric_name}"
                
                metrics[full_name] = CreatorMetricDefinition(
                    name=full_name,
                    type=metric_config.get('type', 'gauge'),
                    description=metric_config.get('description', ''),
                    labels=metric_config.get('labels', []),
                    business_context=metric_config.get('business_context', ''),
                    thresholds=metric_config.get('thresholds', {})
                )
        
        return metrics
    
    def _parse_business_metrics(self, business_kpis: Dict) -> Dict[str, CreatorMetricDefinition]:
        """Parse les métriques business KPI"""
        metrics = {}
        
        for kpi_category, kpi_config in business_kpis.items():
            for metric_name, metric_config in kpi_config.get('metrics', {}).items():
                full_name = f"ainflue_business_{kpi_category}_{metric_name}"
                
                metrics[full_name] = CreatorMetricDefinition(
                    name=full_name,
                    type=metric_config.get('type', 'gauge'),
                    description=metric_config.get('description', ''),
                    labels=metric_config.get('labels', []),
                    business_context=metric_config.get('business_context', ''),
                    thresholds=metric_config.get('thresholds', {})
                )
        
        return metrics
    
    def _initialize_metrics(self):
        """Initialise les métriques Prometheus"""
        for metric_name, metric_def in {**self.workflow_metrics, **self.business_metrics}.items():
            try:
                if metric_def.type == 'gauge':
                    metric = Gauge(
                        metric_def.name,
                        metric_def.description,
                        labelnames=metric_def.labels,
                        registry=self.registry
                    )
                elif metric_def.type == 'counter':
                    metric = Counter(
                        metric_def.name,
                        metric_def.description,
                        labelnames=metric_def.labels,
                        registry=self.registry
                    )
                elif metric_def.type == 'histogram':
                    metric = Histogram(
                        metric_def.name,
                        metric_def.description,
                        labelnames=metric_def.labels,
                        registry=self.registry
                    )
                
                self.exporters[metric_name] = metric
                logger.debug(f"Initialized metric: {metric_name}")
                
            except Exception as e:
                logger.error(f"Error initializing metric {metric_name}: {e}")
    
    def _create_default_config(self):
        """Crée une configuration par défaut"""
        default_config = {
            'creator_workflows': {
                'upload': {
                    'metrics': {
                        'upload_success_rate': {
                            'type': 'gauge',
                            'description': 'Creator upload success rate',
                            'labels': ['creator_id', 'content_type', 'format'],
                            'business_context': 'Upload Multi-Format workflow success',
                            'thresholds': {'warning': 0.95, 'critical': 0.90}
                        },
                        'processing_time_seconds': {
                            'type': 'histogram',
                            'description': 'Content processing time in seconds',
                            'labels': ['creator_id', 'content_type', 'processing_stage'],
                            'business_context': 'IA Processing performance',
                            'thresholds': {'warning': 30, 'critical': 60}
                        },
                        'format_distribution': {
                            'type': 'counter',
                            'description': 'Distribution of uploaded content formats',
                            'labels': ['format', 'creator_tier'],
                            'business_context': 'Multi-format content analytics',
                            'thresholds': {}
                        }
                    }
                },
                'protection': {
                    'metrics': {
                        'ip_protection_accuracy': {
                            'type': 'gauge',
                            'description': 'IP protection detection accuracy',
                            'labels': ['creator_id', 'protection_type'],
                            'business_context': 'IA Protection effectiveness',
                            'thresholds': {'warning': 0.98, 'critical': 0.95}
                        },
                        'false_positive_rate': {
                            'type': 'gauge',
                            'description': 'Protection false positive rate',
                            'labels': ['creator_id', 'detection_method'],
                            'business_context': 'Protection accuracy optimization',
                            'thresholds': {'warning': 0.05, 'critical': 0.10}
                        }
                    }
                },
                'seo': {
                    'metrics': {
                        'seo_score_improvement': {
                            'type': 'gauge',
                            'description': 'SEO score improvement over time',
                            'labels': ['creator_id', 'content_id', 'platform'],
                            'business_context': 'SEO Professionnel performance',
                            'thresholds': {'target': 0.20, 'excellent': 0.40}
                        },
                        'search_ranking_position': {
                            'type': 'gauge',
                            'description': 'Content search ranking position',
                            'labels': ['creator_id', 'keyword', 'search_engine'],
                            'business_context': 'Search visibility optimization',
                            'thresholds': {'target': 10, 'excellent': 3}
                        }
                    }
                },
                'collaboration': {
                    'metrics': {
                        'match_success_rate': {
                            'type': 'gauge',
                            'description': 'Creator-brand matching success rate',
                            'labels': ['creator_category', 'brand_category'],
                            'business_context': 'Matching Collaboration effectiveness',
                            'thresholds': {'warning': 0.60, 'target': 0.75}
                        },
                        'partnership_conversion_rate': {
                            'type': 'gauge',
                            'description': 'Match to partnership conversion rate',
                            'labels': ['creator_tier', 'collaboration_type'],
                            'business_context': 'Collaboration monetization',
                            'thresholds': {'warning': 0.30, 'target': 0.50}
                        }
                    }
                },
                'gamification': {
                    'metrics': {
                        'achievement_completion_rate': {
                            'type': 'gauge',
                            'description': 'Achievement completion rate',
                            'labels': ['creator_id', 'achievement_type'],
                            'business_context': 'Gamification engagement',
                            'thresholds': {'target': 0.40, 'excellent': 0.70}
                        },
                        'engagement_score': {
                            'type': 'gauge',
                            'description': 'Creator engagement score',
                            'labels': ['creator_id', 'time_period'],
                            'business_context': 'Creator retention metrics',
                            'thresholds': {'warning': 0.60, 'target': 0.80}
                        }
                    }
                },
                'distribution': {
                    'metrics': {
                        'cross_platform_reach': {
                            'type': 'gauge',
                            'description': 'Cross-platform content reach',
                            'labels': ['creator_id', 'content_id', 'platform'],
                            'business_context': 'Distribution Multi-Plateformes effectiveness',
                            'thresholds': {'target': 1000, 'excellent': 10000}
                        },
                        'engagement_correlation': {
                            'type': 'gauge',
                            'description': 'Engagement correlation across platforms',
                            'labels': ['creator_id', 'platform_pair'],
                            'business_context': 'Cross-platform synergy',
                            'thresholds': {'weak': 0.30, 'strong': 0.70}
                        }
                    }
                }
            },
            'business_kpis': {
                'revenue': {
                    'metrics': {
                        'revenue_per_creator': {
                            'type': 'gauge',
                            'description': 'Revenue generated per creator',
                            'labels': ['creator_id', 'revenue_stream'],
                            'business_context': 'Creator monetization effectiveness',
                            'thresholds': {'target': 1000, 'excellent': 5000}
                        },
                        'revenue_growth_rate': {
                            'type': 'gauge',
                            'description': 'Monthly revenue growth rate',
                            'labels': ['creator_tier', 'month'],
                            'business_context': 'Business growth tracking',
                            'thresholds': {'target': 0.10, 'excellent': 0.25}
                        }
                    }
                },
                'engagement': {
                    'metrics': {
                        'creator_retention_rate': {
                            'type': 'gauge',
                            'description': 'Creator retention rate',
                            'labels': ['cohort', 'time_period'],
                            'business_context': 'Creator satisfaction and loyalty',
                            'thresholds': {'warning': 0.80, 'target': 0.90}
                        },
                        'content_engagement_rate': {
                            'type': 'gauge',
                            'description': 'Content engagement rate',
                            'labels': ['creator_id', 'content_type', 'platform'],
                            'business_context': 'Content quality and appeal',
                            'thresholds': {'target': 0.05, 'excellent': 0.10}
                        }
                    }
                }
            },
            'service_discovery': {
                'kubernetes': {
                    'enabled': True,
                    'namespace': 'iacherie-creators',
                    'service_labels': ['creator-api', 'creator-analytics']
                },
                'consul': {
                    'enabled': False,
                    'datacenter': 'dc1'
                }
            }
        }
        
        # Sauvegarde la configuration par défaut
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        self._process_config(default_config)
    
    def get_metric(self, metric_name: str) -> Optional[Any]:
        """Récupère une métrique par nom"""
        return self.exporters.get(metric_name)
    
    def update_metric(self, metric_name: str, value: Union[int, float], labels: Dict[str, str] = None):
        """Met à jour une métrique avec la valeur et les labels donnés"""
        metric = self.get_metric(metric_name)
        if metric is None:
            logger.error(f"Metric not found: {metric_name}")
            return
        
        try:
            if labels:
                if hasattr(metric, 'labels'):
                    metric.labels(**labels).set(value)
                else:
                    metric.inc(value) if hasattr(metric, 'inc') else metric.observe(value)
            else:
                metric.set(value) if hasattr(metric, 'set') else metric.inc(value)
                
            logger.debug(f"Updated metric {metric_name} with value {value}")
        except Exception as e:
            logger.error(f"Error updating metric {metric_name}: {e}")
    
    def get_thresholds(self, metric_name: str) -> Dict[str, float]:
        """Récupère les seuils d'alerte pour une métrique"""
        metric_def = self.workflow_metrics.get(metric_name) or self.business_metrics.get(metric_name)
        return metric_def.thresholds if metric_def else {}
    
    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Génère la configuration Prometheus pour les métriques créateur"""
        config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': []
        }
        
        # Configuration pour les métriques créateur
        creator_config = {
            'job_name': 'iacherie-creator-metrics',
            'static_configs': [{
                'targets': ['localhost:8000']
            }],
            'metrics_path': '/metrics/creator',
            'scrape_interval': '10s'
        }
        
        # Service discovery Kubernetes si activé
        if self.service_config.get('kubernetes', {}).get('enabled'):
            kubernetes_config = {
                'job_name': 'iacherie-creator-k8s',
                'kubernetes_sd_configs': [{
                    'role': 'pod',
                    'namespaces': {
                        'names': [self.service_config['kubernetes']['namespace']]
                    }
                }],
                'relabel_configs': [
                    {
                        'source_labels': ['__meta_kubernetes_pod_label_app'],
                        'regex': 'creator-.*',
                        'action': 'keep'
                    }
                ]
            }
            config['scrape_configs'].append(kubernetes_config)
        
        config['scrape_configs'].append(creator_config)
        return config
    
    def export_registry(self) -> CollectorRegistry:
        """Exporte le registry Prometheus pour les métriques"""
        return self.registry