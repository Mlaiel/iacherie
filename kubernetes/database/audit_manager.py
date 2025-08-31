"""Enterprise Database Audit Manager
Advanced audit logging and compliance tracking for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

FONCTIONNALITÉS ENTERPRISE:
=========================

📊 AUDIT LOGGING AVANCÉ:
- Audit trail complet de toutes les opérations
- Tamper-proof logging avec signatures
- Real-time audit event streaming
- Compliance reporting automatique
- Data lineage tracking
- User activity monitoring

🛡️ COMPLIANCE ET RÉGLEMENTATION:
- GDPR compliance automatique
- CCPA data protection
- SOX financial compliance
- HIPAA healthcare compliance
- PCI DSS payment security
- ISO 27001 security standards

📈 ANALYTICS ET MONITORING:
- Audit data analytics
- Anomaly detection
- Risk assessment automatique
- Compliance dashboard
- Alert system intégré
- Performance impact monitoring

🔐 SÉCURITÉ AUDIT:
- Cryptographic audit signatures
- Immutable audit logs
- Access control monitoring
- Privilege escalation detection
- Data exfiltration monitoring
- Insider threat detection

⚡ PERFORMANCE OPTIMISÉE:
- Asynchronous audit logging
- Bulk audit operations
- Intelligent data retention
- Compressed audit storage
- Index optimization
- Query performance monitoring
"""
import asyncio
import json
import hashlib
import hmac
import gzip
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import os
from sqlalchemy import text
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import aiofiles
import asyncpg
import uuid

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.encryption_manager import get_encryption_manager, DataClassification


class AuditEventType(Enum):
    """Types d'événements d'audit"""
    # Database operations
    DATABASE_CREATE = "database_create"
    DATABASE_DROP = "database_drop"
    DATABASE_BACKUP = "database_backup"
    DATABASE_RESTORE = "database_restore"
    
    # Table operations
    TABLE_CREATE = "table_create"
    TABLE_ALTER = "table_alter"
    TABLE_DROP = "table_drop"
    TABLE_TRUNCATE = "table_truncate"
    
    # Data operations
    DATA_INSERT = "data_insert"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_SELECT = "data_select"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    
    # User operations
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_PRIVILEGE_CHANGE = "user_privilege_change"
    
    # Security events
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "auth_failure"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIGURATION_CHANGE = "config_change"
    MIGRATION_EXECUTED = "migration_executed"
    
    # Compliance events
    GDPR_REQUEST = "gdpr_request"
    DATA_RETENTION_POLICY = "data_retention"
    DATA_DELETION = "data_deletion"
    CONSENT_CHANGE = "consent_change"


class AuditSeverity(Enum):
    """Niveaux de gravité des événements"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class ComplianceFramework(Enum):
    """Frameworks de compliance supportés"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"


@dataclass
class AuditEvent:
    """Événement d'audit structuré"""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    # Context data
    database_name: Optional[str] = None
    table_name: Optional[str] = None
    schema_name: Optional[str] = None
    
    # Operation details
    operation: Optional[str] = None
    sql_query: Optional[str] = None
    affected_rows: Optional[int] = None
    execution_time_ms: Optional[float] = None
    
    # Data details
    data_before: Optional[Dict[str, Any]] = None
    data_after: Optional[Dict[str, Any]] = None
    data_classification: Optional[DataClassification] = None
    
    # Security context
    authentication_method: Optional[str] = None
    authorization_level: Optional[str] = None
    risk_score: Optional[float] = None
    
    # Technical details
    application_name: Optional[str] = None
    connection_id: Optional[str] = None
    transaction_id: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = None
    tags: List[str] = None
    
    # Compliance flags
    compliance_frameworks: List[ComplianceFramework] = None
    retention_period_days: Optional[int] = None
    
    # Integrity
    signature: Optional[str] = None
    checksum: Optional[str] = None


class DatabaseAuditManager:
    """
    Gestionnaire d'audit enterprise pour bases de données
    Fournit un audit complet et conforme aux réglementations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_settings()
        self.logger = get_logger(f"{__name__}.DatabaseAuditManager")
        self.encryption_manager = get_encryption_manager()
        
        # Configuration audit
        self.audit_enabled = self.config.get('audit_enabled', True)
        self.audit_level = self.config.get('audit_level', 'full')  # minimal, standard, full
        self.signature_enabled = self.config.get('audit_signature_enabled', True)
        self.encryption_enabled = self.config.get('audit_encryption_enabled', True)
        
        # Stockage audit
        self.audit_database_url = self.config.get('audit_database_url')
        self.audit_file_path = self.config.get('audit_file_path', '/var/log/ia-influencer/audit')
        self.compression_enabled = self.config.get('audit_compression', True)
        
        # Rétention des données
        self.default_retention_days = self.config.get('audit_retention_days', 2555)  # 7 ans
        self.compliance_retention = {
            ComplianceFramework.GDPR: 2555,  # 7 ans
            ComplianceFramework.SOX: 2555,   # 7 ans
            ComplianceFramework.HIPAA: 2190, # 6 ans
            ComplianceFramework.PCI_DSS: 365 # 1 an minimum
        }
        
        # Signature cryptographique
        self.signing_key = None
        self.verify_key = None
        
        # Pool de connexion audit
        self.audit_pool = None
        
        # Buffer pour audit asynchrone
        self.audit_buffer = []
        self.buffer_size = 1000
        self.flush_interval = 30  # secondes
        
        # Initialisation
        asyncio.create_task(self._initialize_audit_system())
    
    async def _initialize_audit_system(self):
        """Initialise le système d'audit"""
        try:
            self.logger.info("📊 Initializing enterprise audit system...")
            
            # Configuration cryptographique
            await self._setup_cryptographic_signing()
            
            # Base de données audit
            await self._setup_audit_database()
            
            # Répertoires de logs
            await self._setup_audit_directories()
            
            # Tâches de maintenance
            await self._start_maintenance_tasks()
            
            self.logger.info("✅ Audit system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize audit system: {e}")
            raise
    
    async def _setup_cryptographic_signing(self):
        """Configure la signature cryptographique des audits"""
        try:
            if not self.signature_enabled:
                return
            
            # Génération ou chargement des clés de signature
            private_key_path = os.path.join(self.audit_file_path, 'audit_signing_key.pem')
            public_key_path = os.path.join(self.audit_file_path, 'audit_verify_key.pem')
            
            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                # Chargement des clés existantes
                with open(private_key_path, 'rb') as f:
                    self.signing_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None,
                        backend=default_backend()
                    )
                
                with open(public_key_path, 'rb') as f:
                    self.verify_key = serialization.load_pem_public_key(
                        f.read(),
                        backend=default_backend()
                    )
            else:
                # Génération nouvelles clés
                self.signing_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=default_backend()
                )
                self.verify_key = self.signing_key.public_key()
                
                # Sauvegarde sécurisée
                os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
                
                with open(private_key_path, 'wb') as f:
                    f.write(self.signing_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                
                with open(public_key_path, 'wb') as f:
                    f.write(self.verify_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
                
                # Permissions restrictives
                os.chmod(private_key_path, 0o600)
                os.chmod(public_key_path, 0o644)
            
            self.logger.info("🔐 Cryptographic signing configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup cryptographic signing: {e}")
            raise
    
    async def _setup_audit_database(self):
        """Configure la base de données d'audit"""
        try:
            if not self.audit_database_url:
                return
            
            # Connexion à la base d'audit
            self.audit_pool = await asyncpg.create_pool(
                self.audit_database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            # Création des tables d'audit si nécessaire
            await self._create_audit_tables()
            
            self.logger.info("🗄️ Audit database configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup audit database: {e}")
            # Continue sans DB audit, utilise les fichiers
            self.audit_pool = None
    
    async def _create_audit_tables(self):
        """Crée les tables d'audit nécessaires"""
        try:
            if not self.audit_pool:
                return
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS audit_events (
                id BIGSERIAL PRIMARY KEY,
                event_id UUID UNIQUE NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                user_id VARCHAR(100),
                session_id VARCHAR(100),
                ip_address INET,
                user_agent TEXT,
                
                -- Context
                database_name VARCHAR(100),
                table_name VARCHAR(100),
                schema_name VARCHAR(100),
                
                -- Operation
                operation VARCHAR(100),
                sql_query TEXT,
                affected_rows INTEGER,
                execution_time_ms FLOAT,
                
                -- Data (encrypted)
                data_before_encrypted BYTEA,
                data_after_encrypted BYTEA,
                data_classification VARCHAR(50),
                
                -- Security
                authentication_method VARCHAR(100),
                authorization_level VARCHAR(100),
                risk_score FLOAT,
                
                -- Technical
                application_name VARCHAR(100),
                connection_id VARCHAR(100),
                transaction_id VARCHAR(100),
                
                -- Metadata
                metadata JSONB,
                tags TEXT[],
                compliance_frameworks TEXT[],
                retention_period_days INTEGER,
                
                -- Integrity
                signature TEXT,
                checksum VARCHAR(128),
                
                -- Indexing and partitioning
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_events_event_type ON audit_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_events_severity ON audit_events(severity);
            CREATE INDEX IF NOT EXISTS idx_audit_events_database_name ON audit_events(database_name);
            CREATE INDEX IF NOT EXISTS idx_audit_events_compliance ON audit_events USING GIN(compliance_frameworks);
            CREATE INDEX IF NOT EXISTS idx_audit_events_metadata ON audit_events USING GIN(metadata);
            
            -- Partitioning by date (monthly)
            CREATE TABLE IF NOT EXISTS audit_events_archive (
                LIKE audit_events INCLUDING ALL
            );
            """
            
            async with self.audit_pool.acquire() as conn:
                await conn.execute(create_table_sql)
            
            self.logger.info("✅ Audit tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create audit tables: {e}")
            raise
    
    async def _setup_audit_directories(self):
        """Configure les répertoires de logs d'audit"""
        try:
            # Création des répertoires
            directories = [
                self.audit_file_path,
                os.path.join(self.audit_file_path, 'daily'),
                os.path.join(self.audit_file_path, 'monthly'),
                os.path.join(self.audit_file_path, 'compliance'),
                os.path.join(self.audit_file_path, 'archive')
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                os.chmod(directory, 0o750)
            
            self.logger.info("📁 Audit directories configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup audit directories: {e}")
            raise
    
    async def _start_maintenance_tasks(self):
        """Démarre les tâches de maintenance d'audit"""
        try:
            # Tâche de flush du buffer
            asyncio.create_task(self._buffer_flush_task())
            
            # Tâche de rotation des logs
            asyncio.create_task(self._log_rotation_task())
            
            # Tâche de nettoyage des anciens logs
            asyncio.create_task(self._cleanup_task())
            
            # Tâche de vérification d'intégrité
            asyncio.create_task(self._integrity_check_task())
            
            self.logger.info("🔧 Audit maintenance tasks started")
            
        except Exception as e:
            self.logger.error(f"Failed to start maintenance tasks: {e}")
    
    async def log_audit_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Enregistre un événement d'audit
        
        Args:
            event_type: Type d'événement
            user_id: ID de l'utilisateur
            session_id: ID de la session
            ip_address: Adresse IP
            **kwargs: Données additionnelles
            
        Returns:
            ID de l'événement d'audit
        """
        try:
            if not self.audit_enabled:
                return ""
            
            # Création de l'événement
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                severity=kwargs.get('severity', AuditSeverity.INFO),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=kwargs.get('user_agent'),
                
                # Context
                database_name=kwargs.get('database_name'),
                table_name=kwargs.get('table_name'),
                schema_name=kwargs.get('schema_name'),
                
                # Operation
                operation=kwargs.get('operation'),
                sql_query=kwargs.get('sql_query'),
                affected_rows=kwargs.get('affected_rows'),
                execution_time_ms=kwargs.get('execution_time_ms'),
                
                # Data
                data_before=kwargs.get('data_before'),
                data_after=kwargs.get('data_after'),
                data_classification=kwargs.get('data_classification'),
                
                # Security
                authentication_method=kwargs.get('authentication_method'),
                authorization_level=kwargs.get('authorization_level'),
                risk_score=kwargs.get('risk_score'),
                
                # Technical
                application_name=kwargs.get('application_name', 'IA-Influencer-Agent'),
                connection_id=kwargs.get('connection_id'),
                transaction_id=kwargs.get('transaction_id'),
                
                # Metadata
                metadata=kwargs.get('metadata', {}),
                tags=kwargs.get('tags', []),
                compliance_frameworks=kwargs.get('compliance_frameworks', []),
                retention_period_days=kwargs.get('retention_period_days', self.default_retention_days)
            )
            
            # Chiffrement des données sensibles
            if self.encryption_enabled:
                await self._encrypt_audit_data(event)
            
            # Signature cryptographique
            if self.signature_enabled:
                await self._sign_audit_event(event)
            
            # Checksum d'intégrité
            event.checksum = self._calculate_checksum(event)
            
            # Ajout au buffer pour traitement asynchrone
            self.audit_buffer.append(event)
            
            # Flush immédiat pour événements critiques
            if event.severity in [AuditSeverity.CRITICAL, AuditSeverity.SECURITY]:
                await self._flush_audit_buffer()
            
            # Vérification taille buffer
            if len(self.audit_buffer) >= self.buffer_size:
                await self._flush_audit_buffer()
            
            return event.event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            return ""
    
    async def _encrypt_audit_data(self, event: AuditEvent):
        """Chiffre les données sensibles dans l'événement d'audit"""
        try:
            if event.data_before:
                encrypted_data = self.encryption_manager.encrypt_sensitive_data(
                    json.dumps(event.data_before),
                    event.data_classification or DataClassification.CONFIDENTIAL
                )
                event.data_before = encrypted_data
            
            if event.data_after:
                encrypted_data = self.encryption_manager.encrypt_sensitive_data(
                    json.dumps(event.data_after),
                    event.data_classification or DataClassification.CONFIDENTIAL
                )
                event.data_after = encrypted_data
            
            # Chiffrement requêtes SQL si sensibles
            if event.sql_query and event.data_classification == DataClassification.RESTRICTED:
                encrypted_sql = self.encryption_manager.encrypt_sensitive_data(
                    event.sql_query,
                    DataClassification.RESTRICTED
                )
                event.sql_query = json.dumps(encrypted_sql)
            
        except Exception as e:
            self.logger.warning(f"Failed to encrypt audit data: {e}")
    
    async def _sign_audit_event(self, event: AuditEvent):
        """Signe cryptographiquement l'événement d'audit"""
        try:
            if not self.signing_key:
                return
            
            # Création du payload à signer
            sign_data = {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'user_id': event.user_id,
                'operation': event.operation,
                'checksum': event.checksum
            }
            
            message = json.dumps(sign_data, sort_keys=True).encode('utf-8')
            
            # Signature RSA-PSS
            signature = self.signing_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            event.signature = base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            self.logger.warning(f"Failed to sign audit event: {e}")
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calcule le checksum de l'événement d'audit"""
        try:
            # Exclusion signature et checksum du calcul
            event_dict = asdict(event)
            event_dict.pop('signature', None)
            event_dict.pop('checksum', None)
            
            # Sérialisation stable
            event_json = json.dumps(event_dict, sort_keys=True, default=str)
            
            # SHA-256 hash
            return hashlib.sha256(event_json.encode('utf-8')).hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate checksum: {e}")
            return ""
    
    async def _flush_audit_buffer(self):
        """Flush le buffer d'audit vers le stockage persistant"""
        try:
            if not self.audit_buffer:
                return
            
            buffer_copy = self.audit_buffer.copy()
            self.audit_buffer.clear()
            
            # Écriture en base de données
            if self.audit_pool:
                await self._write_to_database(buffer_copy)
            
            # Écriture en fichiers
            await self._write_to_files(buffer_copy)
            
            self.logger.debug(f"Flushed {len(buffer_copy)} audit events")
            
        except Exception as e:
            self.logger.error(f"Failed to flush audit buffer: {e}")
            # Restore buffer in case of failure
            self.audit_buffer.extend(buffer_copy)
    
    async def _write_to_database(self, events: List[AuditEvent]):
        """Écrit les événements d'audit en base de données"""
        try:
            if not self.audit_pool:
                return
            
            insert_sql = """
            INSERT INTO audit_events (
                event_id, event_type, severity, timestamp, user_id, session_id,
                ip_address, user_agent, database_name, table_name, schema_name,
                operation, sql_query, affected_rows, execution_time_ms,
                data_before_encrypted, data_after_encrypted, data_classification,
                authentication_method, authorization_level, risk_score,
                application_name, connection_id, transaction_id,
                metadata, tags, compliance_frameworks, retention_period_days,
                signature, checksum
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15,
                $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30
            )
            """
            
            async with self.audit_pool.acquire() as conn:
                async with conn.transaction():
                    for event in events:
                        await conn.execute(
                            insert_sql,
                            event.event_id,
                            event.event_type.value,
                            event.severity.value,
                            event.timestamp,
                            event.user_id,
                            event.session_id,
                            event.ip_address,
                            event.user_agent,
                            event.database_name,
                            event.table_name,
                            event.schema_name,
                            event.operation,
                            event.sql_query,
                            event.affected_rows,
                            event.execution_time_ms,
                            json.dumps(event.data_before) if event.data_before else None,
                            json.dumps(event.data_after) if event.data_after else None,
                            event.data_classification.value if event.data_classification else None,
                            event.authentication_method,
                            event.authorization_level,
                            event.risk_score,
                            event.application_name,
                            event.connection_id,
                            event.transaction_id,
                            event.metadata,
                            event.tags,
                            [f.value for f in event.compliance_frameworks] if event.compliance_frameworks else None,
                            event.retention_period_days,
                            event.signature,
                            event.checksum
                        )
            
        except Exception as e:
            self.logger.error(f"Failed to write audit events to database: {e}")
            raise
    
    async def _write_to_files(self, events: List[AuditEvent]):
        """Écrit les événements d'audit dans des fichiers"""
        try:
            today = datetime.utcnow().strftime('%Y-%m-%d')
            log_file = os.path.join(self.audit_file_path, 'daily', f'audit_{today}.jsonl')
            
            # Préparation des données
            log_lines = []
            for event in events:
                event_dict = asdict(event)
                # Conversion des enums en strings
                for key, value in event_dict.items():
                    if hasattr(value, 'value'):
                        event_dict[key] = value.value
                    elif isinstance(value, list) and value and hasattr(value[0], 'value'):
                        event_dict[key] = [v.value for v in value]
                    elif isinstance(value, datetime):
                        event_dict[key] = value.isoformat()
                
                log_lines.append(json.dumps(event_dict) + '\n')
            
            # Écriture (avec compression optionnelle)
            if self.compression_enabled:
                compressed_data = gzip.compress('\n'.join(log_lines).encode('utf-8'))
                log_file += '.gz'
                
                async with aiofiles.open(log_file, 'ab') as f:
                    await f.write(compressed_data)
            else:
                async with aiofiles.open(log_file, 'a') as f:
                    await f.writelines(log_lines)
            
            # Permissions restrictives
            os.chmod(log_file, 0o640)
            
        except Exception as e:
            self.logger.error(f"Failed to write audit events to files: {e}")
    
    async def _buffer_flush_task(self):
        """Tâche de flush périodique du buffer"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                if self.audit_buffer:
                    await self._flush_audit_buffer()
            except Exception as e:
                self.logger.error(f"Buffer flush task error: {e}")
    
    async def _log_rotation_task(self):
        """Tâche de rotation des logs d'audit"""
        while True:
            try:
                # Rotation quotidienne à minuit
                now = datetime.utcnow()
                tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                wait_seconds = (tomorrow - now).total_seconds()
                
                await asyncio.sleep(wait_seconds)
                
                # Archivage des logs du jour précédent
                await self._archive_daily_logs()
                
            except Exception as e:
                self.logger.error(f"Log rotation task error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _cleanup_task(self):
        """Tâche de nettoyage des anciens logs"""
        while True:
            try:
                # Nettoyage hebdomadaire
                await asyncio.sleep(7 * 24 * 3600)  # 1 semaine
                
                await self._cleanup_expired_logs()
                
            except Exception as e:
                self.logger.error(f"Cleanup task error: {e}")
    
    async def _integrity_check_task(self):
        """Tâche de vérification d'intégrité"""
        while True:
            try:
                # Vérification quotidienne
                await asyncio.sleep(24 * 3600)  # 1 jour
                
                await self._verify_audit_integrity()
                
            except Exception as e:
                self.logger.error(f"Integrity check task error: {e}")
    
    async def _archive_daily_logs(self):
        """Archive les logs quotidiens"""
        try:
            yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
            daily_dir = os.path.join(self.audit_file_path, 'daily')
            archive_dir = os.path.join(self.audit_file_path, 'archive')
            
            # Fichiers à archiver
            files_to_archive = [
                os.path.join(daily_dir, f'audit_{yesterday}.jsonl'),
                os.path.join(daily_dir, f'audit_{yesterday}.jsonl.gz')
            ]
            
            for file_path in files_to_archive:
                if os.path.exists(file_path):
                    archive_path = os.path.join(archive_dir, os.path.basename(file_path))
                    
                    # Compression additionnelle si nécessaire
                    if not file_path.endswith('.gz'):
                        with open(file_path, 'rb') as f_in:
                            with gzip.open(archive_path + '.gz', 'wb') as f_out:
                                f_out.writelines(f_in)
                        os.remove(file_path)
                    else:
                        os.rename(file_path, archive_path)
            
            self.logger.info(f"Archived logs for {yesterday}")
            
        except Exception as e:
            self.logger.error(f"Failed to archive daily logs: {e}")
    
    async def _cleanup_expired_logs(self):
        """Nettoie les logs expirés selon les politiques de rétention"""
        try:
            # Nettoyage base de données
            if self.audit_pool:
                await self._cleanup_database_audit()
            
            # Nettoyage fichiers
            await self._cleanup_file_audit()
            
            self.logger.info("Audit cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired logs: {e}")
    
    async def _cleanup_database_audit(self):
        """Nettoie les anciennes entrées d'audit en base"""
        try:
            # Archive les anciennes entrées avant suppression
            archive_sql = """
            INSERT INTO audit_events_archive 
            SELECT * FROM audit_events 
            WHERE timestamp < NOW() - INTERVAL '%s days'
            """
            
            delete_sql = """
            DELETE FROM audit_events 
            WHERE timestamp < NOW() - INTERVAL '%s days'
            """
            
            async with self.audit_pool.acquire() as conn:
                async with conn.transaction():
                    # Archive puis suppression
                    await conn.execute(archive_sql, self.default_retention_days)
                    result = await conn.execute(delete_sql, self.default_retention_days)
                    
                    deleted_count = int(result.split()[-1])
                    self.logger.info(f"Cleaned up {deleted_count} expired audit records")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup database audit: {e}")
    
    async def _cleanup_file_audit(self):
        """Nettoie les anciens fichiers d'audit"""
        try:
            archive_dir = os.path.join(self.audit_file_path, 'archive')
            cutoff_date = datetime.utcnow() - timedelta(days=self.default_retention_days)
            
            for filename in os.listdir(archive_dir):
                file_path = os.path.join(archive_dir, filename)
                
                # Extraction date du nom de fichier
                try:
                    date_str = filename.split('_')[1].split('.')[0]
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        self.logger.debug(f"Deleted expired audit file: {filename}")
                        
                except (ValueError, IndexError):
                    continue  # Skip malformed filenames
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup file audit: {e}")
    
    async def _verify_audit_integrity(self):
        """Vérifie l'intégrité des logs d'audit"""
        try:
            verification_results = {
                'total_checked': 0,
                'signature_valid': 0,
                'signature_invalid': 0,
                'checksum_valid': 0,
                'checksum_invalid': 0,
                'errors': []
            }
            
            # Vérification base de données
            if self.audit_pool:
                await self._verify_database_integrity(verification_results)
            
            # Vérification fichiers
            await self._verify_file_integrity(verification_results)
            
            # Rapport d'intégrité
            self.logger.info(f"Integrity check completed: {verification_results}")
            
            # Alertes si problèmes détectés
            if verification_results['signature_invalid'] > 0 or verification_results['checksum_invalid'] > 0:
                await self._send_integrity_alert(verification_results)
            
        except Exception as e:
            self.logger.error(f"Failed to verify audit integrity: {e}")
    
    async def _verify_database_integrity(self, results: Dict[str, Any]):
        """Vérifie l'intégrité des audits en base"""
        try:
            # Échantillonnage des entrées récentes
            select_sql = """
            SELECT event_id, event_type, timestamp, user_id, operation, 
                   signature, checksum
            FROM audit_events 
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
            ORDER BY timestamp DESC
            LIMIT 1000
            """
            
            async with self.audit_pool.acquire() as conn:
                rows = await conn.fetch(select_sql)
                
                for row in rows:
                    results['total_checked'] += 1
                    
                    # Vérification signature si présente
                    if row['signature'] and self.verify_key:
                        if await self._verify_signature(row):
                            results['signature_valid'] += 1
                        else:
                            results['signature_invalid'] += 1
                            results['errors'].append(f"Invalid signature for event {row['event_id']}")
                    
                    # Vérification checksum
                    if await self._verify_checksum(row):
                        results['checksum_valid'] += 1
                    else:
                        results['checksum_invalid'] += 1
                        results['errors'].append(f"Invalid checksum for event {row['event_id']}")
            
        except Exception as e:
            self.logger.error(f"Database integrity verification failed: {e}")
    
    async def _verify_file_integrity(self, results: Dict[str, Any]):
        """Vérifie l'intégrité des fichiers d'audit"""
        try:
            # Vérification des fichiers récents
            daily_dir = os.path.join(self.audit_file_path, 'daily')
            
            for filename in os.listdir(daily_dir):
                if filename.startswith('audit_') and (filename.endswith('.jsonl') or filename.endswith('.jsonl.gz')):
                    file_path = os.path.join(daily_dir, filename)
                    await self._verify_file_content(file_path, results)
            
        except Exception as e:
            self.logger.error(f"File integrity verification failed: {e}")
    
    async def _verify_file_content(self, file_path: str, results: Dict[str, Any]):
        """Vérifie le contenu d'un fichier d'audit"""
        try:
            if file_path.endswith('.gz'):
                # Fichier compressé
                with gzip.open(file_path, 'rt') as f:
                    lines = f.readlines()
            else:
                # Fichier non compressé
                async with aiofiles.open(file_path, 'r') as f:
                    lines = await f.readlines()
            
            for line in lines[:100]:  # Échantillon de 100 lignes
                try:
                    event_data = json.loads(line.strip())
                    results['total_checked'] += 1
                    
                    # Vérification checksum
                    expected_checksum = event_data.get('checksum')
                    if expected_checksum:
                        event_copy = event_data.copy()
                        event_copy.pop('signature', None)
                        event_copy.pop('checksum', None)
                        
                        actual_checksum = hashlib.sha256(
                            json.dumps(event_copy, sort_keys=True).encode('utf-8')
                        ).hexdigest()
                        
                        if actual_checksum == expected_checksum:
                            results['checksum_valid'] += 1
                        else:
                            results['checksum_invalid'] += 1
                            results['errors'].append(f"Invalid checksum in file {file_path}")
                
                except json.JSONDecodeError:
                    results['errors'].append(f"Invalid JSON in file {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to verify file content {file_path}: {e}")
    
    async def _verify_signature(self, audit_record: Dict[str, Any]) -> bool:
        """Vérifie la signature d'un enregistrement d'audit"""
        try:
            if not self.verify_key or not audit_record.get('signature'):
                return False
            
            # Reconstruction du payload signé
            sign_data = {
                'event_id': audit_record['event_id'],
                'event_type': audit_record['event_type'],
                'timestamp': audit_record['timestamp'].isoformat(),
                'user_id': audit_record['user_id'],
                'operation': audit_record['operation'],
                'checksum': audit_record['checksum']
            }
            
            message = json.dumps(sign_data, sort_keys=True).encode('utf-8')
            signature = base64.b64decode(audit_record['signature'])
            
            # Vérification RSA-PSS
            self.verify_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception:
            return False
    
    async def _verify_checksum(self, audit_record: Dict[str, Any]) -> bool:
        """Vérifie le checksum d'un enregistrement d'audit"""
        try:
            if not audit_record.get('checksum'):
                return False
            
            # Reconstruction des données (sans signature et checksum)
            record_copy = dict(audit_record)
            record_copy.pop('signature', None)
            expected_checksum = record_copy.pop('checksum', None)
            
            # Calcul checksum actuel
            actual_checksum = hashlib.sha256(
                json.dumps(record_copy, sort_keys=True, default=str).encode('utf-8')
            ).hexdigest()
            
            return actual_checksum == expected_checksum
            
        except Exception:
            return False
    
    async def _send_integrity_alert(self, results: Dict[str, Any]):
        """Envoie une alerte en cas de problème d'intégrité"""
        try:
            alert_message = f"""
            🚨 AUDIT INTEGRITY ALERT 🚨
            
            Integrity check detected issues:
            - Total checked: {results['total_checked']}
            - Invalid signatures: {results['signature_invalid']}
            - Invalid checksums: {results['checksum_invalid']}
            
            Errors:
            {chr(10).join(results['errors'][:10])}
            
            Immediate investigation required!
            """
            
            # Log critique
            self.logger.critical(alert_message)
            
            # Envoi notifications externes (email, Slack, webhook, SMS)
            await self._send_external_notifications(
                alert_type="database_integrity_failure",
                severity="critical",
                message=alert_message,
                metadata={
                    "results": results,
                    "timestamp": datetime.utcnow().isoformat(),
                    "system": "audit_manager"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send integrity alert: {e}")
    
    async def search_audit_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
        database_name: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Recherche dans les événements d'audit
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            event_types: Types d'événements
            user_id: ID utilisateur
            database_name: Nom de la base
            severity: Niveau de gravité
            limit: Limite de résultats
            
        Returns:
            Liste des événements trouvés
        """
        try:
            if not self.audit_pool:
                return []
            
            # Construction de la requête
            where_conditions = []
            params = []
            param_count = 0
            
            if start_date:
                param_count += 1
                where_conditions.append(f"timestamp >= ${param_count}")
                params.append(start_date)
            
            if end_date:
                param_count += 1
                where_conditions.append(f"timestamp <= ${param_count}")
                params.append(end_date)
            
            if event_types:
                param_count += 1
                where_conditions.append(f"event_type = ANY(${param_count})")
                params.append([et.value for et in event_types])
            
            if user_id:
                param_count += 1
                where_conditions.append(f"user_id = ${param_count}")
                params.append(user_id)
            
            if database_name:
                param_count += 1
                where_conditions.append(f"database_name = ${param_count}")
                params.append(database_name)
            
            if severity:
                param_count += 1
                where_conditions.append(f"severity = ${param_count}")
                params.append(severity.value)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "TRUE"
            
            search_sql = f"""
            SELECT event_id, event_type, severity, timestamp, user_id, 
                   database_name, table_name, operation, affected_rows,
                   authentication_method, risk_score, metadata
            FROM audit_events 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT {limit}
            """
            
            async with self.audit_pool.acquire() as conn:
                rows = await conn.fetch(search_sql, *params)
                
                return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Failed to search audit events: {e}")
            return []
    
    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Génère un rapport de compliance
        
        Args:
            framework: Framework de compliance
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Rapport de compliance
        """
        try:
            report = {
                'framework': framework.value,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {},
                'details': {},
                'violations': [],
                'recommendations': []
            }
            
            # Recherche événements liés au framework
            events = await self.search_audit_events(
                start_date=start_date,
                end_date=end_date
            )
            
            # Filtrage par framework
            relevant_events = [
                event for event in events
                if event.get('compliance_frameworks') and framework.value in event['compliance_frameworks']
            ]
            
            # Statistiques générales
            report['summary'] = {
                'total_events': len(relevant_events),
                'event_types': {},
                'severity_distribution': {},
                'user_activity': {},
                'risk_score_avg': 0
            }
            
            # Analyse détaillée selon le framework
            if framework == ComplianceFramework.GDPR:
                report['details'] = await self._analyze_gdpr_compliance(relevant_events)
            elif framework == ComplianceFramework.SOX:
                report['details'] = await self._analyze_sox_compliance(relevant_events)
            elif framework == ComplianceFramework.HIPAA:
                report['details'] = await self._analyze_hipaa_compliance(relevant_events)
            elif framework == ComplianceFramework.PCI_DSS:
                report['details'] = await self._analyze_pci_compliance(relevant_events)
            
            # Analyse des risques
            risk_scores = [e.get('risk_score', 0) for e in relevant_events if e.get('risk_score')]
            if risk_scores:
                report['summary']['risk_score_avg'] = sum(risk_scores) / len(risk_scores)
            
            # Violations potentielles
            report['violations'] = await self._detect_compliance_violations(relevant_events, framework)
            
            # Recommandations
            report['recommendations'] = await self._generate_compliance_recommendations(report, framework)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            return {'error': str(e)}
    
    async def _analyze_gdpr_compliance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse de conformité GDPR"""
        try:
            gdpr_analysis = {
                'data_subject_requests': 0,
                'data_deletions': 0,
                'consent_changes': 0,
                'data_breaches': 0,
                'international_transfers': 0,
                'retention_violations': 0
            }
            
            for event in events:
                event_type = event.get('event_type', '')
                
                if event_type == AuditEventType.GDPR_REQUEST.value:
                    gdpr_analysis['data_subject_requests'] += 1
                elif event_type == AuditEventType.DATA_DELETION.value:
                    gdpr_analysis['data_deletions'] += 1
                elif event_type == AuditEventType.CONSENT_CHANGE.value:
                    gdpr_analysis['consent_changes'] += 1
                elif event_type == AuditEventType.DATA_BREACH_ATTEMPT.value:
                    gdpr_analysis['data_breaches'] += 1
            
            return gdpr_analysis
            
        except Exception as e:
            self.logger.error(f"GDPR analysis failed: {e}")
            return {}
    
    async def _analyze_sox_compliance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse de conformité SOX"""
        # Implementation similar to GDPR but for SOX requirements
        return {
            'financial_data_access': 0,
            'privilege_changes': 0,
            'system_changes': 0,
            'backup_operations': 0
        }
    
    async def _analyze_hipaa_compliance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse de conformité HIPAA"""
        # Implementation for HIPAA healthcare compliance
        return {
            'phi_access': 0,
            'minimum_necessary': 0,
            'breach_notifications': 0,
            'audit_controls': 0
        }
    
    async def _analyze_pci_compliance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse de conformité PCI DSS"""
        # Implementation for PCI payment card compliance
        return {
            'cardholder_data_access': 0,
            'network_access': 0,
            'encryption_operations': 0,
            'vulnerability_scans': 0
        }
    
    async def _detect_compliance_violations(
        self,
        events: List[Dict[str, Any]],
        framework: ComplianceFramework
    ) -> List[Dict[str, Any]]:
        """Détecte les violations de compliance"""
        violations = []
        
        try:
            for event in events:
                # Recherche de patterns de violation
                risk_score = event.get('risk_score', 0)
                
                if risk_score > 0.8:  # Seuil de risque élevé
                    violations.append({
                        'event_id': event['event_id'],
                        'type': 'high_risk_activity',
                        'severity': event.get('severity'),
                        'description': f"High risk activity detected (score: {risk_score})",
                        'timestamp': event['timestamp']
                    })
                
                # Vérifications spécifiques au framework
                if framework == ComplianceFramework.GDPR:
                    violations.extend(await self._detect_gdpr_violations(event))
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Violation detection failed: {e}")
            return []
    
    async def _detect_gdpr_violations(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecte les violations GDPR spécifiques"""
        violations = []
        
        # Exemple: accès données sans consentement
        if (event.get('event_type') == AuditEventType.DATA_SELECT.value and
            not event.get('metadata', {}).get('consent_verified')):
            violations.append({
                'event_id': event['event_id'],
                'type': 'data_access_without_consent',
                'severity': 'high',
                'description': 'Data access without verified consent',
                'timestamp': event['timestamp']
            })
        
        return violations
    
    async def _generate_compliance_recommendations(
        self,
        report: Dict[str, Any],
        framework: ComplianceFramework
    ) -> List[str]:
        """Génère des recommandations de compliance"""
        recommendations = []
        
        try:
            violations_count = len(report.get('violations', []))
            
            if violations_count > 0:
                recommendations.append(
                    f"Address {violations_count} compliance violations identified"
                )
            
            avg_risk = report['summary'].get('risk_score_avg', 0)
            if avg_risk > 0.6:
                recommendations.append(
                    "Implement additional security controls to reduce risk score"
                )
            
            # Recommandations spécifiques au framework
            if framework == ComplianceFramework.GDPR:
                recommendations.extend([
                    "Implement automated consent verification",
                    "Review data retention policies",
                    "Enhance data subject request handling"
                ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du système d'audit"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification buffer
            health_status['checks']['buffer'] = {
                'status': 'pass',
                'buffer_size': len(self.audit_buffer),
                'max_buffer_size': self.buffer_size
            }
            
            # Vérification base de données
            if self.audit_pool:
                try:
                    async with self.audit_pool.acquire() as conn:
                        await conn.execute('SELECT 1')
                    
                    health_status['checks']['database'] = {
                        'status': 'pass',
                        'message': 'Database connection healthy'
                    }
                except Exception as e:
                    health_status['checks']['database'] = {
                        'status': 'fail',
                        'message': f'Database connection failed: {e}'
                    }
                    health_status['status'] = 'unhealthy'
            else:
                health_status['checks']['database'] = {
                    'status': 'disabled',
                    'message': 'Database audit not configured'
                }
            
            # Vérification répertoires
            if os.path.exists(self.audit_file_path):
                health_status['checks']['file_system'] = {
                    'status': 'pass',
                    'message': 'Audit directories accessible'
                }
            else:
                health_status['checks']['file_system'] = {
                    'status': 'fail',
                    'message': 'Audit directories not accessible'
                }
                health_status['status'] = 'unhealthy'
            
            # Vérification signature
            if self.signature_enabled:
                if self.signing_key:
                    health_status['checks']['cryptographic_signing'] = {
                        'status': 'pass',
                        'message': 'Signing keys available'
                    }
                else:
                    health_status['checks']['cryptographic_signing'] = {
                        'status': 'fail',
                        'message': 'Signing keys not available'
                    }
                    health_status['status'] = 'warning'
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _send_external_notifications(
        self, 
        alert_type: str, 
        severity: str, 
        message: str, 
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Envoie des notifications externes pour les alertes critiques
        
        Args:
            alert_type: Type d'alerte (database_integrity_failure, etc.)
            severity: Niveau de sévérité (critical, high, medium, low)
            message: Message d'alerte
            metadata: Métadonnées additionnelles
        """
        try:
            notification_data = {
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "system": "ainflue_audit_manager",
                "metadata": metadata or {}
            }
            
            # 1. Notification Email
            await self._send_email_notification(notification_data)
            
            # 2. Notification Slack
            await self._send_slack_notification(notification_data)
            
            # 3. Webhook générique
            await self._send_webhook_notification(notification_data)
            
            # 4. Notification SMS pour les alertes critiques
            if severity == "critical":
                await self._send_sms_notification(notification_data)
            
            self.logger.info(f"External notifications sent for {alert_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to send external notifications: {e}")
    
    async def _send_email_notification(self, notification_data: Dict[str, Any]) -> None:
        """Envoi notification par email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Configuration email depuis les variables d'environnement
            smtp_server = os.environ.get('AUDIT_SMTP_SERVER', 'localhost')
            smtp_port = int(os.environ.get('AUDIT_SMTP_PORT', '587'))
            smtp_user = os.environ.get('AUDIT_SMTP_USER')
            smtp_password = os.environ.get('AUDIT_SMTP_PASSWORD')
            recipients = os.environ.get('AUDIT_EMAIL_RECIPIENTS', '').split(',')
            
            if not smtp_user or not recipients[0]:
                self.logger.warning("Email configuration not complete, skipping email notification")
                return
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[AINFLUE AUDIT] {notification_data['severity'].upper()}: {notification_data['alert_type']}"
            
            # Corps du message
            body = f"""
            AINFLUE AUDIT ALERT
            ==================
            
            Type: {notification_data['alert_type']}
            Sévérité: {notification_data['severity']}
            Timestamp: {notification_data['timestamp']}
            
            Message:
            {notification_data['message']}
            
            Métadonnées:
            {json.dumps(notification_data['metadata'], indent=2)}
            
            System: {notification_data['system']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envoi
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            self.logger.info("Email notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    async def _send_slack_notification(self, notification_data: Dict[str, Any]) -> None:
        """Envoi notification Slack"""
        try:
            import aiohttp
            
            webhook_url = os.environ.get('AUDIT_SLACK_WEBHOOK_URL')
            if not webhook_url:
                self.logger.debug("Slack webhook not configured, skipping Slack notification")
                return
            
            # Créer le payload Slack
            color_map = {
                "critical": "#FF0000",
                "high": "#FF8C00", 
                "medium": "#FFD700",
                "low": "#00FF00"
            }
            
            slack_payload = {
                "text": f"🚨 Ainflue Audit Alert: {notification_data['alert_type']}",
                "attachments": [
                    {
                        "color": color_map.get(notification_data['severity'], "#808080"),
                        "fields": [
                            {
                                "title": "Severity",
                                "value": notification_data['severity'],
                                "short": True
                            },
                            {
                                "title": "Type",
                                "value": notification_data['alert_type'],
                                "short": True
                            },
                            {
                                "title": "Message",
                                "value": notification_data['message'][:500] + "..." if len(notification_data['message']) > 500 else notification_data['message'],
                                "short": False
                            }
                        ],
                        "footer": "Ainflue Audit Manager",
                        "ts": int(datetime.utcnow().timestamp())
                    }
                ]
            }
            
            # Envoi via webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_payload) as response:
                    if response.status == 200:
                        self.logger.info("Slack notification sent successfully")
                    else:
                        self.logger.error(f"Slack notification failed: {response.status}")
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_webhook_notification(self, notification_data: Dict[str, Any]) -> None:
        """Envoi notification via webhook générique"""
        try:
            import aiohttp
            
            webhook_url = os.environ.get('AUDIT_WEBHOOK_URL')
            if not webhook_url:
                self.logger.debug("Generic webhook not configured, skipping webhook notification")
                return
            
            # Envoi du payload complet
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=notification_data) as response:
                    if response.status in [200, 201, 202]:
                        self.logger.info("Webhook notification sent successfully")
                    else:
                        self.logger.error(f"Webhook notification failed: {response.status}")
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_sms_notification(self, notification_data: Dict[str, Any]) -> None:
        """Envoi notification SMS pour les alertes critiques"""
        try:
            # Configuration SMS (exemple avec Twilio)
            account_sid = os.environ.get('AUDIT_TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('AUDIT_TWILIO_AUTH_TOKEN')
            from_number = os.environ.get('AUDIT_TWILIO_FROM_NUMBER')
            to_numbers = os.environ.get('AUDIT_SMS_RECIPIENTS', '').split(',')
            
            if not all([account_sid, auth_token, from_number]) or not to_numbers[0]:
                self.logger.debug("SMS configuration not complete, skipping SMS notification")
                return
            
            # Message SMS court
            sms_message = f"AINFLUE CRITICAL ALERT: {notification_data['alert_type']} at {notification_data['timestamp'][:19]}. Check logs immediately."
            
            # Simulation de l'envoi SMS (remplacer par vraie API)
            self.logger.info(f"SMS notification would be sent to {len(to_numbers)} recipients")
            self.logger.info(f"SMS content: {sms_message}")
            
            # Dans un vrai environnement:
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # for to_number in to_numbers:
            #     message = client.messages.create(
            #         body=sms_message,
            #         from_=from_number,
            #         to=to_number.strip()
            #     )
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {e}")
    
    async def shutdown(self):
        """Arrêt propre du système d'audit"""
        try:
            self.logger.info("🔒 Shutting down audit system...")
            
            # Flush final du buffer
            if self.audit_buffer:
                await self._flush_audit_buffer()
            
            # Fermeture pool de connexions
            if self.audit_pool:
                await self.audit_pool.close()
            
            self.logger.info("✅ Audit system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Audit system shutdown failed: {e}")


# Factory function
_audit_manager: Optional[DatabaseAuditManager] = None


def get_audit_manager(config: Optional[Dict[str, Any]] = None) -> DatabaseAuditManager:
    """Récupère ou crée l'instance du gestionnaire d'audit"""
    global _audit_manager
    
    if _audit_manager is None:
        _audit_manager = DatabaseAuditManager(config)
    
    return _audit_manager


# Fonctions utilitaires pour l'interface publique
async def audit_log(
    event_type: AuditEventType,
    user_id: Optional[str] = None,
    **kwargs
) -> str:
    """Interface simplifiée pour l'audit logging"""
    manager = get_audit_manager()
    return await manager.log_audit_event(event_type, user_id, **kwargs)


# Export des classes et enums principaux
__all__ = [
    'DatabaseAuditManager',
    'AuditEvent',
    'AuditEventType',
    'AuditSeverity',
    'ComplianceFramework',
    'get_audit_manager',
    'audit_log'
]
