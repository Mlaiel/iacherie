"""
🎯 Prompt Template Registry - Central Template Management System
===============================================================

Enterprise-grade template registry for AI prompt management with versioning,
categorization, and intelligent template discovery for creator economy platform.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - IA Prompt Engineer Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import get_settings
from utils.exceptions import TemplateError, ValidationError, SecurityError
from monitoring.prompt_metrics import PromptMetricsCollector
from .security_validator import SecurityValidator
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)
settings = get_settings()


class TemplateStatus(Enum):
    """Template status states"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    TESTING = "testing"
    OPTIMIZING = "optimizing"


class TemplateCategory(Enum):
    """Template categories for creator economy"""
    CONTENT_GENERATION = "content_generation"
    ANALYTICS_SEO = "analytics_seo"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PROTECTION_SECURITY = "protection_security"
    GAMIFICATION = "gamification"
    MULTI_FORMAT = "multi_format"
    AI_ORCHESTRATION = "ai_orchestration"
    PERFORMANCE = "performance"
    MULTILINGUAL = "multilingual"
    RESEARCH = "research"
    REAL_TIME = "real_time"
    CREATOR_ECONOMY = "creator_economy"
    WORKFLOW = "workflow"
    KNOWLEDGE = "knowledge"


class TemplatePriority(Enum):
    """Template priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXPERIMENTAL = "experimental"


@dataclass
class TemplateMetadata:
    """Template metadata structure"""
    id: str
    name: str
    version: str
    category: TemplateCategory
    description: str
    author: str = "Fahed Mlaiel (mlaiel@live.de)"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: TemplateStatus = TemplateStatus.DRAFT
    priority: TemplatePriority = TemplatePriority.MEDIUM
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    supported_models: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    cost_per_token: float = 0.0
    creator_economy_integration: bool = True
    security_validated: bool = False
    optimization_level: str = "standard"


class TemplateRegistryModel(BaseModel):
    """Pydantic model for template registration"""
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    category: TemplateCategory
    description: str = Field(..., min_length=10, max_length=500)
    template_content: str = Field(..., min_length=1)
    variables: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list, max_items=10)
    supported_models: List[str] = Field(default_factory=list)
    priority: TemplatePriority = TemplatePriority.MEDIUM
    creator_economy_features: Dict[str, bool] = Field(default_factory=dict)
    security_requirements: Dict[str, bool] = Field(default_factory=dict)
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate template tags"""
        valid_tags = {
            'creator', 'monetization', 'collaboration', 'seo', 'analytics',
            'security', 'gamification', 'real-time', 'multi-format', 'ai',
            'optimization', 'performance', 'enterprise', 'professional'
        }
        for tag in v:
            if tag not in valid_tags:
                raise ValueError(f"Invalid tag: {tag}. Must be one of {valid_tags}")
        return v
    
    @validator('supported_models')
    def validate_models(cls, v):
        """Validate supported AI models"""
        valid_models = {
            'gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo', 'claude-3', 'claude-2',
            'claude-instant', 'gemini-pro', 'palm-2', 'text-bison', 'command',
            'command-light', 'command-nightly'
        }
        for model in v:
            if model not in valid_models:
                raise ValueError(f"Unsupported model: {model}")
        return v


class PromptTemplateRegistry:
    """
    🎯 Enterprise Prompt Template Registry
    
    Central registry for managing AI prompt templates with:
    - Template versioning and rollback
    - Intelligent template discovery
    - Performance tracking and optimization
    - Security validation and compliance
    - Creator economy integration
    - Multi-model compatibility
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.templates: Dict[str, TemplateMetadata] = {}
        self.template_cache: Dict[str, str] = {}
        self.security_validator = SecurityValidator()
        self.performance_monitor = PerformanceMonitor()
        self.metrics_collector = PromptMetricsCollector()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize registry connections and cache"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Initialize MongoDB connection
            self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Create database tables if not exist
            await self._create_tables()
            
            # Load templates from database
            await self._load_templates()
            
            # Initialize security validator and performance monitor
            await self.security_validator.initialize()
            await self.performance_monitor.initialize()
            
            self._initialized = True
            logger.info("Prompt Template Registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prompt Template Registry: {e}")
            raise TemplateError(f"Registry initialization failed: {e}")
    
    async def _create_tables(self) -> None:
        """Create database tables for template storage"""
        create_template_table = """
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            version VARCHAR(50) NOT NULL,
            category VARCHAR(100) NOT NULL,
            description TEXT,
            template_content TEXT NOT NULL,
            metadata JSONB,
            variables JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'draft',
            author VARCHAR(255) DEFAULT 'Fahed Mlaiel (mlaiel@live.de)',
            UNIQUE(name, version)
        );
        """
        
        create_template_metrics_table = """
        CREATE TABLE IF NOT EXISTS template_metrics (
            id SERIAL PRIMARY KEY,
            template_id VARCHAR(255) REFERENCES prompt_templates(id),
            usage_count INTEGER DEFAULT 0,
            success_rate FLOAT DEFAULT 0.0,
            avg_response_time FLOAT DEFAULT 0.0,
            cost_per_token FLOAT DEFAULT 0.0,
            performance_score FLOAT DEFAULT 0.0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_template_versions_table = """
        CREATE TABLE IF NOT EXISTS template_versions (
            id SERIAL PRIMARY KEY,
            template_id VARCHAR(255) REFERENCES prompt_templates(id),
            version VARCHAR(50) NOT NULL,
            changelog TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(255) DEFAULT 'Fahed Mlaiel (mlaiel@live.de)'
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_template_table)
            await conn.execute(create_template_metrics_table)
            await conn.execute(create_template_versions_table)
    
    async def _load_templates(self) -> None:
        """Load templates from database into memory cache"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT t.*, tm.usage_count, tm.success_rate, 
                           tm.avg_response_time, tm.cost_per_token
                    FROM prompt_templates t
                    LEFT JOIN (
                        SELECT template_id, 
                               AVG(usage_count) as usage_count,
                               AVG(success_rate) as success_rate,
                               AVG(avg_response_time) as avg_response_time,
                               AVG(cost_per_token) as cost_per_token
                        FROM template_metrics 
                        GROUP BY template_id
                    ) tm ON t.id = tm.template_id
                    WHERE t.status IN ('active', 'testing')
                """)
                
                for row in rows:
                    metadata = TemplateMetadata(
                        id=row['id'],
                        name=row['name'],
                        version=row['version'],
                        category=TemplateCategory(row['category']),
                        description=row['description'],
                        author=row['author'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        status=TemplateStatus(row['status']),
                        usage_count=row['usage_count'] or 0,
                        success_rate=row['success_rate'] or 0.0,
                        avg_response_time=row['avg_response_time'] or 0.0,
                        cost_per_token=row['cost_per_token'] or 0.0
                    )
                    
                    if row['metadata']:
                        metadata_dict = json.loads(row['metadata'])
                        for key, value in metadata_dict.items():
                            if hasattr(metadata, key):
                                setattr(metadata, key, value)
                    
                    self.templates[row['id']] = metadata
                    self.template_cache[row['id']] = row['template_content']
                
                logger.info(f"Loaded {len(self.templates)} templates into registry")
        
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            raise TemplateError(f"Template loading failed: {e}")
    
    async def register_template(self, template_data: TemplateRegistryModel) -> str:
        """
        Register new prompt template with validation and security checks
        
        Args:
            template_data: Template registration data
            
        Returns:
            Template ID
        """
        try:
            # Generate unique template ID
            template_id = self._generate_template_id(template_data.name, template_data.version)
            
            # Security validation
            security_result = await self.security_validator.validate_template(
                template_data.template_content
            )
            
            if not security_result.is_safe:
                raise SecurityError(f"Template failed security validation: {security_result.issues}")
            
            # Create metadata
            metadata = TemplateMetadata(
                id=template_id,
                name=template_data.name,
                version=template_data.version,
                category=template_data.category,
                description=template_data.description,
                tags=template_data.tags,
                supported_models=template_data.supported_models,
                priority=template_data.priority,
                security_validated=True,
                creator_economy_integration=bool(template_data.creator_economy_features)
            )
            
            # Store in database
            await self._store_template(template_id, template_data, metadata)
            
            # Update cache
            self.templates[template_id] = metadata
            self.template_cache[template_id] = template_data.template_content
            
            # Cache in Redis
            await self._cache_template(template_id, template_data.template_content, metadata)
            
            # Record metrics
            await self.metrics_collector.record_template_registration(template_id, metadata)
            
            logger.info(f"Template registered successfully: {template_id}")
            return template_id
        
        except Exception as e:
            logger.error(f"Failed to register template: {e}")
            raise TemplateError(f"Template registration failed: {e}")
    
    async def get_template(self, template_id: str) -> Optional[Tuple[str, TemplateMetadata]]:
        """
        Retrieve template by ID with performance tracking
        
        Args:
            template_id: Template identifier
            
        Returns:
            Tuple of (template_content, metadata) or None
        """
        try:
            # Check memory cache first
            if template_id in self.template_cache and template_id in self.templates:
                return self.template_cache[template_id], self.templates[template_id]
            
            # Check Redis cache
            cached_template = await self.redis_client.get(f"template:{template_id}")
            cached_metadata = await self.redis_client.get(f"template_meta:{template_id}")
            
            if cached_template and cached_metadata:
                metadata = pickle.loads(cached_metadata.encode('latin-1'))
                self.template_cache[template_id] = cached_template
                self.templates[template_id] = metadata
                return cached_template, metadata
            
            # Load from database
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM prompt_templates WHERE id = $1 AND status IN ('active', 'testing')
                """, template_id)
                
                if not row:
                    return None
                
                metadata = TemplateMetadata(
                    id=row['id'],
                    name=row['name'],
                    version=row['version'],
                    category=TemplateCategory(row['category']),
                    description=row['description'],
                    author=row['author'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    status=TemplateStatus(row['status'])
                )
                
                # Update caches
                self.template_cache[template_id] = row['template_content']
                self.templates[template_id] = metadata
                await self._cache_template(template_id, row['template_content'], metadata)
                
                return row['template_content'], metadata
        
        except Exception as e:
            logger.error(f"Failed to retrieve template {template_id}: {e}")
            raise TemplateError(f"Template retrieval failed: {e}")
    
    async def discover_templates(
        self,
        category: Optional[TemplateCategory] = None,
        tags: Optional[List[str]] = None,
        model: Optional[str] = None,
        creator_focus: bool = True,
        limit: int = 50
    ) -> List[TemplateMetadata]:
        """
        Intelligent template discovery with creator economy focus
        
        Args:
            category: Template category filter
            tags: Tags to filter by
            model: AI model compatibility
            creator_focus: Prioritize creator economy templates
            limit: Maximum results
            
        Returns:
            List of matching template metadata
        """
        try:
            query_conditions = ["t.status IN ('active', 'testing')"]
            query_params = []
            param_count = 0
            
            if category:
                param_count += 1
                query_conditions.append(f"t.category = ${param_count}")
                query_params.append(category.value)
            
            if tags:
                param_count += 1
                query_conditions.append(f"t.metadata->>'tags' @> ${param_count}")
                query_params.append(json.dumps(tags))
            
            if model:
                param_count += 1
                query_conditions.append(f"t.metadata->>'supported_models' @> ${param_count}")
                query_params.append(json.dumps([model]))
            
            if creator_focus:
                query_conditions.append("t.metadata->>'creator_economy_integration' = 'true'")
            
            query = f"""
                SELECT t.*, 
                       COALESCE(tm.usage_count, 0) as usage_count,
                       COALESCE(tm.success_rate, 0.0) as success_rate,
                       COALESCE(tm.avg_response_time, 0.0) as avg_response_time,
                       COALESCE(tm.performance_score, 0.0) as performance_score
                FROM prompt_templates t
                LEFT JOIN (
                    SELECT template_id, 
                           AVG(usage_count) as usage_count,
                           AVG(success_rate) as success_rate,
                           AVG(avg_response_time) as avg_response_time,
                           AVG(performance_score) as performance_score
                    FROM template_metrics 
                    GROUP BY template_id
                ) tm ON t.id = tm.template_id
                WHERE {' AND '.join(query_conditions)}
                ORDER BY tm.performance_score DESC, tm.usage_count DESC, t.created_at DESC
                LIMIT {limit}
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, *query_params)
                
                results = []
                for row in rows:
                    metadata = TemplateMetadata(
                        id=row['id'],
                        name=row['name'],
                        version=row['version'],
                        category=TemplateCategory(row['category']),
                        description=row['description'],
                        author=row['author'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        status=TemplateStatus(row['status']),
                        usage_count=row['usage_count'],
                        success_rate=row['success_rate'],
                        avg_response_time=row['avg_response_time']
                    )
                    
                    if row['metadata']:
                        metadata_dict = json.loads(row['metadata'])
                        for key, value in metadata_dict.items():
                            if hasattr(metadata, key):
                                setattr(metadata, key, value)
                    
                    results.append(metadata)
                
                logger.info(f"Discovered {len(results)} templates matching criteria")
                return results
        
        except Exception as e:
            logger.error(f"Template discovery failed: {e}")
            raise TemplateError(f"Template discovery failed: {e}")
    
    async def update_template_metrics(
        self,
        template_id: str,
        usage_count: int = 0,
        success_rate: float = 0.0,
        response_time: float = 0.0,
        cost_per_token: float = 0.0,
        performance_score: float = 0.0
    ) -> None:
        """Update template performance metrics"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO template_metrics 
                    (template_id, usage_count, success_rate, avg_response_time, 
                     cost_per_token, performance_score)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, template_id, usage_count, success_rate, response_time,
                    cost_per_token, performance_score)
                
                # Update cached metadata
                if template_id in self.templates:
                    metadata = self.templates[template_id]
                    metadata.usage_count += usage_count
                    metadata.success_rate = success_rate
                    metadata.avg_response_time = response_time
                    metadata.cost_per_token = cost_per_token
                    metadata.updated_at = datetime.utcnow()
            
            logger.debug(f"Updated metrics for template: {template_id}")
        
        except Exception as e:
            logger.error(f"Failed to update template metrics: {e}")
    
    async def get_creator_economy_templates(self) -> List[TemplateMetadata]:
        """Get templates optimized for creator economy workflows"""
        return await self.discover_templates(
            creator_focus=True,
            tags=['creator', 'monetization', 'collaboration'],
            limit=100
        )
    
    async def get_trending_templates(self, days: int = 7) -> List[TemplateMetadata]:
        """Get trending templates based on recent usage"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT t.*, 
                           SUM(tm.usage_count) as total_usage,
                           AVG(tm.success_rate) as avg_success_rate,
                           AVG(tm.performance_score) as avg_performance
                    FROM prompt_templates t
                    JOIN template_metrics tm ON t.id = tm.template_id
                    WHERE tm.recorded_at >= $1 AND t.status = 'active'
                    GROUP BY t.id
                    ORDER BY total_usage DESC, avg_performance DESC
                    LIMIT 20
                """, cutoff_date)
                
                results = []
                for row in rows:
                    metadata = TemplateMetadata(
                        id=row['id'],
                        name=row['name'],
                        version=row['version'],
                        category=TemplateCategory(row['category']),
                        description=row['description'],
                        usage_count=row['total_usage'],
                        success_rate=row['avg_success_rate']
                    )
                    results.append(metadata)
                
                return results
        
        except Exception as e:
            logger.error(f"Failed to get trending templates: {e}")
            return []
    
    def _generate_template_id(self, name: str, version: str) -> str:
        """Generate unique template identifier"""
        content = f"{name}:{version}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _store_template(
        self,
        template_id: str,
        template_data: TemplateRegistryModel,
        metadata: TemplateMetadata
    ) -> None:
        """Store template in database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO prompt_templates 
                (id, name, version, category, description, template_content, 
                 metadata, variables, status, author)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (name, version) DO UPDATE SET
                template_content = EXCLUDED.template_content,
                updated_at = CURRENT_TIMESTAMP
            """, template_id, template_data.name, template_data.version,
                template_data.category.value, template_data.description,
                template_data.template_content, json.dumps(metadata.__dict__),
                json.dumps(template_data.variables), metadata.status.value,
                metadata.author)
    
    async def _cache_template(
        self,
        template_id: str,
        content: str,
        metadata: TemplateMetadata
    ) -> None:
        """Cache template in Redis"""
        try:
            await self.redis_client.setex(
                f"template:{template_id}",
                3600,  # 1 hour TTL
                content
            )
            
            await self.redis_client.setex(
                f"template_meta:{template_id}",
                3600,
                pickle.dumps(metadata).decode('latin-1')
            )
        except Exception as e:
            logger.warning(f"Failed to cache template {template_id}: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup registry resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            if self.mongo_client:
                self.mongo_client.close()
            
            logger.info("Prompt Template Registry cleanup completed")
        
        except Exception as e:
            logger.error(f"Registry cleanup failed: {e}")


# Global registry instance
template_registry = PromptTemplateRegistry()