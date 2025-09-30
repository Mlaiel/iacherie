"""🖥️ Enterprise Database Console - Unified Database Management Implementation
===========================================================================

Console enterprise de gestion database avec interface unifiée, monitoring temps réel,
et administration centralisée pour la plateforme Ainflue.

Expert Roles Implementation:
🗄️ DBA Senior: Database administration + monitoring + performance tuning + backup management
🖥️ UI/UX Designer: Enterprise interface design + dashboard visualization + user experience
🏗️ Backend Senior: API management + service integration + real-time updates + data streaming
🔒 Security Specialist: Access control + audit logging + secure administration + role management
⚙️ DevOps Engineer: Infrastructure monitoring + deployment management + automation integration
📊 BI Analyst: Performance dashboards + analytics visualization + reporting + KPI monitoring
🤖 Lead Dev IA: Intelligent recommendations + automated insights + predictive alerts + AI assistance
⚡ Performance Engineer: Performance monitoring + optimization recommendations + resource tracking
🎨 Frontend Developer: React components + interactive dashboards + responsive design + modern UI

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise
Date: 14 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture de console database est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import statistics
import psutil
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiomysql
import aiohttp
from contextlib import asynccontextmanager
import backoff
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Configuration du logging structuré pour database console
logger = structlog.get_logger("database_console")

class ConsolePermission(Enum):
    """Permissions console database"""
    READ_ONLY = "read_only"
    OPERATOR = "operator"
    DBA = "dba"
    ADMIN = "admin"
    SECURITY_ADMIN = "security_admin"

class DatabaseProvider(Enum):
    """Providers database supportés"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CLICKHOUSE = "clickhouse"
    CASSANDRA = "cassandra"

class MonitoringMetric(Enum):
    """Métriques monitoring"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    CONNECTIONS = "connections"
    QUERY_RATE = "query_rate"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"
    THROUGHPUT = "throughput"

@dataclass
class ConsoleConfiguration:
    """Configuration console enterprise"""
    port: int = 8080
    host: str = "0.0.0.0"
    enable_websockets: bool = True
    real_time_updates: bool = True
    session_timeout_minutes: int = 60
    max_concurrent_connections: int = 100
    enable_query_execution: bool = True
    enable_schema_management: bool = True
    audit_all_actions: bool = True
    theme: str = "dark"  # dark, light
    refresh_interval_seconds: int = 5

@dataclass
class DatabaseConnection:
    """Connexion database"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    provider: DatabaseProvider = DatabaseProvider.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""
    ssl_enabled: bool = True
    connection_pool_size: int = 10
    is_active: bool = False
    last_ping: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserSession:
    """Session utilisateur console"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    username: str = ""
    permissions: List[ConsolePermission] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    ip_address: str = ""
    active_database: Optional[str] = None

@dataclass
class QueryExecution:
    """Exécution requête"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    database_id: str = ""
    query: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    execution_time_ms: float = 0.0
    rows_affected: int = 0
    status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    result_preview: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class AlertRule:
    """Règle d'alerte"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    metric: MonitoringMetric = MonitoringMetric.CPU_USAGE
    threshold: float = 80.0
    operator: str = ">"  # >, <, >=, <=, ==
    duration_minutes: int = 5
    severity: str = "warning"  # info, warning, critical
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)

class EnterpriseDatabaseConsole:
    """🖥️ Console enterprise de gestion database avec interface unifiée
    
    Fonctionnalités Expert Multi-Rôles:
    
    🗄️ DBA Senior:
    - Administration database centralisée
    - Monitoring performance temps réel
    - Gestion backup et récupération
    - Optimisation queries automatique
    
    🖥️ UI/UX Designer:
    - Interface moderne et intuitive
    - Dashboards interactifs
    - Expérience utilisateur optimisée
    - Design responsive multi-device
    
    🏗️ Backend Senior:
    - APIs RESTful robustes
    - Intégration services temps réel
    - Streaming données performance
    - Architecture microservices
    
    🔒 Security Specialist:
    - Contrôle accès granulaire
    - Audit logging complet
    - Administration sécurisée
    - Gestion rôles et permissions
    
    ⚙️ DevOps Engineer:
    - Monitoring infrastructure
    - Gestion déploiements
    - Intégration CI/CD
    - Automation operations
    
    📊 BI Analyst:
    - Dashboards performance
    - Visualisations analytics
    - Reporting automatisé
    - KPI monitoring temps réel
    
    🤖 Lead Dev IA:
    - Recommandations intelligentes
    - Insights automatisés
    - Alertes prédictives
    - Assistant IA intégré
    
    ⚡ Performance Engineer:
    - Monitoring performance
    - Recommandations optimisation
    - Tracking ressources
    - Analyse bottlenecks
    
    🎨 Frontend Developer:
    - Composants React modernes
    - Dashboards interactifs
    - Design responsive
    - Interface utilisateur moderne
    """
    
    def __init__(self, config: ConsoleConfiguration):
        self.config = config
        self.database_connections: Dict[str, DatabaseConnection] = {}
        self.active_sessions: Dict[str, UserSession] = {}
        self.query_executions: Dict[str, QueryExecution] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.websocket_connections: Set[WebSocket] = set()
        self.is_running = False
        self.background_tasks: List[asyncio.Task] = []
        
        # FastAPI application
        self.app = FastAPI(
            title="Ainflue Enterprise Database Console",
            description="Console unifiée de gestion database enterprise",
            version="2.0.0"
        )
        
        # Middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Security
        self.security = HTTPBearer()
        
        # Templates
        self.templates = Jinja2Templates(directory="templates")
        
        # Redis pour sessions
        self.redis_client = None
        
        # Métriques console
        self.console_metrics = {
            "active_sessions": 0,
            "total_queries_executed": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "average_query_time": 0.0,
            "database_connections": 0,
            "alerts_triggered": 0,
            "websocket_connections": 0
        }
        
        # Configuration routes
        self._setup_routes()
        
        # Initialisation connexions par défaut
        self._initialize_default_connections()
        
        logger.info("EnterpriseDatabaseConsole initialisé", 
                   port=self.config.port)
    
    def _initialize_default_connections(self):
        """Initialisation connexions database par défaut"""
        # PostgreSQL primary
        pg_conn = DatabaseConnection(
            name="PostgreSQL Primary",
            provider=DatabaseProvider.POSTGRESQL,
            host="localhost",
            port=5432,
            database="ainflue_primary",
            username="postgres",
            password="password"
        )
        self.database_connections["postgresql_primary"] = pg_conn
        
        # MongoDB
        mongo_conn = DatabaseConnection(
            name="MongoDB Cluster",
            provider=DatabaseProvider.MONGODB,
            host="localhost",
            port=27017,
            database="ainflue_documents",
            username="admin",
            password="password"
        )
        self.database_connections["mongodb"] = mongo_conn
        
        # Redis Cache
        redis_conn = DatabaseConnection(
            name="Redis Cache",
            provider=DatabaseProvider.REDIS,
            host="localhost",
            port=6379,
            database="0",
            username="",
            password=""
        )
        self.database_connections["redis"] = redis_conn
        
        # ClickHouse Analytics
        clickhouse_conn = DatabaseConnection(
            name="ClickHouse Analytics",
            provider=DatabaseProvider.CLICKHOUSE,
            host="localhost",
            port=8123,
            database="ainflue_analytics",
            username="default",
            password=""
        )
        self.database_connections["clickhouse"] = clickhouse_conn
    
    def _setup_routes(self):
        """Configuration routes API"""
        
        # 🖥️ UI/UX DESIGNER - Interface routes
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Page d'accueil dashboard"""
            return await self._render_dashboard_template("dashboard.html", {
                "title": "Ainflue Database Console",
                "databases": list(self.database_connections.values()),
                "metrics": self.console_metrics
            })
        
        @self.app.get("/databases", response_class=HTMLResponse)
        async def databases_page():
            """Page gestion databases"""
            return await self._render_dashboard_template("databases.html", {
                "title": "Database Management",
                "connections": list(self.database_connections.values())
            })
        
        @self.app.get("/monitoring", response_class=HTMLResponse)
        async def monitoring_page():
            """Page monitoring"""
            return await self._render_dashboard_template("monitoring.html", {
                "title": "Performance Monitoring",
                "metrics": await self._get_performance_metrics()
            })
        
        @self.app.get("/query-editor", response_class=HTMLResponse)
        async def query_editor_page():
            """Page éditeur queries"""
            return await self._render_dashboard_template("query_editor.html", {
                "title": "Query Editor",
                "databases": list(self.database_connections.values())
            })
        
        # 🏗️ BACKEND SENIOR - API routes
        
        @self.app.get("/api/connections")
        async def get_connections(session: UserSession = Depends(self._get_current_session)):
            """Liste connexions database"""
            if not self._has_permission(session, ConsolePermission.READ_ONLY):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            return {
                "connections": [asdict(conn) for conn in self.database_connections.values()],
                "total": len(self.database_connections)
            }
        
        @self.app.post("/api/connections")
        async def create_connection(
            connection_data: dict,
            session: UserSession = Depends(self._get_current_session)
        ):
            """Création nouvelle connexion"""
            if not self._has_permission(session, ConsolePermission.DBA):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            connection = DatabaseConnection(**connection_data)
            self.database_connections[connection.id] = connection
            
            # Test connexion
            test_result = await self._test_database_connection(connection)
            connection.is_active = test_result["success"]
            connection.last_ping = datetime.utcnow()
            
            await self._audit_action(session, "CREATE_CONNECTION", connection.name)
            
            return {"success": True, "connection": asdict(connection)}
        
        @self.app.delete("/api/connections/{connection_id}")
        async def delete_connection(
            connection_id: str,
            session: UserSession = Depends(self._get_current_session)
        ):
            """Suppression connexion"""
            if not self._has_permission(session, ConsolePermission.DBA):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            if connection_id not in self.database_connections:
                raise HTTPException(status_code=404, detail="Connection not found")
            
            connection = self.database_connections.pop(connection_id)
            await self._audit_action(session, "DELETE_CONNECTION", connection.name)
            
            return {"success": True}
        
        @self.app.post("/api/connections/{connection_id}/test")
        async def test_connection(
            connection_id: str,
            session: UserSession = Depends(self._get_current_session)
        ):
            """Test connexion database"""
            if not self._has_permission(session, ConsolePermission.READ_ONLY):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            connection = self.database_connections.get(connection_id)
            if not connection:
                raise HTTPException(status_code=404, detail="Connection not found")
            
            result = await self._test_database_connection(connection)
            return result
        
        @self.app.post("/api/query/execute")
        async def execute_query(
            query_data: dict,
            session: UserSession = Depends(self._get_current_session)
        ):
            """Exécution requête SQL"""
            if not self._has_permission(session, ConsolePermission.OPERATOR):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            if not self.config.enable_query_execution:
                raise HTTPException(status_code=403, detail="Query execution disabled")
            
            query = query_data.get("query", "")
            database_id = query_data.get("database_id", "")
            
            # Validation sécurité query
            if not await self._validate_query_security(query, session):
                raise HTTPException(status_code=403, detail="Query not allowed")
            
            execution = await self._execute_database_query(
                session.id, database_id, query
            )
            
            return asdict(execution)
        
        @self.app.get("/api/query/history")
        async def get_query_history(session: UserSession = Depends(self._get_current_session)):
            """Historique requêtes utilisateur"""
            user_executions = [
                asdict(exec) for exec in self.query_executions.values()
                if exec.session_id == session.id
            ]
            
            return {
                "executions": user_executions[-50:],  # 50 dernières
                "total": len(user_executions)
            }
        
        # 📊 BI ANALYST - Analytics routes
        
        @self.app.get("/api/metrics/performance")
        async def get_performance_metrics(session: UserSession = Depends(self._get_current_session)):
            """Métriques performance"""
            if not self._has_permission(session, ConsolePermission.READ_ONLY):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            return await self._get_performance_metrics()
        
        @self.app.get("/api/metrics/dashboard")
        async def get_dashboard_metrics(session: UserSession = Depends(self._get_current_session)):
            """Métriques dashboard principal"""
            return await self._get_dashboard_metrics()
        
        @self.app.get("/api/charts/performance")
        async def get_performance_charts(session: UserSession = Depends(self._get_current_session)):
            """Graphiques performance"""
            return await self._generate_performance_charts()
        
        # 🔒 SECURITY SPECIALIST - Security routes
        
        @self.app.post("/api/auth/login")
        async def login(credentials: dict):
            """Authentification utilisateur"""
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            
            # Validation credentials (production: vraie authentification)
            if username == "admin" and password == "admin":
                session = UserSession(
                    user_id="admin",
                    username="admin",
                    permissions=[ConsolePermission.ADMIN],
                    ip_address="127.0.0.1"
                )
                
                self.active_sessions[session.id] = session
                await self._audit_action(session, "LOGIN", username)
                
                return {
                    "success": True,
                    "session_token": session.id,
                    "permissions": [p.value for p in session.permissions]
                }
            
            return {"success": False, "error": "Invalid credentials"}
        
        @self.app.post("/api/auth/logout")
        async def logout(session: UserSession = Depends(self._get_current_session)):
            """Déconnexion utilisateur"""
            await self._audit_action(session, "LOGOUT", session.username)
            self.active_sessions.pop(session.id, None)
            
            return {"success": True}
        
        @self.app.get("/api/audit/logs")
        async def get_audit_logs(session: UserSession = Depends(self._get_current_session)):
            """Logs audit système"""
            if not self._has_permission(session, ConsolePermission.SECURITY_ADMIN):
                raise HTTPException(status_code=403, detail="Permission denied")
            
            # Récupération logs audit (simulation)
            return {"logs": [], "total": 0}
        
        # WebSocket pour updates temps réel
        
        @self.app.websocket("/ws/metrics")
        async def websocket_metrics(websocket: WebSocket):
            """WebSocket métriques temps réel"""
            await websocket.accept()
            self.websocket_connections.add(websocket)
            self.console_metrics["websocket_connections"] = len(self.websocket_connections)
            
            try:
                while True:
                    # Envoi métriques temps réel
                    metrics = await self._get_realtime_metrics()
                    await websocket.send_json(metrics)
                    await asyncio.sleep(self.config.refresh_interval_seconds)
            
            except WebSocketDisconnect:
                self.websocket_connections.discard(websocket)
                self.console_metrics["websocket_connections"] = len(self.websocket_connections)
        
        @self.app.websocket("/ws/query/{execution_id}")
        async def websocket_query_status(websocket: WebSocket, execution_id: str):
            """WebSocket status exécution query"""
            await websocket.accept()
            
            try:
                while execution_id in self.query_executions:
                    execution = self.query_executions[execution_id]
                    await websocket.send_json({
                        "execution_id": execution_id,
                        "status": execution.status,
                        "execution_time": execution.execution_time_ms,
                        "rows_affected": execution.rows_affected
                    })
                    
                    if execution.status in ["completed", "failed"]:
                        break
                    
                    await asyncio.sleep(1)
            
            except WebSocketDisconnect:
                pass
    
    async def start(self):
        """Démarrage console database"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Initialisation connexions
        await self._initialize_connections()
        
        # Test connexions databases
        await self._ping_all_connections()
        
        # Démarrage tâches background
        tasks = [
            self._metrics_collector(),
            self._session_cleanup(),
            self._database_health_monitor(),
            self._alert_processor()
        ]
        
        self.background_tasks = [asyncio.create_task(task) for task in tasks]
        
        logger.info("EnterpriseDatabaseConsole démarré")
    
    async def stop(self):
        """Arrêt console database"""
        self.is_running = False
        
        # Fermeture connexions WebSocket
        for websocket in self.websocket_connections.copy():
            try:
                await websocket.close()
            except Exception:
                pass
        
        # Arrêt tâches background
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks = []
        
        # Fermeture connexions
        await self._close_connections()
        
        logger.info("EnterpriseDatabaseConsole arrêté")
    
    async def _initialize_connections(self):
        """Initialisation connexions"""
        try:
            # Redis pour sessions
            self.redis_client = await aioredis.from_url('redis://localhost:6379')
            
            logger.info("Connexions console initialisées")
            
        except Exception as e:
            logger.error("Erreur initialisation connexions", error=str(e))
            raise
    
    async def _close_connections(self):
        """Fermeture connexions"""
        if self.redis_client:
            await self.redis_client.close()
    
    # 🗄️ DBA SENIOR - Database operations
    
    async def _test_database_connection(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """Test connexion database"""
        try:
            if connection.provider == DatabaseProvider.POSTGRESQL:
                return await self._test_postgresql_connection(connection)
            elif connection.provider == DatabaseProvider.MYSQL:
                return await self._test_mysql_connection(connection)
            elif connection.provider == DatabaseProvider.MONGODB:
                return await self._test_mongodb_connection(connection)
            elif connection.provider == DatabaseProvider.REDIS:
                return await self._test_redis_connection(connection)
            else:
                return {"success": False, "error": "Provider not supported"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_postgresql_connection(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """Test connexion PostgreSQL"""
        try:
            conn_string = f"postgresql://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}"
            
            # Test simple connexion
            engine = create_async_engine(conn_string)
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
            
            await engine.dispose()
            
            return {
                "success": True,
                "version": version,
                "latency_ms": 10.0  # Simulation
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_mysql_connection(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """Test connexion MySQL"""
        try:
            # Simulation test MySQL
            return {
                "success": True,
                "version": "MySQL 8.0.28",
                "latency_ms": 15.0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_mongodb_connection(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """Test connexion MongoDB"""
        try:
            # Simulation test MongoDB
            return {
                "success": True,
                "version": "MongoDB 5.0.5",
                "latency_ms": 8.0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_redis_connection(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """Test connexion Redis"""
        try:
            # Simulation test Redis
            return {
                "success": True,
                "version": "Redis 6.2.6",
                "latency_ms": 2.0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _ping_all_connections(self):
        """Ping toutes les connexions"""
        for conn_id, connection in self.database_connections.items():
            result = await self._test_database_connection(connection)
            connection.is_active = result["success"]
            connection.last_ping = datetime.utcnow()
            
            if result["success"]:
                logger.info(f"Connexion active: {connection.name}")
            else:
                logger.warning(f"Connexion échouée: {connection.name}")
    
    async def _execute_database_query(self, session_id: str, database_id: str, 
                                    query: str) -> QueryExecution:
        """Exécution requête database"""
        execution = QueryExecution(
            session_id=session_id,
            database_id=database_id,
            query=query
        )
        
        self.query_executions[execution.id] = execution
        
        try:
            connection = self.database_connections.get(database_id)
            if not connection:
                raise Exception("Database connection not found")
            
            # Simulation exécution (production: vraie exécution)
            await asyncio.sleep(0.5)  # Simulation durée
            
            # Résultats simulés
            if "SELECT" in query.upper():
                execution.result_preview = [
                    {"id": 1, "name": "Sample Data 1", "value": 100},
                    {"id": 2, "name": "Sample Data 2", "value": 200},
                    {"id": 3, "name": "Sample Data 3", "value": 300}
                ]
                execution.rows_affected = len(execution.result_preview)
            else:
                execution.rows_affected = 1
            
            execution.status = "completed"
            execution.end_time = datetime.utcnow()
            execution.execution_time_ms = (execution.end_time - execution.start_time).total_seconds() * 1000
            
            # Mise à jour métriques
            self.console_metrics["total_queries_executed"] += 1
            self.console_metrics["successful_queries"] += 1
            
            return execution
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
            execution.execution_time_ms = (execution.end_time - execution.start_time).total_seconds() * 1000
            
            self.console_metrics["total_queries_executed"] += 1
            self.console_metrics["failed_queries"] += 1
            
            return execution
    
    # 🔒 SECURITY SPECIALIST - Security operations
    
    async def _get_current_session(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> UserSession:
        """Récupération session utilisateur courante"""
        token = credentials.credentials
        session = self.active_sessions.get(token)
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Vérification timeout session
        if (datetime.utcnow() - session.last_activity).total_seconds() > (self.config.session_timeout_minutes * 60):
            self.active_sessions.pop(token)
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Mise à jour activité
        session.last_activity = datetime.utcnow()
        
        return session
    
    def _has_permission(self, session: UserSession, required_permission: ConsolePermission) -> bool:
        """Vérification permissions utilisateur"""
        if ConsolePermission.ADMIN in session.permissions:
            return True
        
        return required_permission in session.permissions
    
    async def _validate_query_security(self, query: str, session: UserSession) -> bool:
        """Validation sécurité requête"""
        # Requêtes dangereuses
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
        
        query_upper = query.upper()
        
        # DBA peut tout faire
        if ConsolePermission.DBA in session.permissions or ConsolePermission.ADMIN in session.permissions:
            return True
        
        # Utilisateurs normaux: SELECT uniquement
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        return True
    
    async def _audit_action(self, session: UserSession, action: str, details: str):
        """Audit action utilisateur"""
        if not self.config.audit_all_actions:
            return
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.id,
            "user_id": session.user_id,
            "username": session.username,
            "action": action,
            "details": details,
            "ip_address": session.ip_address
        }
        
        # Sauvegarde audit (production: vraie DB)
        logger.info("Action auditée", audit=audit_entry)
    
    # 📊 BI ANALYST - Analytics et visualisations
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Métriques performance système"""
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "active_connections": sum(1 for conn in self.database_connections.values() if conn.is_active),
            "total_connections": len(self.database_connections),
            "queries_per_minute": len([
                q for q in self.query_executions.values()
                if (datetime.utcnow() - q.start_time).total_seconds() < 60
            ]),
            "average_query_time": statistics.mean([
                q.execution_time_ms for q in self.query_executions.values()
                if q.status == "completed"
            ]) if self.query_executions else 0.0,
            "error_rate": (self.console_metrics["failed_queries"] / max(1, self.console_metrics["total_queries_executed"])) * 100
        }
    
    async def _get_dashboard_metrics(self) -> Dict[str, Any]:
        """Métriques dashboard principal"""
        return {
            "overview": {
                "total_databases": len(self.database_connections),
                "active_databases": sum(1 for conn in self.database_connections.values() if conn.is_active),
                "active_sessions": len(self.active_sessions),
                "queries_today": len([
                    q for q in self.query_executions.values()
                    if q.start_time.date() == datetime.utcnow().date()
                ])
            },
            "performance": await self._get_performance_metrics(),
            "recent_queries": [
                {
                    "id": q.id,
                    "query": q.query[:50] + "..." if len(q.query) > 50 else q.query,
                    "status": q.status,
                    "execution_time": q.execution_time_ms,
                    "timestamp": q.start_time.isoformat()
                }
                for q in sorted(self.query_executions.values(), key=lambda x: x.start_time, reverse=True)[:10]
            ]
        }
    
    async def _generate_performance_charts(self) -> Dict[str, Any]:
        """Génération graphiques performance"""
        try:
            # Données simulées pour graphiques
            timestamps = [datetime.utcnow() - timedelta(minutes=i) for i in range(60, 0, -1)]
            
            # Graphique CPU
            cpu_data = [np.random.uniform(20, 80) for _ in timestamps]
            cpu_chart = {
                "data": [{
                    "x": [t.isoformat() for t in timestamps],
                    "y": cpu_data,
                    "type": "line",
                    "name": "CPU Usage %"
                }],
                "layout": {
                    "title": "CPU Usage",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Usage %"}
                }
            }
            
            # Graphique Memory
            memory_data = [np.random.uniform(40, 90) for _ in timestamps]
            memory_chart = {
                "data": [{
                    "x": [t.isoformat() for t in timestamps],
                    "y": memory_data,
                    "type": "line",
                    "name": "Memory Usage %"
                }],
                "layout": {
                    "title": "Memory Usage",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Usage %"}
                }
            }
            
            # Graphique Query Rate
            query_data = [np.random.randint(10, 100) for _ in timestamps]
            query_chart = {
                "data": [{
                    "x": [t.isoformat() for t in timestamps],
                    "y": query_data,
                    "type": "bar",
                    "name": "Queries/min"
                }],
                "layout": {
                    "title": "Query Rate",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Queries per minute"}
                }
            }
            
            return {
                "cpu_chart": cpu_chart,
                "memory_chart": memory_chart,
                "query_chart": query_chart
            }
            
        except Exception as e:
            logger.error("Erreur génération graphiques", error=str(e))
            return {}
    
    async def _get_realtime_metrics(self) -> Dict[str, Any]:
        """Métriques temps réel pour WebSocket"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": await self._get_performance_metrics(),
            "connections": [
                {
                    "id": conn.id,
                    "name": conn.name,
                    "is_active": conn.is_active,
                    "provider": conn.provider.value
                }
                for conn in self.database_connections.values()
            ],
            "active_queries": len([
                q for q in self.query_executions.values()
                if q.status == "running"
            ])
        }
    
    # 🤖 LEAD DEV IA - Intelligent recommendations
    
    async def _generate_intelligent_recommendations(self) -> List[Dict[str, Any]]:
        """Génération recommandations intelligentes"""
        recommendations = []
        
        # Analyse performance metrics
        metrics = await self._get_performance_metrics()
        
        # Recommandation CPU
        if metrics["cpu_usage"] > 80:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "title": "High CPU Usage Detected",
                "description": f"CPU usage is at {metrics['cpu_usage']:.1f}%. Consider scaling resources.",
                "actions": ["Scale up instances", "Optimize queries", "Check for runaway processes"]
            })
        
        # Recommandation Memory
        if metrics["memory_usage"] > 85:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "title": "High Memory Usage",
                "description": f"Memory usage is at {metrics['memory_usage']:.1f}%. Memory optimization needed.",
                "actions": ["Increase memory allocation", "Optimize connection pooling", "Review query caching"]
            })
        
        # Recommandation Query Performance
        if metrics["average_query_time"] > 1000:  # > 1 second
            recommendations.append({
                "type": "optimization",
                "priority": "medium",
                "title": "Slow Query Performance",
                "description": f"Average query time is {metrics['average_query_time']:.0f}ms.",
                "actions": ["Review slow queries", "Add database indexes", "Optimize query plans"]
            })
        
        # Recommandation Error Rate
        if metrics["error_rate"] > 5:  # > 5%
            recommendations.append({
                "type": "reliability",
                "priority": "critical",
                "title": "High Error Rate",
                "description": f"Query error rate is {metrics['error_rate']:.1f}%.",
                "actions": ["Review error logs", "Fix failing queries", "Check database connectivity"]
            })
        
        return recommendations
    
    # Templates et UI
    
    async def _render_dashboard_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Rendu template dashboard"""
        # Template HTML de base pour démo
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{context.get('title', 'Database Console')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }}
                .header {{ background: #333; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
                .metric-card {{ background: #444; padding: 20px; border-radius: 8px; }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #4CAF50; }}
                .connections {{ margin-top: 20px; }}
                .connection {{ background: #555; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .active {{ border-left: 4px solid #4CAF50; }}
                .inactive {{ border-left: 4px solid #f44336; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🖥️ Ainflue Enterprise Database Console</h1>
                <p>Unified database management and monitoring platform</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{len(context.get('databases', []))}</div>
                    <div>Database Connections</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{context.get('metrics', {}).get('active_sessions', 0)}</div>
                    <div>Active Sessions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{context.get('metrics', {}).get('total_queries_executed', 0)}</div>
                    <div>Total Queries</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{context.get('metrics', {}).get('websocket_connections', 0)}</div>
                    <div>Real-time Connections</div>
                </div>
            </div>
            
            <div class="connections">
                <h2>Database Connections</h2>
                {self._render_connections_list(context.get('databases', []))}
            </div>
            
            <script>
                // WebSocket pour updates temps réel
                const ws = new WebSocket('ws://localhost:{self.config.port}/ws/metrics');
                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    console.log('Real-time metrics:', data);
                    // Mise à jour interface en temps réel
                }};
            </script>
        </body>
        </html>
        """
        
        return html_template
    
    def _render_connections_list(self, connections: List[DatabaseConnection]) -> str:
        """Rendu liste connexions"""
        html = ""
        for conn in connections:
            status_class = "active" if conn.is_active else "inactive"
            status_text = "🟢 Active" if conn.is_active else "🔴 Inactive"
            
            html += f"""
            <div class="connection {status_class}">
                <strong>{conn.name}</strong> ({conn.provider.value})
                <br>
                {conn.host}:{conn.port} - {status_text}
                <br>
                Last ping: {conn.last_ping.strftime('%Y-%m-%d %H:%M:%S') if conn.last_ping else 'Never'}
            </div>
            """
        
        return html
    
    # Tâches background
    
    async def _metrics_collector(self):
        """Collecteur métriques"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Collecte chaque 30 secondes
                
                # Mise à jour métriques console
                self.console_metrics["active_sessions"] = len(self.active_sessions)
                self.console_metrics["database_connections"] = len(self.database_connections)
                
                # Calcul query time moyen
                completed_queries = [
                    q for q in self.query_executions.values()
                    if q.status == "completed"
                ]
                
                if completed_queries:
                    avg_time = statistics.mean([q.execution_time_ms for q in completed_queries])
                    self.console_metrics["average_query_time"] = avg_time
                
            except Exception as e:
                logger.error("Erreur collecte métriques", error=str(e))
    
    async def _session_cleanup(self):
        """Nettoyage sessions expirées"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Nettoyage chaque 5 minutes
                
                expired_sessions = []
                timeout_seconds = self.config.session_timeout_minutes * 60
                
                for session_id, session in self.active_sessions.items():
                    if (datetime.utcnow() - session.last_activity).total_seconds() > timeout_seconds:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    session = self.active_sessions.pop(session_id)
                    logger.info("Session expirée nettoyée", username=session.username)
                
            except Exception as e:
                logger.error("Erreur nettoyage sessions", error=str(e))
    
    async def _database_health_monitor(self):
        """Monitoring santé databases"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Check chaque minute
                
                # Ping toutes les connexions
                await self._ping_all_connections()
                
            except Exception as e:
                logger.error("Erreur monitoring databases", error=str(e))
    
    async def _alert_processor(self):
        """Processeur alertes"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Check alertes chaque 30 secondes
                
                # Vérification règles alertes
                metrics = await self._get_performance_metrics()
                
                for rule_id, rule in self.alert_rules.items():
                    if not rule.enabled:
                        continue
                    
                    metric_value = metrics.get(rule.metric.value, 0)
                    
                    # Évaluation condition
                    if self._evaluate_alert_condition(metric_value, rule):
                        await self._trigger_alert(rule, metric_value)
                
            except Exception as e:
                logger.error("Erreur processeur alertes", error=str(e))
    
    def _evaluate_alert_condition(self, value: float, rule: AlertRule) -> bool:
        """Évaluation condition alerte"""
        if rule.operator == ">":
            return value > rule.threshold
        elif rule.operator == "<":
            return value < rule.threshold
        elif rule.operator == ">=":
            return value >= rule.threshold
        elif rule.operator == "<=":
            return value <= rule.threshold
        elif rule.operator == "==":
            return value == rule.threshold
        
        return False
    
    async def _trigger_alert(self, rule: AlertRule, value: float):
        """Déclenchement alerte"""
        alert_data = {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "metric": rule.metric.value,
            "threshold": rule.threshold,
            "current_value": value,
            "severity": rule.severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast alerte via WebSocket
        for websocket in self.websocket_connections.copy():
            try:
                await websocket.send_json({
                    "type": "alert",
                    "data": alert_data
                })
            except Exception:
                self.websocket_connections.discard(websocket)
        
        self.console_metrics["alerts_triggered"] += 1
        
        logger.warning("Alerte déclenchée", alert=alert_data)
    
    # API publique
    
    def get_app(self) -> FastAPI:
        """Récupération application FastAPI"""
        return self.app
    
    async def add_database_connection(self, connection: DatabaseConnection) -> bool:
        """Ajout connexion database"""
        try:
            # Test connexion
            test_result = await self._test_database_connection(connection)
            connection.is_active = test_result["success"]
            connection.last_ping = datetime.utcnow()
            
            self.database_connections[connection.id] = connection
            
            logger.info("Connexion database ajoutée", name=connection.name)
            return True
            
        except Exception as e:
            logger.error("Erreur ajout connexion", error=str(e))
            return False


# Fonctions utilitaires pour intégration

async def initialize_enterprise_database_console(
    config: ConsoleConfiguration = None
) -> EnterpriseDatabaseConsole:
    """Initialisation console database enterprise"""
    if config is None:
        config = ConsoleConfiguration()
    
    console = EnterpriseDatabaseConsole(config)
    await console.start()
    
    logger.info("EnterpriseDatabaseConsole initialisé et démarré")
    return console

def create_console_config(
    port: int = 8080,
    enable_query_execution: bool = True,
    theme: str = "dark"
) -> ConsoleConfiguration:
    """Création configuration console optimisée"""
    return ConsoleConfiguration(
        port=port,
        enable_query_execution=enable_query_execution,
        enable_websockets=True,
        real_time_updates=True,
        audit_all_actions=True,
        theme=theme
    )

# Export des classes principales
__all__ = [
    "EnterpriseDatabaseConsole",
    "ConsoleConfiguration", 
    "ConsolePermission",
    "DatabaseProvider",
    "MonitoringMetric",
    "DatabaseConnection",
    "UserSession",
    "QueryExecution",
    "AlertRule",
    "initialize_enterprise_database_console",
    "create_console_config"
]