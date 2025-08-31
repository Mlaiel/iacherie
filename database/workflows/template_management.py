"""
Workflow Templates and Configuration Database System

Enterprise workflow template management system with AI-powered template
generation, smart configuration, version control, and marketplace features
for content creator workflow optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy import ForeignKey
import asyncio
import logging
import hashlib

Base = declarative_base()
logger = logging.getLogger(__name__)


class TemplateCategory(Enum):
    """Workflow template categories"""
    CONTENT_CREATION = "content_creation"
    SOCIAL_MEDIA_MANAGEMENT = "social_media_management"
    COLLABORATION = "collaboration"
    MARKETING_CAMPAIGN = "marketing_campaign"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    ANALYTICS_REPORTING = "analytics_reporting"
    QUALITY_ASSURANCE = "quality_assurance"
    COMPLIANCE = "compliance"
    BACKUP_RECOVERY = "backup_recovery"
    CUSTOM = "custom"


class TemplateComplexity(Enum):
    """Template complexity levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TemplateStatus(Enum):
    """Template lifecycle status"""
    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ParameterType(Enum):
    """Template parameter types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    ENUM = "enum"
    FILE = "file"
    USER_ID = "user_id"
    WORKFLOW_ID = "workflow_id"


class ConfigurationScope(Enum):
    """Configuration scope levels"""
    GLOBAL = "global"
    USER = "user"
    ORGANIZATION = "organization"
    WORKFLOW = "workflow"
    TEMPLATE = "template"
    SESSION = "session"


class WorkflowTemplateMarketplace(Base):
    """
    Database model for workflow template marketplace
    """
    __tablename__ = "workflow_template_marketplace"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(200), nullable=False)
    template_description = Column(Text)
    short_description = Column(String(500))
    
    # Template metadata
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100))
    complexity_level = Column(String(20), nullable=False)
    estimated_setup_time = Column(Integer)  # minutes
    
    # Creator information
    created_by_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_name = Column(String(200))
    creator_type = Column(String(50))
    organization_id = Column(UUID(as_uuid=True))
    
    # Template definition
    template_definition = Column(JSON, nullable=False)
    parameter_schema = Column(JSON, nullable=False)
    configuration_schema = Column(JSON)
    default_values = Column(JSON)
    
    # Compatibility and requirements
    supported_platforms = Column(ARRAY(String))
    supported_content_types = Column(ARRAY(String))
    supported_creator_types = Column(ARRAY(String))
    required_integrations = Column(ARRAY(String))
    minimum_requirements = Column(JSON)
    
    # Versioning
    version = Column(String(20), default="1.0.0", nullable=False)
    parent_template_id = Column(UUID(as_uuid=True))  # For forks/derivatives
    version_history = Column(JSON)
    changelog = Column(Text)
    
    # Marketplace metrics
    download_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    rating_average = Column(Numeric(3, 2), default=0.0)
    rating_count = Column(Integer, default=0)
    popularity_score = Column(Numeric(8, 4), default=0.0)
    
    # Success metrics
    success_rate = Column(Numeric(5, 4), default=0.0)
    completion_rate = Column(Numeric(5, 4), default=0.0)
    user_satisfaction = Column(Numeric(3, 2), default=0.0)
    performance_score = Column(Numeric(5, 2), default=0.0)
    
    # Pricing and licensing
    is_free = Column(Boolean, default=True)
    price = Column(Numeric(10, 2), default=0.0)
    currency = Column(String(3), default="USD")
    license_type = Column(String(50), default="mit")
    license_terms = Column(Text)
    
    # Visibility and access
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    access_level = Column(String(20), default="public")  # public, premium, private
    
    # Content and media
    thumbnail_url = Column(String(500))
    preview_images = Column(ARRAY(String))
    demo_video_url = Column(String(500))
    documentation_url = Column(String(500))
    
    # AI insights
    ai_generated = Column(Boolean, default=False)
    ai_optimization_score = Column(Numeric(5, 2))
    ai_recommendations = Column(JSON)
    learning_patterns = Column(JSON)
    
    # Quality assurance
    tested_scenarios = Column(JSON)
    quality_score = Column(Numeric(5, 2))
    security_score = Column(Numeric(5, 2))
    performance_benchmarks = Column(JSON)
    
    # Status and lifecycle
    status = Column(String(20), default="active", nullable=False)
    approval_status = Column(String(20), default="pending")
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True))
    weekly_usage = Column(Integer, default=0)
    monthly_usage = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0.0)
    
    # Metadata
    tags = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    target_audience = Column(JSON)
    use_cases = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_template_marketplace_creator', 'created_by_user_id'),
        Index('idx_template_marketplace_category', 'category'),
        Index('idx_template_marketplace_popularity', 'popularity_score'),
        Index('idx_template_marketplace_rating', 'rating_average'),
        Index('idx_template_marketplace_status', 'status'),
        Index('idx_template_marketplace_public', 'is_public'),
        Index('idx_template_marketplace_platforms', 'supported_platforms'),
        Index('idx_template_marketplace_tags', 'tags'),
    )


class WorkflowTemplateParameter(Base):
    """
    Database model for template parameters
    """
    __tablename__ = "workflow_template_parameters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey('workflow_template_marketplace.id'), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False)
    parameter_key = Column(String(100), nullable=False)
    
    # Parameter definition
    parameter_type = Column(String(20), nullable=False)
    parameter_description = Column(Text)
    display_name = Column(String(200))
    placeholder_text = Column(String(500))
    help_text = Column(Text)
    
    # Validation rules
    is_required = Column(Boolean, default=False)
    default_value = Column(JSON)
    validation_rules = Column(JSON)  # min, max, pattern, enum values, etc.
    allowed_values = Column(JSON)  # For enum types
    
    # UI configuration
    display_order = Column(Integer, default=0)
    group_name = Column(String(100))
    ui_component = Column(String(50))  # input, select, checkbox, etc.
    ui_properties = Column(JSON)  # Additional UI configuration
    
    # Dependencies
    depends_on_parameters = Column(ARRAY(String))
    conditional_logic = Column(JSON)  # Show/hide based on other parameters
    
    # Advanced features
    dynamic_values = Column(Boolean, default=False)  # Values fetched dynamically
    data_source = Column(JSON)  # For dynamic value sources
    auto_populate = Column(Boolean, default=False)
    
    # Validation and constraints
    min_length = Column(Integer)
    max_length = Column(Integer)
    min_value = Column(Numeric(20, 6))
    max_value = Column(Numeric(20, 6))
    regex_pattern = Column(String(500))
    
    # Metadata
    parameter_category = Column(String(50))
    is_sensitive = Column(Boolean, default=False)  # For passwords, API keys
    is_advanced = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_template_param_template', 'template_id'),
        Index('idx_template_param_key', 'parameter_key'),
        Index('idx_template_param_type', 'parameter_type'),
        Index('idx_template_param_order', 'display_order'),
    )


class WorkflowConfiguration(Base):
    """
    Database model for workflow configurations
    """
    __tablename__ = "workflow_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_name = Column(String(200), nullable=False)
    configuration_description = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Configuration scope
    scope = Column(String(20), nullable=False)
    scope_id = Column(UUID(as_uuid=True))  # Reference to scoped entity
    
    # Configuration data
    configuration_data = Column(JSON, nullable=False)
    configuration_schema = Column(JSON)
    validation_rules = Column(JSON)
    
    # Environment and context
    environment = Column(String(50), default="production")  # dev, staging, production
    context_filters = Column(JSON)  # When configuration applies
    priority = Column(Integer, default=1)  # Configuration priority
    
    # Inheritance and overrides
    parent_configuration_id = Column(UUID(as_uuid=True))
    inherited_from = Column(UUID(as_uuid=True))
    override_rules = Column(JSON)
    merge_strategy = Column(String(20), default="deep_merge")
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    version_history = Column(JSON)
    is_default = Column(Boolean, default=False)
    
    # Security and access
    encryption_enabled = Column(Boolean, default=False)
    access_permissions = Column(JSON)
    allowed_users = Column(ARRAY(UUID))
    restricted_fields = Column(ARRAY(String))
    
    # Validation and quality
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSON)
    last_validation_at = Column(DateTime(timezone=True))
    quality_score = Column(Numeric(5, 2))
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    usage_statistics = Column(JSON)
    
    # AI optimization
    ai_optimized = Column(Boolean, default=False)
    ai_suggestions = Column(JSON)
    optimization_score = Column(Numeric(5, 2))
    learning_data = Column(JSON)
    
    # Metadata
    tags = Column(ARRAY(String))
    category = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_workflow_config_user', 'user_id'),
        Index('idx_workflow_config_scope', 'scope', 'scope_id'),
        Index('idx_workflow_config_environment', 'environment'),
        Index('idx_workflow_config_default', 'is_default'),
        Index('idx_workflow_config_category', 'category'),
    )


class TemplateUsageHistory(Base):
    """
    Database model for template usage tracking
    """
    __tablename__ = "template_usage_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey('workflow_template_marketplace.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workflow_id = Column(UUID(as_uuid=True), index=True)
    
    # Usage details
    usage_type = Column(String(50), nullable=False)  # download, instantiate, customize
    customization_data = Column(JSON)  # How template was customized
    parameter_values = Column(JSON)  # Parameters used
    
    # Context information
    use_case = Column(String(200))
    project_context = Column(JSON)
    user_profile = Column(JSON)  # User characteristics at time of use
    
    # Success tracking
    usage_successful = Column(Boolean)
    completion_status = Column(String(50))
    time_to_complete = Column(Integer)  # seconds
    customization_time = Column(Integer)  # seconds
    
    # Feedback and ratings
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    reported_issues = Column(JSON)
    improvement_suggestions = Column(JSON)
    
    # Performance metrics
    workflow_performance = Column(JSON)
    outcome_metrics = Column(JSON)
    cost_savings = Column(Numeric(10, 2))
    time_savings = Column(Integer)  # minutes
    
    # Technical metrics
    execution_time = Column(Integer)  # milliseconds
    resource_usage = Column(JSON)
    error_count = Column(Integer, default=0)
    errors_encountered = Column(JSON)
    
    # A/B testing data
    test_variant = Column(String(50))
    test_group = Column(String(50))
    conversion_metrics = Column(JSON)
    
    # Metadata
    device_info = Column(JSON)
    browser_info = Column(JSON)
    session_data = Column(JSON)
    
    used_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_template_usage_template', 'template_id'),
        Index('idx_template_usage_user', 'user_id'),
        Index('idx_template_usage_workflow', 'workflow_id'),
        Index('idx_template_usage_type', 'usage_type'),
        Index('idx_template_usage_date', 'used_at'),
        Index('idx_template_usage_rating', 'user_rating'),
    )


class TemplateReview(Base):
    """
    Database model for template reviews and ratings
    """
    __tablename__ = "template_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey('workflow_template_marketplace.id'), nullable=False, index=True)
    reviewer_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_title = Column(String(200))
    review_text = Column(Text)
    pros = Column(ARRAY(String))
    cons = Column(ARRAY(String))
    
    # Detailed ratings
    ease_of_use = Column(Integer)  # 1-5
    documentation_quality = Column(Integer)  # 1-5
    performance = Column(Integer)  # 1-5
    value_for_money = Column(Integer)  # 1-5
    support_quality = Column(Integer)  # 1-5
    
    # Review context
    use_case = Column(String(200))
    experience_level = Column(String(20))
    project_size = Column(String(20))
    usage_duration = Column(String(20))
    
    # Verification
    verified_purchase = Column(Boolean, default=False)
    verified_usage = Column(Boolean, default=False)
    usage_evidence = Column(JSON)
    
    # Helpfulness
    helpful_votes = Column(Integer, default=0)
    unhelpful_votes = Column(Integer, default=0)
    flagged_count = Column(Integer, default=0)
    moderation_status = Column(String(20), default="approved")
    
    # Response from creator
    creator_response = Column(Text)
    creator_response_date = Column(DateTime(timezone=True))
    
    # Review metrics
    review_helpfulness_score = Column(Numeric(5, 2))
    review_quality_score = Column(Numeric(5, 2))
    sentiment_score = Column(Numeric(3, 2))  # -1 to 1
    
    # Metadata
    device_used = Column(String(100))
    version_reviewed = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_template_review_template', 'template_id'),
        Index('idx_template_review_reviewer', 'reviewer_user_id'),
        Index('idx_template_review_rating', 'rating'),
        Index('idx_template_review_date', 'created_at'),
        Index('idx_template_review_verified', 'verified_purchase'),
    )


class WorkflowTemplateManager:
    """
    Enterprise workflow template management system
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.ai_generator = AITemplateGenerator(db_session)
        self.configuration_manager = ConfigurationManager(db_session)
        self.marketplace_manager = MarketplaceManager(db_session)
    
    async def create_template(
        self,
        template_data: Dict[str, Any],
        creator_user_id: str
    ) -> str:
        """
        Create new workflow template
        
        Args:
            template_data: Template configuration data
            creator_user_id: User creating the template
            
        Returns:
            Template ID
        """
        # Validate template definition
        await self._validate_template_definition(template_data['template_definition'])
        
        # Generate template schema if not provided
        if 'parameter_schema' not in template_data:
            template_data['parameter_schema'] = await self._generate_parameter_schema(
                template_data['template_definition']
            )
        
        # Create template record
        template = WorkflowTemplateMarketplace(
            template_name=template_data['template_name'],
            template_description=template_data.get('template_description', ''),
            short_description=template_data.get('short_description', ''),
            category=template_data['category'],
            subcategory=template_data.get('subcategory'),
            complexity_level=template_data.get('complexity_level', 'intermediate'),
            estimated_setup_time=template_data.get('estimated_setup_time'),
            created_by_user_id=creator_user_id,
            creator_name=template_data.get('creator_name'),
            creator_type=template_data.get('creator_type'),
            template_definition=template_data['template_definition'],
            parameter_schema=template_data['parameter_schema'],
            configuration_schema=template_data.get('configuration_schema'),
            default_values=template_data.get('default_values', {}),
            supported_platforms=template_data.get('supported_platforms', []),
            supported_content_types=template_data.get('supported_content_types', []),
            supported_creator_types=template_data.get('supported_creator_types', []),
            required_integrations=template_data.get('required_integrations', []),
            minimum_requirements=template_data.get('minimum_requirements', {}),
            is_free=template_data.get('is_free', True),
            price=template_data.get('price', 0.0),
            license_type=template_data.get('license_type', 'mit'),
            is_public=template_data.get('is_public', True),
            thumbnail_url=template_data.get('thumbnail_url'),
            documentation_url=template_data.get('documentation_url'),
            tags=template_data.get('tags', []),
            keywords=template_data.get('keywords', []),
            target_audience=template_data.get('target_audience', {}),
            use_cases=template_data.get('use_cases', [])
        )
        
        self.db_session.add(template)
        self.db_session.commit()
        
        # Create parameter definitions
        await self._create_template_parameters(template.id, template_data['parameter_schema'])
        
        # Generate quality scores
        await self._calculate_template_quality_scores(template.id)
        
        logger.info(f"Created workflow template: {template.id}")
        return str(template.id)
    
    async def generate_ai_template(
        self,
        requirements: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Generate workflow template using AI
        
        Args:
            requirements: Template requirements and specifications
            user_id: User requesting template generation
            
        Returns:
            Generated template ID
        """
        # Use AI to generate template
        generated_template = await self.ai_generator.generate_template(requirements, user_id)
        
        # Create the template
        template_id = await self.create_template(generated_template, user_id)
        
        # Mark as AI-generated
        template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == template_id
        ).first()
        
        if template:
            template.ai_generated = True
            template.ai_optimization_score = generated_template.get('optimization_score', 0.0)
            self.db_session.commit()
        
        logger.info(f"Generated AI template: {template_id}")
        return template_id
    
    async def customize_template(
        self,
        template_id: str,
        customization_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Create customized version of existing template
        
        Args:
            template_id: Base template ID
            customization_data: Customization parameters
            user_id: User creating customization
            
        Returns:
            Customized template ID
        """
        # Get base template
        base_template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == template_id
        ).first()
        
        if not base_template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Apply customizations
        customized_definition = await self._apply_customizations(
            base_template.template_definition,
            customization_data
        )
        
        # Create new template
        customized_template_data = {
            'template_name': f"{base_template.template_name} (Customized)",
            'template_description': f"Customized version of {base_template.template_name}",
            'category': base_template.category,
            'complexity_level': base_template.complexity_level,
            'template_definition': customized_definition,
            'parameter_schema': base_template.parameter_schema,
            'supported_platforms': base_template.supported_platforms,
            'supported_content_types': base_template.supported_content_types,
            'is_public': False,  # Customized templates are private by default
            'tags': base_template.tags
        }
        
        customized_template_id = await self.create_template(customized_template_data, user_id)
        
        # Link to parent template
        customized_template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == customized_template_id
        ).first()
        
        if customized_template:
            customized_template.parent_template_id = base_template.id
            self.db_session.commit()
        
        # Track usage
        await self._track_template_usage(template_id, user_id, "customize", customization_data)
        
        logger.info(f"Created customized template: {customized_template_id} from {template_id}")
        return customized_template_id
    
    async def search_templates(
        self,
        search_criteria: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search workflow templates with advanced filtering
        
        Args:
            search_criteria: Search and filter criteria
            user_id: Optional user ID for personalization
            
        Returns:
            List of matching templates
        """
        query = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.is_active == True,
            WorkflowTemplateMarketplace.status == "active"
        )
        
        # Apply search filters
        if 'category' in search_criteria:
            query = query.filter(WorkflowTemplateMarketplace.category == search_criteria['category'])
        
        if 'complexity_level' in search_criteria:
            query = query.filter(WorkflowTemplateMarketplace.complexity_level == search_criteria['complexity_level'])
        
        if 'platforms' in search_criteria:
            for platform in search_criteria['platforms']:
                query = query.filter(WorkflowTemplateMarketplace.supported_platforms.contains([platform]))
        
        if 'content_types' in search_criteria:
            for content_type in search_criteria['content_types']:
                query = query.filter(WorkflowTemplateMarketplace.supported_content_types.contains([content_type]))
        
        if 'is_free' in search_criteria:
            query = query.filter(WorkflowTemplateMarketplace.is_free == search_criteria['is_free'])
        
        if 'min_rating' in search_criteria:
            query = query.filter(WorkflowTemplateMarketplace.rating_average >= search_criteria['min_rating'])
        
        if 'keywords' in search_criteria:
            keywords = search_criteria['keywords']
            if isinstance(keywords, str):
                keywords = [keywords]
            for keyword in keywords:
                query = query.filter(
                    func.array_to_string(WorkflowTemplateMarketplace.keywords, ' ').ilike(f'%{keyword}%')
                )
        
        # Apply sorting
        sort_by = search_criteria.get('sort_by', 'popularity')
        if sort_by == 'popularity':
            query = query.order_by(WorkflowTemplateMarketplace.popularity_score.desc())
        elif sort_by == 'rating':
            query = query.order_by(WorkflowTemplateMarketplace.rating_average.desc())
        elif sort_by == 'newest':
            query = query.order_by(WorkflowTemplateMarketplace.created_at.desc())
        elif sort_by == 'most_used':
            query = query.order_by(WorkflowTemplateMarketplace.usage_count.desc())
        
        # Apply pagination
        limit = search_criteria.get('limit', 20)
        offset = search_criteria.get('offset', 0)
        query = query.limit(limit).offset(offset)
        
        templates = query.all()
        
        # Convert to dictionary format
        results = []
        for template in templates:
            template_dict = {
                'template_id': str(template.id),
                'template_name': template.template_name,
                'description': template.template_description,
                'short_description': template.short_description,
                'category': template.category,
                'complexity_level': template.complexity_level,
                'rating_average': float(template.rating_average) if template.rating_average else 0.0,
                'rating_count': template.rating_count,
                'usage_count': template.usage_count,
                'is_free': template.is_free,
                'price': float(template.price) if template.price else 0.0,
                'creator_name': template.creator_name,
                'supported_platforms': template.supported_platforms,
                'supported_content_types': template.supported_content_types,
                'thumbnail_url': template.thumbnail_url,
                'tags': template.tags,
                'created_at': template.created_at.isoformat(),
                'estimated_setup_time': template.estimated_setup_time
            }
            
            # Add personalization if user provided
            if user_id:
                template_dict['personalization'] = await self._get_template_personalization(
                    template.id, user_id
                )
            
            results.append(template_dict)
        
        return results
    
    async def get_template_details(
        self,
        template_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed template information
        
        Args:
            template_id: Template ID
            user_id: Optional user ID for personalization
            
        Returns:
            Detailed template information
        """
        template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == template_id
        ).first()
        
        if not template:
            return {}
        
        # Get template parameters
        parameters = self.db_session.query(WorkflowTemplateParameter).filter(
            WorkflowTemplateParameter.template_id == template_id,
            WorkflowTemplateParameter.is_active == True
        ).order_by(WorkflowTemplateParameter.display_order).all()
        
        # Get recent reviews
        reviews = self.db_session.query(TemplateReview).filter(
            TemplateReview.template_id == template_id,
            TemplateReview.is_active == True
        ).order_by(TemplateReview.created_at.desc()).limit(10).all()
        
        # Get usage statistics
        usage_stats = await self._calculate_template_usage_stats(template_id)
        
        template_details = {
            'template_id': str(template.id),
            'template_name': template.template_name,
            'description': template.template_description,
            'category': template.category,
            'complexity_level': template.complexity_level,
            'version': template.version,
            'creator_name': template.creator_name,
            'template_definition': template.template_definition,
            'parameter_schema': template.parameter_schema,
            'supported_platforms': template.supported_platforms,
            'supported_content_types': template.supported_content_types,
            'required_integrations': template.required_integrations,
            'minimum_requirements': template.minimum_requirements,
            'is_free': template.is_free,
            'price': float(template.price) if template.price else 0.0,
            'license_type': template.license_type,
            'rating_average': float(template.rating_average) if template.rating_average else 0.0,
            'rating_count': template.rating_count,
            'usage_count': template.usage_count,
            'success_rate': float(template.success_rate) if template.success_rate else 0.0,
            'thumbnail_url': template.thumbnail_url,
            'documentation_url': template.documentation_url,
            'tags': template.tags,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat(),
            'estimated_setup_time': template.estimated_setup_time,
            'parameters': [
                {
                    'parameter_name': param.parameter_name,
                    'parameter_key': param.parameter_key,
                    'parameter_type': param.parameter_type,
                    'description': param.parameter_description,
                    'is_required': param.is_required,
                    'default_value': param.default_value,
                    'validation_rules': param.validation_rules,
                    'ui_component': param.ui_component,
                    'display_order': param.display_order
                }
                for param in parameters
            ],
            'reviews': [
                {
                    'rating': review.rating,
                    'review_title': review.review_title,
                    'review_text': review.review_text,
                    'reviewer_name': review.reviewer_user_id,  # Would get actual name
                    'created_at': review.created_at.isoformat(),
                    'verified_purchase': review.verified_purchase
                }
                for review in reviews
            ],
            'usage_statistics': usage_stats
        }
        
        # Add personalization if user provided
        if user_id:
            template_details['personalization'] = await self._get_template_personalization(
                template_id, user_id
            )
        
        return template_details
    
    async def _validate_template_definition(self, template_definition: Dict[str, Any]):
        """Validate template definition structure"""
        required_fields = ['name', 'tasks', 'triggers']
        
        for field in required_fields:
            if field not in template_definition:
                raise ValueError(f"Template definition missing required field: {field}")
        
        # Validate tasks structure
        if not isinstance(template_definition['tasks'], list):
            raise ValueError("Template tasks must be a list")
        
        for i, task in enumerate(template_definition['tasks']):
            if 'name' not in task or 'type' not in task:
                raise ValueError(f"Task {i} missing required fields: name, type")
    
    async def _generate_parameter_schema(self, template_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameter schema from template definition"""
        # This would analyze the template and extract parameterizable values
        # For now, return basic schema
        return {
            'parameters': [],
            'groups': [],
            'validation': {}
        }
    
    async def _create_template_parameters(self, template_id: str, parameter_schema: Dict[str, Any]):
        """Create parameter definitions for template"""
        parameters = parameter_schema.get('parameters', [])
        
        for i, param_def in enumerate(parameters):
            parameter = WorkflowTemplateParameter(
                template_id=template_id,
                parameter_name=param_def['name'],
                parameter_key=param_def['key'],
                parameter_type=param_def['type'],
                parameter_description=param_def.get('description', ''),
                is_required=param_def.get('required', False),
                default_value=param_def.get('default_value'),
                validation_rules=param_def.get('validation_rules', {}),
                display_order=i,
                ui_component=param_def.get('ui_component', 'input')
            )
            
            self.db_session.add(parameter)
        
        self.db_session.commit()
    
    async def _calculate_template_quality_scores(self, template_id: str):
        """Calculate quality scores for template"""
        # Implementation would analyze template quality
        template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == template_id
        ).first()
        
        if template:
            template.quality_score = 4.5
            template.security_score = 4.0
            template.performance_score = 4.2
            self.db_session.commit()
    
    async def _apply_customizations(
        self,
        base_definition: Dict[str, Any],
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply customizations to base template definition"""
        # Deep copy base definition
        import copy
        customized_definition = copy.deepcopy(base_definition)
        
        # Apply customizations
        for key, value in customizations.items():
            # This would intelligently merge customizations
            if key in customized_definition:
                customized_definition[key] = value
        
        return customized_definition
    
    async def _track_template_usage(
        self,
        template_id: str,
        user_id: str,
        usage_type: str,
        usage_data: Dict[str, Any]
    ):
        """Track template usage for analytics"""
        usage_record = TemplateUsageHistory(
            template_id=template_id,
            user_id=user_id,
            usage_type=usage_type,
            customization_data=usage_data,
            usage_successful=True,  # Would track actual success
            user_rating=None  # To be filled later
        )
        
        self.db_session.add(usage_record)
        
        # Update template usage count
        template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == template_id
        ).first()
        
        if template:
            template.usage_count += 1
            template.last_used_at = datetime.now(timezone.utc)
        
        self.db_session.commit()
    
    async def _get_template_personalization(
        self,
        template_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get personalized recommendations for template"""
        # Implementation would analyze user preferences and history
        return {
            'compatibility_score': 0.85,
            'recommended_customizations': [],
            'similar_templates': [],
            'estimated_setup_time': 15  # minutes
        }
    
    async def _calculate_template_usage_stats(self, template_id: str) -> Dict[str, Any]:
        """Calculate template usage statistics"""
        usage_records = self.db_session.query(TemplateUsageHistory).filter(
            TemplateUsageHistory.template_id == template_id
        ).all()
        
        if not usage_records:
            return {}
        
        successful_uses = sum(1 for record in usage_records if record.usage_successful)
        total_uses = len(usage_records)
        
        return {
            'total_uses': total_uses,
            'success_rate': successful_uses / total_uses if total_uses > 0 else 0,
            'average_setup_time': 15,  # Would calculate from actual data
            'most_common_customizations': [],
            'user_satisfaction': 4.2
        }


class AITemplateGenerator:
    """AI-powered template generation system"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def generate_template(
        self,
        requirements: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Generate workflow template using AI"""
        # AI would analyze requirements and generate optimized template
        # For now, return mock template
        return {
            'template_name': f"AI Generated Template for {requirements.get('purpose', 'Workflow')}",
            'template_description': "AI-generated workflow template optimized for your requirements",
            'category': requirements.get('category', 'content_creation'),
            'complexity_level': 'intermediate',
            'template_definition': {
                'name': 'AI Generated Workflow',
                'tasks': [
                    {
                        'name': 'Content Creation',
                        'type': 'content_processing',
                        'parameters': {}
                    }
                ],
                'triggers': [
                    {
                        'type': 'manual',
                        'conditions': {}
                    }
                ]
            },
            'parameter_schema': {
                'parameters': []
            },
            'optimization_score': 0.92,
            'supported_platforms': requirements.get('platforms', []),
            'supported_content_types': requirements.get('content_types', [])
        }


class ConfigurationManager:
    """Advanced configuration management system"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def create_configuration(
        self,
        config_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """Create new workflow configuration"""
        configuration = WorkflowConfiguration(
            configuration_name=config_data['configuration_name'],
            configuration_description=config_data.get('configuration_description', ''),
            user_id=user_id,
            scope=config_data['scope'],
            scope_id=config_data.get('scope_id'),
            configuration_data=config_data['configuration_data'],
            environment=config_data.get('environment', 'production'),
            priority=config_data.get('priority', 1),
            is_default=config_data.get('is_default', False),
            tags=config_data.get('tags', [])
        )
        
        self.db_session.add(configuration)
        self.db_session.commit()
        
        return str(configuration.id)
    
    async def get_configuration(
        self,
        scope: str,
        scope_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get configuration for specific scope"""
        config = self.db_session.query(WorkflowConfiguration).filter(
            WorkflowConfiguration.scope == scope,
            WorkflowConfiguration.scope_id == scope_id,
            WorkflowConfiguration.user_id == user_id,
            WorkflowConfiguration.is_active == True
        ).first()
        
        if config:
            return config.configuration_data
        
        return {}


class MarketplaceManager:
    """Template marketplace management system"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def publish_template(
        self,
        template_id: str,
        marketplace_data: Dict[str, Any]
    ) -> bool:
        """Publish template to marketplace"""
        template = self.db_session.query(WorkflowTemplateMarketplace).filter(
            WorkflowTemplateMarketplace.id == template_id
        ).first()
        
        if not template:
            return False
        
        # Update marketplace-specific fields
        template.is_public = True
        template.published_at = datetime.now(timezone.utc)
        template.approval_status = "pending"
        
        # Update pricing and licensing
        if 'price' in marketplace_data:
            template.price = marketplace_data['price']
            template.is_free = marketplace_data['price'] == 0
        
        if 'license_type' in marketplace_data:
            template.license_type = marketplace_data['license_type']
        
        self.db_session.commit()
        
        logger.info(f"Published template {template_id} to marketplace")
        return True
    
    async def submit_review(
        self,
        template_id: str,
        reviewer_user_id: str,
        review_data: Dict[str, Any]
    ) -> str:
        """Submit template review"""
        review = TemplateReview(
            template_id=template_id,
            reviewer_user_id=reviewer_user_id,
            rating=review_data['rating'],
            review_title=review_data.get('review_title'),
            review_text=review_data.get('review_text'),
            ease_of_use=review_data.get('ease_of_use'),
            documentation_quality=review_data.get('documentation_quality'),
            performance=review_data.get('performance'),
            value_for_money=review_data.get('value_for_money'),
            use_case=review_data.get('use_case'),
            experience_level=review_data.get('experience_level'),
            verified_purchase=review_data.get('verified_purchase', False)
        )
        
        self.db_session.add(review)
        self.db_session.commit()
        
        # Update template rating average
        await self._update_template_rating(template_id)
        
        logger.info(f"Submitted review for template {template_id}")
        return str(review.id)
    
    async def _update_template_rating(self, template_id: str):
        """Update template average rating"""
        reviews = self.db_session.query(TemplateReview).filter(
            TemplateReview.template_id == template_id,
            TemplateReview.is_active == True
        ).all()
        
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            
            template = self.db_session.query(WorkflowTemplateMarketplace).filter(
                WorkflowTemplateMarketplace.id == template_id
            ).first()
            
            if template:
                template.rating_average = avg_rating
                template.rating_count = len(reviews)
                self.db_session.commit()
