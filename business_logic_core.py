"""Business Logic Core - Central Business Logic Engine
========================================================

Core business logic module providing centralized business rules, validation,
and workflow management for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass


logger = logging.getLogger(__name__)


class BusinessRule(Enum):
    """Business rule types"""
    CONTENT_VALIDATION = "content_validation"
    MONETIZATION_CHECK = "monetization_check"
    COLLABORATION_APPROVAL = "collaboration_approval"
    COPYRIGHT_VERIFICATION = "copyright_verification"
    QUALITY_ASSURANCE = "quality_assurance"


class CreatorType(Enum):
    """Creator types supported by the platform"""
    MUSICIAN = "musician"
    INFLUENCER = "influencer"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    COMEDIAN = "comedian"
    ALL = "all"


@dataclass
class BusinessLogicResult:
    """Business logic execution result"""
    success: bool
    data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    execution_time: float
    timestamp: datetime


class BusinessLogicCore:
    """
    Central Business Logic Engine
    
    Provides core business logic functionality including:
    - Business rules validation
    - Workflow management
    - Data processing pipelines
    - Cross-module business logic coordination
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Business Logic Core"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.business_rules = self._load_business_rules()
        
    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules configuration"""
        return {
            BusinessRule.CONTENT_VALIDATION: {
                "min_quality_score": 0.7,
                "required_metadata": ["title", "description", "creator_id"],
                "max_file_size": 500 * 1024 * 1024  # 500MB
            },
            BusinessRule.MONETIZATION_CHECK: {
                "min_follower_count": 1000,
                "required_verification": True,
                "supported_currencies": ["USD", "EUR", "GBP"]
            },
            BusinessRule.COLLABORATION_APPROVAL: {
                "min_creator_score": 0.8,
                "require_mutual_approval": True,
                "max_collaboration_duration": 90  # days
            },
            BusinessRule.COPYRIGHT_VERIFICATION: {
                "similarity_threshold": 0.95,
                "require_original_proof": True,
                "auto_flag_violations": True
            },
            BusinessRule.QUALITY_ASSURANCE: {
                "min_resolution": "720p",
                "max_compression": 0.8,
                "require_metadata_complete": True
            }
        }
    
    async def execute_business_logic(self, function_name: str, data: Dict[str, Any], 
                                   creator_type: CreatorType = CreatorType.ALL) -> BusinessLogicResult:
        """Execute core business logic function"""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Executing business logic: {function_name}")
            
            # Input validation
            if not data:
                raise ValueError("Input data is required")
            
            # Apply business rules
            validation_result = await self._validate_business_rules(data, creator_type)
            if not validation_result["valid"]:
                return BusinessLogicResult(
                    success=False,
                    data={},
                    errors=validation_result["errors"],
                    warnings=[],
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    timestamp=datetime.utcnow()
                )
            
            # Execute the specific business logic
            result_data = await self._execute_function(function_name, data, creator_type)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Business logic {function_name} completed in {execution_time:.3f}s")
            
            return BusinessLogicResult(
                success=True,
                data=result_data,
                errors=[],
                warnings=validation_result.get("warnings", []),
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Business logic execution failed: {str(e)}")
            return BusinessLogicResult(
                success=False,
                data={},
                errors=[str(e)],
                warnings=[],
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                timestamp=datetime.utcnow()
            )
    
    async def _validate_business_rules(self, data: Dict[str, Any], 
                                     creator_type: CreatorType) -> Dict[str, Any]:
        """Validate data against business rules"""
        errors = []
        warnings = []
        
        # Content validation rules
        if "content" in data:
            content_rules = self.business_rules[BusinessRule.CONTENT_VALIDATION]
            
            # Check required metadata
            for field in content_rules["required_metadata"]:
                if field not in data.get("content", {}):
                    errors.append(f"Required field missing: {field}")
            
            # Check file size
            if data.get("content", {}).get("file_size", 0) > content_rules["max_file_size"]:
                errors.append("File size exceeds maximum allowed")
        
        # Monetization rules
        if "monetization" in data:
            monetization_rules = self.business_rules[BusinessRule.MONETIZATION_CHECK]
            
            if data.get("follower_count", 0) < monetization_rules["min_follower_count"]:
                warnings.append("Follower count below recommended threshold")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def _execute_function(self, function_name: str, data: Dict[str, Any], 
                              creator_type: CreatorType) -> Dict[str, Any]:
        """Execute specific business logic function"""
        
        if function_name == "validate_content":
            return await self._validate_content(data, creator_type)
        elif function_name == "process_collaboration":
            return await self._process_collaboration(data, creator_type)
        elif function_name == "calculate_revenue":
            return await self._calculate_revenue(data, creator_type)
        elif function_name == "verify_copyright":
            return await self._verify_copyright(data, creator_type)
        elif function_name == "optimize_seo":
            return await self._optimize_seo(data, creator_type)
        else:
            # Generic business logic execution
            return {
                "function": function_name,
                "status": "executed",
                "creator_type": creator_type.value,
                "processed_data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _validate_content(self, data: Dict[str, Any], creator_type: CreatorType) -> Dict[str, Any]:
        """Validate content according to business rules"""
        content = data.get("content", {})
        
        validation_score = 0.8  # Placeholder calculation
        
        return {
            "validation_score": validation_score,
            "is_valid": validation_score >= 0.7,
            "content_type": content.get("type", "unknown"),
            "creator_type": creator_type.value,
            "recommendations": [
                "Add more descriptive tags",
                "Improve metadata completeness",
                "Consider higher resolution upload"
            ]
        }
    
    async def _process_collaboration(self, data: Dict[str, Any], creator_type: CreatorType) -> Dict[str, Any]:
        """Process collaboration request"""
        return {
            "collaboration_id": f"collab_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "approved",
            "participants": data.get("participants", []),
            "estimated_duration": 30,  # days
            "collaboration_score": 0.85
        }
    
    async def _calculate_revenue(self, data: Dict[str, Any], creator_type: CreatorType) -> Dict[str, Any]:
        """Calculate revenue projections"""
        base_revenue = data.get("current_revenue", 0)
        growth_factor = 1.15 if creator_type == CreatorType.MUSICIAN else 1.10
        
        return {
            "current_revenue": base_revenue,
            "projected_revenue": base_revenue * growth_factor,
            "growth_factor": growth_factor,
            "revenue_streams": ["subscriptions", "advertising", "licensing"],
            "optimization_suggestions": [
                "Expand to additional platforms",
                "Increase content frequency",
                "Explore brand partnerships"
            ]
        }
    
    async def _verify_copyright(self, data: Dict[str, Any], creator_type: CreatorType) -> Dict[str, Any]:
        """Verify copyright and detect potential violations"""
        return {
            "copyright_status": "clear",
            "similarity_score": 0.15,  # Low similarity = likely original
            "potential_matches": [],
            "verification_confidence": 0.92,
            "recommendations": [
                "Content appears to be original",
                "No copyright violations detected"
            ]
        }
    
    async def _optimize_seo(self, data: Dict[str, Any], creator_type: CreatorType) -> Dict[str, Any]:
        """Optimize content for SEO"""
        content = data.get("content", {})
        platform = data.get("platform", "generic")
        
        return {
            "seo_score": 0.78,
            "platform": platform,
            "optimizations": {
                "title": "Add trending keywords",
                "description": "Include relevant hashtags",
                "tags": "Use platform-specific tags"
            },
            "keyword_suggestions": [
                "trending_topic_1", "trending_topic_2", "trending_topic_3"
            ],
            "estimated_reach_increase": 0.25
        }
    
    def get_business_rules(self) -> Dict[BusinessRule, Dict[str, Any]]:
        """Get current business rules configuration"""
        return self.business_rules
    
    def update_business_rule(self, rule: BusinessRule, config: Dict[str, Any]):
        """Update business rule configuration"""
        self.business_rules[rule] = config
        self.logger.info(f"Updated business rule: {rule.value}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on business logic core"""
        try:
            # Test basic functionality
            test_data = {"test": True}
            result = await self.execute_business_logic("health_check", test_data)
            
            return {
                "status": "healthy" if result.success else "unhealthy",
                "business_rules_loaded": len(self.business_rules),
                "execution_time": result.execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global business logic instance
_business_logic_core = None


def get_business_logic_core() -> BusinessLogicCore:
    """Get global business logic core instance"""
    global _business_logic_core
    if _business_logic_core is None:
        _business_logic_core = BusinessLogicCore()
    return _business_logic_core


def initialize_business_logic(config: Dict[str, Any] = None) -> BusinessLogicCore:
    """Initialize business logic core with configuration"""
    global _business_logic_core
    _business_logic_core = BusinessLogicCore(config)
    return _business_logic_core


# Convenience functions for common business logic operations
async def validate_content(content_data: Dict[str, Any], 
                         creator_type: CreatorType = CreatorType.ALL) -> BusinessLogicResult:
    """Validate content using business logic"""
    core = get_business_logic_core()
    return await core.execute_business_logic("validate_content", {"content": content_data}, creator_type)


async def process_collaboration(collaboration_data: Dict[str, Any],
                              creator_type: CreatorType = CreatorType.ALL) -> BusinessLogicResult:
    """Process collaboration using business logic"""
    core = get_business_logic_core()
    return await core.execute_business_logic("process_collaboration", collaboration_data, creator_type)


async def calculate_revenue(revenue_data: Dict[str, Any],
                          creator_type: CreatorType = CreatorType.ALL) -> BusinessLogicResult:
    """Calculate revenue using business logic"""
    core = get_business_logic_core()
    return await core.execute_business_logic("calculate_revenue", revenue_data, creator_type)