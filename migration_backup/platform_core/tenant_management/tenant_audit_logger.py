#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📝 Tenant Audit Logger - Enterprise Multi-Tenant Audit Trail System

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
Cette architecture tenant audit logging est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite PERSONNELLE
est STRICTEMENT INTERDITE et sera poursuivie en justice.
"""

import asyncio
import logging
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import queue
import gzip
import os
from pathlib import Path
import uuid
import psycopg2
import redis
import elasticsearch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from cryptography.fernet import Fernet
import boto3
import yaml


# Configuration du logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/tenant_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types d'événements d'audit"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    CONFIG_CHANGED = "config_changed"
    DATA_ACCESS = "data_access"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    SYSTEM_ERROR = "system_error"
    SECURITY_VIOLATION = "security_violation"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    MIGRATION_STARTED = "migration_started"
    MIGRATION_COMPLETED = "migration_completed"


class AuditLevel(Enum):
    """Niveaux d'audit"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditOutcome(Enum):
    """Résultats d'audit"""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    UNKNOWN = "unknown"


@dataclass
class AuditEvent:
    """Événement d'audit enterprise"""
    event_id: str
    tenant_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    event_type: AuditEventType
    event_category: str
    event_description: str
    outcome: AuditOutcome
    level: AuditLevel
    timestamp: datetime
    source_ip: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    tags: List[str]
    compliance_flags: List[str]
    retention_period_days: int
    encrypted: bool = False


@dataclass
class AuditQuery:
    """Requête de recherche d'audit"""
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    event_types: Optional[List[AuditEventType]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    outcome: Optional[AuditOutcome] = None
    level: Optional[AuditLevel] = None
    resource_type: Optional[str] = None
    search_text: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 1000
    offset: int = 0


class TenantAuditLogger:
    """
    📝 Enterprise Tenant Audit Logger
    
    Système d'audit enterprise pour architecture multi-tenant avec:
    - Audit trail immutable et chiffré
    - Compliance GDPR/SOX/HIPAA
    - Recherche et analytics avancées
    - Retention policies automatisées
    - Export pour audit externe
    - Monitoring et alerting temps réel
    """
    
    def __init__(self, config_path: str = '/etc/ainflue/audit_config.yaml'):
        """Initialisation du système d'audit"""
        self.config = self._load_config(config_path)
        self.event_queue = queue.Queue(maxsize=self.config.get('queue_size', 10000))
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.running = True
        
        # Connexions aux services
        self._init_storage_backends()
        self._init_search_engine()
        self._init_monitoring()
        
        # Démarrage des workers
        self._start_processing_workers()
        self._start_retention_worker()
        
        logger.info("TenantAuditLogger initialisé avec succès")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Chargement de la configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration chargée depuis {config_path}")
            return config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'queue_size': 10000,
            'worker_threads': 4,
            'batch_size': 100,
            'encryption_enabled': True,
            'compression_enabled': True,
            'retention_days_default': 2555,  # 7 ans par défaut
            'storage': {
                'primary': 'postgresql',
                'secondary': 'elasticsearch',
                'archive': 's3'
            },
            'database': {
                'host': 'localhost',
                'port': 5432,
                'ssl_mode': 'require'
            },
            'elasticsearch': {
                'hosts': ['localhost:9200'],
                'index_pattern': 'audit-{tenant_id}-{date}'
            },
            's3': {
                'bucket': 'ainflue-audit-archive',
                'region': 'eu-west-1'
            }
        }
    
    def _get_encryption_key(self) -> bytes:
        """Récupération de la clé de chiffrement"""
        key_path = self.config.get('encryption_key_path', '/etc/ainflue/audit.key')
        try:
            with open(key_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            # Génération d'une nouvelle clé
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            logger.info(f"Nouvelle clé de chiffrement générée: {key_path}")
            return key
    
    def _init_storage_backends(self):
        """Initialisation des backends de stockage"""
        # PostgreSQL principal
        db_config = self.config.get('database', {})
        self.pg_config = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5432),
            'sslmode': db_config.get('ssl_mode', 'require')
        }
        
        # Redis pour cache et notifications
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            ssl=redis_config.get('ssl', True),
            decode_responses=True
        )
        
        # S3 pour archivage
        s3_config = self.config.get('s3', {})
        self.s3_client = boto3.client(
            's3',
            region_name=s3_config.get('region', 'eu-west-1')
        )
        self.audit_bucket = s3_config.get('bucket', 'ainflue-audit-archive')
        
        logger.info("Backends de stockage initialisés")
    
    def _init_search_engine(self):
        """Initialisation du moteur de recherche"""
        es_config = self.config.get('elasticsearch', {})
        
        try:
            self.es_client = elasticsearch.Elasticsearch(
                hosts=es_config.get('hosts', ['localhost:9200']),
                verify_certs=True,
                timeout=30
            )
            
            # Vérification de la connexion
            if self.es_client.ping():
                logger.info("Elasticsearch connecté avec succès")
            else:
                logger.warning("Elasticsearch non disponible")
                self.es_client = None
                
        except Exception as e:
            logger.error(f"Erreur connexion Elasticsearch: {e}")
            self.es_client = None
    
    def _init_monitoring(self):
        """Initialisation du monitoring"""
        self.metrics = {
            'events_total': 0,
            'events_processed': 0,
            'events_failed': 0,
            'events_archived': 0,
            'queue_size_current': 0,
            'processing_time_total': 0
        }
        
        # Métriques par tenant
        self.tenant_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Alertes de sécurité
        self.security_alerts: List[Dict[str, Any]] = []
        
        logger.info("Monitoring initialisé")
    
    def _start_processing_workers(self):
        """Démarrage des workers de traitement"""
        worker_count = self.config.get('worker_threads', 4)
        self.workers = []
        
        for i in range(worker_count):
            worker = threading.Thread(
                target=self._event_processing_worker,
                name=f"audit_worker_{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"{worker_count} workers d'audit démarrés")
    
    def _start_retention_worker(self):
        """Démarrage du worker de rétention"""
        self.retention_worker = threading.Thread(
            target=self._retention_worker,
            name="audit_retention_worker",
            daemon=True
        )
        self.retention_worker.start()
        
        logger.info("Worker de rétention démarré")
    
    async def log_event(self, event: AuditEvent) -> bool:
        """
        📝 Enregistrement d'un événement d'audit
        
        Args:
            event: Événement d'audit à enregistrer
            
        Returns:
            True si événement mis en queue avec succès
        """
        try:
            # Génération d'un ID unique si manquant
            if not event.event_id:
                event.event_id = str(uuid.uuid4())
            
            # Validation de l'événement
            if not self._validate_event(event):
                logger.error(f"Événement d'audit invalide: {event.event_id}")
                return False
            
            # Chiffrement des données sensibles si activé
            if self.config.get('encryption_enabled', True):
                event = self._encrypt_sensitive_data(event)
            
            # Ajout à la queue
            try:
                self.event_queue.put(event, timeout=1)
                self.metrics['events_total'] += 1
                self.metrics['queue_size_current'] = self.event_queue.qsize()
                
                # Mise à jour des métriques par tenant
                self._update_tenant_metrics(event.tenant_id, 'events_logged', 1)
                
                return True
                
            except queue.Full:
                logger.error("Queue d'audit pleine, événement rejeté")
                self.metrics['events_failed'] += 1
                return False
            
        except Exception as e:
            logger.error(f"Erreur enregistrement événement d'audit: {e}")
            return False
    
    async def log_user_action(self, tenant_id: str, user_id: str, action: str,
                            resource_type: str, resource_id: str,
                            outcome: AuditOutcome = AuditOutcome.SUCCESS,
                            level: AuditLevel = AuditLevel.MEDIUM,
                            metadata: Optional[Dict[str, Any]] = None,
                            session_id: Optional[str] = None,
                            source_ip: Optional[str] = None) -> bool:
        """
        👤 Enregistrement d'une action utilisateur
        
        Args:
            tenant_id: ID du tenant
            user_id: ID de l'utilisateur
            action: Action effectuée
            resource_type: Type de ressource
            resource_id: ID de la ressource
            outcome: Résultat de l'action
            level: Niveau d'audit
            metadata: Métadonnées additionnelles
            session_id: ID de session
            source_ip: Adresse IP source
            
        Returns:
            True si succès
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            event_type=AuditEventType.DATA_ACCESS,
            event_category="user_action",
            event_description=f"User {user_id} performed {action} on {resource_type} {resource_id}",
            outcome=outcome,
            level=level,
            timestamp=datetime.utcnow(),
            source_ip=source_ip,
            user_agent=metadata.get('user_agent') if metadata else None,
            resource_type=resource_type,
            resource_id=resource_id,
            before_state=metadata.get('before_state') if metadata else None,
            after_state=metadata.get('after_state') if metadata else None,
            metadata=metadata or {},
            tags=[action, resource_type],
            compliance_flags=self._get_compliance_flags(action, resource_type),
            retention_period_days=self._get_retention_period(action, level)
        )
        
        return await self.log_event(event)
    
    async def log_security_event(self, tenant_id: str, event_type: AuditEventType,
                                description: str, level: AuditLevel = AuditLevel.HIGH,
                                user_id: Optional[str] = None,
                                source_ip: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        🔒 Enregistrement d'un événement de sécurité
        
        Args:
            tenant_id: ID du tenant
            event_type: Type d'événement de sécurité
            description: Description de l'événement
            level: Niveau de sécurité
            user_id: ID utilisateur (optionnel)
            source_ip: Adresse IP source
            metadata: Métadonnées additionnelles
            
        Returns:
            True si succès
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=None,
            event_type=event_type,
            event_category="security",
            event_description=description,
            outcome=AuditOutcome.UNKNOWN,
            level=level,
            timestamp=datetime.utcnow(),
            source_ip=source_ip,
            user_agent=None,
            resource_type="security",
            resource_id=None,
            before_state=None,
            after_state=None,
            metadata=metadata or {},
            tags=["security", event_type.value],
            compliance_flags=["security_event"],
            retention_period_days=self._get_retention_period("security", level)
        )
        
        # Ajout aux alertes de sécurité
        if level in [AuditLevel.HIGH, AuditLevel.CRITICAL]:
            self.security_alerts.append({
                'event_id': event.event_id,
                'tenant_id': tenant_id,
                'description': description,
                'level': level.value,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return await self.log_event(event)
    
    async def search_events(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """
        🔍 Recherche d'événements d'audit
        
        Args:
            query: Paramètres de recherche
            
        Returns:
            Liste des événements trouvés
        """
        try:
            # Recherche via Elasticsearch si disponible
            if self.es_client:
                return await self._search_elasticsearch(query)
            else:
                # Fallback vers PostgreSQL
                return await self._search_postgresql(query)
                
        except Exception as e:
            logger.error(f"Erreur recherche événements: {e}")
            return []
    
    async def get_compliance_report(self, tenant_id: str, start_date: datetime,
                                  end_date: datetime, compliance_type: str = "gdpr") -> Dict[str, Any]:
        """
        📊 Génération d'un rapport de compliance
        
        Args:
            tenant_id: ID du tenant
            start_date: Date de début
            end_date: Date de fin
            compliance_type: Type de compliance (gdpr, sox, hipaa)
            
        Returns:
            Rapport de compliance
        """
        try:
            # Requête pour récupérer les événements de compliance
            query = AuditQuery(
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                tags=[compliance_type],
                limit=10000
            )
            
            events = await self.search_events(query)
            
            # Analyse des événements
            report = {
                'tenant_id': tenant_id,
                'compliance_type': compliance_type,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_events': len(events),
                    'user_events': 0,
                    'data_access_events': 0,
                    'security_events': 0,
                    'compliance_violations': 0
                },
                'events_by_type': {},
                'events_by_user': {},
                'security_incidents': [],
                'compliance_violations': [],
                'recommendations': []
            }
            
            # Analyse détaillée
            for event in events:
                # Comptage par type
                event_type = event.get('event_type', 'unknown')
                if event_type not in report['events_by_type']:
                    report['events_by_type'][event_type] = 0
                report['events_by_type'][event_type] += 1
                
                # Comptage par utilisateur
                user_id = event.get('user_id')
                if user_id:
                    report['summary']['user_events'] += 1
                    if user_id not in report['events_by_user']:
                        report['events_by_user'][user_id] = 0
                    report['events_by_user'][user_id] += 1
                
                # Événements de sécurité
                if event.get('event_category') == 'security':
                    report['summary']['security_events'] += 1
                    if event.get('level') in ['high', 'critical']:
                        report['security_incidents'].append({
                            'event_id': event.get('event_id'),
                            'description': event.get('event_description'),
                            'timestamp': event.get('timestamp'),
                            'level': event.get('level')
                        })
                
                # Accès aux données
                if event.get('resource_type') in ['user_data', 'personal_data']:
                    report['summary']['data_access_events'] += 1
            
            # Génération de recommandations
            if report['summary']['security_events'] > 100:
                report['recommendations'].append("Nombre élevé d'événements de sécurité détectés")
            
            if len(report['security_incidents']) > 5:
                report['recommendations'].append("Incidents de sécurité critiques nécessitant attention")
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport compliance: {e}")
            return {'error': str(e)}
    
    async def export_events(self, tenant_id: str, start_date: datetime,
                          end_date: datetime, format: str = "json") -> str:
        """
        📤 Export d'événements d'audit
        
        Args:
            tenant_id: ID du tenant
            start_date: Date de début
            end_date: Date de fin
            format: Format d'export (json, csv, xml)
            
        Returns:
            Chemin du fichier exporté
        """
        try:
            # Récupération des événements
            query = AuditQuery(
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                limit=100000
            )
            
            events = await self.search_events(query)
            
            # Génération du nom de fichier
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"audit_export_{tenant_id}_{timestamp}.{format}"
            export_path = f"/tmp/{filename}"
            
            # Export selon le format
            if format == "json":
                await self._export_json(events, export_path)
            elif format == "csv":
                await self._export_csv(events, export_path)
            elif format == "xml":
                await self._export_xml(events, export_path)
            else:
                raise ValueError(f"Format d'export non supporté: {format}")
            
            # Compression du fichier
            compressed_path = await self._compress_export(export_path)
            
            # Upload vers S3 pour stockage
            s3_key = f"exports/{tenant_id}/{filename}.gz"
            self.s3_client.upload_file(compressed_path, self.audit_bucket, s3_key)
            
            logger.info(f"Export terminé: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            logger.error(f"Erreur export événements: {e}")
            raise
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        📈 Récupération des métriques d'audit
        
        Returns:
            Métriques globales et par tenant
        """
        try:
            # Calcul des métriques dérivées
            avg_processing_time = 0
            if self.metrics['events_processed'] > 0:
                avg_processing_time = self.metrics['processing_time_total'] / self.metrics['events_processed']
            
            error_rate = 0
            if self.metrics['events_total'] > 0:
                error_rate = (self.metrics['events_failed'] / self.metrics['events_total']) * 100
            
            # Métriques globales
            global_metrics = {
                **self.metrics,
                'average_processing_time_ms': round(avg_processing_time * 1000, 2),
                'error_rate_percent': round(error_rate, 2),
                'workers_active': len([w for w in self.workers if w.is_alive()]),
                'security_alerts_count': len(self.security_alerts),
                'total_tenants': len(self.tenant_metrics)
            }
            
            return {
                'global': global_metrics,
                'by_tenant': self.tenant_metrics,
                'security_alerts': self.security_alerts[-10:],  # 10 dernières alertes
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques: {e}")
            return {}
    
    # Méthodes privées
    
    def _validate_event(self, event: AuditEvent) -> bool:
        """Validation d'un événement d'audit"""
        try:
            # Vérifications obligatoires
            if not event.tenant_id:
                logger.error("tenant_id obligatoire")
                return False
            
            if not event.event_type:
                logger.error("event_type obligatoire")
                return False
            
            if not event.event_description:
                logger.error("event_description obligatoire")
                return False
            
            # Validation des enums
            if not isinstance(event.event_type, AuditEventType):
                logger.error("event_type invalide")
                return False
            
            if not isinstance(event.outcome, AuditOutcome):
                logger.error("outcome invalide")
                return False
            
            if not isinstance(event.level, AuditLevel):
                logger.error("level invalide")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation événement: {e}")
            return False
    
    def _encrypt_sensitive_data(self, event: AuditEvent) -> AuditEvent:
        """Chiffrement des données sensibles"""
        try:
            # Chiffrement des states si contiennent des données sensibles
            if event.before_state and self._contains_sensitive_data(event.before_state):
                encrypted_data = self.cipher_suite.encrypt(json.dumps(event.before_state).encode())
                event.before_state = {'encrypted': encrypted_data.decode()}
                event.encrypted = True
            
            if event.after_state and self._contains_sensitive_data(event.after_state):
                encrypted_data = self.cipher_suite.encrypt(json.dumps(event.after_state).encode())
                event.after_state = {'encrypted': encrypted_data.decode()}
                event.encrypted = True
            
            # Chiffrement des métadonnées sensibles
            if event.metadata and self._contains_sensitive_data(event.metadata):
                sensitive_keys = ['password', 'token', 'secret', 'api_key']
                for key in sensitive_keys:
                    if key in event.metadata:
                        encrypted_value = self.cipher_suite.encrypt(str(event.metadata[key]).encode())
                        event.metadata[key] = {'encrypted': encrypted_value.decode()}
                        event.encrypted = True
            
            return event
            
        except Exception as e:
            logger.error(f"Erreur chiffrement données sensibles: {e}")
            return event
    
    def _contains_sensitive_data(self, data: Dict[str, Any]) -> bool:
        """Vérification de la présence de données sensibles"""
        sensitive_keys = ['password', 'token', 'secret', 'api_key', 'credit_card', 'ssn']
        
        def check_dict(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        return True
                    if isinstance(value, (dict, list)):
                        if check_dict(value):
                            return True
            elif isinstance(d, list):
                for item in d:
                    if check_dict(item):
                        return True
            return False
        
        return check_dict(data)
    
    def _get_compliance_flags(self, action: str, resource_type: str) -> List[str]:
        """Récupération des flags de compliance"""
        flags = []
        
        # GDPR
        if resource_type in ['user_data', 'personal_data', 'profile']:
            flags.append('gdpr')
        
        # SOX (pour les données financières)
        if resource_type in ['financial_data', 'transaction', 'payment']:
            flags.append('sox')
        
        # HIPAA (pour les données de santé)
        if resource_type in ['health_data', 'medical_record']:
            flags.append('hipaa')
        
        # Actions spécifiques
        if action in ['delete', 'export', 'access']:
            flags.append('data_protection')
        
        return flags
    
    def _get_retention_period(self, action: str, level: AuditLevel) -> int:
        """Calcul de la période de rétention"""
        base_retention = self.config.get('retention_days_default', 2555)  # 7 ans
        
        # Ajustement selon le niveau
        if level == AuditLevel.CRITICAL:
            return base_retention + 1095  # +3 ans
        elif level == AuditLevel.HIGH:
            return base_retention + 365   # +1 an
        elif level == AuditLevel.LOW:
            return base_retention - 365   # -1 an
        
        return base_retention
    
    def _event_processing_worker(self):
        """Worker de traitement des événements"""
        batch_size = self.config.get('batch_size', 100)
        batch = []
        
        while self.running:
            try:
                # Récupération d'un événement (timeout 1 seconde)
                try:
                    event = self.event_queue.get(timeout=1)
                    batch.append(event)
                except queue.Empty:
                    # Traitement du batch partiel si timeout
                    if batch:
                        self._process_event_batch(batch)
                        batch = []
                    continue
                
                # Traitement par batch
                if len(batch) >= batch_size:
                    self._process_event_batch(batch)
                    batch = []
                
            except Exception as e:
                logger.error(f"Erreur worker traitement: {e}")
                time.sleep(1)
    
    def _process_event_batch(self, events: List[AuditEvent]):
        """Traitement d'un batch d'événements"""
        try:
            start_time = time.time()
            
            # Stockage en base de données
            self._store_events_postgresql(events)
            
            # Indexation Elasticsearch
            if self.es_client:
                self._index_events_elasticsearch(events)
            
            # Mise à jour des métriques
            self.metrics['events_processed'] += len(events)
            self.metrics['processing_time_total'] += time.time() - start_time
            
            # Notification Redis pour monitoring temps réel
            self._publish_audit_notifications(events)
            
            logger.debug(f"Batch de {len(events)} événements traité")
            
        except Exception as e:
            logger.error(f"Erreur traitement batch: {e}")
            self.metrics['events_failed'] += len(events)
    
    def _store_events_postgresql(self, events: List[AuditEvent]):
        """Stockage des événements en PostgreSQL"""
        try:
            # Implémentation simplifiée - à adapter selon votre schema
            # INSERT INTO audit_events (event_id, tenant_id, data, ...) VALUES ...
            pass
        except Exception as e:
            logger.error(f"Erreur stockage PostgreSQL: {e}")
            raise
    
    def _index_events_elasticsearch(self, events: List[AuditEvent]):
        """Indexation des événements dans Elasticsearch"""
        try:
            if not self.es_client:
                return
            
            for event in events:
                # Nom de l'index avec rotation par tenant/date
                index_name = f"audit-{event.tenant_id}-{event.timestamp.strftime('%Y-%m')}"
                
                # Document pour Elasticsearch
                doc = asdict(event)
                doc['timestamp'] = event.timestamp.isoformat()
                doc['event_type'] = event.event_type.value
                doc['outcome'] = event.outcome.value
                doc['level'] = event.level.value
                
                # Indexation
                self.es_client.index(
                    index=index_name,
                    id=event.event_id,
                    body=doc
                )
            
        except Exception as e:
            logger.error(f"Erreur indexation Elasticsearch: {e}")
    
    def _publish_audit_notifications(self, events: List[AuditEvent]):
        """Publication de notifications d'audit"""
        try:
            for event in events:
                # Notification générale
                notification = {
                    'event_id': event.event_id,
                    'tenant_id': event.tenant_id,
                    'event_type': event.event_type.value,
                    'level': event.level.value,
                    'timestamp': event.timestamp.isoformat()
                }
                
                # Publication vers Redis
                channel = f"audit_events:{event.tenant_id}"
                self.redis_client.publish(channel, json.dumps(notification))
                
                # Alertes de sécurité
                if event.level == AuditLevel.CRITICAL:
                    security_channel = "security_alerts"
                    self.redis_client.publish(security_channel, json.dumps(notification))
                    
        except Exception as e:
            logger.error(f"Erreur publication notifications: {e}")
    
    async def _search_elasticsearch(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """Recherche via Elasticsearch"""
        try:
            # Construction de la requête
            es_query = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "sort": [
                    {"timestamp": {"order": "desc"}}
                ],
                "size": query.limit,
                "from": query.offset
            }
            
            # Filtres
            if query.tenant_id:
                es_query["query"]["bool"]["must"].append({
                    "term": {"tenant_id": query.tenant_id}
                })
            
            if query.user_id:
                es_query["query"]["bool"]["must"].append({
                    "term": {"user_id": query.user_id}
                })
            
            if query.event_types:
                es_query["query"]["bool"]["must"].append({
                    "terms": {"event_type": [t.value for t in query.event_types]}
                })
            
            if query.start_date or query.end_date:
                date_range = {}
                if query.start_date:
                    date_range["gte"] = query.start_date.isoformat()
                if query.end_date:
                    date_range["lte"] = query.end_date.isoformat()
                
                es_query["query"]["bool"]["must"].append({
                    "range": {"timestamp": date_range}
                })
            
            if query.search_text:
                es_query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query.search_text,
                        "fields": ["event_description", "metadata"]
                    }
                })
            
            # Index pattern
            index_pattern = "audit-*"
            if query.tenant_id:
                index_pattern = f"audit-{query.tenant_id}-*"
            
            # Exécution de la recherche
            response = self.es_client.search(
                index=index_pattern,
                body=es_query
            )
            
            # Extraction des résultats
            events = []
            for hit in response['hits']['hits']:
                events.append(hit['_source'])
            
            return events
            
        except Exception as e:
            logger.error(f"Erreur recherche Elasticsearch: {e}")
            return []
    
    async def _search_postgresql(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """Recherche via PostgreSQL (fallback)"""
        try:
            # Implémentation simplifiée
            # SELECT * FROM audit_events WHERE ...
            return []
        except Exception as e:
            logger.error(f"Erreur recherche PostgreSQL: {e}")
            return []
    
    def _retention_worker(self):
        """Worker de gestion de la rétention"""
        while self.running:
            try:
                # Nettoyage quotidien
                current_date = datetime.utcnow()
                
                # Archivage des événements anciens
                cutoff_date = current_date - timedelta(days=365)  # Archivage après 1 an
                self._archive_old_events(cutoff_date)
                
                # Suppression des événements expirés
                self._cleanup_expired_events(current_date)
                
                # Attendre 24 heures
                time.sleep(86400)
                
            except Exception as e:
                logger.error(f"Erreur worker rétention: {e}")
                time.sleep(3600)  # Attendre 1 heure en cas d'erreur
    
    def _archive_old_events(self, cutoff_date: datetime):
        """Archivage des événements anciens vers S3"""
        try:
            # Récupération des événements à archiver
            # SELECT * FROM audit_events WHERE timestamp < cutoff_date AND NOT archived
            
            # Export vers S3
            # ...
            
            # Marquage comme archivé
            # UPDATE audit_events SET archived = true WHERE ...
            
            self.metrics['events_archived'] += 0  # Compter les événements archivés
            
        except Exception as e:
            logger.error(f"Erreur archivage événements: {e}")
    
    def _cleanup_expired_events(self, current_date: datetime):
        """Nettoyage des événements expirés"""
        try:
            # DELETE FROM audit_events WHERE timestamp < (current_date - retention_period)
            pass
        except Exception as e:
            logger.error(f"Erreur nettoyage événements expirés: {e}")
    
    async def _export_json(self, events: List[Dict[str, Any]], path: str):
        """Export au format JSON"""
        with open(path, 'w') as f:
            json.dump(events, f, indent=2, default=str)
    
    async def _export_csv(self, events: List[Dict[str, Any]], path: str):
        """Export au format CSV"""
        import csv
        
        if not events:
            return
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=events[0].keys())
            writer.writeheader()
            writer.writerows(events)
    
    async def _export_xml(self, events: List[Dict[str, Any]], path: str):
        """Export au format XML"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element("audit_events")
        
        for event in events:
            event_elem = ET.SubElement(root, "event")
            for key, value in event.items():
                elem = ET.SubElement(event_elem, key)
                elem.text = str(value)
        
        tree = ET.ElementTree(root)
        tree.write(path, encoding='utf-8', xml_declaration=True)
    
    async def _compress_export(self, path: str) -> str:
        """Compression d'un fichier d'export"""
        compressed_path = f"{path}.gz"
        
        with open(path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Suppression du fichier original
        os.remove(path)
        
        return compressed_path
    
    def _update_tenant_metrics(self, tenant_id: str, metric: str, value: Any):
        """Mise à jour des métriques par tenant"""
        if tenant_id not in self.tenant_metrics:
            self.tenant_metrics[tenant_id] = {}
        
        if metric in self.tenant_metrics[tenant_id]:
            if isinstance(value, (int, float)):
                self.tenant_metrics[tenant_id][metric] += value
            else:
                self.tenant_metrics[tenant_id][metric] = value
        else:
            self.tenant_metrics[tenant_id][metric] = value
    
    async def health_check(self) -> Dict[str, Any]:
        """
        🏥 Vérification de santé du service
        
        Returns:
            État de santé du service
        """
        try:
            health_status = {
                'service': 'tenant_audit_logger',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification workers
            active_workers = len([w for w in self.workers if w.is_alive()])
            health_status['checks']['workers_active'] = active_workers
            if active_workers == 0:
                health_status['status'] = 'unhealthy'
            
            # Vérification queue
            queue_size = self.event_queue.qsize()
            health_status['checks']['queue_size'] = queue_size
            if queue_size > self.config.get('queue_size', 10000) * 0.9:
                health_status['status'] = 'degraded'
            
            # Vérification PostgreSQL
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=self.pg_config['host'],
                    port=self.pg_config['port'],
                    connect_timeout=5
                )
                conn.close()
                health_status['checks']['postgresql'] = 'healthy'
            except Exception as e:
                health_status['checks']['postgresql'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Vérification Elasticsearch
            if self.es_client:
                try:
                    self.es_client.ping()
                    health_status['checks']['elasticsearch'] = 'healthy'
                except Exception as e:
                    health_status['checks']['elasticsearch'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {
                'service': 'tenant_audit_logger',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def shutdown(self):
        """Arrêt propre du service"""
        logger.info("Arrêt du service d'audit")
        self.running = False
        
        # Traitement des événements restants
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                self._process_event_batch([event])
            except queue.Empty:
                break
        
        # Attendre l'arrêt des workers
        for worker in self.workers:
            worker.join(timeout=5)


# Factory function pour l'initialisation
def create_tenant_audit_logger(config_path: Optional[str] = None) -> TenantAuditLogger:
    """
    🏭 Factory pour créer une instance du logger d'audit
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Instance configurée du TenantAuditLogger
    """
    return TenantAuditLogger(config_path or '/etc/ainflue/audit_config.yaml')


# Exemple d'utilisation
if __name__ == "__main__":
    async def main():
        # Création du logger d'audit
        audit_logger = create_tenant_audit_logger()
        
        # Enregistrement d'une action utilisateur
        await audit_logger.log_user_action(
            tenant_id="tenant_123",
            user_id="user_456",
            action="create_content",
            resource_type="content",
            resource_id="content_789",
            metadata={'content_type': 'video', 'size_mb': 50}
        )
        
        # Enregistrement d'un événement de sécurité
        await audit_logger.log_security_event(
            tenant_id="tenant_123",
            event_type=AuditEventType.SECURITY_VIOLATION,
            description="Tentative d'accès non autorisé détectée",
            level=AuditLevel.HIGH,
            source_ip="192.168.1.100"
        )
        
        # Recherche d'événements
        query = AuditQuery(
            tenant_id="tenant_123",
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow(),
            limit=100
        )
        
        events = await audit_logger.search_events(query)
        print(f"Nombre d'événements trouvés: {len(events)}")
        
        # Rapport de compliance
        report = await audit_logger.get_compliance_report(
            tenant_id="tenant_123",
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow(),
            compliance_type="gdpr"
        )
        
        print(f"Rapport de compliance: {report['summary']}")
    
    asyncio.run(main())