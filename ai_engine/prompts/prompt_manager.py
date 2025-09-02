"""Prompt Manager

Central management system for AI prompts and templates in the IA Influencer platform.
Handles prompt creation, optimization, versioning, and performance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PromptCategory(Enum):
    """
Categories of prompts"""

    CONTENT_CREATION = "content_creation"
    CREATIVE_WRITING = "creative_writing"
    BUSINESS_COMMUNICATION = "business_communication"
    SOCIAL_MEDIA = "social_media"
    MARKETING = "marketing"
    EDUCATIONAL = "educational"
    TECHNICAL = "technical"
    ENTERTAINMENT = "entertainment"
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"


class PromptType(Enum):
    """Types of prompts"""

    INSTRUCTION = "instruction"
    QUESTION = "question"
    COMPLETION = "completion"
    CONVERSATION = "conversation"
    ROLE_PLAY = "role_play"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    TEMPLATE = "template"
    DYNAMIC = "dynamic"


class PromptStatus(Enum):
    """Status of prompts"""

    DRAFT = "draft"
    ACTIVE = "active"
    TESTING = "testing"
    OPTIMIZED = "optimized"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class PromptVariable:
    """Variable definition in prompt templates"""
    name: str
    type: str  # string, number, boolean, list, object
    description: str
    required: bool = True
    default_value: Any = None
    validation_rules: Dict[str, Any] = None
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.validation_rules = {}


@dataclass
class PromptTemplate:
    """
Template definition for prompts"""
    template_id: str
    name: str
    description: str
    category: PromptCategory
    prompt_type: PromptType
    template_text: str
    variables: List[PromptVariable]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"
    author: str = "Fahed Mlaiel"
    tags: List[str] = None
    status: PromptStatus = PromptStatus.DRAFT
    performance_metrics: Dict[str, float] = None
    usage_count: int = 0
    success_rate: float = 0.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class PromptExecution:
    """Record of prompt execution"""
    execution_id: str
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
    template_id: str
    input_variables: Dict[str, Any]
    generated_prompt: str
    model_used: str
    response: str
    execution_time_ms: float
    success: bool
    quality_score: float
    feedback: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class PromptManager:
    """
    Central manager for AI prompts and templates
    
    Features:
    - Template creation and management
    - Variable interpolation and validation
    - Performance tracking and optimization
    - Version control and rollback
    - A/B testing for prompts
    - Multi-language support
    - Context-aware prompt generation
    - Quality assessment and improvement
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize prompt manager"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Template storage
        self.templates: Dict[str, PromptTemplate] = {}
        self.template_versions: Dict[str, List[str]] = {}
        self.active_templates: Dict[str, str] = {}  # template_name -> template_id
        
        # Execution tracking
        self.execution_history: List[PromptExecution] = []
        self.performance_cache: Dict[str, Dict[str, Any]] = {}
        
        # Storage configuration
        self.storage_path = Path(self.config.get('storage_path', './prompts'))
        self.backup_path = Path(self.config.get('backup_path', './prompt_backups'))
        
        # Performance settings
        self.max_history_size = self.config.get('max_history_size', 10000)
        self.cache_ttl_hours = self.config.get('cache_ttl_hours', 24)
        
        # Quality assessment
        self.quality_threshold = self.config.get('quality_threshold', 0.7)
        self.min_executions_for_stats = self.config.get('min_executions_for_stats', 10)
        
        # Metrics
        self.metrics = {
            'total_templates': 0,
            'total_executions': 0,
            'average_quality_score': 0.0,
            'average_execution_time': 0.0,
            'success_rate': 0.0,
            'most_used_category': '',
            'optimization_improvements': 0
        }
    
    async def initialize(self) -> bool:
        """
Initialize the prompt manager"""
        try:
            self.logger.info("Initializing Prompt Manager...")
            
            # Create storage directories
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing templates
            await self._load_existing_templates()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            # Start optimization tasks
            await self._start_optimization_tasks()
            
            self.logger.info("Prompt Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize prompt manager: {str(e)}")
            return False
    
    async def create_template(
        self,
        name: str,
        description: str,
        category: PromptCategory,
        prompt_type: PromptType,
        template_text: str,
        variables: List[PromptVariable],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new prompt template"""
        try:
            self.logger.info(f"Creating prompt template: {name}")
            
            # Generate template ID
            template_id = f"{name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            
            # Create template
            template = PromptTemplate(
                template_id=template_id,
                name=name,
                description=description,
                category=category,
                prompt_type=prompt_type,
                template_text=template_text,
                variables=variables,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Validate template
            validation_result = await self._validate_template(template)
            if not validation_result['valid']:
                raise ValueError(f"Template validation failed: {validation_result['errors']}")
            
            # Store template
            self.templates[template_id] = template
            
            # Update version tracking
            if name not in self.template_versions:
                self.template_versions[name] = []
            self.template_versions[name].append(template_id)
            self.active_templates[name] = template_id
            
            # Save to storage
            await self._save_template(template)
            
            # Update metrics
            self.metrics['total_templates'] += 1
            
            self.logger.info(f"Template {name} created successfully with ID: {template_id}")
            return template_id
            
        except Exception as e:
            self.logger.error(f"Failed to create template {name}: {str(e)}")
            raise
    
    async def generate_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a prompt from a template"""
        try:
            # Get active template
            if template_name not in self.active_templates:
                raise ValueError(f"Template {template_name} not found")
            
            template_id = self.active_templates[template_name]
            template = self.templates[template_id]
            
            # Validate variables
            validation_result = await self._validate_variables(template, variables)
            if not validation_result['valid']:
                raise ValueError(f"Variable validation failed: {validation_result['errors']}")
            
            # Apply context if provided
            if context:
                variables = await self._apply_context(variables, context)
            
            # Generate prompt
            generated_prompt = await self._interpolate_template(template, variables)
            
            # Apply optimizations
            optimized_prompt = await self._apply_optimizations(generated_prompt, template, context)
            
            self.logger.debug(f"Generated prompt for template {template_name}")
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to generate prompt for {template_name}: {str(e)}")
            raise
    
    async def execute_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
        model_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PromptExecution:
        """Execute a prompt and track performance"""
        start_time = datetime.utcnow()
        execution_id = str(uuid.uuid4())
        
        try:
            # Generate prompt
            generated_prompt = await self.generate_prompt(template_name, variables, context)
            
            # Execute with AI model (placeholder - would integrate with actual AI service)
            response = await self._execute_with_model(generated_prompt, model_name)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Assess quality
            quality_score = await self._assess_quality(generated_prompt, response, context)
            
            # Create execution record
            template_id = self.active_templates[template_name]
            execution = PromptExecution(
                execution_id=execution_id,
                template_id=template_id,
                input_variables=variables,
                generated_prompt=generated_prompt,
                model_used=model_name,
                response=response,
                execution_time_ms=execution_time,
                success=True,
                quality_score=quality_score,
                timestamp=start_time
            )
            
            # Store execution
            await self._store_execution(execution)
            
            # Update template metrics
            await self._update_template_metrics(template_id, execution)
            
            self.logger.info(f"Prompt executed successfully: {execution_id}")
            return execution
            
        except Exception as e:
            self.logger.error(f"Prompt execution failed: {str(e)}")
            
            # Create failed execution record
            execution = PromptExecution(
                execution_id=execution_id,
                template_id=self.active_templates.get(template_name, ""),
                input_variables=variables,
                generated_prompt="",
                model_used=model_name,
                response="",
                execution_time_ms=0.0,
                success=False,
                quality_score=0.0,
                feedback=str(e),
                timestamp=start_time
            )
            
            await self._store_execution(execution)
            return execution
    
    async def optimize_template(
        self,
        template_name: str,
        optimization_strategy: str = "performance"
    ) -> Dict[str, Any]:
        """Optimize a template based on performance data"""
        try:
            self.logger.info(f"Optimizing template: {template_name}")
            
            if template_name not in self.active_templates:
                raise ValueError(f"Template {template_name} not found")
            
            template_id = self.active_templates[template_name]
            template = self.templates[template_id]
            
            # Get performance data
            performance_data = await self._get_template_performance(template_id)
            
            if len(performance_data) < self.min_executions_for_stats:
                return {
                    'optimized': False,
                    'reason': f'Insufficient data for optimization (need {self.min_executions_for_stats} executions)'
                }
            
            # Apply optimization strategy
            if optimization_strategy == "performance":
                optimizations = await self._optimize_for_performance(template, performance_data)
            elif optimization_strategy == "quality":
                optimizations = await self._optimize_for_quality(template, performance_data)
            elif optimization_strategy == "engagement":
                optimizations = await self._optimize_for_engagement(template, performance_data)
            else:
                raise ValueError(f"Unknown optimization strategy: {optimization_strategy}")
            
            if optimizations['improved']:
                # Create new version
                new_template = await self._create_optimized_version(template, optimizations)
                
                # Update active template
                self.active_templates[template_name] = new_template.template_id
                
                # Update metrics
                self.metrics['optimization_improvements'] += 1
                
                return {
                    'optimized': True,
                    'new_template_id': new_template.template_id,
                    'improvements': optimizations['changes'],
                    'expected_improvement': optimizations['expected_improvement']
                }
            
            return {
                'optimized': False,
                'reason': 'No significant improvements found'
            }
            
        except Exception as e:
            self.logger.error(f"Template optimization failed: {str(e)}")
            return {'optimized': False, 'error': str(e)}
    
    async def get_template_analytics(
        self,
        template_name: str,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a template"""
        try:
            if template_name not in self.active_templates:
                raise ValueError(f"Template {template_name} not found")
            
            template_id = self.active_templates[template_name]
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            
            # Get relevant executions
            executions = [
                e for e in self.execution_history
                if e.template_id == template_id and e.timestamp >= cutoff_date
            ]
            
            if not executions:
                return {'template_name': template_name, 'no_data': True}
            
            # Calculate analytics
            total_executions = len(executions)
            successful_executions = [e for e in executions if e.success]
            success_rate = len(successful_executions) / total_executions if total_executions > 0 else 0
            
            avg_quality = sum(e.quality_score for e in successful_executions) / len(successful_executions) if successful_executions else 0
            avg_execution_time = sum(e.execution_time_ms for e in executions) / total_executions if total_executions > 0 else 0
            
            # Get variable usage statistics
            variable_stats = await self._analyze_variable_usage(executions)
            
            # Get performance trends
            performance_trends = await self._analyze_performance_trends(executions)
            
            return {
                'template_name': template_name,
                'template_id': template_id,
                'time_range_days': time_range_days,
                'total_executions': total_executions,
                'success_rate': success_rate,
                'average_quality_score': avg_quality,
                'average_execution_time_ms': avg_execution_time,
                'variable_statistics': variable_stats,
                'performance_trends': performance_trends,
                'quality_grade': self._get_quality_grade(avg_quality),
                'recommendations': await self._get_optimization_recommendations(template_id, executions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for {template_name}: {str(e)}")
            return {'error': str(e)}
    
    async def list_templates(
        self,
        category: Optional[PromptCategory] = None,
        status: Optional[PromptStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all templates with optional filtering"""
        try:
            templates = []
            
            for template_id, template in self.templates.items():
                if category and template.category != category:
                    continue
                if status and template.status != status:
                    continue
                
                template_info = {
                    'template_id': template_id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category.value,
                    'prompt_type': template.prompt_type.value,
                    'status': template.status.value,
                    'version': template.version,
                    'created_at': template.created_at.isoformat(),
                    'updated_at': template.updated_at.isoformat(),
                    'usage_count': template.usage_count,
                    'success_rate': template.success_rate,
                    'is_active': template_id in self.active_templates.values()
                }
                
                templates.append(template_info)
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to list templates: {str(e)}")
            return []
    
    async def get_manager_status(self) -> Dict[str, Any]:
        """Get prompt manager status"""
        try:
            # Calculate category distribution
            category_counts = {}
            for template in self.templates.values():
                category = template.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Find most used category
            most_used_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else ""
            self.metrics['most_used_category'] = most_used_category
            
            return {
                'total_templates': len(self.templates),
                'active_templates': len(self.active_templates),
                'total_executions': len(self.execution_history),
                'metrics': self.metrics.copy(),
                'category_distribution': category_counts,
                'storage_info': {
                    'storage_path': str(self.storage_path),
                    'backup_path': str(self.backup_path)
                },
                'performance_summary': await self._get_performance_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get manager status: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    async def _validate_template(self, template: PromptTemplate) -> Dict[str, Any]:
        """Validate template configuration"""
        errors = []
        
        # Check required fields
        if not template.name:
            errors.append("Template name is required")
        if not template.template_text:
            errors.append("Template text is required")
        
        # Validate variables in template text
        for variable in template.variables:
            placeholder = f"{{{variable.name}}}"
            if placeholder not in template.template_text:
                errors.append(f"Variable {variable.name} not found in template text")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    async def _validate_variables(
        self,
        template: PromptTemplate,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate variables against template requirements"""
        errors = []
        
        # Check required variables
        for var_def in template.variables:
            if var_def.required and var_def.name not in variables:
                errors.append(f"Required variable {var_def.name} is missing")
            
            if var_def.name in variables:
                # Type validation (simplified)
                value = variables[var_def.name]
                if var_def.type == "string" and not isinstance(value, str):
                    errors.append(f"Variable {var_def.name} must be a string")
                elif var_def.type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Variable {var_def.name} must be a number")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    async def _interpolate_template(
        self,
        template: PromptTemplate,
        variables: Dict[str, Any]
    ) -> str:
        """Interpolate variables into template text"""
        result = template.template_text
        
        for var_def in template.variables:
            placeholder = f"{{{var_def.name}}}"
            value = variables.get(var_def.name, var_def.default_value)
            
            if value is not None:
                result = result.replace(placeholder, str(value))
        
        return result
    
    async def _apply_context(
        self,
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply context to variables"""
        # Placeholder for context application
        # Could include user preferences, platform optimization, etc.
        return variables
    
    async def _apply_optimizations(
        self,
        prompt: str,
        template: PromptTemplate,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
Apply performance optimizations to generated prompt"""
        # Placeholder for prompt optimization
        # Could include A/B test results, performance data, etc.
        return prompt
    
    async def _execute_with_model(self, prompt: str, model_name: str) -> str:
        """
Execute prompt with AI model (placeholder)"""
        # This would integrate with actual AI service
        await asyncio.sleep(0.1)  # Simulate API call
        return f"Mock response for prompt of length {len(prompt)}"
    
    async def _assess_quality(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Assess quality of prompt execution"""
        # Placeholder quality assessment
        # Could use various metrics: relevance, coherence, engagement, etc.
        base_score = 0.7
        
        # Length bonus
        if len(response) > 100:
            base_score += 0.1
        
        # Prompt clarity bonus
        if len(prompt.split()) > 10:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    async def _store_execution(self, execution: PromptExecution):
        """
Store execution record"""
        self.execution_history.append(execution)
        
        # Maintain history size limit
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size:]
        
        # Update global metrics
        self.metrics['total_executions'] += 1
        
        # Update average metrics
        total_time = sum(e.execution_time_ms for e in self.execution_history)
        self.metrics['average_execution_time'] = total_time / len(self.execution_history)
        
        successful = [e for e in self.execution_history if e.success]
        if successful:
            total_quality = sum(e.quality_score for e in successful)
            self.metrics['average_quality_score'] = total_quality / len(successful)
            self.metrics['success_rate'] = len(successful) / len(self.execution_history)
    
    async def _update_template_metrics(self, template_id: str, execution: PromptExecution):
        """
Update template-specific metrics"""
        template = self.templates[template_id]
        template.usage_count += 1
        
        # Calculate success rate for this template
        template_executions = [e for e in self.execution_history if e.template_id == template_id]
        successful = [e for e in template_executions if e.success]
        template.success_rate = len(successful) / len(template_executions) if template_executions else 0
    
    async def _get_template_performance(self, template_id: str) -> List[PromptExecution]:
        """
Get performance data for a template"""
        return [e for e in self.execution_history if e.template_id == template_id]
    
    async def _optimize_for_performance(
        self,
        template: PromptTemplate,
        performance_data: List[PromptExecution]
    ) -> Dict[str, Any]:
        """
Optimize template for performance"""
        # Placeholder optimization logic
        avg_time = sum(e.execution_time_ms for e in performance_data) / len(performance_data)
        
        improvements = []
        if avg_time > 1000:  # If average time > 1 second
            improvements.append("Shortened prompt for faster execution")
        
        return {
            'improved': len(improvements) > 0,
            'changes': improvements,
            'expected_improvement': 0.2 if improvements else 0
        }
    
    async def _optimize_for_quality(
        self,
        template: PromptTemplate,
        performance_data: List[PromptExecution]
    ) -> Dict[str, Any]:
        """Optimize template for quality"""
        # Placeholder optimization logic
        successful = [e for e in performance_data if e.success]
        avg_quality = sum(e.quality_score for e in successful) / len(successful) if successful else 0
        
        improvements = []
        if avg_quality < self.quality_threshold:
            improvements.append("Enhanced prompt clarity and specificity")
        
        return {
            'improved': len(improvements) > 0,
            'changes': improvements,
            'expected_improvement': 0.15 if improvements else 0
        }
    
    async def _optimize_for_engagement(
        self,
        template: PromptTemplate,
        performance_data: List[PromptExecution]
    ) -> Dict[str, Any]:
        """Optimize template for engagement"""
        # Placeholder optimization logic
        improvements = ["Added engagement-focused keywords", "Improved call-to-action"]
        
        return {
            'improved': True,
            'changes': improvements,
            'expected_improvement': 0.25
        }
    
    async def _create_optimized_version(
        self,
        original_template: PromptTemplate,
        optimizations: Dict[str, Any]
    ) -> PromptTemplate:
        """Create optimized version of template"""
        # Generate new template ID
        new_template_id = f"{original_template.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        # Create optimized template (placeholder)
        optimized_template = PromptTemplate(
            template_id=new_template_id,
            name=original_template.name,
            description=original_template.description + " (Optimized)",
            category=original_template.category,
            prompt_type=original_template.prompt_type,
            template_text=original_template.template_text,  # Would be modified based on optimizations
            variables=original_template.variables,
            metadata=original_template.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            version=self._increment_version(original_template.version),
            status=PromptStatus.OPTIMIZED
        )
        
        # Store optimized template
        self.templates[new_template_id] = optimized_template
        self.template_versions[original_template.name].append(new_template_id)
        
        return optimized_template
    
    def _increment_version(self, version: str) -> str:
        """Increment version number"""
        try:
            parts = version.split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            return '.'.join(parts)
        except:
            return "1.0.1"
    
    async def _analyze_variable_usage(self, executions: List[PromptExecution]) -> Dict[str, Any]:
        """Analyze variable usage patterns"""
        # Placeholder analysis
        return {'analysis': 'Variable usage analysis would go here'}
    
    async def _analyze_performance_trends(self, executions: List[PromptExecution]) -> Dict[str, Any]:
        """
Analyze performance trends over time"""
        # Placeholder analysis
        return {'trends': 'Performance trend analysis would go here'}
    
    def _get_quality_grade(self, avg_quality: float) -> str:
        """
Get quality grade based on average quality score"""
        if avg_quality >= 0.9:
            return "A"
        elif avg_quality >= 0.8:
            return "B"
        elif avg_quality >= 0.7:
            return "C"
        elif avg_quality >= 0.6:
        try:
            logger.info(f"Executing _load_existing_templates")
            
            # Implementation for _load_existing_templates
            # TODO: Add specific business logic here
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _save_template completed")
                        return True
                
                except Exception as e:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
        try:
            logger.info(f"Executing _start_optimization_tasks")
            
            # Implementation for _start_optimization_tasks
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_start_optimization_tasks completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_start_optimization_tasks failed: {e}")
            raise
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric _setup_monitoring collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection _setup_monitoring failed: {e}")
                    return None
                    logger.error(f"Database operation _save_template failed: {e}")
                    raise
            logger.info(f"_load_existing_templates completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_load_existing_templates failed: {e}")
            raise
            return "F"
    
    async def _get_optimization_recommendations(
        self,
        template_id: str,
        executions: List[PromptExecution]
    ) -> List[str]:
        """Get optimization recommendations for template"""
        recommendations = []
        
        if len(executions) < 10:
            recommendations.append("Collect more execution data for better insights")
        
        successful = [e for e in executions if e.success]
        if len(successful) / len(executions) < 0.8:
            recommendations.append("Improve prompt clarity to reduce failure rate")
        
        avg_quality = sum(e.quality_score for e in successful) / len(successful) if successful else 0
        if avg_quality < 0.7:
            recommendations.append("Enhance prompt specificity to improve quality")
        
        return recommendations
    
    async def _load_existing_templates(self):
        """Load templates from storage"""
        # Placeholder for loading from persistent storage
        pass
    
    async def _save_template(self, template: PromptTemplate):
        """
Save template to storage"""
        # Placeholder for saving to persistent storage
        pass
    
    async def _setup_monitoring(self):
        """
Setup performance monitoring"""
        # Placeholder for monitoring setup
        pass
    
    async def _start_optimization_tasks(self):
        """
Start background optimization tasks"""
        # Placeholder for background task setup
        pass
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """
Get performance summary"""
        return {
            'total_executions': len(self.execution_history),
            'recent_performance': 'Good',
            'optimization_opportunities': 3
        }
