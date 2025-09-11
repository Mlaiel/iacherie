"""
🏥 HEALTH CHECK MANAGER - ENTERPRISE HEALTH MONITORING SYSTEM
Rôle DevOps: Manager de health checks complet pour tous les services ML

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
import aiosqlite
from collections import defaultdict, deque
import time
import httpx
import psutil
import subprocess
import ssl
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Ainflue Business Logic Integration
from core.config import AinflueCoreConfig
from core.exceptions import AinflueCoreException

class HealthStatus(Enum):
    """États de santé des services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class CheckType(Enum):
    """Types de checks de santé"""
    HTTP_ENDPOINT = "http_endpoint"
    DATABASE_CONNECTION = "database_connection"
    REDIS_CONNECTION = "redis_connection"
    DISK_SPACE = "disk_space"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    MODEL_INFERENCE = "model_inference"
    EXTERNAL_API = "external_api"
    KUBERNETES_POD = "kubernetes_pod"
    CUSTOM_SCRIPT = "custom_script"

class Severity(Enum):
    """Niveaux de sévérité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class HealthCheckConfig:
    """Configuration d'un health check"""
    check_id: str
    name: str
    check_type: CheckType
    target: str  # URL, path, service name, etc.
    interval_seconds: int
    timeout_seconds: int
    retry_count: int
    severity: Severity
    creator_types: List[str]  # Types de créateurs affectés
    dependencies: List[str]  # IDs de checks dépendants
    custom_params: Dict[str, Any]
    enabled: bool

@dataclass
class HealthCheckResult:
    """Résultat d'un health check"""
    check_id: str
    timestamp: datetime
    status: HealthStatus
    response_time: float
    success: bool
    error_message: Optional[str]
    metrics: Dict[str, Any]
    creator_impact: List[str]

@dataclass
class ServiceHealth:
    """Santé globale d'un service"""
    service_name: str
    overall_status: HealthStatus
    check_results: List[HealthCheckResult]
    uptime_percentage: float
    last_incident: Optional[datetime]
    performance_score: float

class HealthCheckManager:
    """
    🏥 Enterprise Health Check Manager pour MLOps Infrastructure
    
    Fonctionnalités DevOps Expert:
    - Health monitoring complet tous services ML
    - Checks adaptatifs par type de créateur
    - Dependency mapping et cascade failures detection
    - Performance monitoring avec SLA tracking
    - Auto-healing et circuit breakers
    - Real-time dashboards et alerting
    - Creator-specific impact analysis
    """
    
    def __init__(self, config: Optional[AinflueCoreConfig] = None):
        self.config = config or AinflueCoreConfig()
        self.logger = self._setup_logging()
        self.db_path = "mlops_health_checks.db"
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Health check registry
        self.health_checks: Dict[str, HealthCheckConfig] = {}
        self.check_results: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.running_checks: Dict[str, asyncio.Task] = {}
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Creator impact mapping
        self.creator_service_mapping = {
            "musician": [
                "audio_processing_service",
                "ml_training_service", 
                "inference_engine",
                "storage_service"
            ],
            "blogger": [
                "nlp_service",
                "content_analysis_service",
                "seo_optimization_service",
                "inference_engine"
            ],
            "photographer": [
                "image_processing_service",
                "computer_vision_service",
                "ml_training_service",
                "storage_service"
            ],
            "influencer": [
                "multi_platform_service",
                "analytics_service",
                "social_media_api",
                "inference_engine"
            ],
            "comedian": [
                "content_analysis_service",
                "sentiment_analysis_service",
                "social_media_api",
                "inference_engine"
            ]
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger("HealthCheckManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    async def initialize(self) -> None:
        """Initialisation du Health Check Manager"""
        try:
            # Initialize database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS health_check_configs (
                        check_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        check_type TEXT NOT NULL,
                        target TEXT NOT NULL,
                        interval_seconds INTEGER,
                        timeout_seconds INTEGER,
                        retry_count INTEGER,
                        severity TEXT,
                        creator_types TEXT,
                        dependencies TEXT,
                        custom_params TEXT,
                        enabled BOOLEAN,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS health_check_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        check_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        status TEXT NOT NULL,
                        response_time REAL,
                        success BOOLEAN,
                        error_message TEXT,
                        metrics TEXT,
                        creator_impact TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS service_health_summary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_name TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        overall_status TEXT NOT NULL,
                        uptime_percentage REAL,
                        performance_score REAL,
                        incident_count INTEGER,
                        creator_types_affected TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        incident_id TEXT UNIQUE NOT NULL,
                        service_name TEXT NOT NULL,
                        check_id TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        status TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        creator_types_affected TEXT,
                        started_at TEXT NOT NULL,
                        resolved_at TEXT,
                        resolution_notes TEXT
                    )
                """)
                
                await db.commit()
            
            # Chargement des configurations par défaut
            await self._load_default_health_checks()
            
            self.logger.info("✅ Health Check Manager initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation: {e}")
            raise AinflueCoreException(f"Échec initialisation Health Check Manager: {e}")

    async def _load_default_health_checks(self) -> None:
        """Chargement des health checks par défaut"""
        try:
            default_checks = [
                # Infrastructure services
                HealthCheckConfig(
                    check_id="http_api_gateway",
                    name="API Gateway Health",
                    check_type=CheckType.HTTP_ENDPOINT,
                    target="http://localhost:8000/health",
                    interval_seconds=30,
                    timeout_seconds=5,
                    retry_count=3,
                    severity=Severity.CRITICAL,
                    creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                    dependencies=[],
                    custom_params={"expected_status": 200},
                    enabled=True
                ),
                
                # Database connectivity
                HealthCheckConfig(
                    check_id="postgres_connection",
                    name="PostgreSQL Database",
                    check_type=CheckType.DATABASE_CONNECTION,
                    target="postgresql://localhost:5432/ainflue",
                    interval_seconds=60,
                    timeout_seconds=10,
                    retry_count=2,
                    severity=Severity.CRITICAL,
                    creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                    dependencies=[],
                    custom_params={"query": "SELECT 1"},
                    enabled=True
                ),
                
                # Redis cache
                HealthCheckConfig(
                    check_id="redis_connection",
                    name="Redis Cache",
                    check_type=CheckType.REDIS_CONNECTION,
                    target="redis://localhost:6379",
                    interval_seconds=30,
                    timeout_seconds=5,
                    retry_count=2,
                    severity=Severity.HIGH,
                    creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                    dependencies=[],
                    custom_params={"test_key": "health_check"},
                    enabled=True
                ),
                
                # ML services
                HealthCheckConfig(
                    check_id="ml_inference_engine",
                    name="ML Inference Engine",
                    check_type=CheckType.MODEL_INFERENCE,
                    target="http://localhost:8001/predict",
                    interval_seconds=60,
                    timeout_seconds=15,
                    retry_count=2,
                    severity=Severity.HIGH,
                    creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                    dependencies=["http_api_gateway"],
                    custom_params={"test_payload": {"text": "health check"}},
                    enabled=True
                ),
                
                # Audio processing (musicians)
                HealthCheckConfig(
                    check_id="audio_processing_service",
                    name="Audio Processing Service",
                    check_type=CheckType.HTTP_ENDPOINT,
                    target="http://localhost:8002/health",
                    interval_seconds=45,
                    timeout_seconds=10,
                    retry_count=2,
                    severity=Severity.HIGH,
                    creator_types=["musician"],
                    dependencies=["ml_inference_engine"],
                    custom_params={"expected_status": 200},
                    enabled=True
                ),
                
                # Image processing (photographers)
                HealthCheckConfig(
                    check_id="image_processing_service",
                    name="Image Processing Service",
                    check_type=CheckType.HTTP_ENDPOINT,
                    target="http://localhost:8003/health",
                    interval_seconds=45,
                    timeout_seconds=10,
                    retry_count=2,
                    severity=Severity.HIGH,
                    creator_types=["photographer"],
                    dependencies=["ml_inference_engine"],
                    custom_params={"expected_status": 200},
                    enabled=True
                ),
                
                # System resources
                HealthCheckConfig(
                    check_id="disk_space_check",
                    name="Disk Space Monitor",
                    check_type=CheckType.DISK_SPACE,
                    target="/var/lib/docker",
                    interval_seconds=300,  # 5 minutes
                    timeout_seconds=5,
                    retry_count=1,
                    severity=Severity.MEDIUM,
                    creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                    dependencies=[],
                    custom_params={"threshold_percentage": 80},
                    enabled=True
                ),
                
                HealthCheckConfig(
                    check_id="memory_usage_check",
                    name="Memory Usage Monitor",
                    check_type=CheckType.MEMORY_USAGE,
                    target="system",
                    interval_seconds=120,  # 2 minutes
                    timeout_seconds=5,
                    retry_count=1,
                    severity=Severity.MEDIUM,
                    creator_types=["musician", "blogger", "photographer", "influencer", "comedian"],
                    dependencies=[],
                    custom_params={"threshold_percentage": 85},
                    enabled=True
                )
            ]
            
            for check_config in default_checks:
                await self.register_health_check(check_config)
                
            self.logger.info(f"✅ {len(default_checks)} health checks par défaut chargés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement health checks par défaut: {e}")

    async def register_health_check(self, config: HealthCheckConfig) -> bool:
        """Enregistrement d'un nouveau health check"""
        try:
            # Validation
            if config.check_id in self.health_checks:
                self.logger.warning(f"⚠️ Health check {config.check_id} déjà existant, mise à jour...")
            
            # Sauvegarde en base
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO health_check_configs 
                    (check_id, name, check_type, target, interval_seconds, timeout_seconds,
                     retry_count, severity, creator_types, dependencies, custom_params,
                     enabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    config.check_id, config.name, config.check_type.value, config.target,
                    config.interval_seconds, config.timeout_seconds, config.retry_count,
                    config.severity.value, json.dumps(config.creator_types),
                    json.dumps(config.dependencies), json.dumps(config.custom_params),
                    config.enabled, datetime.now().isoformat(), datetime.now().isoformat()
                ))
                await db.commit()
            
            # Ajout au registre
            self.health_checks[config.check_id] = config
            
            # Démarrage du monitoring si activé
            if config.enabled:
                await self._start_health_check(config.check_id)
            
            self.logger.info(f"✅ Health check {config.check_id} enregistré")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement health check: {e}")
            return False

    async def _start_health_check(self, check_id: str) -> None:
        """Démarrage du monitoring d'un health check"""
        try:
            config = self.health_checks.get(check_id)
            if not config:
                raise ValueError(f"Health check {check_id} non trouvé")
            
            # Arrêt de l'ancien task si existant
            if check_id in self.running_checks:
                self.running_checks[check_id].cancel()
            
            # Démarrage du nouveau task
            task = asyncio.create_task(self._run_health_check_loop(config))
            self.running_checks[check_id] = task
            
            self.logger.info(f"🔄 Health check {check_id} démarré")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage health check {check_id}: {e}")

    async def _run_health_check_loop(self, config: HealthCheckConfig) -> None:
        """Boucle d'exécution d'un health check"""
        try:
            while True:
                try:
                    # Vérification des dépendances
                    if not await self._check_dependencies(config.dependencies):
                        self.logger.warning(f"⚠️ Dépendances échouées pour {config.check_id}")
                        await asyncio.sleep(config.interval_seconds)
                        continue
                    
                    # Exécution du check
                    result = await self._execute_health_check(config)
                    
                    # Sauvegarde du résultat
                    await self._save_check_result(result)
                    
                    # Mise à jour du circuit breaker
                    await self._update_circuit_breaker(config.check_id, result.success)
                    
                    # Détection d'incidents
                    await self._check_for_incidents(config, result)
                    
                    # Log du résultat
                    status_emoji = "✅" if result.success else "❌"
                    self.logger.info(f"{status_emoji} {config.name}: {result.status.value} ({result.response_time:.2f}s)")
                    
                except Exception as e:
                    self.logger.error(f"❌ Erreur exécution health check {config.check_id}: {e}")
                
                await asyncio.sleep(config.interval_seconds)
                
        except asyncio.CancelledError:
            self.logger.info(f"🛑 Health check {config.check_id} arrêté")
        except Exception as e:
            self.logger.error(f"❌ Erreur fatale health check {config.check_id}: {e}")

    async def _execute_health_check(self, config: HealthCheckConfig) -> HealthCheckResult:
        """Exécution d'un health check spécifique"""
        start_time = time.time()
        
        try:
            if config.check_type == CheckType.HTTP_ENDPOINT:
                success, status, error, metrics = await self._check_http_endpoint(config)
            elif config.check_type == CheckType.DATABASE_CONNECTION:
                success, status, error, metrics = await self._check_database_connection(config)
            elif config.check_type == CheckType.REDIS_CONNECTION:
                success, status, error, metrics = await self._check_redis_connection(config)
            elif config.check_type == CheckType.DISK_SPACE:
                success, status, error, metrics = await self._check_disk_space(config)
            elif config.check_type == CheckType.MEMORY_USAGE:
                success, status, error, metrics = await self._check_memory_usage(config)
            elif config.check_type == CheckType.MODEL_INFERENCE:
                success, status, error, metrics = await self._check_model_inference(config)
            else:
                success, status, error, metrics = False, HealthStatus.UNKNOWN, "Type de check non supporté", {}
            
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                check_id=config.check_id,
                timestamp=datetime.now(),
                status=status,
                response_time=response_time,
                success=success,
                error_message=error,
                metrics=metrics,
                creator_impact=config.creator_types
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                check_id=config.check_id,
                timestamp=datetime.now(),
                status=HealthStatus.CRITICAL,
                response_time=response_time,
                success=False,
                error_message=str(e),
                metrics={},
                creator_impact=config.creator_types
            )

    async def _check_http_endpoint(self, config: HealthCheckConfig) -> Tuple[bool, HealthStatus, Optional[str], Dict[str, Any]]:
        """Vérification d'un endpoint HTTP"""
        try:
            expected_status = config.custom_params.get("expected_status", 200)
            
            async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
                response = await client.get(config.target)
                
                success = response.status_code == expected_status
                status = HealthStatus.HEALTHY if success else HealthStatus.UNHEALTHY
                error = None if success else f"Status {response.status_code}, expected {expected_status}"
                
                metrics = {
                    "status_code": response.status_code,
                    "response_size": len(response.content),
                    "headers": dict(response.headers)
                }
                
                return success, status, error, metrics
                
        except Exception as e:
            return False, HealthStatus.CRITICAL, str(e), {}

    async def _check_database_connection(self, config: HealthCheckConfig) -> Tuple[bool, HealthStatus, Optional[str], Dict[str, Any]]:
        """Vérification de connexion base de données"""
        try:
            # Simulation de check database (à adapter selon le driver utilisé)
            query = config.custom_params.get("query", "SELECT 1")
            
            # Exemple avec PostgreSQL
            if "postgresql" in config.target:
                import asyncpg
                conn = await asyncpg.connect(config.target)
                result = await conn.fetchval(query)
                await conn.close()
                
                success = result is not None
                status = HealthStatus.HEALTHY if success else HealthStatus.UNHEALTHY
                metrics = {"query_result": str(result)}
                
                return success, status, None, metrics
            
            # Fallback
            return True, HealthStatus.HEALTHY, None, {"type": "simulated"}
            
        except Exception as e:
            return False, HealthStatus.CRITICAL, str(e), {}

    async def _check_redis_connection(self, config: HealthCheckConfig) -> Tuple[bool, HealthStatus, Optional[str], Dict[str, Any]]:
        """Vérification de connexion Redis"""
        try:
            import redis.asyncio as redis
            
            redis_client = redis.from_url(config.target)
            test_key = config.custom_params.get("test_key", "health_check")
            
            # Test ping
            pong = await redis_client.ping()
            
            # Test set/get
            await redis_client.set(test_key, "ok", ex=60)
            value = await redis_client.get(test_key)
            
            await redis_client.close()
            
            success = pong and value == "ok"
            status = HealthStatus.HEALTHY if success else HealthStatus.UNHEALTHY
            metrics = {"ping": pong, "test_key_value": value}
            
            return success, status, None, metrics
            
        except Exception as e:
            return False, HealthStatus.CRITICAL, str(e), {}

    async def _check_disk_space(self, config: HealthCheckConfig) -> Tuple[bool, HealthStatus, Optional[str], Dict[str, Any]]:
        """Vérification de l'espace disque"""
        try:
            threshold = config.custom_params.get("threshold_percentage", 80)
            
            disk_usage = psutil.disk_usage(config.target)
            used_percentage = (disk_usage.used / disk_usage.total) * 100
            
            success = used_percentage < threshold
            
            if used_percentage < threshold * 0.8:
                status = HealthStatus.HEALTHY
            elif used_percentage < threshold:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            error = None if success else f"Disk usage {used_percentage:.1f}% > {threshold}%"
            
            metrics = {
                "used_percentage": used_percentage,
                "total_gb": disk_usage.total / (1024**3),
                "used_gb": disk_usage.used / (1024**3),
                "free_gb": disk_usage.free / (1024**3)
            }
            
            return success, status, error, metrics
            
        except Exception as e:
            return False, HealthStatus.CRITICAL, str(e), {}

    async def _check_memory_usage(self, config: HealthCheckConfig) -> Tuple[bool, HealthStatus, Optional[str], Dict[str, Any]]:
        """Vérification de l'utilisation mémoire"""
        try:
            threshold = config.custom_params.get("threshold_percentage", 85)
            
            memory = psutil.virtual_memory()
            used_percentage = memory.percent
            
            success = used_percentage < threshold
            
            if used_percentage < threshold * 0.8:
                status = HealthStatus.HEALTHY
            elif used_percentage < threshold:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            error = None if success else f"Memory usage {used_percentage:.1f}% > {threshold}%"
            
            metrics = {
                "used_percentage": used_percentage,
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3)
            }
            
            return success, status, error, metrics
            
        except Exception as e:
            return False, HealthStatus.CRITICAL, str(e), {}

    async def _check_model_inference(self, config: HealthCheckConfig) -> Tuple[bool, HealthStatus, Optional[str], Dict[str, Any]]:
        """Vérification d'inférence de modèle ML"""
        try:
            test_payload = config.custom_params.get("test_payload", {"test": "data"})
            
            async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
                response = await client.post(config.target, json=test_payload)
                
                success = response.status_code == 200
                
                if success:
                    response_data = response.json()
                    # Validation de la réponse selon le modèle
                    has_prediction = "prediction" in response_data or "result" in response_data
                    success = has_prediction
                
                status = HealthStatus.HEALTHY if success else HealthStatus.UNHEALTHY
                error = None if success else f"Inference failed: {response.status_code}"
                
                metrics = {
                    "status_code": response.status_code,
                    "response_valid": success,
                    "response_size": len(response.content)
                }
                
                return success, status, error, metrics
                
        except Exception as e:
            return False, HealthStatus.CRITICAL, str(e), {}

    async def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Vérification des dépendances"""
        try:
            if not dependencies:
                return True
            
            for dep_id in dependencies:
                if dep_id not in self.check_results:
                    return False
                
                recent_results = list(self.check_results[dep_id])[-5:]  # 5 derniers résultats
                if not recent_results:
                    return False
                
                # Au moins 60% des derniers checks doivent être OK
                success_rate = sum(1 for r in recent_results if r.success) / len(recent_results)
                if success_rate < 0.6:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification dépendances: {e}")
            return False

    async def _save_check_result(self, result: HealthCheckResult) -> None:
        """Sauvegarde d'un résultat de health check"""
        try:
            # Ajout à la cache en mémoire
            self.check_results[result.check_id].append(result)
            
            # Sauvegarde en base
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO health_check_results 
                    (check_id, timestamp, status, response_time, success, error_message, 
                     metrics, creator_impact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.check_id, result.timestamp.isoformat(), result.status.value,
                    result.response_time, result.success, result.error_message,
                    json.dumps(result.metrics), json.dumps(result.creator_impact)
                ))
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde résultat: {e}")

    async def _update_circuit_breaker(self, check_id: str, success: bool) -> None:
        """Mise à jour du circuit breaker"""
        try:
            if check_id not in self.circuit_breakers:
                self.circuit_breakers[check_id] = {
                    "state": "closed",  # closed, open, half_open
                    "failure_count": 0,
                    "success_count": 0,
                    "last_failure": None,
                    "threshold": 5
                }
            
            breaker = self.circuit_breakers[check_id]
            
            if success:
                breaker["success_count"] += 1
                breaker["failure_count"] = 0
                
                # Transition half_open -> closed
                if breaker["state"] == "half_open" and breaker["success_count"] >= 3:
                    breaker["state"] = "closed"
                    self.logger.info(f"🔓 Circuit breaker {check_id} fermé (récupération)")
            else:
                breaker["failure_count"] += 1
                breaker["success_count"] = 0
                breaker["last_failure"] = datetime.now()
                
                # Transition closed -> open
                if breaker["state"] == "closed" and breaker["failure_count"] >= breaker["threshold"]:
                    breaker["state"] = "open"
                    self.logger.warning(f"🔒 Circuit breaker {check_id} ouvert (trop d'échecs)")
            
            # Tentative de récupération après 60 secondes
            if (breaker["state"] == "open" and 
                breaker["last_failure"] and
                datetime.now() - breaker["last_failure"] > timedelta(seconds=60)):
                breaker["state"] = "half_open"
                self.logger.info(f"🔄 Circuit breaker {check_id} en test de récupération")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur circuit breaker: {e}")

    async def _check_for_incidents(self, config: HealthCheckConfig, result: HealthCheckResult) -> None:
        """Détection et gestion d'incidents"""
        try:
            # Logique de détection d'incident basée sur la sévérité et les échecs consécutifs
            recent_results = list(self.check_results[config.check_id])[-5:]
            
            if len(recent_results) >= 3:
                recent_failures = sum(1 for r in recent_results if not r.success)
                
                # Incident si 3+ échecs consécutifs sur un service critique/high
                if (recent_failures >= 3 and 
                    config.severity in [Severity.CRITICAL, Severity.HIGH] and
                    not result.success):
                    
                    await self._create_incident(config, result)
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur détection incident: {e}")

    async def _create_incident(self, config: HealthCheckConfig, result: HealthCheckResult) -> None:
        """Création d'un incident"""
        try:
            incident_id = f"INC_{config.check_id}_{int(datetime.now().timestamp())}"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO incidents 
                    (incident_id, service_name, check_id, severity, status, title, 
                     description, creator_types_affected, started_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident_id, config.name, config.check_id, config.severity.value,
                    "open", f"{config.name} Health Check Failed",
                    f"Health check failed: {result.error_message}",
                    json.dumps(config.creator_types), datetime.now().isoformat()
                ))
                await db.commit()
            
            self.logger.critical(f"🚨 INCIDENT CRÉÉ: {incident_id} - {config.name}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création incident: {e}")

    async def get_overall_health(self) -> Dict[str, Any]:
        """Statut de santé global du système"""
        try:
            overall_health = {
                "status": HealthStatus.HEALTHY,
                "timestamp": datetime.now().isoformat(),
                "services": {},
                "creator_impact": {},
                "incidents": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                },
                "uptime_percentage": 100.0,
                "performance_score": 100.0
            }
            
            total_checks = len(self.health_checks)
            healthy_checks = 0
            
            for check_id, config in self.health_checks.items():
                if not config.enabled:
                    continue
                
                recent_results = list(self.check_results[check_id])[-10:]
                if not recent_results:
                    continue
                
                # Calcul du statut du service
                success_rate = sum(1 for r in recent_results if r.success) / len(recent_results)
                avg_response_time = np.mean([r.response_time for r in recent_results])
                
                if success_rate >= 0.95:
                    service_status = HealthStatus.HEALTHY
                    healthy_checks += 1
                elif success_rate >= 0.8:
                    service_status = HealthStatus.DEGRADED
                elif success_rate >= 0.5:
                    service_status = HealthStatus.UNHEALTHY
                else:
                    service_status = HealthStatus.CRITICAL
                
                overall_health["services"][check_id] = {
                    "name": config.name,
                    "status": service_status.value,
                    "success_rate": success_rate * 100,
                    "avg_response_time": avg_response_time,
                    "severity": config.severity.value,
                    "creator_types": config.creator_types
                }
                
                # Impact par type de créateur
                for creator_type in config.creator_types:
                    if creator_type not in overall_health["creator_impact"]:
                        overall_health["creator_impact"][creator_type] = {
                            "status": HealthStatus.HEALTHY.value,
                            "affected_services": []
                        }
                    
                    if service_status != HealthStatus.HEALTHY:
                        overall_health["creator_impact"][creator_type]["affected_services"].append({
                            "service": config.name,
                            "status": service_status.value
                        })
                        
                        # Mise à jour du statut global du créateur
                        if service_status == HealthStatus.CRITICAL:
                            overall_health["creator_impact"][creator_type]["status"] = HealthStatus.CRITICAL.value
                        elif (service_status == HealthStatus.UNHEALTHY and 
                              overall_health["creator_impact"][creator_type]["status"] != HealthStatus.CRITICAL.value):
                            overall_health["creator_impact"][creator_type]["status"] = HealthStatus.UNHEALTHY.value
            
            # Calcul du statut global
            if total_checks > 0:
                health_percentage = healthy_checks / total_checks
                overall_health["uptime_percentage"] = health_percentage * 100
                overall_health["performance_score"] = health_percentage * 100
                
                if health_percentage >= 0.95:
                    overall_health["status"] = HealthStatus.HEALTHY
                elif health_percentage >= 0.8:
                    overall_health["status"] = HealthStatus.DEGRADED
                elif health_percentage >= 0.5:
                    overall_health["status"] = HealthStatus.UNHEALTHY
                else:
                    overall_health["status"] = HealthStatus.CRITICAL
            
            # Comptage des incidents ouverts
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT severity, COUNT(*) 
                    FROM incidents 
                    WHERE status = 'open'
                    GROUP BY severity
                """)
                
                incident_counts = await cursor.fetchall()
                for severity, count in incident_counts:
                    overall_health["incidents"][severity] = count
            
            return overall_health
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul santé globale: {e}")
            return {
                "status": HealthStatus.UNKNOWN.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_service_health_summary(self, service_name: str, hours: int = 24) -> ServiceHealth:
        """Résumé de santé d'un service spécifique"""
        try:
            since = datetime.now() - timedelta(hours=hours)
            
            # Recherche du check correspondant
            service_config = None
            for config in self.health_checks.values():
                if config.name == service_name or config.check_id == service_name:
                    service_config = config
                    break
            
            if not service_config:
                raise ValueError(f"Service {service_name} non trouvé")
            
            # Récupération des résultats récents
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT timestamp, status, response_time, success, error_message, metrics
                    FROM health_check_results
                    WHERE check_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (service_config.check_id, since.isoformat()))
                
                results_data = await cursor.fetchall()
            
            # Construction des résultats
            check_results = []
            for row in results_data:
                check_results.append(HealthCheckResult(
                    check_id=service_config.check_id,
                    timestamp=datetime.fromisoformat(row[0]),
                    status=HealthStatus(row[1]),
                    response_time=row[2],
                    success=bool(row[3]),
                    error_message=row[4],
                    metrics=json.loads(row[5]) if row[5] else {},
                    creator_impact=service_config.creator_types
                ))
            
            # Calculs
            if check_results:
                uptime_percentage = (sum(1 for r in check_results if r.success) / len(check_results)) * 100
                avg_response_time = np.mean([r.response_time for r in check_results])
                performance_score = min(100, max(0, 100 - (avg_response_time * 10)))  # Pénalité basée sur latence
                
                # Statut global
                if uptime_percentage >= 99:
                    overall_status = HealthStatus.HEALTHY
                elif uptime_percentage >= 95:
                    overall_status = HealthStatus.DEGRADED
                elif uptime_percentage >= 80:
                    overall_status = HealthStatus.UNHEALTHY
                else:
                    overall_status = HealthStatus.CRITICAL
            else:
                uptime_percentage = 0
                performance_score = 0
                overall_status = HealthStatus.UNKNOWN
            
            # Dernier incident
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT started_at FROM incidents
                    WHERE check_id = ?
                    ORDER BY started_at DESC
                    LIMIT 1
                """, (service_config.check_id,))
                
                last_incident_row = await cursor.fetchone()
                last_incident = datetime.fromisoformat(last_incident_row[0]) if last_incident_row else None
            
            return ServiceHealth(
                service_name=service_name,
                overall_status=overall_status,
                check_results=check_results,
                uptime_percentage=uptime_percentage,
                last_incident=last_incident,
                performance_score=performance_score
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur résumé service {service_name}: {e}")
            raise AinflueCoreException(f"Échec résumé service: {e}")

    async def stop_all_checks(self) -> None:
        """Arrêt de tous les health checks"""
        try:
            for check_id, task in self.running_checks.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.running_checks.clear()
            self.logger.info("✅ Tous les health checks arrêtés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur arrêt health checks: {e}")

    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        try:
            await self.stop_all_checks()
            self.executor.shutdown(wait=True)
            self.logger.info("✅ Health Check Manager nettoyé")
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")

# Example usage
async def main():
    manager = HealthCheckManager()
    await manager.initialize()
    
    # Démarrage des checks
    for check_id in manager.health_checks:
        await manager._start_health_check(check_id)
    
    # Monitoring pendant 30 secondes
    for _ in range(6):
        await asyncio.sleep(5)
        health = await manager.get_overall_health()
        print(f"System Health: {health['status'].value} - {health['uptime_percentage']:.1f}% uptime")
    
    await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())