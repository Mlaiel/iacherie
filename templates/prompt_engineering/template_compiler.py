"""
🎯 Template Compiler - AI Prompt Template Compilation System
==========================================================

Enterprise-grade template compilation with variable substitution, validation,
and optimization for creator economy prompt templates.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - Backend Senior + IA Prompt Engineer
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import re
import ast
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import asyncpg
from jinja2 import Environment, Template, StrictUndefined, meta
from jinja2.exceptions import TemplateError, TemplateSyntaxError, UndefinedError
from pydantic import BaseModel, Field, validator
import yaml

from core.config import get_settings
from utils.exceptions import CompilationError, ValidationError
from .security_validator import SecurityValidator

logger = logging.getLogger(__name__)
settings = get_settings()


class TemplateFormat(Enum):
    """Template format types"""
    JINJA2 = "jinja2"
    MUSTACHE = "mustache"
    F_STRING = "f_string"
    SIMPLE_SUBSTITUTION = "simple_substitution"
    YAML_TEMPLATE = "yaml_template"
    JSON_TEMPLATE = "json_template"


class VariableType(Enum):
    """Variable data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    DATE = "date"
    URL = "url"
    EMAIL = "email"
    CREATOR_ID = "creator_id"
    CONTENT_TYPE = "content_type"


class ValidationLevel(Enum):
    """Template validation levels"""
    STRICT = "strict"
    NORMAL = "normal"
    PERMISSIVE = "permissive"
    CREATOR_ECONOMY = "creator_economy"


@dataclass
class VariableDefinition:
    """Template variable definition"""
    name: str
    type: VariableType
    description: str
    required: bool = True
    default_value: Optional[Any] = None
    validation_pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    creator_economy_context: bool = False
    sensitive: bool = False
    examples: List[str] = field(default_factory=list)


@dataclass
class TemplateMetadata:
    """Template compilation metadata"""
    template_id: str
    format: TemplateFormat
    variables: List[VariableDefinition]
    dependencies: List[str] = field(default_factory=list)
    creator_economy_features: Dict[str, bool] = field(default_factory=dict)
    compilation_time: float = 0.0
    cache_enabled: bool = True
    version: str = "1.0.0"
    author: str = "Fahed Mlaiel (mlaiel@live.de)"


@dataclass
class CompilationResult:
    """Template compilation result"""
    compiled_prompt: str
    metadata: TemplateMetadata
    variables_used: Set[str]
    warnings: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    security_validated: bool = False
    compilation_successful: bool = True
    error_message: Optional[str] = None


class TemplateCompilationRequest(BaseModel):
    """Template compilation request"""
    template_content: str = Field(..., min_length=1)
    variables: Dict[str, Any] = Field(default_factory=dict)
    template_format: TemplateFormat = TemplateFormat.JINJA2
    validation_level: ValidationLevel = ValidationLevel.NORMAL
    enable_caching: bool = True
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    optimization_enabled: bool = True
    security_validation: bool = True
    
    @validator('template_content')
    def validate_template_content(cls, v):
        """Validate template content"""
        if not v.strip():
            raise ValueError("Template content cannot be empty")
        if len(v) > 100000:  # 100KB limit
            raise ValueError("Template content too large")
        return v.strip()


class TemplateCompiler:
    """
    🎯 Enterprise Template Compilation System
    
    Advanced template compilation with:
    - Multi-format template support (Jinja2, Mustache, F-strings)
    - Intelligent variable validation and substitution
    - Creator economy context integration
    - Security validation and sanitization
    - Performance optimization and caching
    - Dependency tracking and management
    - Error handling and debugging support
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.jinja_env: Optional[Environment] = None
        self.security_validator = SecurityValidator()
        self.compiled_cache: Dict[str, Any] = {}
        self.variable_validators: Dict[VariableType, callable] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize template compiler"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=3,
                max_size=10
            )
            
            # Initialize Jinja2 environment
            self._setup_jinja_environment()
            
            # Setup variable validators
            self._setup_variable_validators()
            
            # Create database tables
            await self._create_tables()
            
            # Initialize security validator
            await self.security_validator.initialize()
            
            self._initialized = True
            logger.info("Template Compiler initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Template Compiler: {e}")
            raise CompilationError(f"Template Compiler initialization failed: {e}")
    
    def _setup_jinja_environment(self) -> None:
        """Setup Jinja2 environment with custom functions"""
        self.jinja_env = Environment(
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters and functions for creator economy
        self.jinja_env.filters['creator_format'] = self._creator_format_filter
        self.jinja_env.filters['content_type'] = self._content_type_filter
        self.jinja_env.filters['monetization'] = self._monetization_filter
        self.jinja_env.globals['creator_context'] = self._get_creator_context
        self.jinja_env.globals['platform_optimize'] = self._platform_optimize
    
    def _creator_format_filter(self, content: str, creator_type: str) -> str:
        """Filter content based on creator type"""
        if creator_type == "musician":
            return f"🎵 {content}"
        elif creator_type == "blogger":
            return f"📝 {content}"
        elif creator_type == "photographer":
            return f"📸 {content}"
        elif creator_type == "influencer":
            return f"⭐ {content}"
        return content
    
    def _content_type_filter(self, content: str, content_type: str) -> str:
        """Format content based on content type"""
        if content_type == "video":
            return f"[VIDEO] {content}"
        elif content_type == "audio":
            return f"[AUDIO] {content}"
        elif content_type == "image":
            return f"[IMAGE] {content}"
        elif content_type == "text":
            return f"[TEXT] {content}"
        return content
    
    def _monetization_filter(self, content: str, strategy: str) -> str:
        """Add monetization context to content"""
        strategies = {
            "sponsorship": "Consider sponsorship opportunities",
            "affiliate": "Include affiliate marketing potential",
            "subscription": "Optimize for subscription conversion",
            "merchandise": "Highlight merchandise opportunities"
        }
        
        if strategy in strategies:
            return f"{content}\n\n💰 {strategies[strategy]}"
        return content
    
    def _get_creator_context(self) -> Dict[str, Any]:
        """Get creator context for templates"""
        return {
            "platform": "iacherie",
            "features": ["ai_optimization", "multi_format", "monetization"],
            "support": "enterprise"
        }
    
    def _platform_optimize(self, content: str, platform: str) -> str:
        """Optimize content for specific platforms"""
        optimizations = {
            "instagram": "Add hashtags and visual focus",
            "youtube": "Optimize for video format and engagement",
            "tiktok": "Short-form, trending content",
            "linkedin": "Professional tone and networking focus",
            "twitter": "Concise, shareable format"
        }
        
        if platform in optimizations:
            return f"{content}\n\n📱 {optimizations[platform]}"
        return content
    
    def _setup_variable_validators(self) -> None:
        """Setup variable type validators"""
        self.variable_validators = {
            VariableType.STRING: self._validate_string,
            VariableType.INTEGER: self._validate_integer,
            VariableType.FLOAT: self._validate_float,
            VariableType.BOOLEAN: self._validate_boolean,
            VariableType.LIST: self._validate_list,
            VariableType.DICT: self._validate_dict,
            VariableType.DATE: self._validate_date,
            VariableType.URL: self._validate_url,
            VariableType.EMAIL: self._validate_email,
            VariableType.CREATOR_ID: self._validate_creator_id,
            VariableType.CONTENT_TYPE: self._validate_content_type
        }
    
    def _validate_string(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate string variable"""
        if not isinstance(value, str):
            return False, f"Expected string, got {type(value).__name__}"
        
        if definition.validation_pattern:
            if not re.match(definition.validation_pattern, value):
                return False, f"Value does not match pattern: {definition.validation_pattern}"
        
        if definition.allowed_values and value not in definition.allowed_values:
            return False, f"Value must be one of: {definition.allowed_values}"
        
        return True, ""
    
    def _validate_integer(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate integer variable"""
        try:
            int(value)
            return True, ""
        except (ValueError, TypeError):
            return False, f"Expected integer, got {type(value).__name__}"
    
    def _validate_float(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate float variable"""
        try:
            float(value)
            return True, ""
        except (ValueError, TypeError):
            return False, f"Expected float, got {type(value).__name__}"
    
    def _validate_boolean(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate boolean variable"""
        if isinstance(value, bool):
            return True, ""
        if isinstance(value, str) and value.lower() in ['true', 'false', '1', '0']:
            return True, ""
        return False, f"Expected boolean, got {type(value).__name__}"
    
    def _validate_list(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate list variable"""
        if not isinstance(value, list):
            return False, f"Expected list, got {type(value).__name__}"
        return True, ""
    
    def _validate_dict(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate dictionary variable"""
        if not isinstance(value, dict):
            return False, f"Expected dict, got {type(value).__name__}"
        return True, ""
    
    def _validate_date(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate date variable"""
        if isinstance(value, datetime):
            return True, ""
        
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return True, ""
            except ValueError:
                return False, "Invalid date format. Use ISO format (YYYY-MM-DD)"
        
        return False, f"Expected date, got {type(value).__name__}"
    
    def _validate_url(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate URL variable"""
        if not isinstance(value, str):
            return False, f"Expected string URL, got {type(value).__name__}"
        
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        if re.match(url_pattern, value):
            return True, ""
        
        return False, "Invalid URL format"
    
    def _validate_email(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate email variable"""
        if not isinstance(value, str):
            return False, f"Expected string email, got {type(value).__name__}"
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            return True, ""
        
        return False, "Invalid email format"
    
    def _validate_creator_id(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate creator ID variable"""
        if not isinstance(value, str):
            return False, f"Expected string creator ID, got {type(value).__name__}"
        
        # Creator ID should be alphanumeric with possible dashes/underscores
        if re.match(r'^[a-zA-Z0-9_-]+$', value) and len(value) >= 3:
            return True, ""
        
        return False, "Creator ID must be alphanumeric (3+ characters)"
    
    def _validate_content_type(self, value: Any, definition: VariableDefinition) -> Tuple[bool, str]:
        """Validate content type variable"""
        valid_types = ['text', 'image', 'video', 'audio', 'mixed', 'blog', 'social', 'podcast']
        
        if not isinstance(value, str):
            return False, f"Expected string content type, got {type(value).__name__}"
        
        if value.lower() in valid_types:
            return True, ""
        
        return False, f"Content type must be one of: {valid_types}"
    
    async def _create_tables(self) -> None:
        """Create compilation-related database tables"""
        create_compilation_history_table = """
        CREATE TABLE IF NOT EXISTS compilation_history (
            id SERIAL PRIMARY KEY,
            compilation_id VARCHAR(255) UNIQUE NOT NULL,
            template_id VARCHAR(255),
            template_content_hash VARCHAR(64),
            variables_hash VARCHAR(64),
            compiled_prompt_hash VARCHAR(64),
            compilation_time_ms INTEGER,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            warnings JSONB,
            variables_used JSONB,
            creator_context JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_template_cache_table = """
        CREATE TABLE IF NOT EXISTS template_cache (
            id SERIAL PRIMARY KEY,
            cache_key VARCHAR(255) UNIQUE NOT NULL,
            template_content TEXT NOT NULL,
            compiled_result JSONB NOT NULL,
            variables_schema JSONB,
            hit_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            INDEX (cache_key),
            INDEX (expires_at)
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_compilation_history_table)
            await conn.execute(create_template_cache_table)
    
    async def compile_template(self, request: TemplateCompilationRequest) -> CompilationResult:
        """
        Compile template with variables and validation
        
        Args:
            request: Template compilation request
            
        Returns:
            Compilation result with compiled prompt
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(request)
            
            # Check cache if enabled
            if request.enable_caching:
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    logger.debug(f"Template compilation cache hit: {cache_key}")
                    return cached_result
            
            # Extract template variables
            detected_variables = await self._extract_template_variables(
                request.template_content, request.template_format
            )
            
            # Validate provided variables
            validation_errors = await self._validate_variables(
                request.variables, detected_variables, request.validation_level
            )
            
            if validation_errors and request.validation_level == ValidationLevel.STRICT:
                raise ValidationError(f"Variable validation failed: {', '.join(validation_errors)}")
            
            # Compile template based on format
            compiled_prompt, warnings = await self._compile_by_format(
                request.template_content,
                request.variables,
                request.template_format,
                request.creator_context
            )
            
            # Security validation
            security_validated = False
            if request.security_validation:
                security_result = await self.security_validator.validate_prompt(compiled_prompt)
                security_validated = security_result.is_safe
                
                if not security_validated and request.validation_level == ValidationLevel.STRICT:
                    raise ValidationError("Compiled template failed security validation")
                
                if security_result.issues:
                    warnings.extend([issue.description for issue in security_result.issues])
            
            # Generate optimization suggestions
            optimization_suggestions = []
            if request.optimization_enabled:
                optimization_suggestions = await self._generate_optimization_suggestions(
                    compiled_prompt, request.creator_context
                )
            
            # Create metadata
            metadata = TemplateMetadata(
                template_id=cache_key[:16],
                format=request.template_format,
                variables=[
                    VariableDefinition(
                        name=var_name,
                        type=VariableType.STRING,  # Default type
                        description=f"Variable: {var_name}",
                        required=True
                    ) for var_name in detected_variables
                ],
                compilation_time=(datetime.utcnow() - start_time).total_seconds() * 1000,
                creator_economy_features=self._extract_creator_features(request.creator_context)
            )
            
            result = CompilationResult(
                compiled_prompt=compiled_prompt,
                metadata=metadata,
                variables_used=detected_variables,
                warnings=warnings,
                optimization_suggestions=optimization_suggestions,
                security_validated=security_validated,
                compilation_successful=True
            )
            
            # Cache result if enabled
            if request.enable_caching:
                await self._cache_result(cache_key, result)
            
            # Record compilation history
            await self._record_compilation(request, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Template compilation failed: {e}")
            
            # Return error result
            return CompilationResult(
                compiled_prompt="",
                metadata=TemplateMetadata(
                    template_id="error",
                    format=request.template_format,
                    variables=[]
                ),
                variables_used=set(),
                compilation_successful=False,
                error_message=str(e)
            )
    
    async def _extract_template_variables(self, template_content: str, format: TemplateFormat) -> Set[str]:
        """Extract variables from template content"""
        variables = set()
        
        try:
            if format == TemplateFormat.JINJA2:
                ast_tree = self.jinja_env.parse(template_content)
                variables = meta.find_undeclared_variables(ast_tree)
            
            elif format == TemplateFormat.MUSTACHE:
                # Simple mustache pattern matching
                mustache_pattern = r'\{\{([^}]+)\}\}'
                matches = re.findall(mustache_pattern, template_content)
                variables = set(match.strip() for match in matches)
            
            elif format == TemplateFormat.F_STRING:
                # Extract f-string variables
                fstring_pattern = r'\{([^}]+)\}'
                matches = re.findall(fstring_pattern, template_content)
                variables = set(match.strip() for match in matches if not match.strip().startswith('!'))
            
            elif format == TemplateFormat.SIMPLE_SUBSTITUTION:
                # Simple ${variable} pattern
                simple_pattern = r'\$\{([^}]+)\}'
                matches = re.findall(simple_pattern, template_content)
                variables = set(match.strip() for match in matches)
            
            return variables
        
        except Exception as e:
            logger.warning(f"Variable extraction failed: {e}")
            return set()
    
    async def _validate_variables(
        self,
        provided_vars: Dict[str, Any],
        required_vars: Set[str],
        validation_level: ValidationLevel
    ) -> List[str]:
        """Validate provided variables against requirements"""
        errors = []
        
        # Check for missing required variables
        missing_vars = required_vars - set(provided_vars.keys())
        if missing_vars:
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.NORMAL]:
                errors.extend([f"Missing required variable: {var}" for var in missing_vars])
        
        # Check for extra variables (only in strict mode)
        if validation_level == ValidationLevel.STRICT:
            extra_vars = set(provided_vars.keys()) - required_vars
            if extra_vars:
                errors.extend([f"Unexpected variable: {var}" for var in extra_vars])
        
        # Type validation would go here if we had variable definitions
        # For now, basic validation
        for var_name, value in provided_vars.items():
            if value is None and validation_level == ValidationLevel.STRICT:
                errors.append(f"Variable '{var_name}' cannot be None")
        
        return errors
    
    async def _compile_by_format(
        self,
        template_content: str,
        variables: Dict[str, Any],
        format: TemplateFormat,
        creator_context: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Compile template based on format"""
        warnings = []
        
        try:
            # Add creator context to variables
            enhanced_variables = {**variables, **creator_context}
            
            if format == TemplateFormat.JINJA2:
                template = self.jinja_env.from_string(template_content)
                compiled = template.render(**enhanced_variables)
            
            elif format == TemplateFormat.MUSTACHE:
                # Simple mustache implementation
                compiled = template_content
                for var_name, value in enhanced_variables.items():
                    pattern = f"{{{{ {var_name} }}}}"
                    compiled = compiled.replace(pattern, str(value))
                    pattern = f"{{{{{var_name}}}}}"  # Without spaces
                    compiled = compiled.replace(pattern, str(value))
            
            elif format == TemplateFormat.F_STRING:
                # Convert to f-string and evaluate
                try:
                    compiled = template_content.format(**enhanced_variables)
                except KeyError as e:
                    warnings.append(f"Missing variable for f-string: {e}")
                    compiled = template_content
            
            elif format == TemplateFormat.SIMPLE_SUBSTITUTION:
                compiled = template_content
                for var_name, value in enhanced_variables.items():
                    pattern = f"${{{var_name}}}"
                    compiled = compiled.replace(pattern, str(value))
            
            elif format == TemplateFormat.YAML_TEMPLATE:
                # YAML template processing
                try:
                    yaml_data = yaml.safe_load(template_content)
                    processed_data = self._process_yaml_variables(yaml_data, enhanced_variables)
                    compiled = yaml.dump(processed_data, default_flow_style=False)
                except yaml.YAMLError as e:
                    warnings.append(f"YAML processing error: {e}")
                    compiled = template_content
            
            elif format == TemplateFormat.JSON_TEMPLATE:
                # JSON template processing
                try:
                    json_data = json.loads(template_content)
                    processed_data = self._process_json_variables(json_data, enhanced_variables)
                    compiled = json.dumps(processed_data, indent=2)
                except json.JSONDecodeError as e:
                    warnings.append(f"JSON processing error: {e}")
                    compiled = template_content
            
            else:
                compiled = template_content
                warnings.append(f"Unsupported template format: {format}")
            
            return compiled, warnings
        
        except Exception as e:
            logger.error(f"Template compilation failed: {e}")
            warnings.append(f"Compilation error: {e}")
            return template_content, warnings
    
    def _process_yaml_variables(self, data: Any, variables: Dict[str, Any]) -> Any:
        """Process variables in YAML data structure"""
        if isinstance(data, str):
            # Replace variables in string values
            for var_name, value in variables.items():
                pattern = f"${{{var_name}}}"
                data = data.replace(pattern, str(value))
            return data
        elif isinstance(data, dict):
            return {key: self._process_yaml_variables(value, variables) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._process_yaml_variables(item, variables) for item in data]
        else:
            return data
    
    def _process_json_variables(self, data: Any, variables: Dict[str, Any]) -> Any:
        """Process variables in JSON data structure"""
        return self._process_yaml_variables(data, variables)  # Same logic
    
    async def _generate_optimization_suggestions(
        self,
        compiled_prompt: str,
        creator_context: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization suggestions for compiled prompt"""
        suggestions = []
        
        # Length optimization
        if len(compiled_prompt) > 5000:
            suggestions.append("Consider breaking down long prompts for better performance")
        
        # Creator economy specific suggestions
        creator_type = creator_context.get('creator_type')
        if creator_type:
            if creator_type == "musician" and "music" not in compiled_prompt.lower():
                suggestions.append("Consider adding music-specific context for better results")
            elif creator_type == "blogger" and "blog" not in compiled_prompt.lower():
                suggestions.append("Add blogging context for optimized content generation")
        
        # Platform optimization
        platform = creator_context.get('target_platform')
        if platform:
            suggestions.append(f"Optimize prompt for {platform} platform characteristics")
        
        # Monetization suggestions
        if creator_context.get('monetization_focus') and "monetization" not in compiled_prompt.lower():
            suggestions.append("Include monetization context for revenue-focused content")
        
        return suggestions
    
    def _extract_creator_features(self, creator_context: Dict[str, Any]) -> Dict[str, bool]:
        """Extract creator economy features from context"""
        return {
            "multi_format_support": bool(creator_context.get('content_types')),
            "monetization_focus": bool(creator_context.get('monetization_focus')),
            "collaboration_enabled": bool(creator_context.get('collaboration')),
            "analytics_integration": bool(creator_context.get('analytics')),
            "seo_optimization": bool(creator_context.get('seo_focus'))
        }
    
    def _generate_cache_key(self, request: TemplateCompilationRequest) -> str:
        """Generate cache key for template compilation"""
        import hashlib
        
        key_data = {
            "template": request.template_content,
            "variables": request.variables,
            "format": request.template_format.value,
            "validation": request.validation_level.value
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    async def _get_cached_result(self, cache_key: str) -> Optional[CompilationResult]:
        """Get cached compilation result"""
        try:
            # Check Redis cache first
            cached_data = await self.redis_client.get(f"template_compile:{cache_key}")
            if cached_data:
                result_data = json.loads(cached_data)
                return self._deserialize_compilation_result(result_data)
            
            # Check database cache
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT compiled_result FROM template_cache 
                    WHERE cache_key = $1 AND (expires_at IS NULL OR expires_at > NOW())
                """, cache_key)
                
                if row:
                    await conn.execute("""
                        UPDATE template_cache SET hit_count = hit_count + 1, 
                        last_accessed = NOW() WHERE cache_key = $1
                    """, cache_key)
                    
                    return self._deserialize_compilation_result(row['compiled_result'])
            
            return None
        
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result: CompilationResult) -> None:
        """Cache compilation result"""
        try:
            result_data = self._serialize_compilation_result(result)
            
            # Cache in Redis (short-term)
            await self.redis_client.setex(
                f"template_compile:{cache_key}",
                3600,  # 1 hour
                json.dumps(result_data)
            )
            
            # Cache in database (long-term)
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO template_cache 
                    (cache_key, template_content, compiled_result, expires_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (cache_key) DO UPDATE SET
                    compiled_result = EXCLUDED.compiled_result,
                    expires_at = EXCLUDED.expires_at,
                    last_accessed = NOW()
                """, cache_key, result.metadata.template_id, json.dumps(result_data), expires_at)
        
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def _serialize_compilation_result(self, result: CompilationResult) -> Dict[str, Any]:
        """Serialize compilation result for caching"""
        return {
            "compiled_prompt": result.compiled_prompt,
            "variables_used": list(result.variables_used),
            "warnings": result.warnings,
            "optimization_suggestions": result.optimization_suggestions,
            "security_validated": result.security_validated,
            "compilation_successful": result.compilation_successful,
            "error_message": result.error_message,
            "metadata": {
                "template_id": result.metadata.template_id,
                "format": result.metadata.format.value,
                "compilation_time": result.metadata.compilation_time,
                "version": result.metadata.version
            }
        }
    
    def _deserialize_compilation_result(self, data: Dict[str, Any]) -> CompilationResult:
        """Deserialize compilation result from cache"""
        metadata = TemplateMetadata(
            template_id=data["metadata"]["template_id"],
            format=TemplateFormat(data["metadata"]["format"]),
            variables=[],  # Not cached for simplicity
            compilation_time=data["metadata"]["compilation_time"],
            version=data["metadata"]["version"]
        )
        
        return CompilationResult(
            compiled_prompt=data["compiled_prompt"],
            metadata=metadata,
            variables_used=set(data["variables_used"]),
            warnings=data["warnings"],
            optimization_suggestions=data["optimization_suggestions"],
            security_validated=data["security_validated"],
            compilation_successful=data["compilation_successful"],
            error_message=data["error_message"]
        )
    
    async def _record_compilation(self, request: TemplateCompilationRequest, result: CompilationResult) -> None:
        """Record compilation in history"""
        try:
            import hashlib
            
            compilation_id = f"comp_{int(datetime.utcnow().timestamp())}"
            template_hash = hashlib.sha256(request.template_content.encode()).hexdigest()
            variables_hash = hashlib.sha256(json.dumps(request.variables, sort_keys=True).encode()).hexdigest()
            compiled_hash = hashlib.sha256(result.compiled_prompt.encode()).hexdigest()
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO compilation_history 
                    (compilation_id, template_content_hash, variables_hash, compiled_prompt_hash,
                     compilation_time_ms, success, error_message, warnings, variables_used, creator_context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, compilation_id, template_hash, variables_hash, compiled_hash,
                    int(result.metadata.compilation_time), result.compilation_successful,
                    result.error_message, json.dumps(result.warnings),
                    json.dumps(list(result.variables_used)), json.dumps(request.creator_context))
        
        except Exception as e:
            logger.warning(f"Failed to record compilation history: {e}")
    
    async def get_compilation_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get compilation statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_compilations,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful,
                        COUNT(CASE WHEN success = false THEN 1 END) as failed,
                        AVG(compilation_time_ms) as avg_time_ms,
                        MAX(compilation_time_ms) as max_time_ms
                    FROM compilation_history 
                    WHERE created_at >= $1
                """, cutoff_time)
                
                cache_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as cached_templates,
                        SUM(hit_count) as total_hits,
                        AVG(hit_count) as avg_hits_per_template
                    FROM template_cache
                    WHERE last_accessed >= $1
                """, cutoff_time)
                
                return {
                    "compilation_stats": dict(row) if row else {},
                    "cache_stats": dict(cache_stats) if cache_stats else {},
                    "time_period_hours": hours
                }
        
        except Exception as e:
            logger.error(f"Failed to get compilation stats: {e}")
            return {}
    
    async def cleanup_cache(self, max_age_days: int = 30) -> None:
        """Cleanup old cached templates"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            
            async with self.db_pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM template_cache 
                    WHERE last_accessed < $1 OR expires_at < NOW()
                """, cutoff_date)
                
                # Also cleanup compilation history
                await conn.execute("""
                    DELETE FROM compilation_history 
                    WHERE created_at < $1
                """, cutoff_date)
            
            logger.info(f"Cleaned up template cache (older than {max_age_days} days)")
        
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup template compiler resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("Template Compiler cleanup completed")
        
        except Exception as e:
            logger.error(f"Template Compiler cleanup failed: {e}")


# Global template compiler instance
template_compiler = TemplateCompiler()