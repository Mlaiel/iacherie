#!/usr/bin/env python3
"""📋 Redis Reporting Orchestrator - Advanced Automated Reporting & Documentation System
======================================================================================
Expert: DATA ANALYST + BUSINESS ANALYST + BACKEND SENIOR + DEVOPS
Technologies: Automated Reporting + Document Generation + Scheduled Reports + Creator Economy Reports
Architecture: Level 3 - Reporting Intelligence Layer
Date: 2025-01-14

Ultra-advanced reporting system with automated generation, intelligent scheduling,
multi-format exports, creator economy reports and executive dashboards.
======================================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
======================================================================================
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
import json
import math
import statistics
from collections import deque, defaultdict
import redis
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from jinja2 import Environment, FileSystemLoader
import uuid
import base64
import io
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types de rapports"""
    EXECUTIVE_SUMMARY = "executive_summary"
    PERFORMANCE_REPORT = "performance_report"
    CREATOR_ANALYTICS = "creator_analytics"
    FINANCIAL_REPORT = "financial_report"
    TECHNICAL_REPORT = "technical_report"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    SECURITY_REPORT = "security_report"
    COMPLIANCE_REPORT = "compliance_report"
    CUSTOM_REPORT = "custom_report"

class ReportFormat(Enum):
    """Formats de rapport"""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    POWERPOINT = "powerpoint"
    MARKDOWN = "markdown"

class ReportSchedule(Enum):
    """Fréquences de rapport"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class ReportPriority(Enum):
    """Priorités de rapport"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DeliveryMethod(Enum):
    """Méthodes de livraison"""
    EMAIL = "email"
    DASHBOARD = "dashboard"
    API = "api"
    FILE_SYSTEM = "file_system"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"

@dataclass
class ReportTemplate:
    """Template de rapport"""
    template_id: str = ""
    name: str = ""
    description: str = ""
    report_type: ReportType = ReportType.PERFORMANCE_REPORT
    
    # Structure template
    sections: List[Dict[str, Any]] = field(default_factory=list)
    default_visualizations: List[Dict[str, Any]] = field(default_factory=list)
    required_data_sources: List[str] = field(default_factory=list)
    
    # Configuration
    template_file_path: Optional[str] = None
    style_config: Dict[str, Any] = field(default_factory=dict)
    branding_config: Dict[str, Any] = field(default_factory=dict)
    
    # Personnalisation
    customizable_sections: List[str] = field(default_factory=list)
    parameter_definitions: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    category: str = ""
    tags: List[str] = field(default_factory=list)
    version: str = "1.0"
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ScheduledReport:
    """Rapport programmé"""
    schedule_id: str = ""
    report_name: str = ""
    template_id: str = ""
    
    # Programmation
    schedule: ReportSchedule = ReportSchedule.DAILY
    schedule_config: Dict[str, Any] = field(default_factory=dict)  # heure, jour, etc.
    timezone: str = "UTC"
    
    # Configuration génération
    parameters: Dict[str, Any] = field(default_factory=dict)
    data_filters: Dict[str, Any] = field(default_factory=dict)
    output_formats: List[ReportFormat] = field(default_factory=list)
    
    # Livraison
    delivery_methods: List[DeliveryMethod] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    delivery_config: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    owner_id: str = ""
    priority: ReportPriority = ReportPriority.MEDIUM
    active: bool = True
    
    # Historique
    last_generated: Optional[datetime] = None
    last_delivery_status: str = "pending"
    generation_count: int = 0
    failure_count: int = 0
    
    # Configuration avancée
    conditional_generation: Optional[Dict[str, Any]] = None  # Générer seulement si conditions
    retention_period: int = 2592000  # 30 jours
    notification_on_failure: bool = True

@dataclass
class GeneratedReport:
    """Rapport généré"""
    report_id: str = ""
    schedule_id: Optional[str] = None
    template_id: str = ""
    report_name: str = ""
    
    # Configuration génération
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    data_period: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now(), datetime.now()))
    
    # Contenu
    report_content: Dict[str, Any] = field(default_factory=dict)
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    executive_summary: str = ""
    
    # Métadonnées
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: str = ""
    generation_time: float = 0.0  # temps en secondes
    data_freshness: float = 1.0   # fraîcheur données 0-1
    
    # Formats et livrables
    output_files: Dict[ReportFormat, str] = field(default_factory=dict)  # format -> chemin fichier
    delivery_status: Dict[DeliveryMethod, str] = field(default_factory=dict)
    
    # Qualité
    data_quality_score: float = 1.0
    completeness_score: float = 1.0
    validation_errors: List[str] = field(default_factory=list)
    
    # Analytics rapport
    view_count: int = 0
    download_count: int = 0
    last_accessed: Optional[datetime] = None

@dataclass
class ReportSubscription:
    """Abonnement à des rapports"""
    subscription_id: str = ""
    user_id: str = ""
    subscription_name: str = ""
    
    # Configuration abonnement
    report_types: List[ReportType] = field(default_factory=list)
    frequency: ReportSchedule = ReportSchedule.WEEKLY
    delivery_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Filtres
    content_filters: Dict[str, Any] = field(default_factory=dict)
    creator_filters: List[str] = field(default_factory=list)
    metrics_of_interest: List[str] = field(default_factory=list)
    
    # Personnalisation
    custom_sections: List[str] = field(default_factory=list)
    visualization_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # État
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_delivery: Optional[datetime] = None

class RedisReportingOrchestrator:
    """📋 Orchestrateur de rapports Redis ultra-intelligent"""
    
    def __init__(self):
        """Initialisation orchestrateur rapports"""
        self.redis_client = None
        self.is_running = False
        
        # Storage rapports
        self.report_templates = {}
        self.scheduled_reports = {}
        self.generated_reports = {}
        self.report_subscriptions = {}
        
        # Système de génération
        self.generation_queue = deque()
        self.active_generations = {}
        self.template_engine = None
        
        # Cache et optimisations
        self.data_cache = {}
        self.visualization_cache = {}
        self.template_cache = {}
        
        # Configuration système
        self.config = {
            "max_concurrent_generations": 5,
            "report_retention_days": 90,
            "cache_ttl_seconds": 3600,
            "max_report_size_mb": 100,
            "output_directory": "/tmp/reports",
            "template_directory": "/templates/reports"
        }
        
        # Métriques système
        self.orchestrator_metrics = {
            "reports_generated": 0,
            "scheduled_reports_executed": 0,
            "failed_generations": 0,
            "average_generation_time": 0.0,
            "cache_hit_rate": 0.0,
            "delivery_success_rate": 0.0
        }
        
        # Initialiser templates par défaut
        self._initialize_default_templates()
        
        logger.info("📋 Orchestrateur rapports Redis initialisé")

    async def start(self, redis_connection=None):
        """Démarrer l'orchestrateur rapports"""
        try:
            self.redis_client = redis_connection or redis.Redis(decode_responses=True)
            self.is_running = True
            
            # Initialiser moteur template
            self.template_engine = Environment(
                loader=FileSystemLoader(self.config["template_directory"])
            )
            
            # Démarrer services rapports
            reporting_tasks = [
                self._run_scheduled_reports(),
                self._run_generation_queue(),
                self._run_delivery_system(),
                self._run_cache_maintenance(),
                self._run_cleanup_service(),
                self._run_analytics_collector(),
                self._run_quality_monitor()
            ]
            
            await asyncio.gather(*reporting_tasks, return_exceptions=True)
            
            logger.info("📋 Orchestrateur rapports démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage orchestrateur rapports: {e}")
            raise

    async def stop(self):
        """Arrêter l'orchestrateur"""
        self.is_running = False
        logger.info("📋 Orchestrateur rapports arrêté")

    async def create_report_template(self, template_config: Dict[str, Any]) -> str:
        """Créer un template de rapport"""
        try:
            template_id = str(uuid.uuid4())
            
            template = ReportTemplate(
                template_id=template_id,
                name=template_config.get("name", "Nouveau Template"),
                description=template_config.get("description", ""),
                report_type=ReportType(template_config.get("type", "performance_report")),
                sections=template_config.get("sections", []),
                default_visualizations=template_config.get("visualizations", []),
                required_data_sources=template_config.get("data_sources", []),
                style_config=template_config.get("style", {}),
                branding_config=template_config.get("branding", {}),
                customizable_sections=template_config.get("customizable_sections", []),
                parameter_definitions=template_config.get("parameters", {}),
                category=template_config.get("category", "custom"),
                tags=template_config.get("tags", []),
                created_by=template_config.get("created_by", "system")
            )
            
            # Valider template
            if not await self._validate_template(template):
                raise ValueError("Template de rapport invalide")
            
            # Sauvegarder
            self.report_templates[template_id] = template
            await self._persist_template(template)
            
            logger.info(f"📋 Template rapport créé: {template.name}")
            return template_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création template: {e}")
            raise

    async def schedule_report(self, schedule_config: Dict[str, Any]) -> str:
        """Programmer un rapport"""
        try:
            schedule_id = str(uuid.uuid4())
            
            scheduled_report = ScheduledReport(
                schedule_id=schedule_id,
                report_name=schedule_config.get("name", "Rapport Programmé"),
                template_id=schedule_config["template_id"],
                schedule=ReportSchedule(schedule_config.get("schedule", "daily")),
                schedule_config=schedule_config.get("schedule_config", {}),
                timezone=schedule_config.get("timezone", "UTC"),
                parameters=schedule_config.get("parameters", {}),
                data_filters=schedule_config.get("filters", {}),
                output_formats=[ReportFormat(fmt) for fmt in schedule_config.get("formats", ["pdf"])],
                delivery_methods=[DeliveryMethod(method) for method in schedule_config.get("delivery", ["email"])],
                recipients=schedule_config.get("recipients", []),
                delivery_config=schedule_config.get("delivery_config", {}),
                owner_id=schedule_config.get("owner_id", ""),
                priority=ReportPriority(schedule_config.get("priority", "medium")),
                conditional_generation=schedule_config.get("conditional_generation"),
                retention_period=schedule_config.get("retention_period", 2592000)
            )
            
            # Valider programmation
            if not await self._validate_schedule(scheduled_report):
                raise ValueError("Configuration programmation invalide")
            
            # Sauvegarder
            self.scheduled_reports[schedule_id] = scheduled_report
            await self._persist_scheduled_report(scheduled_report)
            
            logger.info(f"📋 Rapport programmé: {scheduled_report.report_name}")
            return schedule_id
            
        except Exception as e:
            logger.error(f"❌ Erreur programmation rapport: {e}")
            raise

    async def generate_report(self, 
                            template_id: str,
                            parameters: Dict[str, Any] = None,
                            output_formats: List[ReportFormat] = None,
                            requester_id: str = "") -> str:
        """Générer un rapport à la demande"""
        try:
            report_id = str(uuid.uuid4())
            
            # Vérifier template
            template = self.report_templates.get(template_id)
            if not template:
                raise ValueError(f"Template non trouvé: {template_id}")
            
            # Configuration génération
            generation_config = {
                "report_id": report_id,
                "template_id": template_id,
                "parameters": parameters or {},
                "output_formats": output_formats or [ReportFormat.PDF],
                "requester_id": requester_id,
                "priority": ReportPriority.HIGH,  # Reports à demande = haute priorité
                "generate_async": True
            }
            
            # Ajouter à la queue
            self.generation_queue.append(generation_config)
            
            logger.info(f"📋 Rapport ajouté à la queue: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"❌ Erreur génération rapport: {e}")
            raise

    async def generate_creator_report(self, creator_id: str, report_type: str = "analytics") -> str:
        """Générer rapport spécialisé créateur"""
        try:
            # Sélectionner template selon type
            if report_type == "analytics":
                template_id = "creator_analytics_template"
            elif report_type == "performance":
                template_id = "creator_performance_template"
            elif report_type == "monetization":
                template_id = "creator_monetization_template"
            else:
                raise ValueError(f"Type rapport créateur non supporté: {report_type}")
            
            # Paramètres spécialisés créateur
            parameters = {
                "creator_id": creator_id,
                "report_period": "last_30_days",
                "include_predictions": True,
                "include_benchmarking": True,
                "include_recommendations": True,
                "detailed_analytics": True
            }
            
            # Générer rapport
            report_id = await self.generate_report(
                template_id=template_id,
                parameters=parameters,
                output_formats=[ReportFormat.PDF, ReportFormat.HTML],
                requester_id=creator_id
            )
            
            logger.info(f"📋 Rapport créateur programmé: {report_type} pour {creator_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"❌ Erreur rapport créateur: {e}")
            raise

    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Obtenir statut d'un rapport"""
        try:
            # Vérifier rapports générés
            if report_id in self.generated_reports:
                report = self.generated_reports[report_id]
                return {
                    "report_id": report_id,
                    "status": "completed",
                    "generated_at": report.generated_at.isoformat(),
                    "generation_time": report.generation_time,
                    "formats_available": list(report.output_files.keys()),
                    "delivery_status": report.delivery_status,
                    "data_quality_score": report.data_quality_score,
                    "view_count": report.view_count,
                    "download_count": report.download_count
                }
            
            # Vérifier générations actives
            if report_id in self.active_generations:
                generation_info = self.active_generations[report_id]
                return {
                    "report_id": report_id,
                    "status": "generating",
                    "started_at": generation_info["started_at"].isoformat(),
                    "progress": generation_info.get("progress", 0),
                    "current_step": generation_info.get("current_step", "initializing"),
                    "estimated_completion": generation_info.get("estimated_completion")
                }
            
            # Vérifier queue
            for item in self.generation_queue:
                if item["report_id"] == report_id:
                    return {
                        "report_id": report_id,
                        "status": "queued",
                        "queue_position": list(self.generation_queue).index(item) + 1,
                        "estimated_start": "pending"
                    }
            
            return {
                "report_id": report_id,
                "status": "not_found",
                "error": "Rapport non trouvé"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut rapport {report_id}: {e}")
            return {"report_id": report_id, "status": "error", "error": str(e)}

    async def get_available_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """Obtenir templates disponibles"""
        try:
            templates = []
            
            for template in self.report_templates.values():
                if category and template.category != category:
                    continue
                
                template_info = {
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "type": template.report_type.value,
                    "category": template.category,
                    "tags": template.tags,
                    "version": template.version,
                    "customizable_sections": template.customizable_sections,
                    "required_parameters": list(template.parameter_definitions.keys()),
                    "created_at": template.created_at.isoformat()
                }
                templates.append(template_info)
            
            # Trier par nom
            templates.sort(key=lambda x: x["name"])
            
            return templates
            
        except Exception as e:
            logger.error(f"❌ Erreur liste templates: {e}")
            return []

    async def create_subscription(self, subscription_config: Dict[str, Any]) -> str:
        """Créer abonnement rapports"""
        try:
            subscription_id = str(uuid.uuid4())
            
            subscription = ReportSubscription(
                subscription_id=subscription_id,
                user_id=subscription_config["user_id"],
                subscription_name=subscription_config.get("name", "Mon Abonnement"),
                report_types=[ReportType(rt) for rt in subscription_config.get("report_types", [])],
                frequency=ReportSchedule(subscription_config.get("frequency", "weekly")),
                delivery_preferences=subscription_config.get("delivery_preferences", {}),
                content_filters=subscription_config.get("content_filters", {}),
                creator_filters=subscription_config.get("creator_filters", []),
                metrics_of_interest=subscription_config.get("metrics", []),
                custom_sections=subscription_config.get("custom_sections", []),
                visualization_preferences=subscription_config.get("visualization_preferences", {})
            )
            
            # Sauvegarder
            self.report_subscriptions[subscription_id] = subscription
            await self._persist_subscription(subscription)
            
            logger.info(f"📋 Abonnement créé: {subscription.subscription_name}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création abonnement: {e}")
            raise

    async def get_reporting_analytics(self) -> Dict[str, Any]:
        """Obtenir analytics du système de rapports"""
        try:
            analytics = {
                "system_overview": {
                    "templates_count": len(self.report_templates),
                    "scheduled_reports_count": len(self.scheduled_reports),
                    "generated_reports_count": len(self.generated_reports),
                    "active_subscriptions_count": len(self.report_subscriptions),
                    "queue_size": len(self.generation_queue),
                    "active_generations": len(self.active_generations)
                },
                
                "performance_metrics": self.orchestrator_metrics.copy(),
                
                "report_distribution": await self._get_report_type_distribution(),
                "format_usage": await self._get_format_usage_stats(),
                "delivery_stats": await self._get_delivery_method_stats(),
                
                "quality_metrics": {
                    "average_data_quality": await self._calculate_avg_data_quality(),
                    "average_completeness": await self._calculate_avg_completeness(),
                    "generation_success_rate": await self._calculate_generation_success_rate()
                },
                
                "usage_analytics": {
                    "most_popular_templates": await self._get_popular_templates(),
                    "peak_generation_hours": await self._get_peak_hours(),
                    "user_engagement": await self._get_user_engagement_stats()
                },
                
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Erreur analytics rapports: {e}")
            return {"error": str(e)}

    # ================== MÉTHODES PRIVÉES ==================

    def _initialize_default_templates(self):
        """Initialiser templates par défaut"""
        # Template rapport créateur
        creator_template = ReportTemplate(
            template_id="creator_analytics_template",
            name="Rapport Analytics Créateur",
            description="Analyse complète performance créateur",
            report_type=ReportType.CREATOR_ANALYTICS,
            sections=[
                {"name": "executive_summary", "title": "Résumé Exécutif"},
                {"name": "performance_metrics", "title": "Métriques Performance"},
                {"name": "audience_analysis", "title": "Analyse Audience"},
                {"name": "content_performance", "title": "Performance Contenu"},
                {"name": "revenue_analysis", "title": "Analyse Revenus"},
                {"name": "recommendations", "title": "Recommandations"}
            ],
            default_visualizations=[
                {"type": "line_chart", "title": "Évolution Followers"},
                {"type": "bar_chart", "title": "Performance Contenu"},
                {"type": "pie_chart", "title": "Sources Revenus"}
            ],
            required_data_sources=["creator_metrics", "content_data", "revenue_data"],
            category="creator",
            tags=["creator", "analytics", "performance"]
        )
        self.report_templates["creator_analytics_template"] = creator_template
        
        # Template rapport exécutif
        executive_template = ReportTemplate(
            template_id="executive_summary_template",
            name="Rapport Exécutif Plateforme",
            description="Vue d'ensemble exécutive de la plateforme",
            report_type=ReportType.EXECUTIVE_SUMMARY,
            sections=[
                {"name": "key_metrics", "title": "Métriques Clés"},
                {"name": "growth_analysis", "title": "Analyse Croissance"},
                {"name": "revenue_summary", "title": "Résumé Revenus"},
                {"name": "user_engagement", "title": "Engagement Utilisateurs"},
                {"name": "strategic_insights", "title": "Insights Stratégiques"}
            ],
            default_visualizations=[
                {"type": "dashboard", "title": "KPIs Plateforme"},
                {"type": "trend_chart", "title": "Tendances Croissance"}
            ],
            required_data_sources=["platform_metrics", "business_data"],
            category="executive",
            tags=["executive", "platform", "kpis"]
        )
        self.report_templates["executive_summary_template"] = executive_template

    async def _run_scheduled_reports(self):
        """Exécution rapports programmés"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for schedule in self.scheduled_reports.values():
                    if schedule.active and await self._should_generate_report(schedule, current_time):
                        await self._queue_scheduled_report(schedule)
                
                await asyncio.sleep(60)  # Vérification toutes les minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur exécution rapports programmés: {e}")
                await asyncio.sleep(300)

    async def _run_generation_queue(self):
        """Processeur queue génération"""
        while self.is_running:
            try:
                if len(self.active_generations) < self.config["max_concurrent_generations"] and self.generation_queue:
                    generation_config = self.generation_queue.popleft()
                    await self._start_report_generation(generation_config)
                else:
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"❌ Erreur processeur queue: {e}")
                await asyncio.sleep(10)

    async def _run_delivery_system(self):
        """Système de livraison rapports"""
        while self.is_running:
            try:
                await self._process_pending_deliveries()
                await asyncio.sleep(30)  # Toutes les 30 secondes
            except Exception as e:
                logger.error(f"❌ Erreur système livraison: {e}")
                await asyncio.sleep(60)

    async def _run_cache_maintenance(self):
        """Maintenance cache rapports"""
        while self.is_running:
            try:
                await self._clean_expired_cache()
                await asyncio.sleep(600)  # Toutes les 10 minutes
            except Exception as e:
                logger.error(f"❌ Erreur maintenance cache: {e}")
                await asyncio.sleep(300)

    async def _run_cleanup_service(self):
        """Service nettoyage rapports expirés"""
        while self.is_running:
            try:
                await self._cleanup_expired_reports()
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage: {e}")
                await asyncio.sleep(1800)

    async def _run_analytics_collector(self):
        """Collecteur analytics rapports"""
        while self.is_running:
            try:
                await self._collect_reporting_analytics()
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"❌ Erreur collection analytics: {e}")
                await asyncio.sleep(600)

    async def _run_quality_monitor(self):
        """Monitoring qualité rapports"""
        while self.is_running:
            try:
                await self._monitor_report_quality()
                await asyncio.sleep(900)  # Toutes les 15 minutes
            except Exception as e:
                logger.error(f"❌ Erreur monitoring qualité: {e}")
                await asyncio.sleep(1800)

    async def _validate_template(self, template: ReportTemplate) -> bool:
        """Valider template"""
        if not template.name or not template.sections:
            return False
        if not template.required_data_sources:
            return False
        return True

    async def _validate_schedule(self, schedule: ScheduledReport) -> bool:
        """Valider programmation"""
        if schedule.template_id not in self.report_templates:
            return False
        if not schedule.recipients and DeliveryMethod.EMAIL in schedule.delivery_methods:
            return False
        return True

    async def _persist_template(self, template: ReportTemplate):
        """Persister template"""
        try:
            if self.redis_client:
                key = f"reporting:template:{template.template_id}"
                data = {
                    "name": template.name,
                    "type": template.report_type.value,
                    "category": template.category,
                    "created_at": template.created_at.isoformat()
                }
                await self.redis_client.hset(key, mapping=data)
                await self.redis_client.expire(key, 2592000)  # 30 jours
        except Exception as e:
            logger.error(f"❌ Erreur persistence template: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Récupérer métriques orchestrateur"""
        return {
            "orchestrator_type": "reporting_orchestrator",
            "status": "running" if self.is_running else "stopped",
            "templates_count": len(self.report_templates),
            "scheduled_reports_count": len(self.scheduled_reports),
            "generated_reports_count": len(self.generated_reports),
            "subscriptions_count": len(self.report_subscriptions),
            "queue_size": len(self.generation_queue),
            "active_generations": len(self.active_generations),
            "performance_metrics": self.orchestrator_metrics,
            "cache_sizes": {
                "data_cache": len(self.data_cache),
                "visualization_cache": len(self.visualization_cache),
                "template_cache": len(self.template_cache)
            }
        }