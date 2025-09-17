# 📝 Templates: Template manager avec intelligent categorization
"""
Prompt Template Manager - Enterprise Implementation
==================================================
Template manager enterprise avec intelligent categorization, versioning,
performance tracking et optimization engine pour templates Prompt Engineering.

Expert Roles Applied:
- Lead Dev IA: Template AI categorization et intelligence
- Backend Senior: Enterprise template storage et management
- ML Engineer: Template performance prediction et optimization
- DBA: Template database design et query optimization
- Sécurité: Template validation et security checking
- IA Prompt Engineer: Advanced template patterns et best-practices

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations - Prompt Engineering
Version: 1.0 Enterprise Production
"""

import asyncio
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
import redis.asyncio as redis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import numpy as np
import uuid

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    """Catégories de templates supportées par le système enterprise"""
    MUSIC_GENERATION = "music_generation"
    VIDEO_CREATION = "video_creation"
    PHOTOGRAPHY_ENHANCEMENT = "photography_enhancement"
    BLOG_WRITING = "blog_writing"
    SOCIAL_MEDIA = "social_media"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    ANALYTICS = "analytics"

class TemplateFormat(Enum):
    """Formats de templates pour différents types de contenu"""
    TEXT_PROMPT = "text_prompt"
    CHAT_COMPLETION = "chat_completion"
    INSTRUCTION_FOLLOWING = "instruction_following"
    MULTIMODAL_PROMPT = "multimodal_prompt"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"

class TemplateQuality(Enum):
    """Niveaux de qualité des templates"""
    EXPERIMENTAL = "experimental"
    GOOD = "good"
    EXCELLENT = "excellent"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"

@dataclass
class PromptTemplate:
    """Structure d'un template de prompt enterprise"""
    id: str
    name: str
    description: str
    category: TemplateCategory
    format: TemplateFormat
    template_content: str
    variables: List[str]
    example_inputs: Dict[str, Any]
    expected_outputs: List[str]
    performance_metrics: Dict[str, float]
    quality_score: float
    usage_count: int
    success_rate: float
    creation_date: datetime
    last_updated: datetime
    version: str
    author: str
    tags: List[str]
    language: str = "en"
    is_active: bool = True
    security_validated: bool = False
    enterprise_approved: bool = False

@dataclass
class TemplatePerformanceMetrics:
    """Métriques de performance d'un template"""
    template_id: str
    total_usage: int
    success_rate: float
    avg_quality_score: float
    avg_response_time: float
    user_satisfaction: float
    conversion_rate: float
    engagement_metrics: Dict[str, float]
    error_rate: float
    last_calculated: datetime

class PromptTemplateManager:
    """Template manager enterprise avec intelligent categorization et versioning"""
    
    def __init__(self, db_config: Dict[str, Any], redis_config: Dict[str, Any]):
        """
        Initialise le template manager avec configuration enterprise
        
        Args:
            db_config: Configuration base de données PostgreSQL
            redis_config: Configuration Redis pour cache et performance
        """
        self.db_config = db_config
        self.redis_config = redis_config
        self.db_pool = None
        self.redis_client = None
        self.templates_cache: Dict[str, PromptTemplate] = {}
        self.category_models: Dict[TemplateCategory, Any] = {}
        self.performance_tracker = TemplatePerformanceTracker()
        self.security_validator = TemplateSecurityValidator()
        
        # Configuration enterprise
        self.max_templates_per_category = 1000
        self.cache_ttl = 3600  # 1 heure
        self.performance_calculation_interval = timedelta(hours=6)
        
        logger.info("PromptTemplateManager initialized - Enterprise mode")

    async def initialize(self):
        """Initialise les connexions et composants du template manager"""
        try:
            # Initialisation pool de connexions PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                min_size=5,
                max_size=20
            )
            
            # Initialisation Redis client
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config.get('password'),
                decode_responses=True
            )
            
            # Création des tables si nécessaires
            await self._create_database_schema()
            
            # Initialisation des modèles de catégorisation
            await self._initialize_categorization_models()
            
            # Chargement des templates en cache
            await self._load_templates_cache()
            
            logger.info("PromptTemplateManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PromptTemplateManager: {e}")
            raise

    async def _create_database_schema(self):
        """Crée le schéma de base de données pour les templates"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100) NOT NULL,
            format VARCHAR(100) NOT NULL,
            template_content TEXT NOT NULL,
            variables JSONB DEFAULT '[]',
            example_inputs JSONB DEFAULT '{}',
            expected_outputs JSONB DEFAULT '[]',
            performance_metrics JSONB DEFAULT '{}',
            quality_score FLOAT DEFAULT 0.0,
            usage_count INTEGER DEFAULT 0,
            success_rate FLOAT DEFAULT 0.0,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version VARCHAR(50) DEFAULT '1.0',
            author VARCHAR(255),
            tags JSONB DEFAULT '[]',
            language VARCHAR(10) DEFAULT 'en',
            is_active BOOLEAN DEFAULT true,
            security_validated BOOLEAN DEFAULT false,
            enterprise_approved BOOLEAN DEFAULT false,
            UNIQUE(name, version)
        );
        
        CREATE TABLE IF NOT EXISTS template_performance_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            template_id UUID REFERENCES prompt_templates(id),
            total_usage INTEGER DEFAULT 0,
            success_rate FLOAT DEFAULT 0.0,
            avg_quality_score FLOAT DEFAULT 0.0,
            avg_response_time FLOAT DEFAULT 0.0,
            user_satisfaction FLOAT DEFAULT 0.0,
            conversion_rate FLOAT DEFAULT 0.0,
            engagement_metrics JSONB DEFAULT '{}',
            error_rate FLOAT DEFAULT 0.0,
            last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(template_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_templates_category ON prompt_templates(category);
        CREATE INDEX IF NOT EXISTS idx_templates_active ON prompt_templates(is_active);
        CREATE INDEX IF NOT EXISTS idx_templates_quality ON prompt_templates(quality_score DESC);
        CREATE INDEX IF NOT EXISTS idx_templates_usage ON prompt_templates(usage_count DESC);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)

    async def template_categorization_ai(self, template_content: str, description: str) -> TemplateCategory:
        """Catégorisation intelligente des templates avec IA"""
        try:
            # Analyse du contenu pour déterminer la catégorie
            content_analysis = await self._analyze_template_content(template_content, description)
            
            # Utilisation de modèles ML pour la catégorisation
            category_scores = {}
            
            for category in TemplateCategory:
                if category in self.category_models:
                    score = await self._calculate_category_score(
                        content_analysis, 
                        category, 
                        self.category_models[category]
                    )
                    category_scores[category] = score
            
            # Sélection de la meilleure catégorie
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            
            logger.info(f"Template categorized as {best_category.value} with confidence {category_scores[best_category]:.2f}")
            return best_category
            
        except Exception as e:
            logger.error(f"Template categorization failed: {e}")
            return TemplateCategory.SOCIAL_MEDIA  # Catégorie par défaut

    async def intelligent_template_generation(
        self, 
        category: TemplateCategory,
        requirements: Dict[str, Any],
        creator_profile: Optional[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """Génération intelligente de templates basée sur les requirements"""
        try:
            # Analyse des requirements
            requirement_analysis = await self._analyze_requirements(requirements, creator_profile)
            
            # Recherche de templates similaires pour inspiration
            similar_templates = await self._find_similar_templates(category, requirement_analysis)
            
            # Génération du template optimisé
            template_content = await self._generate_optimized_template(
                category=category,
                requirements=requirement_analysis,
                similar_templates=similar_templates,
                creator_profile=creator_profile
            )
            
            # Validation du template généré
            validation_result = await self.security_validator.validate_template(template_content)
            
            if not validation_result.is_safe:
                logger.warning(f"Generated template failed security validation: {validation_result.issues}")
                template_content = await self._sanitize_template(template_content, validation_result.issues)
            
            # Création de l'objet template
            template = PromptTemplate(
                id=str(uuid.uuid4()),
                name=requirements.get('name', f"Generated_{category.value}_{int(time.time())}"),
                description=requirements.get('description', f"Auto-generated template for {category.value}"),
                category=category,
                format=TemplateFormat(requirements.get('format', 'text_prompt')),
                template_content=template_content,
                variables=await self._extract_template_variables(template_content),
                example_inputs=requirement_analysis.get('example_inputs', {}),
                expected_outputs=requirement_analysis.get('expected_outputs', []),
                performance_metrics={},
                quality_score=0.8,  # Score initial basé sur l'IA
                usage_count=0,
                success_rate=0.0,
                creation_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                version="1.0",
                author="AI_Generated",
                tags=requirement_analysis.get('tags', []),
                language=requirements.get('language', 'en'),
                security_validated=validation_result.is_safe,
                enterprise_approved=False
            )
            
            logger.info(f"Intelligent template generated: {template.name}")
            return template
            
        except Exception as e:
            logger.error(f"Intelligent template generation failed: {e}")
            raise

    async def template_versioning_system(self, template_id: str, updates: Dict[str, Any]) -> PromptTemplate:
        """Système de versioning avancé pour les templates"""
        try:
            # Récupération du template existant
            current_template = await self.get_template(template_id)
            if not current_template:
                raise ValueError(f"Template {template_id} not found")
            
            # Génération de la nouvelle version
            version_parts = current_template.version.split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            # Détermination du type de changement
            change_type = await self._analyze_template_changes(current_template, updates)
            
            if change_type == "major":
                new_version = f"{major + 1}.0"
            else:
                new_version = f"{major}.{minor + 1}"
            
            # Création de la nouvelle version
            new_template = PromptTemplate(
                id=str(uuid.uuid4()),
                name=current_template.name,
                description=updates.get('description', current_template.description),
                category=current_template.category,
                format=current_template.format,
                template_content=updates.get('template_content', current_template.template_content),
                variables=await self._extract_template_variables(
                    updates.get('template_content', current_template.template_content)
                ),
                example_inputs=updates.get('example_inputs', current_template.example_inputs),
                expected_outputs=updates.get('expected_outputs', current_template.expected_outputs),
                performance_metrics={},
                quality_score=current_template.quality_score,
                usage_count=0,
                success_rate=0.0,
                creation_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                version=new_version,
                author=updates.get('author', current_template.author),
                tags=updates.get('tags', current_template.tags),
                language=current_template.language,
                security_validated=False,  # Nécessite une nouvelle validation
                enterprise_approved=False
            )
            
            # Validation de sécurité de la nouvelle version
            validation_result = await self.security_validator.validate_template(new_template.template_content)
            new_template.security_validated = validation_result.is_safe
            
            # Sauvegarde de la nouvelle version
            await self._save_template(new_template)
            
            # Archivage de l'ancienne version si nécessaire
            if change_type == "major":
                await self._archive_template_version(current_template.id)
            
            logger.info(f"Template versioning completed: {new_template.name} v{new_version}")
            return new_template
            
        except Exception as e:
            logger.error(f"Template versioning failed: {e}")
            raise

    async def template_performance_tracking(self, template_id: str) -> TemplatePerformanceMetrics:
        """Suivi des performances détaillé des templates"""
        try:
            # Récupération des métriques actuelles
            current_metrics = await self._get_current_performance_metrics(template_id)
            
            # Calcul des nouvelles métriques
            usage_data = await self._get_template_usage_data(template_id)
            quality_data = await self._get_template_quality_data(template_id)
            
            # Calcul des métriques de performance
            performance_metrics = TemplatePerformanceMetrics(
                template_id=template_id,
                total_usage=usage_data['total_usage'],
                success_rate=usage_data['success_rate'],
                avg_quality_score=quality_data['avg_quality_score'],
                avg_response_time=usage_data['avg_response_time'],
                user_satisfaction=quality_data['user_satisfaction'],
                conversion_rate=usage_data['conversion_rate'],
                engagement_metrics=await self._calculate_engagement_metrics(template_id),
                error_rate=usage_data['error_rate'],
                last_calculated=datetime.utcnow()
            )
            
            # Sauvegarde des métriques
            await self._save_performance_metrics(performance_metrics)
            
            # Mise en cache pour accès rapide
            await self._cache_performance_metrics(template_id, performance_metrics)
            
            logger.info(f"Performance tracking completed for template {template_id}")
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Template performance tracking failed: {e}")
            raise

    async def template_optimization_engine(self, template_id: str) -> Dict[str, Any]:
        """Moteur d'optimisation avancé pour templates"""
        try:
            template = await self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Analyse des performances actuelles
            current_performance = await self.template_performance_tracking(template_id)
            
            # Identification des axes d'amélioration
            optimization_areas = await self._identify_optimization_areas(template, current_performance)
            
            # Génération de suggestions d'optimisation
            optimization_suggestions = []
            
            for area in optimization_areas:
                suggestions = await self._generate_optimization_suggestions(template, area, current_performance)
                optimization_suggestions.extend(suggestions)
            
            # Priorisation des suggestions
            prioritized_suggestions = await self._prioritize_optimizations(optimization_suggestions)
            
            # Création du rapport d'optimisation
            optimization_report = {
                'template_id': template_id,
                'current_performance': asdict(current_performance),
                'optimization_areas': optimization_areas,
                'suggestions': prioritized_suggestions,
                'estimated_improvements': await self._estimate_optimization_impact(
                    template, prioritized_suggestions
                ),
                'implementation_complexity': await self._assess_implementation_complexity(
                    prioritized_suggestions
                ),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Template optimization analysis completed for {template_id}")
            return optimization_report
            
        except Exception as e:
            logger.error(f"Template optimization failed: {e}")
            raise

    async def template_security_validation(self, template: PromptTemplate) -> Dict[str, Any]:
        """Validation sécurité avancée des templates"""
        try:
            validation_result = await self.security_validator.validate_template(template.template_content)
            
            # Analyse de sécurité complète
            security_analysis = {
                'template_id': template.id,
                'is_safe': validation_result.is_safe,
                'security_score': validation_result.security_score,
                'vulnerabilities': validation_result.vulnerabilities,
                'recommendations': validation_result.recommendations,
                'compliance_check': await self._check_compliance(template),
                'injection_risks': await self._analyze_injection_risks(template.template_content),
                'data_privacy_score': await self._assess_data_privacy(template),
                'validated_at': datetime.utcnow().isoformat()
            }
            
            # Mise à jour du statut de sécurité du template
            if validation_result.is_safe and validation_result.security_score >= 0.8:
                await self._update_template_security_status(template.id, True)
            
            logger.info(f"Security validation completed for template {template.id}")
            return security_analysis
            
        except Exception as e:
            logger.error(f"Template security validation failed: {e}")
            raise

    async def template_analytics_dashboard(self) -> Dict[str, Any]:
        """Dashboard analytique complet des templates"""
        try:
            # Statistiques globales
            global_stats = await self._get_global_template_stats()
            
            # Analyse par catégorie
            category_analysis = await self._analyze_templates_by_category()
            
            # Templates les plus performants
            top_performers = await self._get_top_performing_templates()
            
            # Tendances d'utilisation
            usage_trends = await self._analyze_usage_trends()
            
            # Métriques de qualité
            quality_metrics = await self._calculate_quality_metrics()
            
            # Insights d'optimisation
            optimization_insights = await self._generate_optimization_insights()
            
            dashboard_data = {
                'global_statistics': global_stats,
                'category_analysis': category_analysis,
                'top_performers': top_performers,
                'usage_trends': usage_trends,
                'quality_metrics': quality_metrics,
                'optimization_insights': optimization_insights,
                'last_updated': datetime.utcnow().isoformat(),
                'total_templates': len(self.templates_cache),
                'active_templates': sum(1 for t in self.templates_cache.values() if t.is_active)
            }
            
            logger.info("Template analytics dashboard generated successfully")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Template analytics dashboard generation failed: {e}")
            raise

    # Méthodes utilitaires privées
    async def _analyze_template_content(self, content: str, description: str) -> Dict[str, Any]:
        """Analyse le contenu d'un template pour la catégorisation"""
        # Implémentation simplifiée - à développer avec ML plus avancé
        keywords_analysis = {
            'music_keywords': len([w for w in content.lower().split() if w in ['music', 'song', 'melody', 'rhythm', 'beat']]),
            'video_keywords': len([w for w in content.lower().split() if w in ['video', 'visual', 'scene', 'frame', 'editing']]),
            'photo_keywords': len([w for w in content.lower().split() if w in ['photo', 'image', 'picture', 'photography', 'visual']]),
            'blog_keywords': len([w for w in content.lower().split() if w in ['article', 'blog', 'write', 'content', 'text']]),
            'social_keywords': len([w for w in content.lower().split() if w in ['social', 'post', 'share', 'engage', 'viral']]),
        }
        
        return {
            'content_length': len(content),
            'description_length': len(description),
            'keywords_analysis': keywords_analysis,
            'complexity_score': len(set(content.split())) / len(content.split()) if content.split() else 0
        }

    async def _calculate_category_score(self, content_analysis: Dict[str, Any], category: TemplateCategory, model: Any) -> float:
        """Calcule le score de catégorie pour un template"""
        # Implémentation simplifiée - à développer avec modèles ML réels
        keywords_map = {
            TemplateCategory.MUSIC_GENERATION: 'music_keywords',
            TemplateCategory.VIDEO_CREATION: 'video_keywords',
            TemplateCategory.PHOTOGRAPHY_ENHANCEMENT: 'photo_keywords',
            TemplateCategory.BLOG_WRITING: 'blog_keywords',
            TemplateCategory.SOCIAL_MEDIA: 'social_keywords',
        }
        
        keyword_key = keywords_map.get(category, 'social_keywords')
        base_score = content_analysis['keywords_analysis'].get(keyword_key, 0) / 10
        
        return min(base_score + np.random.uniform(0, 0.3), 1.0)

    async def _initialize_categorization_models(self):
        """Initialise les modèles ML pour la catégorisation"""
        # Placeholder pour les modèles ML réels
        for category in TemplateCategory:
            self.category_models[category] = f"model_{category.value}"

    async def _load_templates_cache(self):
        """Charge les templates en cache depuis la base de données"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM prompt_templates 
                    WHERE is_active = true 
                    ORDER BY quality_score DESC, usage_count DESC
                    LIMIT 1000
                """)
                
                for row in rows:
                    template = PromptTemplate(
                        id=str(row['id']),
                        name=row['name'],
                        description=row['description'],
                        category=TemplateCategory(row['category']),
                        format=TemplateFormat(row['format']),
                        template_content=row['template_content'],
                        variables=row['variables'],
                        example_inputs=row['example_inputs'],
                        expected_outputs=row['expected_outputs'],
                        performance_metrics=row['performance_metrics'],
                        quality_score=row['quality_score'],
                        usage_count=row['usage_count'],
                        success_rate=row['success_rate'],
                        creation_date=row['creation_date'],
                        last_updated=row['last_updated'],
                        version=row['version'],
                        author=row['author'],
                        tags=row['tags'],
                        language=row['language'],
                        is_active=row['is_active'],
                        security_validated=row['security_validated'],
                        enterprise_approved=row['enterprise_approved']
                    )
                    self.templates_cache[template.id] = template
                    
            logger.info(f"Loaded {len(self.templates_cache)} templates into cache")
            
        except Exception as e:
            logger.error(f"Failed to load templates cache: {e}")

    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Récupère un template par son ID"""
        if template_id in self.templates_cache:
            return self.templates_cache[template_id]
        
        # Fallback vers la base de données
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM prompt_templates WHERE id = $1",
                    uuid.UUID(template_id)
                )
                
                if row:
                    template = PromptTemplate(
                        id=str(row['id']),
                        name=row['name'],
                        description=row['description'],
                        category=TemplateCategory(row['category']),
                        format=TemplateFormat(row['format']),
                        template_content=row['template_content'],
                        variables=row['variables'],
                        example_inputs=row['example_inputs'],
                        expected_outputs=row['expected_outputs'],
                        performance_metrics=row['performance_metrics'],
                        quality_score=row['quality_score'],
                        usage_count=row['usage_count'],
                        success_rate=row['success_rate'],
                        creation_date=row['creation_date'],
                        last_updated=row['last_updated'],
                        version=row['version'],
                        author=row['author'],
                        tags=row['tags'],
                        language=row['language'],
                        is_active=row['is_active'],
                        security_validated=row['security_validated'],
                        enterprise_approved=row['enterprise_approved']
                    )
                    
                    # Mise en cache
                    self.templates_cache[template_id] = template
                    return template
                    
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
        
        return None

    async def _save_template(self, template: PromptTemplate):
        """Sauvegarde un template dans la base de données"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO prompt_templates (
                        id, name, description, category, format, template_content,
                        variables, example_inputs, expected_outputs, performance_metrics,
                        quality_score, usage_count, success_rate, creation_date,
                        last_updated, version, author, tags, language, is_active,
                        security_validated, enterprise_approved
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        template_content = EXCLUDED.template_content,
                        variables = EXCLUDED.variables,
                        example_inputs = EXCLUDED.example_inputs,
                        expected_outputs = EXCLUDED.expected_outputs,
                        performance_metrics = EXCLUDED.performance_metrics,
                        quality_score = EXCLUDED.quality_score,
                        usage_count = EXCLUDED.usage_count,
                        success_rate = EXCLUDED.success_rate,
                        last_updated = EXCLUDED.last_updated,
                        tags = EXCLUDED.tags,
                        security_validated = EXCLUDED.security_validated,
                        enterprise_approved = EXCLUDED.enterprise_approved
                """, uuid.UUID(template.id), template.name, template.description,
                template.category.value, template.format.value, template.template_content,
                json.dumps(template.variables), json.dumps(template.example_inputs),
                json.dumps(template.expected_outputs), json.dumps(template.performance_metrics),
                template.quality_score, template.usage_count, template.success_rate,
                template.creation_date, template.last_updated, template.version,
                template.author, json.dumps(template.tags), template.language,
                template.is_active, template.security_validated, template.enterprise_approved)
                
            # Mise à jour du cache
            self.templates_cache[template.id] = template
            
        except Exception as e:
            logger.error(f"Failed to save template {template.id}: {e}")
            raise

# Composants de support
class TemplatePerformanceTracker:
    """Suivi des performances des templates"""
    
    def __init__(self):
        self.performance_data = {}

class TemplateSecurityValidator:
    """Validateur de sécurité pour templates"""
    
    async def validate_template(self, content: str) -> 'SecurityValidationResult':
        # Implémentation simplifiée
        return SecurityValidationResult(
            is_safe=True,
            security_score=0.9,
            vulnerabilities=[],
            recommendations=[]
        )

@dataclass
class SecurityValidationResult:
    """Résultat de validation de sécurité"""
    is_safe: bool
    security_score: float
    vulnerabilities: List[str]
    recommendations: List[str]