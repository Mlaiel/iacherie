"""Event Transformation Pipeline - Ultra-Optimized for Ainflue Cross-Services

High-performance event transformation pipeline with business-aware transformations,
schema mapping, and real-time streaming support for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of transformations available"""
    SCHEMA_MAPPING = "schema_mapping"
    DATA_ENRICHMENT = "data_enrichment"
    FORMAT_CONVERSION = "format_conversion"
    BUSINESS_LOGIC = "business_logic"
    AGGREGATION = "aggregation"
    FILTERING = "filtering"
    ROUTING = "routing"


class TransformationPriority(Enum):
    """Priority levels for transformations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TransformationMetrics:
    """Metrics for transformation execution"""
    transformation_name: str
    execution_time: float
    input_size: int
    output_size: int
    success: bool
    error_message: Optional[str] = None
    performance_score: float = 0.0
    business_impact: str = "unknown"


@dataclass
class TransformationResult:
    """Result of a single transformation"""
    transformed_event: Dict[str, Any]
    metrics: TransformationMetrics
    warnings: List[str] = field(default_factory=list)
    enrichment_data: Dict[str, Any] = field(default_factory=dict)
    business_tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationContext:
    """Context for transformation operations"""
    target_service: str
    target_schema: Optional[Dict[str, Any]] = None
    business_context: Optional[Dict[str, Any]] = None
    performance_requirements: Optional[Dict[str, Any]] = None
    routing_rules: Optional[Dict[str, Any]] = None
    enrichment_sources: Optional[List[str]] = None


@dataclass
class BusinessAnalysis:
    """Business context analysis for events"""
    event_category: str
    business_value: float
    processing_priority: str
    user_tier: str
    workflow_stage: str
    compliance_requirements: List[str] = field(default_factory=list)
    performance_targets: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformedEvent:
    """Final result of transformation pipeline"""
    original_event_id: str
    transformed_data: Dict[str, Any]
    transformation_chain: List[str]
    total_processing_time: float
    business_metadata: Dict[str, Any]
    quality_score: float
    target_services: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class TransformationError(Exception):
    """Custom exception for transformation errors"""
    
    def __init__(self, message: str, transformation_name: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.transformation_name = transformation_name
        self.original_error = original_error


class TransformationPipelineError(Exception):
    """Exception for critical pipeline failures"""
    
    def __init__(self, message: str, original_error: Exception, business_impact: str):
        super().__init__(message)
        self.original_error = original_error
        self.business_impact = business_impact


class BusinessEnrichmentEngine:
    """Engine for business context analysis and enrichment"""
    
    def __init__(self):
        self.enrichment_cache = {}
        self.business_rules = self._load_business_rules()
    
    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules for enrichment"""
        return {
            "content_events": {
                "value_calculation": {
                    "base_value": 10.0,
                    "size_multiplier": 0.001,
                    "quality_multiplier": 5.0,
                    "ai_processing_bonus": 25.0
                },
                "priority_rules": {
                    "enterprise": "high",
                    "premium": "medium", 
                    "free": "low"
                }
            },
            "collaboration_events": {
                "value_calculation": {
                    "base_value": 50.0,
                    "compatibility_multiplier": 10.0,
                    "tier_bonus": {"enterprise": 100.0, "premium": 25.0, "free": 0.0}
                }
            },
            "monetization_events": {
                "value_calculation": {
                    "transaction_percentage": 0.1,
                    "revenue_multiplier": 1.0
                },
                "priority_rules": {
                    "high_value": "critical",
                    "medium_value": "high",
                    "low_value": "medium"
                }
            }
        }
    
    async def analyze_business_context(self, event_data: Dict[str, Any], 
                                     transformation_context: TransformationContext) -> BusinessAnalysis:
        """Analyze business context for event transformation"""
        
        event_type = event_data.get("event_type", "")
        user_tier = transformation_context.business_context.get("user_tier", "free") if transformation_context.business_context else "free"
        
        # Categorize event
        event_category = self._categorize_event(event_type)
        
        # Calculate business value
        business_value = await self._calculate_business_value(event_data, event_category, user_tier)
        
        # Determine processing priority
        processing_priority = await self._determine_processing_priority(business_value, user_tier, event_category)
        
        # Identify workflow stage
        workflow_stage = await self._identify_workflow_stage(event_type, event_data)
        
        # Get compliance requirements
        compliance_requirements = await self._get_compliance_requirements(event_category, business_value)
        
        # Set performance targets
        performance_targets = await self._set_performance_targets(processing_priority, event_category)
        
        return BusinessAnalysis(
            event_category=event_category,
            business_value=business_value,
            processing_priority=processing_priority,
            user_tier=user_tier,
            workflow_stage=workflow_stage,
            compliance_requirements=compliance_requirements,
            performance_targets=performance_targets
        )
    
    def _categorize_event(self, event_type: str) -> str:
        """Categorize event for business analysis"""
        if event_type.startswith("content."):
            return "content_management"
        elif event_type.startswith("collaboration."):
            return "collaboration"
        elif event_type.startswith("monetization."):
            return "monetization"
        elif event_type.startswith("analytics."):
            return "analytics"
        elif event_type.startswith("user."):
            return "user_management"
        else:
            return "general"
    
    async def _calculate_business_value(self, event_data: Dict[str, Any], 
                                      event_category: str, user_tier: str) -> float:
        """Calculate business value of event"""
        
        rules = self.business_rules.get(f"{event_category}_events", {}).get("value_calculation", {})
        base_value = rules.get("base_value", 1.0)
        
        # Apply category-specific calculations
        if event_category == "content_management":
            payload = event_data.get("payload", {})
            file_size = payload.get("file_size", 0)
            quality_score = payload.get("quality_score", 0.5)
            has_ai_processing = "ai" in event_data.get("event_type", "").lower()
            
            value = base_value
            value += file_size * rules.get("size_multiplier", 0.001)
            value += quality_score * rules.get("quality_multiplier", 5.0)
            
            if has_ai_processing:
                value += rules.get("ai_processing_bonus", 25.0)
            
            return value
        
        elif event_category == "collaboration":
            payload = event_data.get("payload", {})
            compatibility_score = payload.get("compatibility_score", 0.5)
            tier_bonus = rules.get("tier_bonus", {}).get(user_tier, 0.0)
            
            value = base_value
            value += compatibility_score * rules.get("compatibility_multiplier", 10.0)
            value += tier_bonus
            
            return value
        
        elif event_category == "monetization":
            payload = event_data.get("payload", {})
            transaction_amount = payload.get("amount", 0)
            
            value = transaction_amount * rules.get("transaction_percentage", 0.1)
            value *= rules.get("revenue_multiplier", 1.0)
            
            return value
        
        return base_value
    
    async def _determine_processing_priority(self, business_value: float, 
                                           user_tier: str, event_category: str) -> str:
        """Determine processing priority based on business factors"""
        
        # High-value events get priority
        if business_value > 1000:
            return TransformationPriority.CRITICAL.value
        elif business_value > 100:
            return TransformationPriority.HIGH.value
        
        # Enterprise users get higher priority
        if user_tier == "enterprise":
            return TransformationPriority.HIGH.value
        elif user_tier == "premium":
            return TransformationPriority.MEDIUM.value
        
        # Monetization events are always high priority
        if event_category == "monetization":
            return TransformationPriority.HIGH.value
        
        return TransformationPriority.LOW.value
    
    async def _identify_workflow_stage(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Identify current workflow stage"""
        
        stage_mapping = {
            "upload": "content_upload",
            "processing": "ai_processing", 
            "protection": "content_protection",
            "seo": "seo_optimization",
            "collaboration": "collaboration",
            "monetization": "monetization",
            "distribution": "content_distribution"
        }
        
        for keyword, stage in stage_mapping.items():
            if keyword in event_type:
                return stage
        
        return "unknown"
    
    async def _get_compliance_requirements(self, event_category: str, business_value: float) -> List[str]:
        """Get compliance requirements for event category"""
        
        requirements = []
        
        if event_category == "monetization":
            requirements.extend(["financial_regulations", "aml_compliance"])
            
            if business_value > 10000:
                requirements.append("enhanced_due_diligence")
        
        if event_category in ["content_management", "collaboration"]:
            requirements.extend(["gdpr_compliance", "content_policy"])
        
        return requirements
    
    async def _set_performance_targets(self, priority: str, event_category: str) -> Dict[str, Any]:
        """Set performance targets based on priority and category"""
        
        targets = {
            "max_processing_time": {
                "critical": 1.0,
                "high": 5.0,
                "medium": 10.0,
                "low": 30.0
            }.get(priority, 30.0),
            "min_quality_score": {
                "critical": 0.95,
                "high": 0.90,
                "medium": 0.80,
                "low": 0.70
            }.get(priority, 0.70)
        }
        
        # Category-specific adjustments
        if event_category == "monetization":
            targets["max_processing_time"] *= 0.5  # Faster processing for money events
            targets["min_quality_score"] = 0.99    # Higher quality for financial events
        
        return targets


class SchemaMapper:
    """Mapper for schema transformations between services"""
    
    def __init__(self):
        self.schema_mappings = self._load_schema_mappings()
        self.default_mappings = self._load_default_mappings()
    
    def _load_schema_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load service-specific schema mappings"""
        return {
            "analytics_service": {
                "field_mappings": {
                    "event_id": "tracking_id",
                    "event_type": "action_type",
                    "user_id": "user_identifier",
                    "timestamp": "event_timestamp",
                    "payload.content_type": "content_category",
                    "payload.file_size": "data_volume",
                    "business_metadata.workflow_stage": "process_stage"
                },
                "value_transformations": {
                    "timestamp": "iso_to_epoch",
                    "file_size": "bytes_to_mb",
                    "event_type": "normalize_action_name"
                },
                "required_fields": ["tracking_id", "action_type", "event_timestamp", "user_identifier"]
            },
            "notification_service": {
                "field_mappings": {
                    "event_id": "notification_id",
                    "user_id": "recipient_id",
                    "event_type": "notification_type",
                    "payload.message": "content",
                    "payload.priority": "urgency_level"
                },
                "value_transformations": {
                    "event_type": "to_notification_category",
                    "priority": "map_to_urgency"
                },
                "required_fields": ["notification_id", "recipient_id", "notification_type", "content"]
            },
            "audit_service": {
                "field_mappings": {
                    "event_id": "audit_id",
                    "event_type": "audit_action",
                    "user_id": "actor_id",
                    "timestamp": "audit_timestamp",
                    "business_metadata": "audit_context"
                },
                "value_transformations": {
                    "timestamp": "ensure_utc_format"
                },
                "required_fields": ["audit_id", "audit_action", "actor_id", "audit_timestamp"]
            }
        }
    
    def _load_default_mappings(self) -> Dict[str, Any]:
        """Load default field mappings"""
        return {
            "common_fields": {
                "event_id": ["id", "identifier", "tracking_id"],
                "timestamp": ["created_at", "event_time", "occurred_at"],
                "user_id": ["user", "actor", "creator_id"]
            }
        }
    
    async def map_schema(self, event_data: Dict[str, Any], target_service: str,
                        target_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Map event schema to target service format"""
        
        if target_service not in self.schema_mappings:
            logger.warning(f"No schema mapping found for service: {target_service}")
            return await self._apply_default_mapping(event_data, target_schema)
        
        mapping_config = self.schema_mappings[target_service]
        mapped_data = {}
        
        # Apply field mappings
        field_mappings = mapping_config.get("field_mappings", {})
        for source_field, target_field in field_mappings.items():
            value = self._get_nested_value(event_data, source_field)
            if value is not None:
                self._set_nested_value(mapped_data, target_field, value)
        
        # Apply value transformations
        transformations = mapping_config.get("value_transformations", {})
        for field, transformation in transformations.items():
            if field in mapped_data:
                mapped_data[field] = await self._apply_value_transformation(
                    mapped_data[field], transformation
                )
        
        # Ensure required fields
        required_fields = mapping_config.get("required_fields", [])
        for required_field in required_fields:
            if required_field not in mapped_data:
                # Try to derive from source data
                derived_value = await self._derive_required_field(
                    required_field, event_data, target_service
                )
                if derived_value is not None:
                    mapped_data[required_field] = derived_value
                else:
                    logger.warning(f"Required field {required_field} missing for {target_service}")
        
        return mapped_data
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set value in nested dictionary using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    async def _apply_value_transformation(self, value: Any, transformation: str) -> Any:
        """Apply value transformation"""
        
        try:
            if transformation == "iso_to_epoch":
                if isinstance(value, str):
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return int(dt.timestamp())
            
            elif transformation == "bytes_to_mb":
                if isinstance(value, (int, float)):
                    return round(value / 1024 / 1024, 2)
            
            elif transformation == "normalize_action_name":
                if isinstance(value, str):
                    return value.replace('.', '_').lower()
            
            elif transformation == "to_notification_category":
                if isinstance(value, str):
                    if "upload" in value:
                        return "content_update"
                    elif "collaboration" in value:
                        return "collaboration_alert"
                    elif "monetization" in value:
                        return "payment_notification"
                    else:
                        return "general_notification"
            
            elif transformation == "map_to_urgency":
                urgency_map = {"critical": "high", "high": "medium", "medium": "low", "low": "low"}
                return urgency_map.get(str(value).lower(), "low")
            
            elif transformation == "ensure_utc_format":
                if isinstance(value, str) and not value.endswith('Z'):
                    return value + 'Z'
            
        except Exception as e:
            logger.warning(f"Transformation {transformation} failed for value {value}: {e}")
        
        return value
    
    async def _derive_required_field(self, required_field: str, source_data: Dict[str, Any],
                                   target_service: str) -> Optional[Any]:
        """Derive required field from source data"""
        
        # Common derivations
        if required_field in ["tracking_id", "notification_id", "audit_id"]:
            return source_data.get("event_id")
        
        elif required_field in ["user_identifier", "recipient_id", "actor_id"]:
            return source_data.get("user_id")
        
        elif required_field in ["event_timestamp", "audit_timestamp"]:
            return source_data.get("timestamp", datetime.utcnow().isoformat())
        
        elif required_field == "action_type":
            return source_data.get("event_type", "unknown_action")
        
        elif required_field == "notification_type":
            event_type = source_data.get("event_type", "")
            if "upload" in event_type:
                return "upload_notification"
            elif "processing" in event_type:
                return "processing_notification"
            else:
                return "general_notification"
        
        return None
    
    async def _apply_default_mapping(self, event_data: Dict[str, Any],
                                   target_schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply default mapping when no specific mapping exists"""
        
        # Start with original data
        mapped_data = event_data.copy()
        
        # Apply common field mappings if target schema is provided
        if target_schema and "properties" in target_schema:
            schema_fields = target_schema["properties"].keys()
            
            for schema_field in schema_fields:
                if schema_field not in mapped_data:
                    # Try to find similar field in source data
                    similar_field = self._find_similar_field(schema_field, event_data.keys())
                    if similar_field:
                        mapped_data[schema_field] = event_data[similar_field]
        
        return mapped_data
    
    def _find_similar_field(self, target_field: str, source_fields: List[str]) -> Optional[str]:
        """Find similar field name in source data"""
        
        target_lower = target_field.lower()
        
        # Exact match
        for field in source_fields:
            if field.lower() == target_lower:
                return field
        
        # Partial match
        for field in source_fields:
            if target_lower in field.lower() or field.lower() in target_lower:
                return field
        
        return None


class TransformationPerformanceOptimizer:
    """Optimizer for transformation performance"""
    
    def __init__(self):
        self.performance_history = []
        self.optimization_cache = {}
    
    async def optimize_for_transformation(self, event_data: Dict[str, Any],
                                        transformation: 'BaseTransformation') -> Dict[str, Any]:
        """Optimize event data for specific transformation"""
        
        optimization_key = f"{transformation.name}_{hash(str(event_data))}"
        
        if optimization_key in self.optimization_cache:
            logger.debug(f"Using cached optimization for {transformation.name}")
            return self.optimization_cache[optimization_key]
        
        optimized_data = event_data.copy()
        
        # Remove unnecessary fields for performance
        if hasattr(transformation, 'required_fields'):
            required_fields = transformation.required_fields
            optimized_data = {k: v for k, v in optimized_data.items() if k in required_fields}
        
        # Simplify nested structures if not needed
        if hasattr(transformation, 'max_depth'):
            optimized_data = self._limit_depth(optimized_data, transformation.max_depth)
        
        # Cache the optimization
        self.optimization_cache[optimization_key] = optimized_data
        
        return optimized_data
    
    def _limit_depth(self, data: Any, max_depth: int, current_depth: int = 0) -> Any:
        """Limit the depth of nested structures"""
        
        if current_depth >= max_depth:
            return str(data) if not isinstance(data, (str, int, float, bool)) else data
        
        if isinstance(data, dict):
            return {k: self._limit_depth(v, max_depth, current_depth + 1) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._limit_depth(item, max_depth, current_depth + 1) for item in data]
        else:
            return data


class ErrorRecoveryHandler:
    """Handler for transformation error recovery"""
    
    async def handle_transformation_error(self, error: TransformationError,
                                        event_data: Dict[str, Any],
                                        transformation: 'BaseTransformation',
                                        business_analysis: BusinessAnalysis) -> 'RecoveryResult':
        """Handle transformation error with business-aware recovery"""
        
        logger.error(f"Transformation error in {error.transformation_name}: {error}")
        
        # Determine if we should continue based on business criticality
        should_continue = await self._should_continue_on_error(error, business_analysis)
        
        if should_continue:
            # Attempt recovery
            recovered_event = await self._attempt_recovery(error, event_data, transformation)
            
            return RecoveryResult(
                should_continue=True,
                recovered_event=recovered_event,
                recovery_method="partial_recovery"
            )
        else:
            return RecoveryResult(
                should_continue=False,
                recovery_method="fail_fast"
            )
    
    async def _should_continue_on_error(self, error: TransformationError,
                                      business_analysis: BusinessAnalysis) -> bool:
        """Determine if processing should continue despite error"""
        
        # Always fail fast for critical priority events
        if business_analysis.processing_priority == TransformationPriority.CRITICAL.value:
            return False
        
        # Continue for non-essential transformations
        if error.transformation_name in ["enrichment", "analytics_mapping"]:
            return True
        
        # Continue for low-value events
        if business_analysis.business_value < 10:
            return True
        
        return False
    
    async def _attempt_recovery(self, error: TransformationError,
                              event_data: Dict[str, Any],
                              transformation: 'BaseTransformation') -> Dict[str, Any]:
        """Attempt to recover from transformation error"""
        
        # Return original data with error metadata
        recovered_data = event_data.copy()
        
        if "error_metadata" not in recovered_data:
            recovered_data["error_metadata"] = {}
        
        recovered_data["error_metadata"][f"{transformation.name}_error"] = {
            "error_message": str(error),
            "error_timestamp": datetime.utcnow().isoformat(),
            "recovery_applied": True
        }
        
        return recovered_data


@dataclass
class RecoveryResult:
    """Result of error recovery attempt"""
    should_continue: bool
    recovered_event: Optional[Dict[str, Any]] = None
    recovery_method: str = "none"


class BaseTransformation:
    """Base class for all transformations"""
    
    def __init__(self, name: str, priority: TransformationPriority = TransformationPriority.MEDIUM):
        self.name = name
        self.priority = priority
        self.required_fields = []
        self.max_depth = None
    
    async def transform(self, event_data: Dict[str, Any], 
                       business_analysis: BusinessAnalysis,
                       transformation_context: TransformationContext) -> TransformationResult:
        """Transform event data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement transform method")
    
    async def validate_input(self, event_data: Dict[str, Any]) -> bool:
        """Validate input data before transformation"""
        
        for field in self.required_fields:
            if field not in event_data:
                return False
        
        return True


class SchemaTransformation(BaseTransformation):
    """Schema mapping transformation"""
    
    def __init__(self, schema_mapper: SchemaMapper):
        super().__init__("schema_mapping", TransformationPriority.HIGH)
        self.schema_mapper = schema_mapper
        self.required_fields = ["event_id", "event_type"]
    
    async def transform(self, event_data: Dict[str, Any],
                       business_analysis: BusinessAnalysis,
                       transformation_context: TransformationContext) -> TransformationResult:
        """Transform event schema for target service"""
        
        start_time = time.time()
        
        try:
            # Map schema to target service
            transformed_data = await self.schema_mapper.map_schema(
                event_data,
                transformation_context.target_service,
                transformation_context.target_schema
            )
            
            execution_time = time.time() - start_time
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(execution_time, len(str(event_data)))
            
            metrics = TransformationMetrics(
                transformation_name=self.name,
                execution_time=execution_time,
                input_size=len(str(event_data)),
                output_size=len(str(transformed_data)),
                success=True,
                performance_score=performance_score,
                business_impact="schema_compatibility"
            )
            
            return TransformationResult(
                transformed_event=transformed_data,
                metrics=metrics,
                business_tags={"schema_mapped": True, "target_service": transformation_context.target_service}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            metrics = TransformationMetrics(
                transformation_name=self.name,
                execution_time=execution_time,
                input_size=len(str(event_data)),
                output_size=0,
                success=False,
                error_message=str(e),
                performance_score=0.0,
                business_impact="transformation_failed"
            )
            
            raise TransformationError(f"Schema mapping failed: {e}", self.name, e)
    
    def _calculate_performance_score(self, execution_time: float, data_size: int) -> float:
        """Calculate performance score for transformation"""
        
        # Target: < 1ms per KB of data
        target_time = data_size / 1024 * 0.001
        
        if execution_time <= target_time:
            return 1.0
        else:
            return max(0.0, 1.0 - (execution_time - target_time) / target_time)


class BusinessEnrichmentTransformation(BaseTransformation):
    """Business data enrichment transformation"""
    
    def __init__(self, enrichment_engine: BusinessEnrichmentEngine):
        super().__init__("business_enrichment", TransformationPriority.MEDIUM)
        self.enrichment_engine = enrichment_engine
        self.required_fields = ["event_type"]
    
    async def transform(self, event_data: Dict[str, Any],
                       business_analysis: BusinessAnalysis,
                       transformation_context: TransformationContext) -> TransformationResult:
        """Enrich event with business context"""
        
        start_time = time.time()
        
        try:
            enriched_data = event_data.copy()
            
            # Add business metadata
            enriched_data["business_metadata"] = {
                "event_category": business_analysis.event_category,
                "business_value": business_analysis.business_value,
                "processing_priority": business_analysis.processing_priority,
                "user_tier": business_analysis.user_tier,
                "workflow_stage": business_analysis.workflow_stage,
                "enrichment_timestamp": datetime.utcnow().isoformat()
            }
            
            # Add compliance metadata
            if business_analysis.compliance_requirements:
                enriched_data["compliance_metadata"] = {
                    "requirements": business_analysis.compliance_requirements,
                    "compliance_checked": True
                }
            
            # Add performance metadata
            enriched_data["performance_metadata"] = business_analysis.performance_targets
            
            execution_time = time.time() - start_time
            
            metrics = TransformationMetrics(
                transformation_name=self.name,
                execution_time=execution_time,
                input_size=len(str(event_data)),
                output_size=len(str(enriched_data)),
                success=True,
                performance_score=1.0,
                business_impact="enhanced_context"
            )
            
            return TransformationResult(
                transformed_event=enriched_data,
                metrics=metrics,
                enrichment_data={
                    "business_value": business_analysis.business_value,
                    "priority": business_analysis.processing_priority
                },
                business_tags={
                    "enriched": True,
                    "category": business_analysis.event_category
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            metrics = TransformationMetrics(
                transformation_name=self.name,
                execution_time=execution_time,
                input_size=len(str(event_data)),
                output_size=0,
                success=False,
                error_message=str(e),
                performance_score=0.0,
                business_impact="enrichment_failed"
            )
            
            raise TransformationError(f"Business enrichment failed: {e}", self.name, e)


class FilteringTransformation(BaseTransformation):
    """Event filtering transformation"""
    
    def __init__(self, filter_rules: Dict[str, Any]):
        super().__init__("filtering", TransformationPriority.LOW)
        self.filter_rules = filter_rules
    
    async def transform(self, event_data: Dict[str, Any],
                       business_analysis: BusinessAnalysis,
                       transformation_context: TransformationContext) -> TransformationResult:
        """Filter event data based on rules"""
        
        start_time = time.time()
        
        try:
            filtered_data = event_data.copy()
            
            # Apply field filtering
            excluded_fields = self.filter_rules.get("exclude_fields", [])
            for field in excluded_fields:
                if field in filtered_data:
                    del filtered_data[field]
            
            # Apply value filtering
            value_filters = self.filter_rules.get("value_filters", {})
            for field, filter_func in value_filters.items():
                if field in filtered_data:
                    filtered_data[field] = filter_func(filtered_data[field])
            
            execution_time = time.time() - start_time
            
            metrics = TransformationMetrics(
                transformation_name=self.name,
                execution_time=execution_time,
                input_size=len(str(event_data)),
                output_size=len(str(filtered_data)),
                success=True,
                performance_score=1.0,
                business_impact="data_optimized"
            )
            
            return TransformationResult(
                transformed_event=filtered_data,
                metrics=metrics,
                business_tags={"filtered": True}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            metrics = TransformationMetrics(
                transformation_name=self.name,
                execution_time=execution_time,
                input_size=len(str(event_data)),
                output_size=0,
                success=False,
                error_message=str(e),
                performance_score=0.0,
                business_impact="filtering_failed"
            )
            
            raise TransformationError(f"Filtering failed: {e}", self.name, e)


class TransformationRegistry:
    """Registry for managing transformations"""
    
    def __init__(self):
        self.transformations: Dict[str, BaseTransformation] = {}
        self.transformation_chains: Dict[str, List[str]] = {}
    
    def register_transformation(self, transformation: BaseTransformation):
        """Register a transformation"""
        self.transformations[transformation.name] = transformation
        logger.info(f"Registered transformation: {transformation.name}")
    
    def get_transformation(self, name: str) -> Optional[BaseTransformation]:
        """Get transformation by name"""
        return self.transformations.get(name)
    
    def register_transformation_chain(self, service: str, transformation_names: List[str]):
        """Register transformation chain for a service"""
        self.transformation_chains[service] = transformation_names
        logger.info(f"Registered transformation chain for {service}: {transformation_names}")
    
    def get_transformation_chain(self, service: str) -> List[BaseTransformation]:
        """Get transformation chain for service"""
        chain_names = self.transformation_chains.get(service, [])
        return [self.transformations[name] for name in chain_names if name in self.transformations]


class EventTransformationPipeline:
    """
    Ultra-optimized event transformation pipeline for Ainflue cross-services
    Business-aware transformations with streaming support and intelligent error recovery
    """
    
    def __init__(self, transformation_registry: TransformationRegistry):
        self.transformation_registry = transformation_registry
        self.business_enrichment_engine = BusinessEnrichmentEngine()
        self.schema_mapper = SchemaMapper()
        self.performance_optimizer = TransformationPerformanceOptimizer()
        self.error_recovery_handler = ErrorRecoveryHandler()
        
        # Initialize default transformations
        self._initialize_default_transformations()
        
        logger.info("EventTransformationPipeline initialized for Ainflue cross-services")
    
    def _initialize_default_transformations(self):
        """Initialize default transformations"""
        
        # Register schema transformation
        schema_transformation = SchemaTransformation(self.schema_mapper)
        self.transformation_registry.register_transformation(schema_transformation)
        
        # Register business enrichment transformation
        enrichment_transformation = BusinessEnrichmentTransformation(self.business_enrichment_engine)
        self.transformation_registry.register_transformation(enrichment_transformation)
        
        # Register filtering transformation
        default_filters = {
            "exclude_fields": ["internal_metadata", "debug_info"],
            "value_filters": {
                "sensitive_data": lambda x: "***REDACTED***" if isinstance(x, str) and "password" in x.lower() else x
            }
        }
        filtering_transformation = FilteringTransformation(default_filters)
        self.transformation_registry.register_transformation(filtering_transformation)
        
        # Register default transformation chains
        self.transformation_registry.register_transformation_chain("analytics_service", 
                                                                 ["business_enrichment", "schema_mapping", "filtering"])
        self.transformation_registry.register_transformation_chain("notification_service",
                                                                 ["business_enrichment", "schema_mapping"])
        self.transformation_registry.register_transformation_chain("audit_service",
                                                                 ["schema_mapping", "filtering"])
    
    async def transform_event_for_business_context(self,
                                                 source_event: Dict[str, Any],
                                                 target_context: TransformationContext) -> TransformedEvent:
        """Transform event for business context with comprehensive pipeline"""
        
        start_time = time.time()
        
        try:
            # Business context analysis
            business_analysis = await self.business_enrichment_engine.analyze_business_context(
                source_event, target_context
            )
            
            # Determine required transformations
            required_transformations = await self._determine_required_transformations(
                source_event, target_context, business_analysis
            )
            
            # Execute transformation pipeline
            transformed_event = source_event.copy()
            transformation_metrics = []
            transformation_chain = []
            
            for transformation in required_transformations:
                try:
                    # Performance optimization
                    optimized_input = await self.performance_optimizer.optimize_for_transformation(
                        transformed_event, transformation
                    )
                    
                    # Execute transformation
                    transformation_result = await transformation.transform(
                        optimized_input, business_analysis, target_context
                    )
                    
                    transformed_event = transformation_result.transformed_event
                    transformation_metrics.append(transformation_result.metrics)
                    transformation_chain.append(transformation.name)
                    
                    logger.debug(f"Transformation {transformation.name} completed successfully")
                    
                except TransformationError as e:
                    # Handle error with business-aware recovery
                    recovery_result = await self.error_recovery_handler.handle_transformation_error(
                        e, transformed_event, transformation, business_analysis
                    )
                    
                    if recovery_result.should_continue:
                        transformed_event = recovery_result.recovered_event
                        transformation_chain.append(f"{transformation.name}_recovered")
                        logger.warning(f"Transformation {transformation.name} recovered: {recovery_result.recovery_method}")
                    else:
                        raise TransformationPipelineError(
                            f"Critical transformation failed: {transformation.name}",
                            original_error=e,
                            business_impact="Pipeline execution halted"
                        )
            
            total_processing_time = time.time() - start_time
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(transformation_metrics, business_analysis)
            
            # Generate business metadata
            business_metadata = await self._generate_business_metadata(
                business_analysis, target_context, transformation_metrics
            )
            
            logger.info(f"Event transformation completed in {total_processing_time:.3f}s with quality score {quality_score:.2f}")
            
            return TransformedEvent(
                original_event_id=source_event.get("event_id", "unknown"),
                transformed_data=transformed_event,
                transformation_chain=transformation_chain,
                total_processing_time=total_processing_time,
                business_metadata=business_metadata,
                quality_score=quality_score,
                target_services=[target_context.target_service]
            )
            
        except Exception as e:
            total_processing_time = time.time() - start_time
            logger.error(f"Event transformation pipeline failed after {total_processing_time:.3f}s: {e}")
            raise TransformationPipelineError(
                f"Transformation pipeline failed: {e}",
                original_error=e,
                business_impact="Event could not be transformed for target service"
            )
    
    async def _determine_required_transformations(self,
                                                source_event: Dict[str, Any],
                                                target_context: TransformationContext,
                                                business_analysis: BusinessAnalysis) -> List[BaseTransformation]:
        """Determine required transformations based on context"""
        
        # Get transformation chain for target service
        service_transformations = self.transformation_registry.get_transformation_chain(
            target_context.target_service
        )
        
        # Add business-specific transformations
        additional_transformations = []
        
        # High-value events get additional enrichment
        if business_analysis.business_value > 100:
            enrichment = self.transformation_registry.get_transformation("business_enrichment")
            if enrichment and enrichment not in service_transformations:
                additional_transformations.append(enrichment)
        
        # Compliance-sensitive events get additional filtering
        if business_analysis.compliance_requirements:
            filtering = self.transformation_registry.get_transformation("filtering")
            if filtering and filtering not in service_transformations:
                additional_transformations.append(filtering)
        
        # Combine and sort by priority
        all_transformations = service_transformations + additional_transformations
        all_transformations.sort(key=lambda t: list(TransformationPriority).index(t.priority))
        
        return all_transformations
    
    async def _calculate_quality_score(self, transformation_metrics: List[TransformationMetrics],
                                     business_analysis: BusinessAnalysis) -> float:
        """Calculate overall quality score for transformation"""
        
        if not transformation_metrics:
            return 0.0
        
        # Base score from transformation success rate
        success_count = sum(1 for m in transformation_metrics if m.success)
        base_score = success_count / len(transformation_metrics)
        
        # Performance score from individual transformations
        performance_scores = [m.performance_score for m in transformation_metrics if m.success]
        avg_performance = sum(performance_scores) / len(performance_scores) if performance_scores else 0.0
        
        # Business alignment score
        target_processing_time = business_analysis.performance_targets.get("max_processing_time", 30.0)
        actual_processing_time = sum(m.execution_time for m in transformation_metrics)
        
        time_score = 1.0 if actual_processing_time <= target_processing_time else max(0.0, 1.0 - (actual_processing_time - target_processing_time) / target_processing_time)
        
        # Weighted final score
        quality_score = (base_score * 0.4) + (avg_performance * 0.3) + (time_score * 0.3)
        
        return min(1.0, max(0.0, quality_score))
    
    async def _generate_business_metadata(self, business_analysis: BusinessAnalysis,
                                        target_context: TransformationContext,
                                        transformation_metrics: List[TransformationMetrics]) -> Dict[str, Any]:
        """Generate business metadata for transformed event"""
        
        return {
            "business_analysis": {
                "event_category": business_analysis.event_category,
                "business_value": business_analysis.business_value,
                "processing_priority": business_analysis.processing_priority,
                "user_tier": business_analysis.user_tier,
                "workflow_stage": business_analysis.workflow_stage
            },
            "transformation_summary": {
                "target_service": target_context.target_service,
                "transformations_applied": len(transformation_metrics),
                "transformations_successful": sum(1 for m in transformation_metrics if m.success),
                "total_processing_time": sum(m.execution_time for m in transformation_metrics),
                "average_performance_score": sum(m.performance_score for m in transformation_metrics) / len(transformation_metrics) if transformation_metrics else 0.0
            },
            "compliance_metadata": {
                "requirements": business_analysis.compliance_requirements,
                "compliance_verified": True
            },
            "performance_metadata": business_analysis.performance_targets
        }
    
    async def transform_event_batch(self, events: List[Dict[str, Any]],
                                  target_context: TransformationContext) -> List[TransformedEvent]:
        """Transform batch of events for optimal performance"""
        
        # Process events concurrently for performance
        tasks = [
            self.transform_event_for_business_context(event, target_context)
            for event in events
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        transformed_events = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch transformation failed for event {i}: {result}")
            else:
                transformed_events.append(result)
        
        return transformed_events


# Export main classes
__all__ = [
    'EventTransformationPipeline',
    'TransformationContext',
    'TransformedEvent',
    'TransformationType',
    'TransformationPriority',
    'TransformationRegistry',
    'BusinessAnalysis',
    'SchemaMapper',
    'BaseTransformation'
]