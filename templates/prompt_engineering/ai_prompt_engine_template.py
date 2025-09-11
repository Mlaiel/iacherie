"""{{prompt_name}} AI Prompt Engineering Template for Ainflue Platform
{{prompt_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, validator
import tiktoken

from core.config import get_settings
from utils.exceptions import PromptError, ValidationError
from monitoring.prompt_metrics import PromptMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class PromptType(Enum):
    """Types of AI prompts"""
    SYSTEM = "system"
    USER = "user" 
    ASSISTANT = "assistant"
    FUNCTION = "function"
    INSTRUCTION = "instruction"
    EXAMPLE = "example"
    TEMPLATE = "template"


class ModelProvider(Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class PromptCategory(Enum):
    """Prompt categories"""
    CONTENT_GENERATION = "content_generation"
    TEXT_ANALYSIS = "text_analysis"
    CONVERSATION = "conversation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"


@dataclass
class PromptVariable:
    """Prompt template variable"""
    name: str
    type: str = "string"
    description: str = ""
    required: bool = True
    default_value: Any = None
    validation_pattern: Optional[str] = None
    examples: List[str] = field(default_factory=list)


class PromptTemplate(BaseModel):
    """AI prompt template"""
    id: str = Field(..., description="Unique prompt template ID")
    name: str = Field(..., description="Prompt template name")
    description: str = Field(..., description="Template description")
    category: PromptCategory = Field(..., description="Prompt category")
    type: PromptType = Field(default=PromptType.USER, description="Prompt type")
    template: str = Field(..., description="Prompt template text with variables")
    variables: List[PromptVariable] = Field(default_factory=list, description="Template variables")
    provider: Optional[ModelProvider] = Field(default=None, description="Preferred AI provider")
    model: Optional[str] = Field(default=None, description="Specific model name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    examples: List[Dict[str, str]] = Field(default_factory=list, description="Usage examples")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    version: str = Field(default="1.0.0", description="Template version")
    author: Optional[str] = Field(default=None, description="Template author")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('template')
    def validate_template(cls, v):
        if not v or not v.strip():
            raise ValueError('Template cannot be empty')
        return v.strip()


class PromptExecution(BaseModel):
    """Prompt execution request"""
    template_id: str = Field(..., description="Template ID to execute")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Variable values")
    override_parameters: Optional[Dict[str, Any]] = Field(default=None, description="Override model parameters")
    override_model: Optional[str] = Field(default=None, description="Override model")
    override_provider: Optional[ModelProvider] = Field(default=None, description="Override provider")
    context: Optional[List[Dict[str, str]]] = Field(default=None, description="Conversation context")
    user_id: Optional[str] = Field(default=None, description="User ID for tracking")
    session_id: Optional[str] = Field(default=None, description="Session ID for tracking")


class PromptResult(BaseModel):
    """Prompt execution result"""
    execution_id: str = Field(..., description="Execution ID")
    template_id: str = Field(..., description="Template ID used")
    success: bool = Field(..., description="Execution success status")
    prompt: Optional[str] = Field(default=None, description="Final rendered prompt")
    response: Optional[str] = Field(default=None, description="AI model response")
    model_used: Optional[str] = Field(default=None, description="Model used")
    provider_used: Optional[str] = Field(default=None, description="Provider used")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    cost: Optional[float] = Field(default=None, description="Execution cost")
    quality_score: Optional[float] = Field(default=None, description="Response quality score")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{prompt_name}}PromptEngine:
    """{{prompt_description}}
    
    Comprehensive prompt engineering system providing:
    - Dynamic prompt template management
    - Variable substitution and validation
    - Multi-provider AI model integration
    - Prompt optimization and A/B testing
    - Token counting and cost estimation
    - Response quality assessment
    - Prompt versioning and rollback
    - Context-aware conversation handling
    - Batch prompt processing
    - Performance analytics and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_collector = PromptMetricsCollector()
        
        # Template storage
        self.templates: Dict[str, PromptTemplate] = {}
        self.template_versions: Dict[str, List[PromptTemplate]] = {}
        
        # Model configurations
        self.model_configs = {
            ModelProvider.OPENAI: {
                "default_model": "gpt-3.5-turbo",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "max_tokens": 4096,
                "default_params": {
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "top_p": 1.0,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                }
            },
            ModelProvider.ANTHROPIC: {
                "default_model": "claude-3-sonnet",
                "models": ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"],
                "max_tokens": 200000,
                "default_params": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
        }
        
        # Token encoders for different models
        self.encoders = {}
        try:
            self.encoders["gpt-3.5-turbo"] = tiktoken.encoding_for_model("gpt-3.5-turbo")
            self.encoders["gpt-4"] = tiktoken.encoding_for_model("gpt-4")
        except Exception as e:
            logger.warning(f"Failed to initialize token encoders: {e}")
    
    async def create_template(self, template_data: Dict[str, Any]) -> PromptTemplate:
        """Create new prompt template"""
        try:
            # Validate template data
            template = PromptTemplate(**template_data)
            
            # Extract variables from template
            template.variables = self._extract_template_variables(template.template)
            
            # Validate template syntax
            await self._validate_template_syntax(template)
            
            # Store template
            self.templates[template.id] = template
            
            # Store version
            if template.id not in self.template_versions:
                self.template_versions[template.id] = []
            self.template_versions[template.id].append(template)
            
            logger.info(f"Created prompt template: {template.id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create template: {str(e)}")
            raise PromptError(f"Template creation failed: {str(e)}")
    
    async def execute_prompt(self, execution: PromptExecution) -> PromptResult:
        """Execute prompt template with variables"""
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        try:
            # Get template
            template = self.templates.get(execution.template_id)
            if not template:
                raise PromptError(f"Template not found: {execution.template_id}")
            
            # Validate variables
            await self._validate_variables(template, execution.variables)
            
            # Render prompt
            rendered_prompt = await self._render_template(template, execution.variables)
            
            # Count tokens
            token_count = self._count_tokens(rendered_prompt, template.model or "gpt-3.5-turbo")
            
            # Determine provider and model
            provider = execution.override_provider or template.provider or ModelProvider.OPENAI
            model = execution.override_model or template.model or self.model_configs[provider]["default_model"]
            
            # Prepare model parameters
            params = self.model_configs[provider]["default_params"].copy()
            params.update(template.parameters)
            if execution.override_parameters:
                params.update(execution.override_parameters)
            
            # Execute AI model
            response = await self._call_ai_model(
                provider=provider,
                model=model,
                prompt=rendered_prompt,
                context=execution.context,
                parameters=params
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate cost (simplified)
            cost = self._calculate_cost(provider, model, token_count)
            
            # Assess quality
            quality_score = await self._assess_response_quality(rendered_prompt, response)
            
            # Record metrics
            await self.metrics_collector.record_execution_metrics(
                template_id=execution.template_id,
                provider=provider.value,
                model=model,
                tokens_used=token_count,
                execution_time=execution_time,
                success=True
            )
            
            result = PromptResult(
                execution_id=execution_id,
                template_id=execution.template_id,
                success=True,
                prompt=rendered_prompt,
                response=response,
                model_used=model,
                provider_used=provider.value,
                tokens_used=token_count,
                execution_time=execution_time,
                cost=cost,
                quality_score=quality_score
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Prompt execution failed: {str(e)}")
            await self.metrics_collector.record_execution_metrics(
                template_id=execution.template_id,
                provider="unknown",
                model="unknown",
                tokens_used=0,
                execution_time=0,
                success=False
            )
            
            return PromptResult(
                execution_id=execution_id,
                template_id=execution.template_id,
                success=False,
                error_message=str(e)
            )
    
    async def optimize_prompt(self, template_id: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize prompt template using test cases"""
        try:
            template = self.templates.get(template_id)
            if not template:
                raise PromptError(f"Template not found: {template_id}")
            
            results = []
            
            # Test current template
            for test_case in test_cases:
                execution = PromptExecution(
                    template_id=template_id,
                    variables=test_case.get("variables", {}),
                    context=test_case.get("context")
                )
                
                result = await self.execute_prompt(execution)
                
                # Score against expected output if provided
                expected = test_case.get("expected_output")
                if expected:
                    similarity_score = await self._calculate_similarity(result.response, expected)
                    result.quality_score = similarity_score
                
                results.append(result)
            
            # Calculate optimization metrics
            avg_quality = sum(r.quality_score or 0 for r in results) / len(results)
            avg_tokens = sum(r.tokens_used or 0 for r in results) / len(results)
            avg_time = sum(r.execution_time or 0 for r in results) / len(results)
            total_cost = sum(r.cost or 0 for r in results)
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(template, results)
            
            return {
                "template_id": template_id,
                "test_results": [r.dict() for r in results],
                "metrics": {
                    "average_quality_score": avg_quality,
                    "average_tokens_used": avg_tokens,
                    "average_execution_time": avg_time,
                    "total_cost": total_cost
                },
                "optimization_suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Prompt optimization failed: {str(e)}")
            raise PromptError(f"Optimization failed: {str(e)}")
    
    async def batch_execute(self, executions: List[PromptExecution]) -> List[PromptResult]:
        """Execute multiple prompts in batch"""
        results = []
        
        for execution in executions:
            try:
                result = await self.execute_prompt(execution)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch execution failed for template {execution.template_id}: {str(e)}")
                results.append(PromptResult(
                    execution_id=f"batch_{datetime.utcnow().timestamp()}",
                    template_id=execution.template_id,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def _extract_template_variables(self, template: str) -> List[PromptVariable]:
        """Extract variables from template text"""
        # Find variables in {{variable}} format
        variable_pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(variable_pattern, template)
        
        variables = []
        for var_name in set(matches):
            variables.append(PromptVariable(
                name=var_name,
                type="string",
                description=f"Variable: {var_name}",
                required=True
            ))
        
        return variables
    
    async def _validate_template_syntax(self, template: PromptTemplate):
        """Validate template syntax"""
        try:
            # Try to render with dummy variables
            dummy_vars = {var.name: "test_value" for var in template.variables}
            await self._render_template(template, dummy_vars)
        except Exception as e:
            raise ValidationError(f"Template syntax error: {str(e)}")
    
    async def _validate_variables(self, template: PromptTemplate, variables: Dict[str, Any]):
        """Validate provided variables against template requirements"""
        for var in template.variables:
            if var.required and var.name not in variables:
                raise ValidationError(f"Required variable missing: {var.name}")
            
            if var.name in variables and var.validation_pattern:
                value = str(variables[var.name])
                if not re.match(var.validation_pattern, value):
                    raise ValidationError(f"Variable {var.name} does not match pattern: {var.validation_pattern}")
    
    async def _render_template(self, template: PromptTemplate, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        rendered = template.template
        
        for var_name, value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        # Handle default values for missing variables
        for var in template.variables:
            if var.name not in variables and var.default_value is not None:
                placeholder = f"{{{{{var.name}}}}}"
                rendered = rendered.replace(placeholder, str(var.default_value))
        
        return rendered
    
    def _count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for specific model"""
        encoder = self.encoders.get(model)
        if encoder:
            return len(encoder.encode(text))
        else:
            # Fallback estimation: ~4 characters per token
            return len(text) // 4
    
    async def _call_ai_model(
        self,
        provider: ModelProvider,
        model: str,
        prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        parameters: Dict[str, Any] = None
    ) -> str:
        """Call AI model API"""
        # This would integrate with actual AI providers
        # For now, return a mock response
        
        logger.info(f"Calling {provider.value} model {model}")
        
        # Mock response based on prompt content
        if "summarize" in prompt.lower():
            return "This is a mock summary of the provided content."
        elif "translate" in prompt.lower():
            return "This is a mock translation of the text."
        elif "analyze" in prompt.lower():
            return "This is a mock analysis of the provided data."
        else:
            return "This is a mock AI response to your prompt."
    
    def _calculate_cost(self, provider: ModelProvider, model: str, tokens: int) -> float:
        """Calculate execution cost"""
        # Simplified cost calculation
        cost_per_1k_tokens = {
            (ModelProvider.OPENAI, "gpt-3.5-turbo"): 0.002,
            (ModelProvider.OPENAI, "gpt-4"): 0.03,
            (ModelProvider.ANTHROPIC, "claude-3-sonnet"): 0.003
        }
        
        rate = cost_per_1k_tokens.get((provider, model), 0.002)
        return (tokens / 1000) * rate
    
    async def _assess_response_quality(self, prompt: str, response: str) -> float:
        """Assess response quality"""
        # Simplified quality assessment
        quality_score = 0.8  # Base score
        
        # Check response length
        if len(response) < 10:
            quality_score -= 0.3
        elif len(response) > 1000:
            quality_score += 0.1
        
        # Check for common quality indicators
        if response.strip():
            quality_score += 0.1
        
        if not response.lower().startswith("i'm sorry") and not response.lower().startswith("i cannot"):
            quality_score += 0.1
        
        return min(1.0, max(0.0, quality_score))
    
    async def _calculate_similarity(self, response: str, expected: str) -> float:
        """Calculate similarity between response and expected output"""
        # Simplified similarity calculation using character overlap
        response_lower = response.lower()
        expected_lower = expected.lower()
        
        # Calculate Jaccard similarity
        response_words = set(response_lower.split())
        expected_words = set(expected_lower.split())
        
        intersection = len(response_words & expected_words)
        union = len(response_words | expected_words)
        
        return intersection / union if union > 0 else 0.0
    
    async def _generate_optimization_suggestions(
        self,
        template: PromptTemplate,
        results: List[PromptResult]
    ) -> List[str]:
        """Generate optimization suggestions based on test results"""
        suggestions = []
        
        avg_quality = sum(r.quality_score or 0 for r in results) / len(results)
        avg_tokens = sum(r.tokens_used or 0 for r in results) / len(results)
        
        if avg_quality < 0.7:
            suggestions.append("Consider adding more specific instructions or examples to improve response quality")
        
        if avg_tokens > 1000:
            suggestions.append("Consider shortening the prompt to reduce token usage and cost")
        
        # Check for common issues
        template_text = template.template.lower()
        if "please" not in template_text and "kindly" not in template_text:
            suggestions.append("Adding polite language may improve AI response quality")
        
        if len(template.examples) == 0:
            suggestions.append("Adding examples to the template may improve consistency")
        
        return suggestions
    
    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    async def list_templates(
        self,
        category: Optional[PromptCategory] = None,
        tags: Optional[List[str]] = None
    ) -> List[PromptTemplate]:
        """List templates with optional filtering"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        return templates
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> PromptTemplate:
        """Update existing template"""
        template = self.templates.get(template_id)
        if not template:
            raise PromptError(f"Template not found: {template_id}")
        
        # Create new version
        updated_data = template.dict()
        updated_data.update(updates)
        updated_data["updated_at"] = datetime.utcnow()
        updated_data["version"] = self._increment_version(template.version)
        
        new_template = PromptTemplate(**updated_data)
        
        # Store new version
        self.templates[template_id] = new_template
        self.template_versions[template_id].append(new_template)
        
        return new_template
    
    def _increment_version(self, version: str) -> str:
        """Increment version number"""
        parts = version.split(".")
        if len(parts) == 3:
            major, minor, patch = parts
            return f"{major}.{minor}.{int(patch) + 1}"
        return "1.0.1"
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete template"""
        if template_id in self.templates:
            del self.templates[template_id]
            if template_id in self.template_versions:
                del self.template_versions[template_id]
            return True
        return False