"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Audit Service Template for IA Chéries Creator Economy Platform
Enterprise audit service with comprehensive logging, compliance tracking and forensic analysis
"""

import asyncio
import json
import hashlib
import gzip
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from pydantic import BaseModel, validator
from redis import Redis
import elasticsearch
from pymongo import MongoClient
import logging
from prometheus_client import Counter, Histogram, Gauge


class AuditEventType(str, Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    SECURITY_EVENT = "security_event"
    PAYMENT_TRANSACTION = "payment_transaction"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PUBLISH = "content_publish"
    COLLABORATION_INVITE = "collaboration_invite"
    API_CALL = "api_call"
    ERROR_EVENT = "error_event"


class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceFramework(str, Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    SOC2 = "soc2"


@dataclass
class AuditConfig:
    """Configuration du service d'audit"""
    enable_real_time_monitoring: bool = True
    enable_compliance_tracking: bool = True
    enable_forensic_analysis: bool = True
    enable_data_retention: bool = True
    
    # Retention policies
    retention_days: int = 2555  # 7 years for compliance
    archive_after_days: int = 365
    compression_enabled: bool = True
    
    # Storage backends
    primary_storage: str = "elasticsearch"  # elasticsearch, mongodb, postgresql
    backup_storage: str = "mongodb"
    
    # Compliance frameworks
    compliance_frameworks: List[ComplianceFramework] = field(
        default_factory=lambda: [ComplianceFramework.GDPR, ComplianceFramework.SOC2]
    )
    
    # Alerting
    real_time_alerts: bool = True
    alert_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "failed_logins_per_hour": 10,
        "privilege_escalations_per_day": 5,
        "data_exports_per_hour": 20,
        "api_errors_per_minute": 100
    })
    
    # Performance
    batch_size: int = 1000
    async_processing: bool = True


class AuditEvent(BaseModel):
    """Événement d'audit"""
    event_id: str = None
    timestamp: datetime = None
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO
    
    # User context
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    session_id: Optional[str] = None
    
    # Request context
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    api_endpoint: Optional[str] = None
    http_method: Optional[str] = None
    
    # Event details
    description: str
    details: Dict[str, Any] = {}
    
    # Data context
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    old_values: Dict[str, Any] = {}
    new_values: Dict[str, Any] = {}
    
    # Compliance tags
    compliance_tags: List[ComplianceFramework] = []
    sensitive_data: bool = False
    
    # Technical context
    service_name: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    def __init__(self, **data):
        if 'event_id' not in data or not data['event_id']:
            data['event_id'] = str(uuid.uuid4())
        if 'timestamp' not in data or not data['timestamp']:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class AuditQuery(BaseModel):
    """Requête de recherche d'audit"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: List[AuditEventType] = []
    user_ids: List[str] = []
    resource_types: List[str] = []
    severity_levels: List[AuditSeverity] = []
    compliance_frameworks: List[ComplianceFramework] = []
    search_text: Optional[str] = None
    limit: int = 100
    offset: int = 0


class ComplianceReport(BaseModel):
    """Rapport de conformité"""
    report_id: str
    framework: ComplianceFramework
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    
    # Compliance metrics
    total_events: int
    compliant_events: int
    non_compliant_events: int
    compliance_score: float
    
    # Event breakdown
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    
    # Risk assessment
    high_risk_events: List[Dict[str, Any]]
    recommendations: List[str]
    
    # Data protection metrics (GDPR specific)
    data_access_requests: int = 0
    data_deletion_requests: int = 0
    data_portability_requests: int = 0
    consent_events: int = 0


class AuditServiceTemplate:
    """
    Template de service d'audit enterprise pour IA Chéries
    
    Fonctionnalités:
    - Audit complet de toutes les activités
    - Compliance tracking (GDPR, SOC2, etc.)
    - Real-time monitoring et alerting
    - Forensic analysis capabilities
    - Data retention et archiving
    - Recherche et reporting avancés
    - Intégrité et non-répudiation
    - Performance optimisée
    """
    
    def __init__(self, config: AuditConfig = None):
        self.config = config or AuditConfig()
        self.app = FastAPI(
            title="IA Chéries Audit Service",
            description="Enterprise audit service with compliance tracking",
            version="1.0.0"
        )
        
        # Storage backends
        self.redis = Redis(host='localhost', port=6379, db=6, decode_responses=True)
        self.es_client = None
        self.mongo_client = None
        
        # Initialize storage
        self._initialize_storage()
        
        # Event queue pour traitement async
        self.event_queue = asyncio.Queue()
        
        # Métriques Prometheus
        self.audit_events_total = Counter('audit_events_total', ['event_type', 'severity'])
        self.audit_processing_duration = Histogram('audit_processing_duration_seconds', ['operation'])
        self.compliance_score = Gauge('audit_compliance_score', ['framework'])
        self.storage_operations = Counter('audit_storage_operations_total', ['backend', 'operation', 'status'])
        
        # Setup
        self._setup_routes()
        if self.config.async_processing:
            self._start_async_processor()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_storage(self):
        """Initialisation des backends de stockage"""
        try:
            # Elasticsearch
            if self.config.primary_storage == "elasticsearch":
                self.es_client = elasticsearch.Elasticsearch([{'host': 'localhost', 'port': 9200}])
                self._create_elasticsearch_indices()
            
            # MongoDB
            if self.config.backup_storage == "mongodb" or self.config.primary_storage == "mongodb":
                self.mongo_client = MongoClient('mongodb://localhost:27017/')
                self.mongo_db = self.mongo_client['ainflue_audit']
                self._create_mongodb_collections()
            
            self.logger.info("Storage backends initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Storage initialization failed: {str(e)}")

    def _create_elasticsearch_indices(self):
        """Création des indices Elasticsearch"""
        if not self.es_client:
            return
        
        try:
            # Index pour événements d'audit
            audit_mapping = {
                "mappings": {
                    "properties": {
                        "event_id": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "event_type": {"type": "keyword"},
                        "severity": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "user_email": {"type": "keyword"},
                        "source_ip": {"type": "ip"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "details": {"type": "object"},
                        "resource_type": {"type": "keyword"},
                        "resource_id": {"type": "keyword"},
                        "compliance_tags": {"type": "keyword"},
                        "sensitive_data": {"type": "boolean"}
                    }
                },
                "settings": {
                    "number_of_shards": 2,
                    "number_of_replicas": 1,
                    "index.lifecycle.name": "audit_policy",
                    "index.lifecycle.rollover_alias": "audit_events"
                }
            }
            
            index_name = f"audit_events_{datetime.now().strftime('%Y-%m')}"
            
            if not self.es_client.indices.exists(index=index_name):
                self.es_client.indices.create(index=index_name, body=audit_mapping)
                self.logger.info(f"Created Elasticsearch index: {index_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to create Elasticsearch indices: {str(e)}")

    def _create_mongodb_collections(self):
        """Création des collections MongoDB"""
        if not self.mongo_client:
            return
        
        try:
            # Collection pour événements d'audit
            audit_collection = self.mongo_db['audit_events']
            
            # Index pour performance
            audit_collection.create_index([
                ("timestamp", -1),
                ("event_type", 1),
                ("user_id", 1)
            ])
            
            audit_collection.create_index([("event_id", 1)], unique=True)
            audit_collection.create_index([("compliance_tags", 1)])
            
            # Collection pour rapports de conformité
            reports_collection = self.mongo_db['compliance_reports']
            reports_collection.create_index([("report_id", 1)], unique=True)
            reports_collection.create_index([("framework", 1), ("generated_at", -1)])
            
            self.logger.info("MongoDB collections created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB collections: {str(e)}")

    def _start_async_processor(self):
        """Démarre le processeur d'événements async"""
        async def process_events():
            while True:
                try:
                    # Traiter événements par batch
                    events = []
                    for _ in range(self.config.batch_size):
                        try:
                            event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                            events.append(event)
                        except asyncio.TimeoutError:
                            break
                    
                    if events:
                        await self._process_event_batch(events)
                    
                except Exception as e:
                    self.logger.error(f"Event processing error: {str(e)}")
                    await asyncio.sleep(1)
        
        # Démarrer le processeur en arrière-plan
        asyncio.create_task(process_events())

    def _setup_routes(self):
        """Configuration des routes du service"""
        
        @self.app.post("/audit/events")
        async def log_audit_event(event: AuditEvent, background_tasks: BackgroundTasks):
            """Enregistrer un événement d'audit"""
            with self.audit_processing_duration.labels(operation='log_event').time():
                try:
                    if self.config.async_processing:
                        await self.event_queue.put(event)
                    else:
                        await self._store_event(event)
                    
                    # Vérifier alertes en temps réel
                    if self.config.real_time_alerts:
                        background_tasks.add_task(self._check_real_time_alerts, event)
                    
                    # Métriques
                    self.audit_events_total.labels(
                        event_type=event.event_type.value,
                        severity=event.severity.value
                    ).inc()
                    
                    return {"message": "Event logged successfully", "event_id": event.event_id}
                    
                except Exception as e:
                    self.logger.error(f"Failed to log audit event: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to log audit event")

        @self.app.post("/audit/events/batch")
        async def log_audit_events_batch(events: List[AuditEvent]):
            """Enregistrer plusieurs événements d'audit"""
            with self.audit_processing_duration.labels(operation='log_batch').time():
                try:
                    if self.config.async_processing:
                        for event in events:
                            await self.event_queue.put(event)
                    else:
                        await self._process_event_batch(events)
                    
                    return {"message": f"{len(events)} events logged successfully"}
                    
                except Exception as e:
                    self.logger.error(f"Failed to log audit events batch: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to log audit events")

        @self.app.post("/audit/search")
        async def search_audit_events(query: AuditQuery):
            """Rechercher dans les événements d'audit"""
            with self.audit_processing_duration.labels(operation='search').time():
                try:
                    results = await self._search_events(query)
                    return results
                    
                except Exception as e:
                    self.logger.error(f"Audit search failed: {str(e)}")
                    raise HTTPException(status_code=500, detail="Search failed")

        @self.app.get("/audit/events/{event_id}")
        async def get_audit_event(event_id: str):
            """Récupérer un événement d'audit spécifique"""
            try:
                event = await self._get_event_by_id(event_id)
                if not event:
                    raise HTTPException(status_code=404, detail="Event not found")
                
                return event
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get audit event: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve event")

        @self.app.get("/audit/compliance/report/{framework}")
        async def generate_compliance_report(
            framework: ComplianceFramework,
            start_date: datetime,
            end_date: datetime,
            background_tasks: BackgroundTasks
        ):
            """Générer rapport de conformité"""
            try:
                report = await self._generate_compliance_report(framework, start_date, end_date)
                
                # Stocker le rapport
                background_tasks.add_task(self._store_compliance_report, report)
                
                return report
                
            except Exception as e:
                self.logger.error(f"Failed to generate compliance report: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate report")

        @self.app.get("/audit/analytics/dashboard")
        async def get_audit_dashboard(hours: int = 24):
            """Dashboard d'analytics d'audit"""
            try:
                dashboard_data = await self._generate_dashboard_data(hours)
                return dashboard_data
                
            except Exception as e:
                self.logger.error(f"Failed to generate dashboard: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate dashboard")

        @self.app.get("/audit/forensic/timeline")
        async def forensic_timeline(
            user_id: Optional[str] = None,
            resource_id: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
        ):
            """Timeline forensique pour investigation"""
            try:
                timeline = await self._generate_forensic_timeline(user_id, resource_id, start_date, end_date)
                return timeline
                
            except Exception as e:
                self.logger.error(f"Failed to generate forensic timeline: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate timeline")

        @self.app.post("/audit/retention/archive")
        async def archive_old_events(background_tasks: BackgroundTasks):
            """Archiver les anciens événements"""
            try:
                background_tasks.add_task(self._archive_old_events)
                return {"message": "Archive process started"}
                
            except Exception as e:
                self.logger.error(f"Failed to start archive process: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to start archive")

        @self.app.get("/audit/health")
        async def health_check():
            """Health check du service d'audit"""
            try:
                health_status = await self._check_health()
                return health_status
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _store_event(self, event: AuditEvent):
        """Stockage d'un événement d'audit"""
        try:
            event_dict = event.dict()
            
            # Stocker dans le backend principal
            if self.config.primary_storage == "elasticsearch":
                await self._store_to_elasticsearch(event_dict)
            elif self.config.primary_storage == "mongodb":
                await self._store_to_mongodb(event_dict)
            
            # Stocker dans le backup
            if self.config.backup_storage == "mongodb" and self.config.primary_storage != "mongodb":
                await self._store_to_mongodb(event_dict)
            
            # Cache Redis pour événements récents
            await self.redis.lpush("recent_audit_events", json.dumps(event_dict, default=str))
            await self.redis.ltrim("recent_audit_events", 0, 999)  # Garder 1000 derniers
            
        except Exception as e:
            self.logger.error(f"Failed to store event: {str(e)}")
            raise

    async def _store_to_elasticsearch(self, event_dict: Dict):
        """Stockage dans Elasticsearch"""
        if not self.es_client:
            return
        
        try:
            index_name = f"audit_events_{datetime.now().strftime('%Y-%m')}"
            
            self.es_client.index(
                index=index_name,
                body=event_dict,
                id=event_dict["event_id"]
            )
            
            self.storage_operations.labels(
                backend='elasticsearch',
                operation='store',
                status='success'
            ).inc()
            
        except Exception as e:
            self.storage_operations.labels(
                backend='elasticsearch',
                operation='store',
                status='error'
            ).inc()
            raise e

    async def _store_to_mongodb(self, event_dict: Dict):
        """Stockage dans MongoDB"""
        if not self.mongo_client:
            return
        
        try:
            collection = self.mongo_db['audit_events']
            
            # Convertir datetime pour MongoDB
            if isinstance(event_dict.get('timestamp'), str):
                event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
            
            collection.insert_one(event_dict)
            
            self.storage_operations.labels(
                backend='mongodb',
                operation='store',
                status='success'
            ).inc()
            
        except Exception as e:
            self.storage_operations.labels(
                backend='mongodb',
                operation='store',
                status='error'
            ).inc()
            raise e

    async def _process_event_batch(self, events: List[AuditEvent]):
        """Traitement par batch d'événements"""
        try:
            # Préparer données pour stockage bulk
            event_dicts = [event.dict() for event in events]
            
            # Stockage bulk dans Elasticsearch
            if self.config.primary_storage == "elasticsearch" and self.es_client:
                await self._bulk_store_elasticsearch(event_dicts)
            
            # Stockage bulk dans MongoDB
            if self.config.backup_storage == "mongodb" and self.mongo_client:
                await self._bulk_store_mongodb(event_dicts)
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")

    async def _bulk_store_elasticsearch(self, event_dicts: List[Dict]):
        """Stockage bulk dans Elasticsearch"""
        try:
            from elasticsearch.helpers import bulk
            
            actions = []
            index_name = f"audit_events_{datetime.now().strftime('%Y-%m')}"
            
            for event_dict in event_dicts:
                actions.append({
                    "_index": index_name,
                    "_id": event_dict["event_id"],
                    "_source": event_dict
                })
            
            bulk(self.es_client, actions)
            
        except Exception as e:
            self.logger.error(f"Elasticsearch bulk store failed: {str(e)}")

    async def _bulk_store_mongodb(self, event_dicts: List[Dict]):
        """Stockage bulk dans MongoDB"""
        try:
            collection = self.mongo_db['audit_events']
            
            # Convertir timestamps
            for event_dict in event_dicts:
                if isinstance(event_dict.get('timestamp'), str):
                    event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
            
            collection.insert_many(event_dicts)
            
        except Exception as e:
            self.logger.error(f"MongoDB bulk store failed: {str(e)}")

    async def _search_events(self, query: AuditQuery) -> Dict[str, Any]:
        """Recherche d'événements d'audit"""
        if self.config.primary_storage == "elasticsearch" and self.es_client:
            return await self._search_elasticsearch(query)
        elif self.config.primary_storage == "mongodb" and self.mongo_client:
            return await self._search_mongodb(query)
        else:
            # Fallback sur Redis
            return await self._search_redis(query)

    async def _search_elasticsearch(self, query: AuditQuery) -> Dict[str, Any]:
        """Recherche dans Elasticsearch"""
        try:
            es_query = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}],
                "from": query.offset,
                "size": query.limit
            }
            
            # Filtres temporels
            if query.start_date or query.end_date:
                date_range = {}
                if query.start_date:
                    date_range["gte"] = query.start_date.isoformat()
                if query.end_date:
                    date_range["lte"] = query.end_date.isoformat()
                
                es_query["query"]["bool"]["must"].append({
                    "range": {"timestamp": date_range}
                })
            
            # Filtres par type d'événement
            if query.event_types:
                es_query["query"]["bool"]["must"].append({
                    "terms": {"event_type": [et.value for et in query.event_types]}
                })
            
            # Filtres par utilisateur
            if query.user_ids:
                es_query["query"]["bool"]["must"].append({
                    "terms": {"user_id": query.user_ids}
                })
            
            # Recherche textuelle
            if query.search_text:
                es_query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query.search_text,
                        "fields": ["description", "details.*"]
                    }
                })
            
            # Exécuter recherche
            response = self.es_client.search(
                index="audit_events_*",
                body=es_query
            )
            
            return {
                "total": response["hits"]["total"]["value"],
                "events": [hit["_source"] for hit in response["hits"]["hits"]]
            }
            
        except Exception as e:
            self.logger.error(f"Elasticsearch search failed: {str(e)}")
            return {"total": 0, "events": []}

    async def _generate_compliance_report(
        self, framework: ComplianceFramework, start_date: datetime, end_date: datetime
    ) -> ComplianceReport:
        """Génération de rapport de conformité"""
        try:
            # Rechercher tous les événements de la période
            query = AuditQuery(
                start_date=start_date,
                end_date=end_date,
                compliance_frameworks=[framework],
                limit=10000
            )
            
            search_results = await self._search_events(query)
            events = search_results["events"]
            
            # Analyser conformité
            total_events = len(events)
            compliant_events = 0
            high_risk_events = []
            
            events_by_type = {}
            events_by_severity = {}
            
            for event in events:
                # Compter par type
                event_type = event.get("event_type", "unknown")
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                
                # Compter par sévérité
                severity = event.get("severity", "info")
                events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
                
                # Vérifier conformité
                if self._is_event_compliant(event, framework):
                    compliant_events += 1
                else:
                    if severity in ["error", "critical"]:
                        high_risk_events.append({
                            "event_id": event.get("event_id"),
                            "timestamp": event.get("timestamp"),
                            "event_type": event_type,
                            "description": event.get("description", "")
                        })
            
            # Calculer score de conformité
            compliance_score = (compliant_events / total_events * 100) if total_events > 0 else 100
            
            # Générer recommandations
            recommendations = self._generate_compliance_recommendations(framework, events, compliance_score)
            
            # Métriques spécifiques GDPR
            gdpr_metrics = {}
            if framework == ComplianceFramework.GDPR:
                gdpr_metrics = {
                    "data_access_requests": len([e for e in events if e.get("event_type") == "data_access"]),
                    "data_deletion_requests": len([e for e in events if e.get("event_type") == "data_deletion"]),
                    "data_portability_requests": len([e for e in events if "portability" in e.get("description", "").lower()]),
                    "consent_events": len([e for e in events if "consent" in e.get("description", "").lower()])
                }
            
            report = ComplianceReport(
                report_id=str(uuid.uuid4()),
                framework=framework,
                period_start=start_date,
                period_end=end_date,
                generated_at=datetime.utcnow(),
                total_events=total_events,
                compliant_events=compliant_events,
                non_compliant_events=total_events - compliant_events,
                compliance_score=compliance_score,
                events_by_type=events_by_type,
                events_by_severity=events_by_severity,
                high_risk_events=high_risk_events[:10],  # Top 10
                recommendations=recommendations,
                **gdpr_metrics
            )
            
            # Mettre à jour métrique
            self.compliance_score.labels(framework=framework.value).set(compliance_score)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            raise

    def _is_event_compliant(self, event: Dict, framework: ComplianceFramework) -> bool:
        """Vérification de conformité d'un événement"""
        # Logic spécifique par framework
        if framework == ComplianceFramework.GDPR:
            # Vérifier que les accès aux données sensibles sont loggés
            if event.get("sensitive_data") and not event.get("user_id"):
                return False
            
            # Vérifier consentement pour traitement de données
            if event.get("event_type") == "data_modification" and not event.get("details", {}).get("consent_verified"):
                return False
        
        elif framework == ComplianceFramework.SOC2:
            # Vérifier contrôles d'accès
            if event.get("event_type") in ["permission_change", "system_config_change"]:
                if not event.get("details", {}).get("approved_by"):
                    return False
        
        return True

    def _generate_compliance_recommendations(
        self, framework: ComplianceFramework, events: List[Dict], score: float
    ) -> List[str]:
        """Génération de recommandations de conformité"""
        recommendations = []
        
        if score < 90:
            recommendations.append("Améliorer les contrôles d'accès et l'audit des modifications")
        
        if framework == ComplianceFramework.GDPR:
            sensitive_data_events = [e for e in events if e.get("sensitive_data")]
            if len(sensitive_data_events) > 100:
                recommendations.append("Mettre en place des contrôles renforcés pour les données sensibles")
        
        if any(e.get("severity") == "critical" for e in events):
            recommendations.append("Établir des procédures de réponse aux incidents critiques")
        
        return recommendations

    async def _check_real_time_alerts(self, event: AuditEvent):
        """Vérification des alertes en temps réel"""
        try:
            alerts_triggered = []
            
            # Alertes par type d'événement
            if event.event_type == AuditEventType.USER_LOGIN and event.severity == AuditSeverity.ERROR:
                # Compter échecs de connexion par heure
                failed_logins = await self._count_events_in_period(
                    event_type=AuditEventType.USER_LOGIN,
                    severity=AuditSeverity.ERROR,
                    hours=1,
                    user_id=event.user_id
                )
                
                if failed_logins >= self.config.alert_thresholds["failed_logins_per_hour"]:
                    alerts_triggered.append("Multiple failed login attempts detected")
            
            # Traitement des alertes
            for alert in alerts_triggered:
                await self._send_alert(alert, event)
                
        except Exception as e:
            self.logger.error(f"Real-time alert check failed: {str(e)}")

    async def _send_alert(self, alert_message: str, event: AuditEvent):
        """Envoi d'alerte"""
        alert_data = {
            "alert_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "message": alert_message,
            "event_id": event.event_id,
            "severity": event.severity.value,
            "user_id": event.user_id
        }
        
        # Stocker l'alerte
        await self.redis.lpush("security_alerts", json.dumps(alert_data))
        
        # Log de l'alerte
        self.logger.warning(f"Security alert: {alert_message} (Event: {event.event_id})")

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_audit_service(config: AuditConfig = None) -> FastAPI:
    """
    Factory pour créer service d'audit
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    audit_service = AuditServiceTemplate(config)
    return audit_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = AuditConfig(
        enable_real_time_monitoring=True,
        enable_compliance_tracking=True,
        retention_days=2555,  # 7 years
        primary_storage="elasticsearch"
    )
    
    app = create_audit_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )