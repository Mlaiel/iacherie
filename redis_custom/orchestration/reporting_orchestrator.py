#!/usr/bin/env python3
"""📊 Reporting Orchestrator - Advanced Enterprise Reporting System
================================================================
Expert: DATA ENGINEER + BACKEND SENIOR + BUSINESS ANALYST + DEVOPS
Technologies: Business Intelligence + Report Generation + Data Visualization + Automated Reporting
Architecture: Level 3 - Reporting Intelligence Layer
Date: 2025-01-14

Ultra-advanced reporting orchestration system with automated report generation,
business intelligence analytics, data visualization and scheduled reporting.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from abc import ABC, abstractmethod
import statistics
import base64
import io
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types de rapports"""
    OPERATIONAL = "operational"
    BUSINESS = "business"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    CREATOR_ANALYTICS = "creator_analytics"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    EXECUTIVE_SUMMARY = "executive_summary"
    CUSTOM = "custom"

class ReportFormat(Enum):
    """Formats de rapport"""
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    DASHBOARD = "dashboard"
    EMAIL = "email"
    API = "api"

class ReportFrequency(Enum):
    """Fréquences de rapport"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class ReportStatus(Enum):
    """États des rapports"""
    SCHEDULED = "scheduled"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"
    ARCHIVED = "archived"

class DataVisualizationType(Enum):
    """Types de visualisation"""
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    TREEMAP = "treemap"

@dataclass
class ReportDataSource:
    """Source de données pour rapport"""
    source_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    source_type: str = "redis"  # redis, database, api, file
    connection_config: Dict[str, Any] = field(default_factory=dict)
    query: str = ""
    cache_duration: timedelta = timedelta(minutes=5)
    is_active: bool = True
    last_updated: Optional[datetime] = None

@dataclass
class ReportVisualization:
    """Visualisation pour rapport"""
    viz_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    visualization_type: DataVisualizationType = DataVisualizationType.TABLE
    data_source: str = ""
    query: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)
    size: Dict[str, int] = field(default_factory=dict)

@dataclass
class ReportTemplate:
    """Template de rapport"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    report_type: ReportType = ReportType.OPERATIONAL
    format: ReportFormat = ReportFormat.HTML
    template_content: str = ""
    data_sources: List[str] = field(default_factory=list)
    visualizations: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ReportSchedule:
    """Planification de rapport"""
    schedule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_id: str = ""
    frequency: ReportFrequency = ReportFrequency.DAILY
    parameters: Dict[str, Any] = field(default_factory=dict)
    recipients: List[str] = field(default_factory=list)
    delivery_method: str = "email"
    is_active: bool = True
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    created_by: str = ""

@dataclass
class ReportExecution:
    """Exécution de rapport"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    schedule_id: Optional[str] = None
    status: ReportStatus = ReportStatus.SCHEDULED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    output_path: Optional[str] = None
    output_size: int = 0
    parameters: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    generated_by: str = ""
    recipients_notified: List[str] = field(default_factory=list)

@dataclass
class ReportingOrchestratorConfig:
    """Configuration de l'orchestrateur de rapports"""
    max_concurrent_reports: int = 5
    report_timeout: timedelta = timedelta(minutes=30)
    output_directory: str = "/tmp/reports"
    enable_caching: bool = True
    cache_duration: timedelta = timedelta(hours=1)
    enable_scheduling: bool = True
    schedule_check_interval: timedelta = timedelta(minutes=1)
    retention_period: timedelta = timedelta(days=30)
    max_report_size_mb: int = 100
    enable_notifications: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email", "redis"])

class ReportGenerator(ABC):
    """Interface abstraite pour les générateurs de rapport"""
    
    @abstractmethod
    async def generate_report(self, template: ReportTemplate, 
                            parameters: Dict[str, Any]) -> Tuple[str, bytes]:
        """Génère un rapport selon le template"""
        pass

class HTMLReportGenerator(ReportGenerator):
    """Générateur de rapports HTML"""
    
    async def generate_report(self, template: ReportTemplate, 
                            parameters: Dict[str, Any]) -> Tuple[str, bytes]:
        """Génère un rapport HTML"""
        try:
            # Template HTML simple
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{template.name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                    .content {{ margin: 20px 0; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e9e9e9; border-radius: 5px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{template.name}</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>{template.description}</p>
                </div>
                
                <div class="content">
                    <h2>Report Summary</h2>
                    <div class="metric">
                        <strong>Report Type:</strong> {template.report_type.value}
                    </div>
                    <div class="metric">
                        <strong>Time Period:</strong> {parameters.get('time_period', 'Last 24 hours')}
                    </div>
                    
                    <h2>Key Metrics</h2>
                    <table>
                        <tr><th>Metric</th><th>Value</th><th>Trend</th></tr>
                        <tr><td>Total Events</td><td>{parameters.get('total_events', 'N/A')}</td><td>↗</td></tr>
                        <tr><td>Active Users</td><td>{parameters.get('active_users', 'N/A')}</td><td>↗</td></tr>
                        <tr><td>System Health</td><td>{parameters.get('system_health', 'Good')}</td><td>→</td></tr>
                    </table>
                    
                    <h2>Analysis</h2>
                    <p>This report shows key metrics and trends for the specified time period.</p>
                    <p>Generated by Redis Orchestration Reporting System</p>
                </div>
            </body>
            </html>
            """
            
            return "report.html", html_content.encode('utf-8')
            
        except Exception as e:
            logger.error(f"❌ Failed to generate HTML report: {e}")
            raise

class JSONReportGenerator(ReportGenerator):
    """Générateur de rapports JSON"""
    
    async def generate_report(self, template: ReportTemplate, 
                            parameters: Dict[str, Any]) -> Tuple[str, bytes]:
        """Génère un rapport JSON"""
        try:
            report_data = {
                'report_info': {
                    'name': template.name,
                    'type': template.report_type.value,
                    'generated_at': datetime.now().isoformat(),
                    'parameters': parameters
                },
                'metrics': {
                    'total_events': parameters.get('total_events', 0),
                    'active_users': parameters.get('active_users', 0),
                    'system_health': parameters.get('system_health', 'unknown')
                },
                'data': {
                    'time_series': [],
                    'aggregations': {},
                    'trends': {}
                },
                'metadata': {
                    'generated_by': 'Redis Orchestration Reporting System',
                    'version': '1.0.0'
                }
            }
            
            json_content = json.dumps(report_data, indent=2)
            return "report.json", json_content.encode('utf-8')
            
        except Exception as e:
            logger.error(f"❌ Failed to generate JSON report: {e}")
            raise

class RedisReportingOrchestrator:
    """Orchestrateur de rapports Redis enterprise"""
    
    def __init__(self, config: ReportingOrchestratorConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client or redis.Redis()
        self.is_running = False
        
        # Composants internes
        self.data_sources = {}
        self.report_templates = {}
        self.report_schedules = {}
        self.active_executions = {}
        self.execution_history = []
        
        # Générateurs de rapport
        self.report_generators = {
            ReportFormat.HTML: HTMLReportGenerator(),
            ReportFormat.JSON: JSONReportGenerator()
        }
        
        # Cache des données
        self.data_cache = {}
        
        # Métriques de l'orchestrateur
        self.orchestrator_metrics = {
            'reports_generated': 0,
            'reports_failed': 0,
            'reports_delivered': 0,
            'avg_generation_time': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'last_execution': None
        }
        
        # Tâches asynchrones
        self.scheduler_task = None
        self.cleanup_task = None
    
    async def initialize(self) -> bool:
        """Initialise l'orchestrateur de rapports"""
        try:
            logger.info("📊 Initializing Reporting Orchestrator...")
            
            # Créer le répertoire de sortie
            import os
            os.makedirs(self.config.output_directory, exist_ok=True)
            
            # Charger les sources de données
            await self._load_data_sources()
            
            # Charger les templates de rapport
            await self._load_report_templates()
            
            # Charger les planifications
            await self._load_report_schedules()
            
            # Charger l'historique des exécutions
            await self._load_execution_history()
            
            # Créer des templates par défaut si aucun n'existe
            if not self.report_templates:
                await self._create_default_templates()
            
            # Démarrer les tâches
            await self._start_background_tasks()
            
            self.is_running = True
            logger.info("✅ Reporting Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Reporting Orchestrator: {e}")
            return False
    
    async def _load_data_sources(self):
        """Charge les sources de données"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("reporting:datasources:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    source_data = json.loads(data)
                    source = ReportDataSource(**source_data)
                    self.data_sources[source.source_id] = source
            
            logger.info(f"✅ Loaded {len(self.data_sources)} data sources")
            
        except Exception as e:
            logger.error(f"❌ Failed to load data sources: {e}")
    
    async def _load_report_templates(self):
        """Charge les templates de rapport"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("reporting:templates:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    template_data = json.loads(data)
                    template = ReportTemplate(**template_data)
                    self.report_templates[template.template_id] = template
            
            logger.info(f"✅ Loaded {len(self.report_templates)} report templates")
            
        except Exception as e:
            logger.error(f"❌ Failed to load report templates: {e}")
    
    async def _load_report_schedules(self):
        """Charge les planifications de rapport"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("reporting:schedules:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    schedule_data = json.loads(data)
                    schedule = ReportSchedule(**schedule_data)
                    self.report_schedules[schedule.schedule_id] = schedule
            
            logger.info(f"✅ Loaded {len(self.report_schedules)} report schedules")
            
        except Exception as e:
            logger.error(f"❌ Failed to load report schedules: {e}")
    
    async def _load_execution_history(self):
        """Charge l'historique des exécutions"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("reporting:executions:*")]
            for key in keys[-100:]:  # Charger les 100 dernières
                data = self.redis_client.get(key)
                if data:
                    execution_data = json.loads(data)
                    execution = ReportExecution(**execution_data)
                    self.execution_history.append(execution)
            
            # Trier par date
            self.execution_history.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
            
            logger.info(f"✅ Loaded {len(self.execution_history)} execution records")
            
        except Exception as e:
            logger.error(f"❌ Failed to load execution history: {e}")
    
    async def _create_default_templates(self):
        """Crée les templates par défaut"""
        try:
            default_templates = [
                ReportTemplate(
                    name="System Performance Report",
                    description="Daily system performance and health metrics",
                    report_type=ReportType.OPERATIONAL,
                    format=ReportFormat.HTML,
                    template_content="system_performance_template",
                    created_by="system"
                ),
                ReportTemplate(
                    name="Creator Analytics Report",
                    description="Creator economy metrics and insights",
                    report_type=ReportType.CREATOR_ANALYTICS,
                    format=ReportFormat.HTML,
                    template_content="creator_analytics_template",
                    created_by="system"
                ),
                ReportTemplate(
                    name="Business Intelligence Summary",
                    description="Executive business intelligence summary",
                    report_type=ReportType.BUSINESS,
                    format=ReportFormat.JSON,
                    template_content="business_intelligence_template",
                    created_by="system"
                ),
                ReportTemplate(
                    name="Security Audit Report",
                    description="Security events and compliance status",
                    report_type=ReportType.SECURITY,
                    format=ReportFormat.HTML,
                    template_content="security_audit_template",
                    created_by="system"
                )
            ]
            
            for template in default_templates:
                self.report_templates[template.template_id] = template
                await self._store_report_template(template)
            
            logger.info(f"✅ Created {len(default_templates)} default templates")
            
        except Exception as e:
            logger.error(f"❌ Failed to create default templates: {e}")
    
    async def _store_report_template(self, template: ReportTemplate):
        """Stocke un template de rapport"""
        try:
            key = f"reporting:templates:{template.template_id}"
            data = {
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'report_type': template.report_type.value,
                'format': template.format.value,
                'template_content': template.template_content,
                'data_sources': template.data_sources,
                'visualizations': template.visualizations,
                'parameters': template.parameters,
                'styling': template.styling,
                'is_active': template.is_active,
                'created_by': template.created_by,
                'created_at': template.created_at.isoformat()
            }
            
            self.redis_client.setex(key, 30 * 24 * 3600, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store report template: {e}")
    
    async def _start_background_tasks(self):
        """Démarre les tâches de fond"""
        if self.config.enable_scheduling:
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def create_report_template(self, name: str, description: str,
                                   report_type: ReportType, format: ReportFormat,
                                   template_content: str, created_by: str,
                                   data_sources: Optional[List[str]] = None,
                                   parameters: Optional[Dict[str, Any]] = None) -> ReportTemplate:
        """Crée un nouveau template de rapport"""
        try:
            template = ReportTemplate(
                name=name,
                description=description,
                report_type=report_type,
                format=format,
                template_content=template_content,
                data_sources=data_sources or [],
                parameters=parameters or {},
                created_by=created_by
            )
            
            self.report_templates[template.template_id] = template
            await self._store_report_template(template)
            
            logger.info(f"✅ Created report template: {name}")
            return template
            
        except Exception as e:
            logger.error(f"❌ Failed to create report template: {e}")
            raise
    
    async def schedule_report(self, template_id: str, frequency: ReportFrequency,
                            recipients: List[str], created_by: str,
                            parameters: Optional[Dict[str, Any]] = None) -> ReportSchedule:
        """Planifie un rapport récurrent"""
        try:
            if template_id not in self.report_templates:
                raise ValueError(f"Template {template_id} not found")
            
            schedule = ReportSchedule(
                name=f"Schedule for {self.report_templates[template_id].name}",
                template_id=template_id,
                frequency=frequency,
                parameters=parameters or {},
                recipients=recipients,
                created_by=created_by,
                next_run=self._calculate_next_run(frequency)
            )
            
            self.report_schedules[schedule.schedule_id] = schedule
            await self._store_report_schedule(schedule)
            
            logger.info(f"✅ Scheduled report: {schedule.name}")
            return schedule
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule report: {e}")
            raise
    
    def _calculate_next_run(self, frequency: ReportFrequency) -> datetime:
        """Calcule la prochaine exécution selon la fréquence"""
        now = datetime.now()
        
        if frequency == ReportFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == ReportFrequency.DAILY:
            return now.replace(hour=6, minute=0, second=0) + timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            return now.replace(hour=6, minute=0, second=0) + timedelta(days=days_until_monday or 7)
        elif frequency == ReportFrequency.MONTHLY:
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, day=1, hour=6, minute=0, second=0)
            else:
                return now.replace(month=now.month + 1, day=1, hour=6, minute=0, second=0)
        else:
            return now + timedelta(days=1)
    
    async def _store_report_schedule(self, schedule: ReportSchedule):
        """Stocke une planification de rapport"""
        try:
            key = f"reporting:schedules:{schedule.schedule_id}"
            data = {
                'schedule_id': schedule.schedule_id,
                'name': schedule.name,
                'template_id': schedule.template_id,
                'frequency': schedule.frequency.value,
                'parameters': schedule.parameters,
                'recipients': schedule.recipients,
                'delivery_method': schedule.delivery_method,
                'is_active': schedule.is_active,
                'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
                'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
                'created_by': schedule.created_by
            }
            
            self.redis_client.setex(key, 30 * 24 * 3600, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store report schedule: {e}")
    
    async def generate_report(self, template_id: str, parameters: Optional[Dict[str, Any]] = None,
                            generated_by: str = "manual") -> ReportExecution:
        """Génère un rapport à la demande"""
        try:
            if template_id not in self.report_templates:
                raise ValueError(f"Template {template_id} not found")
            
            template = self.report_templates[template_id]
            
            # Créer l'enregistrement d'exécution
            execution = ReportExecution(
                template_id=template_id,
                parameters=parameters or {},
                generated_by=generated_by,
                started_at=datetime.now(),
                status=ReportStatus.GENERATING
            )
            
            self.active_executions[execution.execution_id] = execution
            await self._store_execution(execution)
            
            # Générer le rapport de manière asynchrone
            asyncio.create_task(self._execute_report_generation(execution, template))
            
            logger.info(f"✅ Started report generation: {execution.execution_id}")
            return execution
            
        except Exception as e:
            logger.error(f"❌ Failed to start report generation: {e}")
            raise
    
    async def _execute_report_generation(self, execution: ReportExecution, template: ReportTemplate):
        """Exécute la génération d'un rapport"""
        try:
            start_time = time.time()
            
            # Récupérer les données
            report_data = await self._gather_report_data(template, execution.parameters)
            
            # Générer le rapport
            generator = self.report_generators.get(template.format)
            if not generator:
                raise ValueError(f"No generator for format {template.format}")
            
            filename, content = await generator.generate_report(template, report_data)
            
            # Sauvegarder le fichier
            import os
            output_path = os.path.join(self.config.output_directory, 
                                     f"{execution.execution_id}_{filename}")
            
            with open(output_path, 'wb') as f:
                f.write(content)
            
            # Mettre à jour l'exécution
            execution.status = ReportStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.duration = timedelta(seconds=time.time() - start_time)
            execution.output_path = output_path
            execution.output_size = len(content)
            
            # Mettre à jour les métriques
            self.orchestrator_metrics['reports_generated'] += 1
            self.orchestrator_metrics['avg_generation_time'] = (
                (self.orchestrator_metrics['avg_generation_time'] * 
                 (self.orchestrator_metrics['reports_generated'] - 1) + 
                 execution.duration.total_seconds()) / 
                self.orchestrator_metrics['reports_generated']
            )
            self.orchestrator_metrics['last_execution'] = datetime.now()
            
            # Livrer le rapport si nécessaire
            if execution.schedule_id:
                schedule = self.report_schedules.get(execution.schedule_id)
                if schedule:
                    await self._deliver_report(execution, schedule.recipients, schedule.delivery_method)
            
            logger.info(f"✅ Report generation completed: {execution.execution_id} "
                       f"({execution.duration.total_seconds():.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            
            execution.status = ReportStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error_message = str(e)
            self.orchestrator_metrics['reports_failed'] += 1
        
        finally:
            # Nettoyer et archiver
            await self._store_execution(execution)
            self.active_executions.pop(execution.execution_id, None)
            self.execution_history.insert(0, execution)
            
            # Garder seulement les 1000 dernières exécutions
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[:1000]
    
    async def _gather_report_data(self, template: ReportTemplate, 
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Collecte les données pour le rapport"""
        try:
            # Données de base (simulées pour l'exemple)
            report_data = {
                'total_events': await self._get_metric_value('total_events', parameters),
                'active_users': await self._get_metric_value('active_users', parameters),
                'system_health': await self._get_system_health(),
                'time_period': parameters.get('time_period', 'Last 24 hours'),
                'generated_at': datetime.now().isoformat()
            }
            
            # Ajouter des données spécifiques selon le type de rapport
            if template.report_type == ReportType.CREATOR_ANALYTICS:
                report_data.update(await self._get_creator_analytics_data(parameters))
            elif template.report_type == ReportType.PERFORMANCE:
                report_data.update(await self._get_performance_data(parameters))
            elif template.report_type == ReportType.SECURITY:
                report_data.update(await self._get_security_data(parameters))
            
            return report_data
            
        except Exception as e:
            logger.error(f"❌ Failed to gather report data: {e}")
            return {}
    
    async def _get_metric_value(self, metric_name: str, parameters: Dict[str, Any]) -> Any:
        """Récupère une valeur de métrique"""
        try:
            # Vérifier le cache
            cache_key = f"{metric_name}:{hash(str(parameters))}"
            if self.config.enable_caching and cache_key in self.data_cache:
                cache_entry = self.data_cache[cache_key]
                if datetime.now() - cache_entry['timestamp'] < self.config.cache_duration:
                    self.orchestrator_metrics['cache_hits'] += 1
                    return cache_entry['value']
            
            # Simuler la récupération de données (en production, interroger Redis/DB)
            if metric_name == 'total_events':
                value = np.random.randint(1000, 10000)
            elif metric_name == 'active_users':
                value = np.random.randint(100, 1000)
            else:
                value = 0
            
            # Mettre en cache
            if self.config.enable_caching:
                self.data_cache[cache_key] = {
                    'value': value,
                    'timestamp': datetime.now()
                }
                self.orchestrator_metrics['cache_misses'] += 1
            
            return value
            
        except Exception as e:
            logger.error(f"❌ Failed to get metric value for {metric_name}: {e}")
            return "N/A"
    
    async def _get_system_health(self) -> str:
        """Récupère l'état de santé du système"""
        try:
            # Simuler l'évaluation de la santé du système
            health_score = np.random.uniform(0.7, 1.0)
            
            if health_score > 0.9:
                return "Excellent"
            elif health_score > 0.8:
                return "Good"
            elif health_score > 0.7:
                return "Fair"
            else:
                return "Poor"
                
        except Exception as e:
            logger.error(f"❌ Failed to get system health: {e}")
            return "Unknown"
    
    async def _get_creator_analytics_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données d'analytics créateurs"""
        return {
            'total_creators': np.random.randint(500, 2000),
            'active_creators': np.random.randint(200, 800),
            'content_uploads': np.random.randint(1000, 5000),
            'total_revenue': np.random.uniform(10000, 50000),
            'avg_engagement': np.random.uniform(0.05, 0.15)
        }
    
    async def _get_performance_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de performance"""
        return {
            'avg_response_time': np.random.uniform(50, 200),
            'throughput': np.random.uniform(1000, 5000),
            'error_rate': np.random.uniform(0.001, 0.01),
            'cpu_usage': np.random.uniform(20, 80),
            'memory_usage': np.random.uniform(30, 70)
        }
    
    async def _get_security_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données de sécurité"""
        return {
            'security_events': np.random.randint(0, 10),
            'blocked_attacks': np.random.randint(0, 5),
            'compliance_score': np.random.uniform(0.8, 1.0),
            'vulnerabilities': np.random.randint(0, 3),
            'security_score': np.random.uniform(0.85, 0.99)
        }
    
    async def _deliver_report(self, execution: ReportExecution, recipients: List[str], 
                            delivery_method: str):
        """Livre un rapport aux destinataires"""
        try:
            if delivery_method == "email":
                await self._send_email_report(execution, recipients)
            elif delivery_method == "redis":
                await self._publish_report_notification(execution, recipients)
            
            execution.recipients_notified = recipients
            execution.status = ReportStatus.DELIVERED
            self.orchestrator_metrics['reports_delivered'] += 1
            
            logger.info(f"✅ Report delivered to {len(recipients)} recipients")
            
        except Exception as e:
            logger.error(f"❌ Failed to deliver report: {e}")
    
    async def _send_email_report(self, execution: ReportExecution, recipients: List[str]):
        """Envoie le rapport par email (simulation)"""
        # En production, intégrer avec un service d'email
        logger.info(f"📧 Sending email report to: {', '.join(recipients)}")
    
    async def _publish_report_notification(self, execution: ReportExecution, recipients: List[str]):
        """Publie une notification de rapport sur Redis"""
        try:
            notification = {
                'execution_id': execution.execution_id,
                'template_id': execution.template_id,
                'status': execution.status.value,
                'output_path': execution.output_path,
                'generated_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'recipients': recipients
            }
            
            self.redis_client.publish("reporting:notifications", json.dumps(notification))
            
        except Exception as e:
            logger.error(f"❌ Failed to publish report notification: {e}")
    
    async def _store_execution(self, execution: ReportExecution):
        """Stocke une exécution de rapport"""
        try:
            key = f"reporting:executions:{execution.execution_id}"
            data = {
                'execution_id': execution.execution_id,
                'template_id': execution.template_id,
                'schedule_id': execution.schedule_id,
                'status': execution.status.value,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'duration': execution.duration.total_seconds() if execution.duration else None,
                'output_path': execution.output_path,
                'output_size': execution.output_size,
                'parameters': execution.parameters,
                'error_message': execution.error_message,
                'generated_by': execution.generated_by,
                'recipients_notified': execution.recipients_notified
            }
            
            ttl = int(self.config.retention_period.total_seconds())
            self.redis_client.setex(key, ttl, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store execution: {e}")
    
    async def _scheduler_loop(self):
        """Boucle du planificateur de rapports"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for schedule in self.report_schedules.values():
                    if (schedule.is_active and schedule.next_run and 
                        current_time >= schedule.next_run):
                        
                        # Exécuter le rapport planifié
                        await self._execute_scheduled_report(schedule)
                        
                        # Calculer la prochaine exécution
                        schedule.last_run = current_time
                        schedule.next_run = self._calculate_next_run(schedule.frequency)
                        await self._store_report_schedule(schedule)
                
                await asyncio.sleep(self.config.schedule_check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _execute_scheduled_report(self, schedule: ReportSchedule):
        """Exécute un rapport planifié"""
        try:
            logger.info(f"🕐 Executing scheduled report: {schedule.name}")
            
            execution = await self.generate_report(
                template_id=schedule.template_id,
                parameters=schedule.parameters,
                generated_by=f"schedule:{schedule.schedule_id}"
            )
            
            execution.schedule_id = schedule.schedule_id
            
        except Exception as e:
            logger.error(f"❌ Failed to execute scheduled report: {e}")
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage"""
        while self.is_running:
            try:
                # Nettoyer les rapports anciens
                await self._cleanup_old_reports()
                
                # Nettoyer le cache
                await self._cleanup_data_cache()
                
                # Nettoyer les exécutions archivées
                await self._cleanup_old_executions()
                
                logger.info("✅ Cleanup completed")
                
                # Nettoyer une fois par jour
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_reports(self):
        """Nettoie les anciens fichiers de rapport"""
        try:
            import os
            import glob
            
            cutoff_time = datetime.now() - self.config.retention_period
            
            for filepath in glob.glob(os.path.join(self.config.output_directory, "*")):
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.debug(f"Deleted old report file: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old reports: {e}")
    
    async def _cleanup_data_cache(self):
        """Nettoie le cache de données"""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.data_cache.items():
                if current_time - entry['timestamp'] > self.config.cache_duration:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.data_cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup data cache: {e}")
    
    async def _cleanup_old_executions(self):
        """Nettoie les anciennes exécutions"""
        try:
            cutoff_time = datetime.now() - self.config.retention_period
            keys = [key.decode() for key in self.redis_client.keys("reporting:executions:*")]
            
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    execution_data = json.loads(data)
                    if execution_data.get('started_at'):
                        started_at = datetime.fromisoformat(execution_data['started_at'])
                        if started_at < cutoff_time:
                            self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old executions: {e}")
    
    async def get_report_templates(self) -> List[ReportTemplate]:
        """Récupère tous les templates de rapport"""
        return list(self.report_templates.values())
    
    async def get_report_schedules(self) -> List[ReportSchedule]:
        """Récupère toutes les planifications"""
        return list(self.report_schedules.values())
    
    async def get_execution_history(self, limit: int = 50) -> List[ReportExecution]:
        """Récupère l'historique des exécutions"""
        return self.execution_history[:limit]
    
    async def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de l'orchestrateur"""
        return {
            'reports_generated': self.orchestrator_metrics['reports_generated'],
            'reports_failed': self.orchestrator_metrics['reports_failed'],
            'reports_delivered': self.orchestrator_metrics['reports_delivered'],
            'avg_generation_time': self.orchestrator_metrics['avg_generation_time'],
            'success_rate': (self.orchestrator_metrics['reports_generated'] / 
                           (self.orchestrator_metrics['reports_generated'] + 
                            self.orchestrator_metrics['reports_failed']) 
                           if self.orchestrator_metrics['reports_generated'] + 
                              self.orchestrator_metrics['reports_failed'] > 0 else 0),
            'cache_hit_rate': (self.orchestrator_metrics['cache_hits'] / 
                              (self.orchestrator_metrics['cache_hits'] + 
                               self.orchestrator_metrics['cache_misses'])
                              if self.orchestrator_metrics['cache_hits'] + 
                                 self.orchestrator_metrics['cache_misses'] > 0 else 0),
            'last_execution': (self.orchestrator_metrics['last_execution'].isoformat() 
                              if self.orchestrator_metrics['last_execution'] else None),
            'active_executions': len(self.active_executions),
            'total_templates': len(self.report_templates),
            'active_schedules': len([s for s in self.report_schedules.values() if s.is_active]),
            'is_running': self.is_running
        }
    
    async def shutdown(self):
        """Arrête l'orchestrateur de rapports"""
        try:
            logger.info("🛑 Shutting down Reporting Orchestrator...")
            
            self.is_running = False
            
            # Arrêter les tâches
            if self.scheduler_task and not self.scheduler_task.done():
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            if self.cleanup_task and not self.cleanup_task.done():
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Attendre la fin des rapports en cours
            if self.active_executions:
                logger.info(f"Waiting for {len(self.active_executions)} active reports to complete...")
                # En production, on pourrait attendre ou sauvegarder l'état
            
            logger.info("✅ Reporting Orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Factory function pour créer l'orchestrateur
async def create_reporting_orchestrator(
    config: Optional[ReportingOrchestratorConfig] = None,
    redis_client: Optional[redis.Redis] = None
) -> RedisReportingOrchestrator:
    """Crée et initialise un orchestrateur de rapports"""
    
    if config is None:
        config = ReportingOrchestratorConfig()
    
    orchestrator = RedisReportingOrchestrator(config, redis_client)
    
    if await orchestrator.initialize():
        return orchestrator
    else:
        raise RuntimeError("Failed to initialize Reporting Orchestrator")

__all__ = [
    'RedisReportingOrchestrator',
    'ReportingOrchestratorConfig',
    'ReportTemplate',
    'ReportSchedule',
    'ReportExecution',
    'ReportDataSource',
    'ReportVisualization',
    'ReportType',
    'ReportFormat',
    'ReportFrequency',
    'ReportStatus',
    'DataVisualizationType',
    'ReportGenerator',
    'HTMLReportGenerator',
    'JSONReportGenerator',
    'create_reporting_orchestrator'
]
