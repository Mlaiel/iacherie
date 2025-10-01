#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ IA Chéries Database Template Manager - Enterprise Grade

🚨 PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire

AVERTISSEMENT LÉGAL:
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT  
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Developed by Expert Team:
- Lead Dev IA: Fahed Mlaiel - Template orchestration & AI integration
- Backend Senior: Advanced template management patterns
- DBA Expert: Database template optimization & performance
- Security Expert: Template security validation & compliance
- ML Engineer: Analytics-driven template selection
- Microservices Architect: Distributed template patterns
- DevOps Engineer: Template deployment & versioning
- IA Prompt Engineer: AI-powered template generation

Architecture: Creator Economy Database Template Management
Business Logic: Template Selection → Configuration → Generation → Validation → Deployment
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Type, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import importlib.util
import hashlib
import pickle

from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from pydantic import BaseModel, Field, ValidationError
import redis

logger = logging.getLogger(__name__)

class TemplateCategory(str, Enum):
    """Template categories for organization"""
    CORE_MODELS = "core_models"
    REPOSITORIES = "repositories" 
    MULTI_TENANT = "multi_tenant"
    SPECIALIZED = "specialized"
    MIGRATION = "migration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BACKUP = "backup"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    CREATOR_ECONOMY = "creator_economy"
    NOSQL = "nosql"
    TESTING = "testing"
    TRANSACTION = "transaction"
    MONITORING = "monitoring"
    GLOBAL = "global"
    MODERN = "modern"
    DATA_QUALITY = "data_quality"
    ADVANCED_PERFORMANCE = "advanced_performance"

class TemplateStatus(str, Enum):
    """Template status for lifecycle management"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    DISABLED = "disabled"

@dataclass
class TemplateMetadata:
    """Template metadata for enhanced management"""
    name: str
    category: TemplateCategory
    version: str
    description: str
    author: str = "Fahed Mlaiel <mlaiel@live.de>"
    status: TemplateStatus = TemplateStatus.ACTIVE
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = 0
    performance_score: float = 1.0
    
class TemplateConfiguration(BaseModel):
    """Template configuration schema"""
    template_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    database_config: Dict[str, Any] = Field(default_factory=dict)
    performance_config: Dict[str, Any] = Field(default_factory=dict)
    security_config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"

class TemplateValidationResult(BaseModel):
    """Template validation result"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    performance_issues: List[str] = Field(default_factory=list)
    security_issues: List[str] = Field(default_factory=list)
    
class TemplateGenerationResult(BaseModel):
    """Template generation result"""
    success: bool
    generated_code: Optional[str] = None
    file_path: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DatabaseTemplateManager:
    """
    🏭 Enterprise Database Template Manager
    
    Advanced features:
    - Template lifecycle management
    - Performance monitoring and optimization
    - Security validation and compliance
    - AI-powered template recommendation
    - Caching and optimization
    - Multi-tenant template isolation
    """
    
    def __init__(
        self, 
        cache_enabled: bool = True,
        redis_client: Optional[redis.Redis] = None,
        performance_monitoring: bool = True
    ):
        self.templates: Dict[str, Type] = {}
        self.metadata: Dict[str, TemplateMetadata] = {}
        self.categories: Dict[TemplateCategory, List[str]] = {
            category: [] for category in TemplateCategory
        }
        
        # Performance and caching
        self.cache_enabled = cache_enabled
        self.redis_client = redis_client
        self.performance_monitoring = performance_monitoring
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
        # Security and validation
        self.validation_rules: Dict[str, List[Callable]] = {}
        self.security_policies: Dict[str, Dict[str, Any]] = {}
        
        # AI and analytics
        self.usage_analytics: Dict[str, Dict[str, Any]] = {}
        self.recommendation_engine = None
        
    def register_template(
        self,
        template_class: Type,
        metadata: Optional[TemplateMetadata] = None,
        validation_rules: Optional[List[Callable]] = None,
        security_policy: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a database template with full metadata
        
        Args:
            template_class: Template class to register
            metadata: Template metadata
            validation_rules: Custom validation rules
            security_policy: Security policy configuration
            
        Returns:
            Success status
        """
        try:
            template_name = self._extract_template_name(template_class)
            
            # Create metadata if not provided
            if metadata is None:
                metadata = self._create_default_metadata(template_class, template_name)
            
            # Register template
            self.templates[template_name] = template_class
            self.metadata[template_name] = metadata
            
            # Add to category
            if metadata.category not in self.categories:
                self.categories[metadata.category] = []
            self.categories[metadata.category].append(template_name)
            
            # Register validation rules
            if validation_rules:
                self.validation_rules[template_name] = validation_rules
            
            # Register security policy
            if security_policy:
                self.security_policies[template_name] = security_policy
                
            # Initialize performance metrics
            self.performance_metrics[template_name] = {
                "avg_execution_time": 0.0,
                "success_rate": 1.0,
                "memory_usage": 0.0,
                "cache_hit_rate": 0.0
            }
            
            # Initialize usage analytics
            self.usage_analytics[template_name] = {
                "total_uses": 0,
                "last_used": None,
                "popular_configurations": [],
                "common_errors": []
            }
            
            logger.info(f"Registered template: {template_name} ({metadata.category.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register template {template_class}: {e}")
            return False
    
    def get_template(self, template_name: str) -> Optional[Type]:
        """Get template class by name"""
        return self.templates.get(template_name)
    
    def get_template_metadata(self, template_name: str) -> Optional[TemplateMetadata]:
        """Get template metadata"""
        return self.metadata.get(template_name)
    
    def list_templates(
        self, 
        category: Optional[TemplateCategory] = None,
        status: Optional[TemplateStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        List templates with filtering options
        
        Args:
            category: Filter by category
            status: Filter by status
            tags: Filter by tags
            
        Returns:
            List of template names
        """
        templates = list(self.templates.keys())
        
        if category:
            templates = [t for t in templates if t in self.categories.get(category, [])]
            
        if status:
            templates = [
                t for t in templates 
                if self.metadata.get(t) and self.metadata[t].status == status
            ]
            
        if tags:
            templates = [
                t for t in templates
                if self.metadata.get(t) and 
                all(tag in self.metadata[t].tags for tag in tags)
            ]
            
        return templates
    
    def validate_template(
        self, 
        template_name: str, 
        configuration: Optional[TemplateConfiguration] = None
    ) -> TemplateValidationResult:
        """
        Comprehensive template validation
        
        Args:
            template_name: Name of template to validate
            configuration: Optional configuration to validate
            
        Returns:
            Validation result with detailed feedback
        """
        result = TemplateValidationResult(is_valid=True)
        
        try:
            # Check if template exists
            if template_name not in self.templates:
                result.is_valid = False
                result.errors.append(f"Template '{template_name}' not found")
                return result
            
            template_class = self.templates[template_name]
            metadata = self.metadata.get(template_name)
            
            # Check template status
            if metadata and metadata.status == TemplateStatus.DISABLED:
                result.is_valid = False
                result.errors.append(f"Template '{template_name}' is disabled")
                return result
            
            # Validate template class structure
            required_methods = ['create', 'validate']
            for method in required_methods:
                if not hasattr(template_class, method):
                    result.errors.append(f"Template missing required method: {method}")
            
            # Run custom validation rules
            if template_name in self.validation_rules:
                for rule in self.validation_rules[template_name]:
                    try:
                        rule_result = rule(template_class, configuration)
                        if not rule_result:
                            result.warnings.append(f"Custom validation rule failed")
                    except Exception as e:
                        result.errors.append(f"Validation rule error: {e}")
            
            # Validate configuration if provided
            if configuration:
                try:
                    # Basic configuration validation
                    if configuration.template_name != template_name:
                        result.warnings.append("Configuration template name mismatch")
                        
                    # Check required dependencies
                    if metadata and metadata.dependencies:
                        for dep in metadata.dependencies:
                            if dep not in self.templates:
                                result.warnings.append(f"Dependency '{dep}' not available")
                                
                except Exception as e:
                    result.errors.append(f"Configuration validation error: {e}")
            
            # Security validation
            if template_name in self.security_policies:
                security_result = self._validate_security(template_name, configuration)
                result.security_issues.extend(security_result)
            
            # Performance validation
            perf_result = self._validate_performance(template_name, configuration)
            result.performance_issues.extend(perf_result)
            
            # Set final validation status
            result.is_valid = len(result.errors) == 0
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation failed: {e}")
            
        return result
    
    async def generate_template(
        self,
        template_name: str,
        configuration: TemplateConfiguration,
        output_path: Optional[Path] = None
    ) -> TemplateGenerationResult:
        """
        Generate code from template with full configuration
        
        Args:
            template_name: Name of template to use
            configuration: Template configuration
            output_path: Optional output file path
            
        Returns:
            Generation result with code and metadata
        """
        start_time = time.time()
        result = TemplateGenerationResult(success=False)
        
        try:
            # Validate template first
            validation = self.validate_template(template_name, configuration)
            if not validation.is_valid:
                result.errors = validation.errors
                return result
            
            # Get template
            template_class = self.templates[template_name]
            
            # Check cache first
            if self.cache_enabled:
                cached_result = await self._get_cached_result(template_name, configuration)
                if cached_result:
                    logger.info(f"Cache hit for template: {template_name}")
                    self._update_cache_metrics(template_name, True)
                    return cached_result
            
            # Generate template
            template_instance = template_class()
            
            # Apply configuration
            if hasattr(template_instance, 'configure'):
                template_instance.configure(configuration.dict())
            
            # Generate code
            if hasattr(template_instance, 'generate'):
                generated_code = template_instance.generate()
            elif hasattr(template_instance, 'create'):
                generated_code = template_instance.create(configuration.parameters)
            else:
                raise ValueError(f"Template {template_name} has no generate/create method")
            
            # Save to file if path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                result.file_path = str(output_path)
            
            # Set result
            result.success = True
            result.generated_code = generated_code
            result.metadata = {
                "template_name": template_name,
                "generation_time": time.time() - start_time,
                "code_size": len(generated_code),
                "configuration": configuration.dict()
            }
            
            # Cache result
            if self.cache_enabled:
                await self._cache_result(template_name, configuration, result)
            
            # Update usage analytics
            self._update_usage_analytics(template_name, configuration, True)
            
            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(template_name, execution_time, True)
            
        except Exception as e:
            result.errors.append(f"Generation failed: {e}")
            self._update_usage_analytics(template_name, configuration, False, str(e))
            self._update_performance_metrics(template_name, time.time() - start_time, False)
            
        return result
    
    def get_template_recommendations(
        self,
        use_case: str,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """
        AI-powered template recommendations
        
        Args:
            use_case: Description of the use case
            requirements: Technical requirements
            
        Returns:
            List of recommended template names
        """
        try:
            # Simple rule-based recommendations (can be enhanced with ML)
            recommendations = []
            
            # Creator Economy use cases
            if any(keyword in use_case.lower() for keyword in ["creator", "content", "monetization"]):
                recommendations.extend(self.categories.get(TemplateCategory.CREATOR_ECONOMY, []))
            
            # Performance requirements
            if requirements.get("high_performance", False):
                recommendations.extend(self.categories.get(TemplateCategory.PERFORMANCE, []))
                recommendations.extend(self.categories.get(TemplateCategory.ADVANCED_PERFORMANCE, []))
            
            # Security requirements
            if requirements.get("security_critical", False):
                recommendations.extend(self.categories.get(TemplateCategory.SECURITY, []))
            
            # Multi-tenant requirements
            if requirements.get("multi_tenant", False):
                recommendations.extend(self.categories.get(TemplateCategory.MULTI_TENANT, []))
            
            # Analytics requirements
            if requirements.get("analytics", False):
                recommendations.extend(self.categories.get(TemplateCategory.ANALYTICS, []))
            
            # Remove duplicates and filter by availability/status
            recommendations = list(set(recommendations))
            recommendations = [
                t for t in recommendations 
                if t in self.templates and 
                self.metadata.get(t) and 
                self.metadata[t].status == TemplateStatus.ACTIVE
            ]
            
            # Sort by performance score and usage
            def score_template(template_name: str) -> float:
                metadata = self.metadata.get(template_name)
                metrics = self.performance_metrics.get(template_name, {})
                analytics = self.usage_analytics.get(template_name, {})
                
                score = 0.0
                if metadata:
                    score += metadata.performance_score * 0.4
                score += metrics.get("success_rate", 0.0) * 0.3
                score += min(analytics.get("total_uses", 0) / 100.0, 1.0) * 0.3
                
                return score
            
            recommendations.sort(key=score_template, reverse=True)
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def get_performance_metrics(self, template_name: str) -> Dict[str, Any]:
        """Get performance metrics for a template"""
        return self.performance_metrics.get(template_name, {})
    
    def get_usage_analytics(self, template_name: str) -> Dict[str, Any]:
        """Get usage analytics for a template"""
        return self.usage_analytics.get(template_name, {})
    
    def export_template_config(self, template_name: str) -> Dict[str, Any]:
        """Export template configuration for backup/sharing"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        return {
            "template_name": template_name,
            "metadata": self.metadata.get(template_name).__dict__ if template_name in self.metadata else {},
            "performance_metrics": self.performance_metrics.get(template_name, {}),
            "usage_analytics": self.usage_analytics.get(template_name, {}),
            "security_policy": self.security_policies.get(template_name, {}),
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
    
    # Private helper methods
    def _extract_template_name(self, template_class: Type) -> str:
        """Extract template name from class"""
        class_name = template_class.__name__
        if class_name.endswith('Template'):
            return class_name[:-8].lower()
        return class_name.lower()
    
    def _create_default_metadata(self, template_class: Type, template_name: str) -> TemplateMetadata:
        """Create default metadata for a template"""
        # Try to extract category from class name or module
        category = TemplateCategory.CORE_MODELS  # Default
        
        if "migration" in template_name:
            category = TemplateCategory.MIGRATION
        elif "performance" in template_name or "optimization" in template_name:
            category = TemplateCategory.PERFORMANCE
        elif "security" in template_name or "encryption" in template_name:
            category = TemplateCategory.SECURITY
        elif "creator" in template_name or "monetization" in template_name:
            category = TemplateCategory.CREATOR_ECONOMY
        elif "analytics" in template_name:
            category = TemplateCategory.ANALYTICS
        elif "repository" in template_name:
            category = TemplateCategory.REPOSITORIES
        elif "tenant" in template_name:
            category = TemplateCategory.MULTI_TENANT
        elif "time_series" in template_name:
            category = TemplateCategory.SPECIALIZED
        
        return TemplateMetadata(
            name=template_name,
            category=category,
            version="1.0.0",
            description=f"Enterprise {template_name.replace('_', ' ').title()} Template",
            author="Fahed Mlaiel <mlaiel@live.de>"
        )
    
    def _validate_security(
        self, 
        template_name: str, 
        configuration: Optional[TemplateConfiguration]
    ) -> List[str]:
        """Validate security policies"""
        issues = []
        
        try:
            policy = self.security_policies.get(template_name, {})
            
            if policy.get("requires_encryption", False):
                if not configuration or not configuration.security_config.get("encryption_enabled"):
                    issues.append("Template requires encryption but not configured")
            
            if policy.get("requires_audit", False):
                if not configuration or not configuration.security_config.get("audit_enabled"):
                    issues.append("Template requires audit logging but not configured")
                    
        except Exception as e:
            issues.append(f"Security validation error: {e}")
            
        return issues
    
    def _validate_performance(
        self, 
        template_name: str, 
        configuration: Optional[TemplateConfiguration]
    ) -> List[str]:
        """Validate performance requirements"""
        issues = []
        
        try:
            metrics = self.performance_metrics.get(template_name, {})
            
            if metrics.get("avg_execution_time", 0) > 5.0:  # 5 seconds threshold
                issues.append("Template has high average execution time")
            
            if metrics.get("success_rate", 1.0) < 0.95:  # 95% success rate threshold
                issues.append("Template has low success rate")
                
            if configuration:
                perf_config = configuration.performance_config
                if perf_config.get("max_memory_mb", 0) > 1024:  # 1GB threshold
                    issues.append("High memory usage configured")
                    
        except Exception as e:
            issues.append(f"Performance validation error: {e}")
            
        return issues
    
    async def _get_cached_result(
        self, 
        template_name: str, 
        configuration: TemplateConfiguration
    ) -> Optional[TemplateGenerationResult]:
        """Get cached generation result"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._get_cache_key(template_name, configuration)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return TemplateGenerationResult.parse_raw(cached_data)
                
        except Exception as e:
            logger.debug(f"Cache retrieval error: {e}")
            
        return None
    
    async def _cache_result(
        self, 
        template_name: str, 
        configuration: TemplateConfiguration,
        result: TemplateGenerationResult
    ):
        """Cache generation result"""
        if not self.redis_client:
            return
            
        try:
            cache_key = self._get_cache_key(template_name, configuration)
            cached_data = result.json()
            
            # Cache for 1 hour
            self.redis_client.setex(cache_key, 3600, cached_data)
            
        except Exception as e:
            logger.debug(f"Cache storage error: {e}")
    
    def _get_cache_key(self, template_name: str, configuration: TemplateConfiguration) -> str:
        """Generate cache key for template and configuration"""
        config_hash = hashlib.md5(configuration.json().encode()).hexdigest()
        return f"template:{template_name}:{config_hash}"
    
    def _update_cache_metrics(self, template_name: str, hit: bool):
        """Update cache hit rate metrics"""
        if template_name not in self.performance_metrics:
            return
            
        current_rate = self.performance_metrics[template_name].get("cache_hit_rate", 0.0)
        current_count = self.usage_analytics[template_name].get("total_uses", 1)
        
        # Simple moving average
        new_rate = (current_rate * (current_count - 1) + (1.0 if hit else 0.0)) / current_count
        self.performance_metrics[template_name]["cache_hit_rate"] = new_rate
    
    def _update_usage_analytics(
        self, 
        template_name: str, 
        configuration: TemplateConfiguration,
        success: bool,
        error: Optional[str] = None
    ):
        """Update usage analytics"""
        if template_name not in self.usage_analytics:
            return
            
        analytics = self.usage_analytics[template_name]
        analytics["total_uses"] += 1
        analytics["last_used"] = datetime.now(timezone.utc).isoformat()
        
        if not success and error:
            if "common_errors" not in analytics:
                analytics["common_errors"] = []
            analytics["common_errors"].append({
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            # Keep only last 10 errors
            analytics["common_errors"] = analytics["common_errors"][-10:]
    
    def _update_performance_metrics(
        self, 
        template_name: str, 
        execution_time: float,
        success: bool
    ):
        """Update performance metrics"""
        if template_name not in self.performance_metrics:
            return
            
        metrics = self.performance_metrics[template_name]
        total_uses = self.usage_analytics[template_name].get("total_uses", 1)
        
        # Update average execution time
        current_avg = metrics.get("avg_execution_time", 0.0)
        new_avg = (current_avg * (total_uses - 1) + execution_time) / total_uses
        metrics["avg_execution_time"] = new_avg
        
        # Update success rate
        current_success_rate = metrics.get("success_rate", 1.0)
        new_success_rate = (current_success_rate * (total_uses - 1) + (1.0 if success else 0.0)) / total_uses
        metrics["success_rate"] = new_success_rate


# Global template manager instance
template_manager = DatabaseTemplateManager()

# Export key components
__all__ = [
    "DatabaseTemplateManager",
    "TemplateCategory", 
    "TemplateStatus",
    "TemplateMetadata",
    "TemplateConfiguration",
    "TemplateValidationResult",
    "TemplateGenerationResult",
    "template_manager"
]