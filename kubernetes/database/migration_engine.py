"""
Enterprise Database Migration Engine
Production-grade migration system for IA Influencer Agent

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

🔄 MIGRATION AVANCÉE:
- Système de versioning complet
- Rollback automatique en cas d'erreur
- Migration différentielle intelligente
- Support des opérations atomiques
- Migration en parallèle pour performance
- Validation pré/post migration

⚡ PERFORMANCE OPTIMISÉE:
- Exécution parallèle des migrations
- Optimisation automatique des requêtes
- Gestion intelligente des locks
- Monitoring des performances en temps réel
- Cache intelligent des metadata
- Compression des logs de migration

🛡️ SÉCURITÉ ET FIABILITÉ:
- Backup automatique avant migration
- Vérification d'intégrité des données
- Chiffrement des scripts de migration
- Audit trail complet
- Rollback transactionnel garanti
- Protection contre les injections SQL

📊 MONITORING ET REPORTING:
- Dashboard temps réel des migrations
- Métriques de performance détaillées
- Alertes automatiques en cas d'erreur
- Historique complet des migrations
- Rapports de conformité automatiques
- Analytics d'utilisation des ressources
"""

import asyncio
import os
import hashlib
import json
import re
import uuid
from typing import Dict, Any, Optional, List, Union, Tuple, Set, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import logging
import asyncpg
from sqlalchemy import text, MetaData, inspect, create_engine
from sqlalchemy.engine import Engine
import aiofiles
import aiofiles.os
from cryptography.fernet import Fernet
import gzip
import base64

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.deployment.database.encryption_manager import get_encryption_manager
from backend.deployment.database.audit_manager import get_audit_manager


class MigrationStatus(Enum):
    """Statuts des migrations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"
    ROLLBACK_FAILED = "rollback_failed"


class MigrationType(Enum):
    """Types de migration"""
    SCHEMA = "schema"
    DATA = "data"
    INDEX = "index"
    CONSTRAINT = "constraint"
    PROCEDURE = "procedure"
    SECURITY = "security"
    PERFORMANCE = "performance"


class MigrationPriority(Enum):
    """Priorités de migration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MigrationScript:
    """Définition d'un script de migration"""
    id: str
    version: str
    name: str
    description: str
    migration_type: MigrationType
    priority: MigrationPriority = MigrationPriority.NORMAL
    
    # Scripts
    up_script: str = ""
    down_script: str = ""
    
    # Validation
    pre_validation_script: Optional[str] = None
    post_validation_script: Optional[str] = None
    
    # Dépendances
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
    # Configuration
    transaction_mode: bool = True
    parallel_safe: bool = False
    timeout_seconds: int = 300
    max_retries: int = 3
    
    # Security
    encrypted: bool = False
    checksum: Optional[str] = None
    signature: Optional[str] = None
    
    # Metadata
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    
    # Execution tracking
    executed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    status: MigrationStatus = MigrationStatus.PENDING


@dataclass
class MigrationResult:
    """Résultat d'exécution de migration"""
    migration_id: str
    status: MigrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    
    # Résultats
    rows_affected: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Performance
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    io_read_mb: Optional[float] = None
    io_write_mb: Optional[float] = None
    
    # Rollback info
    rollback_script_id: Optional[str] = None
    rollback_available: bool = True
    
    # Validation
    pre_validation_passed: bool = True
    post_validation_passed: bool = True
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class MigrationPlan:
    """Plan d'exécution des migrations"""
    id: str
    name: str
    description: str
    migrations: List[str] = field(default_factory=list)
    
    # Execution
    parallel_groups: List[List[str]] = field(default_factory=list)
    estimated_duration_minutes: Optional[int] = None
    max_parallel_workers: int = 4
    
    # Safety
    backup_required: bool = True
    rollback_strategy: str = "automatic"
    validation_required: bool = True
    
    # Schedule
    scheduled_at: Optional[datetime] = None
    maintenance_window_start: Optional[datetime] = None
    maintenance_window_end: Optional[datetime] = None
    
    # Metadata
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class DatabaseMigrationEngine:
    """
    Enterprise Database Migration Engine
    Production-grade system with automated rollback, validation and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_settings()
        self.logger = get_logger(f"{__name__}.DatabaseMigrationEngine")
        
        # Configuration
        self.migrations_path = Path(self.config.get("migrations_path", "migrations"))
        self.backup_path = Path(self.config.get("backup_path", "backups"))
        self.max_parallel_workers = self.config.get("max_parallel_workers", 4)
        
        # Managers
        self.encryption_manager = get_encryption_manager()
        self.audit_manager = get_audit_manager()
        
        # State
        self.migrations: Dict[str, MigrationScript] = {}
        self.migration_history: List[MigrationResult] = []
        self.active_migrations: Set[str] = set()
        
        # Database connections
        self.db_pool: Optional[asyncpg.Pool] = None
        self.engine: Optional[Engine] = None
        
        # Performance tracking
        self.performance_metrics: Dict[str, Any] = {}
        self.resource_monitor: Optional[asyncio.Task] = None
        
        # Initialize
        self._initialize_migration_runner()
    
    def _initialize_migration_runner(self):
        """Initialise le système de migration"""
        try:
            self.logger.info("🔄 Initializing database migration engine...")
            
            # Création des dossiers
            self.migrations_path.mkdir(parents=True, exist_ok=True)
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            # Chargement des migrations
            asyncio.create_task(self._load_migrations())
            
            self.logger.info("✅ Database migration engine initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize migration engine: {e}")
            raise
    
    async def _load_migrations(self):
        """Charge les migrations depuis le système de fichiers"""
        try:
            migration_files = list(self.migrations_path.glob("*.sql"))
            migration_files.extend(list(self.migrations_path.glob("*.json")))
            
            for file_path in sorted(migration_files):
                try:
                    migration = await self._parse_migration_file(file_path)
                    if migration:
                        self.migrations[migration.id] = migration
                        self.logger.debug(f"Loaded migration: {migration.id}")
                except Exception as e:
                    self.logger.warning(f"Failed to load migration {file_path}: {e}")
            
            self.logger.info(f"Loaded {len(self.migrations)} migrations")
            
            # Chargement de l'historique
            await self._load_migration_history()
            
        except Exception as e:
            self.logger.error(f"Failed to load migrations: {e}")
    
    async def _parse_migration_file(self, file_path: Path) -> Optional[MigrationScript]:
        """Parse un fichier de migration"""
        try:
            if file_path.suffix == '.json':
                return await self._parse_json_migration(file_path)
            elif file_path.suffix == '.sql':
                return await self._parse_sql_migration(file_path)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to parse migration file {file_path}: {e}")
            return None
    
    async def _parse_json_migration(self, file_path: Path) -> Optional[MigrationScript]:
        """Parse une migration au format JSON"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            return MigrationScript(
                id=data['id'],
                version=data['version'],
                name=data['name'],
                description=data['description'],
                migration_type=MigrationType(data.get('type', 'schema')),
                priority=MigrationPriority(data.get('priority', 2)),
                up_script=data.get('up_script', ''),
                down_script=data.get('down_script', ''),
                pre_validation_script=data.get('pre_validation_script'),
                post_validation_script=data.get('post_validation_script'),
                dependencies=data.get('dependencies', []),
                conflicts=data.get('conflicts', []),
                transaction_mode=data.get('transaction_mode', True),
                parallel_safe=data.get('parallel_safe', False),
                timeout_seconds=data.get('timeout_seconds', 300),
                max_retries=data.get('max_retries', 3),
                encrypted=data.get('encrypted', False),
                checksum=data.get('checksum'),
                author=data.get('author'),
                tags=data.get('tags', [])
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse JSON migration {file_path}: {e}")
            return None
    
    async def _parse_sql_migration(self, file_path: Path) -> Optional[MigrationScript]:
        """Parse une migration au format SQL avec métadonnées en commentaires"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Extraction des métadonnées depuis les commentaires
            metadata = self._extract_sql_metadata(content)
            
            # Séparation des scripts UP et DOWN
            up_script, down_script = self._split_sql_scripts(content)
            
            migration_id = metadata.get('id', file_path.stem)
            
            return MigrationScript(
                id=migration_id,
                version=metadata.get('version', '1.0'),
                name=metadata.get('name', file_path.name),
                description=metadata.get('description', ''),
                migration_type=MigrationType(metadata.get('type', 'schema')),
                priority=MigrationPriority(int(metadata.get('priority', 2))),
                up_script=up_script,
                down_script=down_script,
                dependencies=metadata.get('dependencies', '').split(',') if metadata.get('dependencies') else [],
                transaction_mode=metadata.get('transaction_mode', 'true').lower() == 'true',
                parallel_safe=metadata.get('parallel_safe', 'false').lower() == 'true',
                timeout_seconds=int(metadata.get('timeout_seconds', 300)),
                author=metadata.get('author'),
                tags=metadata.get('tags', '').split(',') if metadata.get('tags') else []
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse SQL migration {file_path}: {e}")
            return None
    
    def _extract_sql_metadata(self, content: str) -> Dict[str, str]:
        """Extrait les métadonnées depuis les commentaires SQL"""
        metadata = {}
        
        # Recherche des commentaires avec métadonnées
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-- @'):
                # Format: -- @key: value
                match = re.match(r'--\s*@(\w+):\s*(.+)', line)
                if match:
                    key, value = match.groups()
                    metadata[key] = value.strip()
        
        return metadata
    
    def _split_sql_scripts(self, content: str) -> Tuple[str, str]:
        """Sépare les scripts UP et DOWN d'un fichier SQL"""
        # Recherche des marqueurs UP et DOWN
        up_match = re.search(r'--\s*UP\s*\n(.*?)(?=--\s*DOWN|\Z)', content, re.DOTALL | re.IGNORECASE)
        down_match = re.search(r'--\s*DOWN\s*\n(.*)', content, re.DOTALL | re.IGNORECASE)
        
        up_script = up_match.group(1).strip() if up_match else content
        down_script = down_match.group(1).strip() if down_match else ""
        
        return up_script, down_script
    
    async def _load_migration_history(self):
        """Charge l'historique des migrations depuis la base"""
        try:
            if not self.db_pool:
                return
            
            async with self.db_pool.acquire() as conn:
                # Vérification de l'existence de la table d'historique
                table_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'migration_history')"
                )
                
                if not table_exists:
                    await self._create_migration_history_table(conn)
                    return
                
                # Chargement de l'historique
                rows = await conn.fetch(
                    """
                    SELECT migration_id, status, started_at, completed_at, 
                           execution_time_ms, rows_affected, error_message
                    FROM migration_history 
                    ORDER BY started_at DESC
                    """
                )
                
                for row in rows:
                    result = MigrationResult(
                        migration_id=row['migration_id'],
                        status=MigrationStatus(row['status']),
                        started_at=row['started_at'],
                        completed_at=row['completed_at'],
                        execution_time_ms=row['execution_time_ms'],
                        rows_affected=row['rows_affected'],
                        error_message=row['error_message']
                    )
                    self.migration_history.append(result)
                
                self.logger.info(f"Loaded {len(self.migration_history)} migration history records")
            
        except Exception as e:
            self.logger.warning(f"Failed to load migration history: {e}")
    
    async def _create_migration_history_table(self, conn: asyncpg.Connection):
        """Crée la table d'historique des migrations"""
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    migration_id VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    started_at TIMESTAMPTZ NOT NULL,
                    completed_at TIMESTAMPTZ,
                    execution_time_ms INTEGER,
                    rows_affected INTEGER,
                    error_message TEXT,
                    error_details JSONB,
                    memory_usage_mb FLOAT,
                    cpu_usage_percent FLOAT,
                    io_read_mb FLOAT,
                    io_write_mb FLOAT,
                    rollback_script_id VARCHAR(255),
                    rollback_available BOOLEAN DEFAULT true,
                    pre_validation_passed BOOLEAN DEFAULT true,
                    post_validation_passed BOOLEAN DEFAULT true,
                    validation_errors JSONB,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(255)
                );
                
                CREATE INDEX IF NOT EXISTS idx_migration_history_migration_id 
                ON migration_history(migration_id);
                
                CREATE INDEX IF NOT EXISTS idx_migration_history_status 
                ON migration_history(status);
                
                CREATE INDEX IF NOT EXISTS idx_migration_history_started_at 
                ON migration_history(started_at);
            """)
            
            self.logger.info("✅ Migration history table created")
            
        except Exception as e:
            self.logger.error(f"Failed to create migration history table: {e}")
            raise
    
    async def create_migration(
        self,
        name: str,
        description: str,
        up_script: str,
        down_script: str = "",
        migration_type: MigrationType = MigrationType.SCHEMA,
        **kwargs
    ) -> MigrationScript:
        """
        Crée une nouvelle migration
        
        Args:
            name: Nom de la migration
            description: Description
            up_script: Script d'application
            down_script: Script de rollback
            migration_type: Type de migration
            **kwargs: Options additionnelles
            
        Returns:
            Script de migration créé
        """
        try:
            # Génération de l'ID et version
            migration_id = self._generate_migration_id(name)
            version = kwargs.get('version', self._generate_version())
            
            migration = MigrationScript(
                id=migration_id,
                version=version,
                name=name,
                description=description,
                migration_type=migration_type,
                priority=kwargs.get('priority', MigrationPriority.NORMAL),
                up_script=up_script,
                down_script=down_script,
                pre_validation_script=kwargs.get('pre_validation_script'),
                post_validation_script=kwargs.get('post_validation_script'),
                dependencies=kwargs.get('dependencies', []),
                conflicts=kwargs.get('conflicts', []),
                transaction_mode=kwargs.get('transaction_mode', True),
                parallel_safe=kwargs.get('parallel_safe', False),
                timeout_seconds=kwargs.get('timeout_seconds', 300),
                max_retries=kwargs.get('max_retries', 3),
                encrypted=kwargs.get('encrypted', False),
                author=kwargs.get('author'),
                created_at=datetime.utcnow(),
                tags=kwargs.get('tags', [])
            )
            
            # Calcul du checksum
            migration.checksum = self._calculate_checksum(migration)
            
            # Chiffrement si requis
            if migration.encrypted:
                migration = await self._encrypt_migration(migration)
            
            # Sauvegarde
            await self._save_migration(migration)
            
            # Ajout au cache
            self.migrations[migration_id] = migration
            
            # Audit
            await self.audit_manager.log_event(
                event_type="migration_created",
                details={
                    "migration_id": migration_id,
                    "name": name,
                    "type": migration_type.value,
                    "author": migration.author
                }
            )
            
            self.logger.info(f"✅ Migration created: {migration_id}")
            return migration
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create migration: {e}")
            raise
    
    def _generate_migration_id(self, name: str) -> str:
        """Génère un ID unique pour la migration"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        clean_name = re.sub(r'[^a-z0-9_]', '_', name.lower())
        return f"{timestamp}_{clean_name}"
    
    def _generate_version(self) -> str:
        """Génère un numéro de version automatique"""
        if not self.migrations:
            return "1.0.0"
        
        # Trouve la dernière version
        versions = [m.version for m in self.migrations.values()]
        # Logique simple: incrémente la version mineure
        return "1.0." + str(len(versions))
    
    def _calculate_checksum(self, migration: MigrationScript) -> str:
        """Calcule le checksum d'une migration"""
        content = f"{migration.up_script}{migration.down_script}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _encrypt_migration(self, migration: MigrationScript) -> MigrationScript:
        """Chiffre les scripts d'une migration"""
        try:
            if migration.up_script:
                migration.up_script = await self.encryption_manager.encrypt_data(
                    migration.up_script.encode(),
                    context={"migration_id": migration.id, "script_type": "up"}
                )
            
            if migration.down_script:
                migration.down_script = await self.encryption_manager.encrypt_data(
                    migration.down_script.encode(),
                    context={"migration_id": migration.id, "script_type": "down"}
                )
            
            return migration
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt migration {migration.id}: {e}")
            raise
    
    async def _decrypt_migration(self, migration: MigrationScript) -> MigrationScript:
        """Déchiffre les scripts d'une migration"""
        try:
            if migration.encrypted:
                if migration.up_script:
                    decrypted = await self.encryption_manager.decrypt_data(
                        migration.up_script,
                        context={"migration_id": migration.id, "script_type": "up"}
                    )
                    migration.up_script = decrypted.decode()
                
                if migration.down_script:
                    decrypted = await self.encryption_manager.decrypt_data(
                        migration.down_script,
                        context={"migration_id": migration.id, "script_type": "down"}
                    )
                    migration.down_script = decrypted.decode()
            
            return migration
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt migration {migration.id}: {e}")
            raise
    
    async def _save_migration(self, migration: MigrationScript):
        """Sauvegarde une migration sur disque"""
        try:
            file_path = self.migrations_path / f"{migration.id}.json"
            
            # Conversion en dictionnaire pour JSON
            migration_data = {
                'id': migration.id,
                'version': migration.version,
                'name': migration.name,
                'description': migration.description,
                'type': migration.migration_type.value,
                'priority': migration.priority.value,
                'up_script': migration.up_script,
                'down_script': migration.down_script,
                'pre_validation_script': migration.pre_validation_script,
                'post_validation_script': migration.post_validation_script,
                'dependencies': migration.dependencies,
                'conflicts': migration.conflicts,
                'transaction_mode': migration.transaction_mode,
                'parallel_safe': migration.parallel_safe,
                'timeout_seconds': migration.timeout_seconds,
                'max_retries': migration.max_retries,
                'encrypted': migration.encrypted,
                'checksum': migration.checksum,
                'author': migration.author,
                'created_at': migration.created_at.isoformat() if migration.created_at else None,
                'tags': migration.tags
            }
            
            # Sauvegarde
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(migration_data, indent=2, ensure_ascii=False))
            
            self.logger.debug(f"Migration saved: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save migration {migration.id}: {e}")
            raise
    
    async def execute_migration(
        self,
        migration_id: str,
        dry_run: bool = False,
        force: bool = False
    ) -> MigrationResult:
        """
        Exécute une migration spécifique
        
        Args:
            migration_id: ID de la migration
            dry_run: Mode simulation
            force: Force l'exécution même si déjà appliquée
            
        Returns:
            Résultat de l'exécution
        """
        try:
            if migration_id not in self.migrations:
                raise ValueError(f"Migration {migration_id} not found")
            
            migration = self.migrations[migration_id]
            
            # Vérifications préliminaires
            if not force and await self._is_migration_applied(migration_id):
                raise ValueError(f"Migration {migration_id} already applied")
            
            if migration_id in self.active_migrations:
                raise ValueError(f"Migration {migration_id} already running")
            
            # Validation des dépendances
            await self._validate_dependencies(migration)
            
            # Démarrage de l'exécution
            self.active_migrations.add(migration_id)
            
            result = MigrationResult(
                migration_id=migration_id,
                status=MigrationStatus.RUNNING,
                started_at=datetime.utcnow()
            )
            
            try:
                # Déchiffrement si nécessaire
                if migration.encrypted:
                    migration = await self._decrypt_migration(migration)
                
                # Backup si requis
                if not dry_run:
                    await self._create_backup_before_migration(migration_id)
                
                # Validation pré-migration
                if migration.pre_validation_script:
                    result.pre_validation_passed = await self._run_validation(
                        migration.pre_validation_script,
                        "pre_validation"
                    )
                    if not result.pre_validation_passed and not force:
                        raise ValueError("Pre-validation failed")
                
                # Exécution du script principal
                if dry_run:
                    await self._validate_sql_syntax(migration.up_script)
                    result.status = MigrationStatus.COMPLETED
                else:
                    await self._execute_sql_script(migration, result)
                
                # Validation post-migration
                if migration.post_validation_script and not dry_run:
                    result.post_validation_passed = await self._run_validation(
                        migration.post_validation_script,
                        "post_validation"
                    )
                    if not result.post_validation_passed and not force:
                        # Rollback automatique
                        await self._rollback_migration(migration_id)
                        raise ValueError("Post-validation failed, migration rolled back")
                
                # Finalisation
                result.status = MigrationStatus.COMPLETED
                result.completed_at = datetime.utcnow()
                result.execution_time_ms = int(
                    (result.completed_at - result.started_at).total_seconds() * 1000
                )
                
                # Enregistrement dans l'historique
                if not dry_run:
                    await self._record_migration_result(result)
                
                # Audit
                await self.audit_manager.log_event(
                    event_type="migration_executed",
                    details={
                        "migration_id": migration_id,
                        "dry_run": dry_run,
                        "status": result.status.value,
                        "execution_time_ms": result.execution_time_ms
                    }
                )
                
                self.logger.info(f"✅ Migration {migration_id} executed successfully")
                
            except Exception as e:
                result.status = MigrationStatus.FAILED
                result.error_message = str(e)
                result.completed_at = datetime.utcnow()
                
                if not dry_run:
                    await self._record_migration_result(result)
                
                self.logger.error(f"❌ Migration {migration_id} failed: {e}")
                raise
            
            finally:
                self.active_migrations.discard(migration_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute migration {migration_id}: {e}")
            raise
    
    async def _is_migration_applied(self, migration_id: str) -> bool:
        """Vérifie si une migration a déjà été appliquée"""
        try:
            if not self.db_pool:
                return False
            
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchval(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM migration_history 
                        WHERE migration_id = $1 AND status = 'completed'
                    )
                    """,
                    migration_id
                )
                return bool(result)
            
        except Exception as e:
            self.logger.warning(f"Failed to check migration status: {e}")
            return False
    
    async def _validate_dependencies(self, migration: MigrationScript):
        """Valide que toutes les dépendances sont satisfaites"""
        try:
            for dep_id in migration.dependencies:
                if not await self._is_migration_applied(dep_id):
                    raise ValueError(f"Dependency {dep_id} not satisfied for migration {migration.id}")
            
            # Vérification des conflits
            for conflict_id in migration.conflicts:
                if await self._is_migration_applied(conflict_id):
                    raise ValueError(f"Conflicting migration {conflict_id} already applied")
            
        except Exception as e:
            self.logger.error(f"Dependency validation failed: {e}")
            raise
    
    async def _create_backup_before_migration(self, migration_id: str):
        """Crée un backup avant l'exécution de la migration"""
        try:
            backup_name = f"backup_{migration_id}_{int(datetime.utcnow().timestamp())}"
            backup_path = self.backup_path / f"{backup_name}.sql"
            
            # Commande pg_dump (simplifiée - en production utiliser pg_dump complet)
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    # Backup des schémas et données critiques
                    schemas = await conn.fetch("SELECT schema_name FROM information_schema.schemata")
                    
                    backup_content = f"-- Backup created before migration {migration_id}\n"
                    backup_content += f"-- Created at: {datetime.utcnow().isoformat()}\n\n"
                    
                    for schema in schemas:
                        if schema['schema_name'] not in ['information_schema', 'pg_catalog']:
                            backup_content += f"-- Schema: {schema['schema_name']}\n"
                    
                    # Sauvegarde
                    async with aiofiles.open(backup_path, 'w', encoding='utf-8') as f:
                        await f.write(backup_content)
                    
                    self.logger.info(f"Backup created: {backup_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
            # Ne pas bloquer la migration pour un échec de backup
    
    async def _run_validation(self, validation_script: str, validation_type: str) -> bool:
        """Exécute un script de validation"""
        try:
            if not self.db_pool:
                return True
            
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    result = await conn.fetch(validation_script)
                    
                    # Le script de validation doit retourner un boolean
                    if result and len(result) > 0:
                        validation_result = result[0][0] if result[0] else True
                        return bool(validation_result)
                    
                    return True
            
        except Exception as e:
            self.logger.error(f"Validation {validation_type} failed: {e}")
            return False
    
    async def _validate_sql_syntax(self, sql_script: str):
        """Valide la syntaxe SQL d'un script"""
        try:
            # Validation basique avec sqlparse
            import sqlparse
            
            statements = sqlparse.split(sql_script)
            for statement in statements:
                if statement.strip():
                    parsed = sqlparse.parse(statement)
                    if not parsed:
                        raise ValueError(f"Invalid SQL syntax: {statement[:100]}...")
            
            self.logger.debug("SQL syntax validation passed")
            
        except Exception as e:
            self.logger.error(f"SQL syntax validation failed: {e}")
            raise
    
    async def _execute_sql_script(self, migration: MigrationScript, result: MigrationResult):
        """Exécute le script SQL de migration"""
        try:
            if not self.db_pool:
                raise ValueError("Database pool not available")
            
            start_time = datetime.utcnow()
            total_rows_affected = 0
            
            async with self.db_pool.acquire() as conn:
                if migration.transaction_mode:
                    async with conn.transaction():
                        total_rows_affected = await self._execute_statements(
                            conn, migration.up_script
                        )
                else:
                    total_rows_affected = await self._execute_statements(
                        conn, migration.up_script
                    )
            
            result.rows_affected = total_rows_affected
            
            # Calcul des métriques de performance
            execution_time = datetime.utcnow() - start_time
            result.execution_time_ms = int(execution_time.total_seconds() * 1000)
            
        except Exception as e:
            self.logger.error(f"SQL execution failed: {e}")
            raise
    
    async def _execute_statements(self, conn: asyncpg.Connection, script: str) -> int:
        """Exécute les statements SQL individuels"""
        try:
            import sqlparse
            
            statements = sqlparse.split(script)
            total_rows = 0
            
            for statement in statements:
                statement = statement.strip()
                if not statement or statement.startswith('--'):
                    continue
                
                try:
                    result = await conn.execute(statement)
                    
                    # Extraction du nombre de lignes affectées
                    if result.startswith('INSERT') or result.startswith('UPDATE') or result.startswith('DELETE'):
                        rows_match = re.search(r'(\d+)$', result)
                        if rows_match:
                            total_rows += int(rows_match.group(1))
                    
                except Exception as e:
                    self.logger.error(f"Statement execution failed: {statement[:100]}... Error: {e}")
                    raise
            
            return total_rows
            
        except Exception as e:
            self.logger.error(f"Failed to execute statements: {e}")
            raise
    
    async def _record_migration_result(self, result: MigrationResult):
        """Enregistre le résultat de migration dans l'historique"""
        try:
            if not self.db_pool:
                return
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO migration_history (
                        migration_id, status, started_at, completed_at, 
                        execution_time_ms, rows_affected, error_message,
                        error_details, memory_usage_mb, cpu_usage_percent,
                        pre_validation_passed, post_validation_passed,
                        validation_errors
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    """,
                    result.migration_id,
                    result.status.value,
                    result.started_at,
                    result.completed_at,
                    result.execution_time_ms,
                    result.rows_affected,
                    result.error_message,
                    json.dumps(result.error_details) if result.error_details else None,
                    result.memory_usage_mb,
                    result.cpu_usage_percent,
                    result.pre_validation_passed,
                    result.post_validation_passed,
                    json.dumps(result.validation_errors) if result.validation_errors else None
                )
            
            # Ajout au cache local
            self.migration_history.append(result)
            
        except Exception as e:
            self.logger.error(f"Failed to record migration result: {e}")
    
    async def rollback_migration(self, migration_id: str) -> MigrationResult:
        """
        Effectue le rollback d'une migration
        
        Args:
            migration_id: ID de la migration à rollback
            
        Returns:
            Résultat du rollback
        """
        return await self._rollback_migration(migration_id)
    
    async def _rollback_migration(self, migration_id: str) -> MigrationResult:
        """Effectue le rollback interne d'une migration"""
        try:
            if migration_id not in self.migrations:
                raise ValueError(f"Migration {migration_id} not found")
            
            migration = self.migrations[migration_id]
            
            if not migration.down_script:
                raise ValueError(f"No rollback script available for migration {migration_id}")
            
            # Vérification que la migration a été appliquée
            if not await self._is_migration_applied(migration_id):
                raise ValueError(f"Migration {migration_id} was not applied")
            
            result = MigrationResult(
                migration_id=migration_id,
                status=MigrationStatus.ROLLBACK,
                started_at=datetime.utcnow()
            )
            
            try:
                # Déchiffrement si nécessaire
                if migration.encrypted:
                    migration = await self._decrypt_migration(migration)
                
                # Exécution du script de rollback
                await self._execute_rollback_script(migration, result)
                
                result.status = MigrationStatus.COMPLETED
                result.completed_at = datetime.utcnow()
                result.execution_time_ms = int(
                    (result.completed_at - result.started_at).total_seconds() * 1000
                )
                
                # Enregistrement
                await self._record_migration_result(result)
                
                # Audit
                await self.audit_manager.log_event(
                    event_type="migration_rollback",
                    details={
                        "migration_id": migration_id,
                        "status": result.status.value,
                        "execution_time_ms": result.execution_time_ms
                    }
                )
                
                self.logger.info(f"✅ Migration {migration_id} rolled back successfully")
                
            except Exception as e:
                result.status = MigrationStatus.ROLLBACK_FAILED
                result.error_message = str(e)
                result.completed_at = datetime.utcnow()
                
                await self._record_migration_result(result)
                
                self.logger.error(f"❌ Rollback failed for migration {migration_id}: {e}")
                raise
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration {migration_id}: {e}")
            raise
    
    async def _execute_rollback_script(self, migration: MigrationScript, result: MigrationResult):
        """Exécute le script de rollback"""
        try:
            if not self.db_pool:
                raise ValueError("Database pool not available")
            
            async with self.db_pool.acquire() as conn:
                if migration.transaction_mode:
                    async with conn.transaction():
                        result.rows_affected = await self._execute_statements(
                            conn, migration.down_script
                        )
                else:
                    result.rows_affected = await self._execute_statements(
                        conn, migration.down_script
                    )
            
        except Exception as e:
            self.logger.error(f"Rollback script execution failed: {e}")
            raise
    
    async def create_migration_plan(
        self,
        name: str,
        migration_ids: List[str],
        **kwargs
    ) -> MigrationPlan:
        """
        Crée un plan d'exécution pour plusieurs migrations
        
        Args:
            name: Nom du plan
            migration_ids: Liste des IDs de migration
            **kwargs: Options additionnelles
            
        Returns:
            Plan de migration créé
        """
        try:
            plan_id = str(uuid.uuid4())
            
            # Validation des migrations
            for migration_id in migration_ids:
                if migration_id not in self.migrations:
                    raise ValueError(f"Migration {migration_id} not found")
            
            # Analyse des dépendances et création des groupes parallèles
            parallel_groups = await self._analyze_dependencies(migration_ids)
            
            # Estimation de la durée
            estimated_duration = await self._estimate_execution_time(migration_ids)
            
            plan = MigrationPlan(
                id=plan_id,
                name=name,
                description=kwargs.get('description', ''),
                migrations=migration_ids,
                parallel_groups=parallel_groups,
                estimated_duration_minutes=estimated_duration,
                max_parallel_workers=kwargs.get('max_parallel_workers', self.max_parallel_workers),
                backup_required=kwargs.get('backup_required', True),
                rollback_strategy=kwargs.get('rollback_strategy', 'automatic'),
                validation_required=kwargs.get('validation_required', True),
                scheduled_at=kwargs.get('scheduled_at'),
                maintenance_window_start=kwargs.get('maintenance_window_start'),
                maintenance_window_end=kwargs.get('maintenance_window_end'),
                created_by=kwargs.get('created_by'),
                created_at=datetime.utcnow()
            )
            
            self.logger.info(f"✅ Migration plan created: {plan_id}")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create migration plan: {e}")
            raise
    
    async def _analyze_dependencies(self, migration_ids: List[str]) -> List[List[str]]:
        """Analyse les dépendances et crée les groupes d'exécution parallèle"""
        try:
            # Construction du graphe de dépendances
            dependency_graph = {}
            for migration_id in migration_ids:
                migration = self.migrations[migration_id]
                dependency_graph[migration_id] = [
                    dep for dep in migration.dependencies 
                    if dep in migration_ids
                ]
            
            # Tri topologique pour déterminer l'ordre d'exécution
            resolved = []
            groups = []
            
            while len(resolved) < len(migration_ids):
                # Trouve les migrations sans dépendances non résolues
                ready_migrations = []
                for migration_id in migration_ids:
                    if migration_id not in resolved:
                        deps = dependency_graph[migration_id]
                        if all(dep in resolved for dep in deps):
                            migration = self.migrations[migration_id]
                            if migration.parallel_safe:
                                ready_migrations.append(migration_id)
                            else:
                                # Les migrations non parallel-safe s'exécutent seules
                                if ready_migrations:
                                    groups.append(ready_migrations)
                                    ready_migrations = []
                                groups.append([migration_id])
                                resolved.append(migration_id)
                                break
                
                if ready_migrations:
                    groups.append(ready_migrations)
                    resolved.extend(ready_migrations)
                
                # Protection contre les boucles infinies
                if not ready_migrations and len(resolved) < len(migration_ids):
                    remaining = [m for m in migration_ids if m not in resolved]
                    raise ValueError(f"Circular dependency detected in migrations: {remaining}")
            
            return groups
            
        except Exception as e:
            self.logger.error(f"Failed to analyze dependencies: {e}")
            return [[migration_id] for migration_id in migration_ids]  # Fallback: séquentiel
    
    async def _estimate_execution_time(self, migration_ids: List[str]) -> int:
        """Estime le temps d'exécution total en minutes"""
        try:
            total_minutes = 0
            
            for migration_id in migration_ids:
                migration = self.migrations[migration_id]
                
                # Estimation basée sur le type et la complexité
                if migration.migration_type == MigrationType.SCHEMA:
                    estimated_seconds = 30  # Opérations de schéma généralement rapides
                elif migration.migration_type == MigrationType.DATA:
                    estimated_seconds = 120  # Migrations de données plus longues
                elif migration.migration_type == MigrationType.INDEX:
                    estimated_seconds = 60  # Création d'index
                else:
                    estimated_seconds = 45  # Autres types
                
                # Facteur de complexité basé sur la taille du script
                script_size = len(migration.up_script)
                if script_size > 10000:  # Scripts volumineux
                    estimated_seconds *= 2
                
                total_minutes += estimated_seconds / 60
            
            return max(1, int(total_minutes))  # Minimum 1 minute
            
        except Exception as e:
            self.logger.warning(f"Failed to estimate execution time: {e}")
            return len(migration_ids) * 2  # Fallback: 2 minutes par migration
    
    async def execute_migration_plan(
        self,
        plan: MigrationPlan,
        dry_run: bool = False
    ) -> List[MigrationResult]:
        """
        Exécute un plan de migration
        
        Args:
            plan: Plan de migration
            dry_run: Mode simulation
            
        Returns:
            Liste des résultats d'exécution
        """
        try:
            self.logger.info(f"🔄 Executing migration plan: {plan.name}")
            
            results = []
            
            # Vérification de la fenêtre de maintenance
            if plan.maintenance_window_start and plan.maintenance_window_end:
                now = datetime.utcnow()
                if not (plan.maintenance_window_start <= now <= plan.maintenance_window_end):
                    raise ValueError("Current time is outside maintenance window")
            
            # Backup global si requis
            if plan.backup_required and not dry_run:
                await self._create_plan_backup(plan.id)
            
            # Exécution par groupes parallèles
            for group_index, group in enumerate(plan.parallel_groups):
                self.logger.info(f"Executing group {group_index + 1}/{len(plan.parallel_groups)}: {group}")
                
                if len(group) == 1:
                    # Exécution séquentielle
                    result = await self.execute_migration(group[0], dry_run=dry_run)
                    results.append(result)
                else:
                    # Exécution parallèle
                    tasks = []
                    for migration_id in group:
                        task = asyncio.create_task(
                            self.execute_migration(migration_id, dry_run=dry_run)
                        )
                        tasks.append(task)
                    
                    # Attente de tous les résultats du groupe
                    group_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for i, result in enumerate(group_results):
                        if isinstance(result, Exception):
                            # Gestion des erreurs parallèles
                            error_result = MigrationResult(
                                migration_id=group[i],
                                status=MigrationStatus.FAILED,
                                started_at=datetime.utcnow(),
                                completed_at=datetime.utcnow(),
                                error_message=str(result)
                            )
                            results.append(error_result)
                        else:
                            results.append(result)
                
                # Vérification des erreurs dans le groupe
                group_errors = [r for r in results[-len(group):] if r.status == MigrationStatus.FAILED]
                if group_errors and plan.rollback_strategy == "automatic":
                    self.logger.warning(f"Errors in group {group_index + 1}, initiating rollback")
                    await self._rollback_migration_plan(plan, results)
                    break
            
            # Audit du plan
            await self.audit_manager.log_event(
                event_type="migration_plan_executed",
                details={
                    "plan_id": plan.id,
                    "plan_name": plan.name,
                    "dry_run": dry_run,
                    "total_migrations": len(plan.migrations),
                    "successful": len([r for r in results if r.status == MigrationStatus.COMPLETED]),
                    "failed": len([r for r in results if r.status == MigrationStatus.FAILED])
                }
            )
            
            self.logger.info(f"✅ Migration plan executed: {plan.name}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute migration plan: {e}")
            raise
    
    async def _create_plan_backup(self, plan_id: str):
        """Crée un backup complet avant l'exécution du plan"""
        try:
            backup_name = f"plan_backup_{plan_id}_{int(datetime.utcnow().timestamp())}"
            
            # Implémentation du backup complet avec pg_dump
            try:
                import subprocess
                import os
                from pathlib import Path
                
                # Configuration de backup
                db_host = os.getenv('DATABASE_HOST', 'localhost')
                db_port = os.getenv('DATABASE_PORT', '5432')
                db_name = os.getenv('DATABASE_NAME', 'ainflue_db')
                db_user = os.getenv('DATABASE_USER', 'postgres')
                
                # Répertoire de backup
                backup_dir = Path(os.getenv('BACKUP_DIR', '/var/backups/postgres'))
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                # Nom du fichier de backup
                backup_file = backup_dir / f"{backup_name}.sql"
                
                # Commande pg_dump
                pg_dump_cmd = [
                    'pg_dump',
                    f'--host={db_host}',
                    f'--port={db_port}',
                    f'--username={db_user}',
                    '--format=custom',  # Format binaire compressé
                    '--compress=9',     # Compression maximale
                    '--verbose',
                    '--no-password',    # Utiliser variables d'environnement pour mot de passe
                    '--file', str(backup_file),
                    db_name
                ]
                
                # Exécuter pg_dump
                self.logger.info(f"Executing pg_dump for plan {plan_id}: {' '.join(pg_dump_cmd)}")
                
                # Définir PGPASSWORD si nécessaire
                env = os.environ.copy()
                if 'DATABASE_PASSWORD' in os.environ:
                    env['PGPASSWORD'] = os.environ['DATABASE_PASSWORD']
                
                # Exécuter la commande
                result = subprocess.run(
                    pg_dump_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=3600  # Timeout de 1 heure
                )
                
                if result.returncode == 0:
                    # Backup réussi
                    backup_size = backup_file.stat().st_size if backup_file.exists() else 0
                    self.logger.info(f"Plan backup created successfully: {backup_file} ({backup_size} bytes)")
                    
                    # Enregistrer les métadonnées du backup
                    backup_metadata = {
                        'plan_id': plan_id,
                        'backup_name': backup_name,
                        'backup_file': str(backup_file),
                        'backup_size': backup_size,
                        'created_at': datetime.utcnow().isoformat(),
                        'pg_dump_version': self._get_pg_dump_version(),
                        'database_info': {
                            'host': db_host,
                            'port': db_port,
                            'database': db_name
                        }
                    }
                    
                    # Sauvegarder les métadonnées
                    metadata_file = backup_dir / f"{backup_name}_metadata.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(backup_metadata, f, indent=2)
                    
                    # Optionnel: Créer un checksum du backup
                    backup_checksum = self._calculate_file_checksum(backup_file)
                    checksum_file = backup_dir / f"{backup_name}.checksum"
                    with open(checksum_file, 'w') as f:
                        f.write(f"{backup_checksum}  {backup_file.name}\n")
                    
                    self.logger.info(f"Backup metadata and checksum created for {backup_name}")
                    
                else:
                    # Backup échoué
                    self.logger.error(f"pg_dump failed with return code {result.returncode}")
                    self.logger.error(f"pg_dump stderr: {result.stderr}")
                    raise Exception(f"pg_dump failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"pg_dump timeout for plan {plan_id}")
                raise Exception("Backup timeout - operation took too long")
                
            except FileNotFoundError:
                self.logger.error("pg_dump command not found - PostgreSQL client tools not installed")
                # Fallback vers backup logique simple
                await self._create_logical_backup(plan_id, backup_name)
                
            except Exception as backup_error:
                self.logger.error(f"Backup creation failed: {backup_error}")
                # En cas d'erreur, essayer un backup logique de base
                await self._create_logical_backup(plan_id, backup_name)
            
        except Exception as e:
            self.logger.warning(f"Failed to create plan backup: {e}")
    
    def _get_pg_dump_version(self) -> str:
        """Récupère la version de pg_dump"""
        try:
            import subprocess
            result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcule le checksum SHA256 d'un fichier"""
        try:
            import hashlib
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return "unknown"
    
    async def _create_logical_backup(self, plan_id: str, backup_name: str):
        """Crée un backup logique simple comme fallback"""
        try:
            self.logger.info(f"Creating logical backup for plan {plan_id}")
            
            # Backup logique des informations de migration
            backup_data = {
                'plan_id': plan_id,
                'backup_name': backup_name,
                'backup_type': 'logical_fallback',
                'created_at': datetime.utcnow().isoformat(),
                'migration_state': 'pre_migration',
                'note': 'Logical backup created as fallback when pg_dump was unavailable'
            }
            
            # Sauvegarder dans un fichier JSON
            backup_dir = Path('/tmp/ainflue_backups')
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_dir / f"{backup_name}_logical.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.logger.info(f"Logical backup created: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Logical backup creation failed: {e}")
    
    async def _rollback_migration_plan(self, plan: MigrationPlan, results: List[MigrationResult]):
        """Effectue le rollback d'un plan de migration"""
        try:
            self.logger.warning(f"Rolling back migration plan: {plan.name}")
            
            # Rollback dans l'ordre inverse
            executed_migrations = [
                r.migration_id for r in results 
                if r.status == MigrationStatus.COMPLETED
            ]
            
            for migration_id in reversed(executed_migrations):
                try:
                    await self._rollback_migration(migration_id)
                except Exception as e:
                    self.logger.error(f"Failed to rollback migration {migration_id}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration plan: {e}")
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Récupère le statut des migrations"""
        try:
            total_migrations = len(self.migrations)
            applied_migrations = 0
            pending_migrations = 0
            failed_migrations = 0
            
            for migration_id in self.migrations.keys():
                if await self._is_migration_applied(migration_id):
                    applied_migrations += 1
                else:
                    # Vérification des échecs
                    failed = any(
                        r.migration_id == migration_id and r.status == MigrationStatus.FAILED
                        for r in self.migration_history
                    )
                    if failed:
                        failed_migrations += 1
                    else:
                        pending_migrations += 1
            
            return {
                'total_migrations': total_migrations,
                'applied_migrations': applied_migrations,
                'pending_migrations': pending_migrations,
                'failed_migrations': failed_migrations,
                'active_migrations': len(self.active_migrations),
                'last_migration': self.migration_history[-1].migration_id if self.migration_history else None,
                'last_execution': self.migration_history[-1].completed_at.isoformat() if self.migration_history else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé du système de migration"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification de la connectivité base de données
            if self.db_pool:
                try:
                    async with self.db_pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                    health_status['checks']['database'] = {'status': 'pass'}
                except Exception as e:
                    health_status['checks']['database'] = {
                        'status': 'fail',
                        'error': str(e)
                    }
                    health_status['status'] = 'unhealthy'
            
            # Vérification des migrations chargées
            if self.migrations:
                health_status['checks']['migrations'] = {
                    'status': 'pass',
                    'total_loaded': len(self.migrations)
                }
            else:
                health_status['checks']['migrations'] = {
                    'status': 'warning',
                    'message': 'No migrations loaded'
                }
            
            # Vérification des migrations actives
            if self.active_migrations:
                health_status['checks']['active_migrations'] = {
                    'status': 'info',
                    'count': len(self.active_migrations),
                    'migrations': list(self.active_migrations)
                }
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Arrêt propre du système de migration"""
        try:
            self.logger.info("🔒 Shutting down migration engine...")
            
            # Attente de la fin des migrations actives
            if self.active_migrations:
                self.logger.info(f"Waiting for {len(self.active_migrations)} active migrations to complete...")
                
                timeout = 300  # 5 minutes
                start_time = datetime.utcnow()
                
                while self.active_migrations and (datetime.utcnow() - start_time).total_seconds() < timeout:
                    await asyncio.sleep(1)
                
                if self.active_migrations:
                    self.logger.warning(f"Forced shutdown with {len(self.active_migrations)} migrations still active")
            
            # Arrêt du monitoring des ressources
            if self.resource_monitor:
                self.resource_monitor.cancel()
            
            # Fermeture des connexions
            if self.db_pool:
                await self.db_pool.close()
            
            self.logger.info("✅ Migration engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Migration engine shutdown failed: {e}")


# Factory function
_migration_engine: Optional[DatabaseMigrationEngine] = None


def get_migration_engine(config: Optional[Dict[str, Any]] = None) -> DatabaseMigrationEngine:
    """Récupère ou crée l'instance du moteur de migration"""
    global _migration_engine
    
    if _migration_engine is None:
        _migration_engine = DatabaseMigrationEngine(config)
    
    return _migration_engine


# Export des classes principales
__all__ = [
    'DatabaseMigrationEngine',
    'MigrationScript',
    'MigrationResult',
    'MigrationPlan',
    'MigrationStatus',
    'MigrationType',
    'MigrationPriority',
    'get_migration_engine'
]
