"""🗄️ Database Adapter - IA-Influencer-Agent Storage Layer
==================================================================
Expert: DBA_ENGINEER + DATA_SPECIALIST
Technologies: PostgreSQL + Redis + MongoDB + File Storage
Date: 2025-07-31 06:28:26

Couche de stockage optimisée avec pools de connexions et cache.
Modèles détectés: 0
==================================================================
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from contextlib import asynccontextmanager
import json

# Imports storage
try:
    import asyncpg
    import aioredis
    import motor.motor_asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    logger.warning(f"Import storage manquant: {e}")

logger = logging.getLogger(__name__)

# =============== CONFIGURATION STORAGE ===============

@dataclass
class StorageConfig:
    """Configuration du stockage"""    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ia_influencer"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # MongoDB
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "ia_influencer"
    
    # Pools
    max_connections: int = 20
    connection_timeout: int = 30

# =============== INTERFACES STORAGE ===============

class IStorageAdapter(ABC):
    """Interface adaptateur de stockage"""    
    @abstractmethod
    async def connect(self) -> bool:
        """Connexion au stockage"""        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Déconnexion du stockage"""        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Vérification de santé"""        pass

# =============== ADAPTATEUR POSTGRESQL ===============

class PostgreSQLAdapter(IStorageAdapter):
    """Adaptateur PostgreSQL optimisé"""    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.pool = None
        self.engine = None
        self.session_factory = None
    
    async def connect(self) -> bool:
        """Connexion PostgreSQL avec pool"""        try:
            # Pool de connexions asyncpg
            self.pool = await asyncpg.create_pool(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                database=self.config.postgres_db,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                max_size=self.config.max_connections,
                command_timeout=self.config.connection_timeout
            )
            
            # SQLAlchemy async engine
            database_url = f"postgresql+asyncpg://{self.config.postgres_user}:{self.config.postgres_password}@{self.config.postgres_host}:{self.config.postgres_port}/{self.config.postgres_db}"
            self.engine = create_async_engine(database_url, echo=False, pool_size=20)
            self.session_factory = sessionmaker(self.engine, class_=AsyncSession)
            
            logger.info("✅ PostgreSQL connecté")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion PostgreSQL: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Déconnexion PostgreSQL"""        try:
            if self.pool:
                await self.pool.close()
            if self.engine:
                await self.engine.dispose()
            logger.info("🔌 PostgreSQL déconnecté")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion PostgreSQL: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Vérification PostgreSQL"""        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetchval("SELECT 1")
                return result == 1
        except Exception:
            return False
    
    @asynccontextmanager
    async def get_session(self):
        """Gestionnaire de session SQLAlchemy"""        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

# =============== ADAPTATEUR REDIS ===============

class RedisAdapter(IStorageAdapter):
    """Adaptateur Redis optimisé"""    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.redis = None
    
    async def connect(self) -> bool:
        """Connexion Redis"""        try:
            self.redis = aioredis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                encoding='utf-8',
                decode_responses=True,
                max_connections=self.config.max_connections
            )
            await self.redis.ping()
            logger.info("✅ Redis connecté")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion Redis: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Déconnexion Redis"""        try:
            if self.redis:
                await self.redis.close()
            logger.info("🔌 Redis déconnecté")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion Redis: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Vérification Redis"""        try:
            await self.redis.ping()
            return True
        except Exception:
            return False
    
    async def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Cache avec expiration"""        try:
            await self.redis.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"❌ Erreur cache set: {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Récupération cache"""        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"❌ Erreur cache get: {e}")
            return None

# =============== GESTIONNAIRE STORAGE PRINCIPAL ===============

class DatabaseAdapterManager:
    """Gestionnaire principal du stockage"""    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.postgres = PostgreSQLAdapter(config)
        self.redis = RedisAdapter(config)
        self.connected = False
    
    async def initialize(self) -> bool:
        """Initialisation complète du stockage"""        try:
            # Connexions parallèles
            postgres_ok, redis_ok = await asyncio.gather(
                self.postgres.connect(),
                self.redis.connect(),
                return_exceptions=True
            )
            
            self.connected = postgres_ok and redis_ok
            
            if self.connected:
                logger.info("🚀 Storage Manager initialisé")
            else:
                logger.error("❌ Échec initialisation Storage")
            
            return self.connected
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation storage: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Arrêt propre du stockage"""        try:
            await asyncio.gather(
                self.postgres.disconnect(),
                self.redis.disconnect(),
                return_exceptions=True
            )
            logger.info("⏹️ Storage Manager arrêté")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur arrêt storage: {e}")
            return False

# =============== EXPORT MODULE ===============

__all__ = [
    "DatabaseAdapterManager",
    "PostgreSQLAdapter",
    "RedisAdapter",
    "StorageConfig",
    "IStorageAdapter"
]
