"""
🚀 Pricing Validators - Comprehensive Pricing Validation System
==============================================================

Advanced validation system for pricing data integrity, business rule compliance,
and market reasonableness checks. Ensures all pricing decisions meet quality
standards and business requirements before implementation.

Project Team Specialists:
- Lead Dev IA: Advanced AI architecture and ML optimization algorithms
- Backend Senior: Enterprise-grade API development and microservices
- ML Engineer: Machine learning models for validation and anomaly detection
- DBA: High-performance database design and query optimization
- Security Expert: Enterprise security protocols and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Audio-specific validation rules
- DevOps: CI/CD pipelines and production deployment automation
- IA Prompt Engineer: AI prompt optimization and natural language processing

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️

This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code or its
underlying concepts without explicit written permission from Fahed Mlaiel is
strictly prohibited and will result in immediate legal action under German and
international copyright laws.

For licensing inquiries and authorization requests:
Email: mlaiel@live.de
All usage must be pre-approved in writing.
==============================================================
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json
import re
import uuid

# Internal imports
from ...core.database import DatabaseManager
from ...core.cache import CacheManager
from ...utils.exceptions import ValidationError, BusinessRuleError
from .models import PricingCalculation, UserSubscription, TierConfiguration

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation result severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class ValidationType(Enum):
    """Types of validation checks"""
    DATA_INTEGRITY = "data_integrity"
    BUSINESS_RULES = "business_rules"
    MARKET_REASONABLENESS = "market_reasonableness"
    PLATFORM_COMPLIANCE = "platform_compliance"
    SECURITY_CHECKS = "security_checks"
    PERFORMANCE_BOUNDS = "performance_bounds"
    TIER_COMPLIANCE = "tier_compliance"
    REGULATORY_COMPLIANCE = "regulatory_compliance"


@dataclass
class ValidationResult:
    """Individual validation result"""
    validation_id: str
    validation_type: ValidationType
    severity: ValidationSeverity
    field_name: Optional[str]
    message: str
    details: Dict[str, Any]
    suggested_fix: Optional[str]
    validation_timestamp: datetime


@dataclass
class ValidationReport:
    """Complete validation report"""
    request_id: str
    creator_id: str
    validation_timestamp: datetime
    overall_status: str
    total_checks: int
    errors: int
    warnings: int
    infos: int
    results: List[ValidationResult]
    summary: Dict[str, Any]
    is_valid: bool


class PricingValidator:
    """
    Comprehensive pricing validation system
    
    Features:
    - Data integrity validation
    - Business rule enforcement
    - Market reasonableness checks
    - Platform compliance verification
    - Security validation
    - Performance bounds checking
    - Tier compliance validation
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_manager: CacheManager
    ):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        
        # Validation rules configuration
        self.validation_rules = self._load_validation_rules()
        
    async def validate_pricing_request(
        self,
        creator_id: str,
        platform: str,
        content_type: str,
        base_price: Decimal,
        pricing_factors: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationReport:
        """Validate a complete pricing request"""
        
        request_id = str(uuid.uuid4())
        validation_results = []
        
        try:
            # Data integrity validation
            data_results = await self._validate_data_integrity(
                creator_id, platform, content_type, base_price, pricing_factors
            )
            validation_results.extend(data_results)
            
            # Business rules validation
            business_results = await self._validate_business_rules(
                creator_id, platform, content_type, base_price, pricing_factors, context
            )
            validation_results.extend(business_results)
            
            # Market reasonableness validation
            market_results = await self._validate_market_reasonableness(
                platform, content_type, base_price, pricing_factors
            )
            validation_results.extend(market_results)
            
            # Platform compliance validation
            platform_results = await self._validate_platform_compliance(
                platform, content_type, base_price, pricing_factors
            )
            validation_results.extend(platform_results)
            
            # Security validation
            security_results = await self._validate_security_requirements(
                creator_id, pricing_factors, context
            )
            validation_results.extend(security_results)
            
            # Performance bounds validation
            performance_results = await self._validate_performance_bounds(
                creator_id, base_price, pricing_factors
            )
            validation_results.extend(performance_results)
            
            # Tier compliance validation
            tier_results = await self._validate_tier_compliance(
                creator_id, pricing_factors, context
            )
            validation_results.extend(tier_results)
            
            # Count severity levels
            errors = len([r for r in validation_results if r.severity == ValidationSeverity.ERROR])
            warnings = len([r for r in validation_results if r.severity == ValidationSeverity.WARNING])
            infos = len([r for r in validation_results if r.severity == ValidationSeverity.INFO])
            
            # Determine overall status
            if errors > 0:
                overall_status = "failed"
                is_valid = False
            elif warnings > 0:
                overall_status = "warning"
                is_valid = True  # Can proceed with warnings
            else:
                overall_status = "success"
                is_valid = True
            
            # Generate summary
            summary = await self._generate_validation_summary(validation_results)
            
            return ValidationReport(
                request_id=request_id,
                creator_id=creator_id,
                validation_timestamp=datetime.utcnow(),
                overall_status=overall_status,
                total_checks=len(validation_results),
                errors=errors,
                warnings=warnings,
                infos=infos,
                results=validation_results,
                summary=summary,
                is_valid=is_valid
            )
            
        except Exception as e:
            logger.error(f"Error during pricing validation: {e}")
            
            # Return error report
            error_result = ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="validation_system",
                message=f"Validation system error: {str(e)}",
                details={'exception': str(e), 'type': type(e).__name__},
                suggested_fix="Contact system administrator",
                validation_timestamp=datetime.utcnow()
            )
            
            return ValidationReport(
                request_id=request_id,
                creator_id=creator_id,
                validation_timestamp=datetime.utcnow(),
                overall_status="system_error",
                total_checks=1,
                errors=1,
                warnings=0,
                infos=0,
                results=[error_result],
                summary={'system_error': True, 'error_message': str(e)},
                is_valid=False
            )
            
    async def validate_pricing_calculation(
        self,
        calculation: Dict[str, Any]
    ) -> ValidationReport:
        """Validate a pricing calculation result"""
        
        request_id = str(uuid.uuid4())
        validation_results = []
        
        try:
            # Validate calculation structure
            structure_results = await self._validate_calculation_structure(calculation)
            validation_results.extend(structure_results)
            
            # Validate calculation logic
            logic_results = await self._validate_calculation_logic(calculation)
            validation_results.extend(logic_results)
            
            # Validate result consistency
            consistency_results = await self._validate_result_consistency(calculation)
            validation_results.extend(consistency_results)
            
            # Validate confidence scores
            confidence_results = await self._validate_confidence_scores(calculation)
            validation_results.extend(confidence_results)
            
            # Count severity levels
            errors = len([r for r in validation_results if r.severity == ValidationSeverity.ERROR])
            warnings = len([r for r in validation_results if r.severity == ValidationSeverity.WARNING])
            infos = len([r for r in validation_results if r.severity == ValidationSeverity.INFO])
            
            # Determine overall status
            overall_status = "failed" if errors > 0 else ("warning" if warnings > 0 else "success")
            is_valid = errors == 0
            
            # Generate summary
            summary = await self._generate_validation_summary(validation_results)
            
            return ValidationReport(
                request_id=request_id,
                creator_id=calculation.get('creator_id', 'unknown'),
                validation_timestamp=datetime.utcnow(),
                overall_status=overall_status,
                total_checks=len(validation_results),
                errors=errors,
                warnings=warnings,
                infos=infos,
                results=validation_results,
                summary=summary,
                is_valid=is_valid
            )
            
        except Exception as e:
            logger.error(f"Error validating pricing calculation: {e}")
            raise ValidationError(f"Calculation validation failed: {e}")
    
    # Data integrity validation methods
    async def _validate_data_integrity(
        self,
        creator_id: str,
        platform: str,
        content_type: str,
        base_price: Decimal,
        pricing_factors: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate data integrity and format"""
        
        results = []
        
        # Validate creator_id
        if not creator_id or not isinstance(creator_id, str):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="creator_id",
                message="Creator ID is required and must be a non-empty string",
                details={'provided_value': creator_id, 'expected_type': 'str'},
                suggested_fix="Provide a valid creator ID string",
                validation_timestamp=datetime.utcnow()
            ))
        elif not re.match(r'^[a-zA-Z0-9_-]{3,50}$', creator_id):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="creator_id",
                message="Creator ID format is invalid",
                details={'provided_value': creator_id, 'pattern': '^[a-zA-Z0-9_-]{3,50}$'},
                suggested_fix="Use alphanumeric characters, hyphens, and underscores only (3-50 chars)",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Validate platform
        valid_platforms = ['spotify', 'youtube', 'instagram', 'tiktok', 'onlyfans', 'patreon', 'other']
        if not platform or platform.lower() not in valid_platforms:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="platform",
                message="Invalid or missing platform",
                details={'provided_value': platform, 'valid_platforms': valid_platforms},
                suggested_fix=f"Use one of: {', '.join(valid_platforms)}",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Validate content_type
        valid_content_types = [
            'audio', 'video', 'image', 'text', 'live_stream', 
            'course', 'tutorial', 'subscription', 'other'
        ]
        if not content_type or content_type.lower() not in valid_content_types:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="content_type",
                message="Invalid or missing content type",
                details={'provided_value': content_type, 'valid_types': valid_content_types},
                suggested_fix=f"Use one of: {', '.join(valid_content_types)}",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Validate base_price
        if not isinstance(base_price, Decimal):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="base_price",
                message="Base price must be a Decimal",
                details={'provided_type': type(base_price).__name__, 'expected_type': 'Decimal'},
                suggested_fix="Convert price to Decimal format",
                validation_timestamp=datetime.utcnow()
            ))
        elif base_price < Decimal('0'):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="base_price",
                message="Base price cannot be negative",
                details={'provided_value': float(base_price)},
                suggested_fix="Provide a positive price value",
                validation_timestamp=datetime.utcnow()
            ))
        elif base_price == Decimal('0'):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.WARNING,
                field_name="base_price",
                message="Base price is zero - unusual for paid content",
                details={'provided_value': float(base_price)},
                suggested_fix="Verify if zero price is intentional",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Validate pricing_factors structure
        if not isinstance(pricing_factors, dict):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                field_name="pricing_factors",
                message="Pricing factors must be a dictionary",
                details={'provided_type': type(pricing_factors).__name__},
                suggested_fix="Provide pricing factors as a dictionary",
                validation_timestamp=datetime.utcnow()
            ))
        elif not pricing_factors:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.DATA_INTEGRITY,
                severity=ValidationSeverity.WARNING,
                field_name="pricing_factors",
                message="No pricing factors provided - may limit optimization",
                details={'factor_count': 0},
                suggested_fix="Provide relevant market factors for better pricing",
                validation_timestamp=datetime.utcnow()
            ))
        
        return results
        
    async def _validate_business_rules(
        self,
        creator_id: str,
        platform: str,
        content_type: str,
        base_price: Decimal,
        pricing_factors: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validate business rules compliance"""
        
        results = []
        
        # Check creator exists and is active
        async with self.db_manager.get_session() as session:
            creator_subscription = session.query(UserSubscription).filter(
                UserSubscription.user_id == creator_id,
                UserSubscription.status == 'active'
            ).first()
            
            if not creator_subscription:
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.BUSINESS_RULES,
                    severity=ValidationSeverity.ERROR,
                    field_name="creator_id",
                    message="Creator has no active subscription",
                    details={'creator_id': creator_id},
                    suggested_fix="Ensure creator has active subscription before pricing",
                    validation_timestamp=datetime.utcnow()
                ))
            else:
                # Check tier-specific limits
                tier = creator_subscription.tier
                if tier:
                    tier_limits = await self._get_tier_limits(tier.tier_name)
                    
                    # Check pricing calculation limits
                    if base_price > tier_limits.get('max_base_price', Decimal('999999')):
                        results.append(ValidationResult(
                            validation_id=str(uuid.uuid4()),
                            validation_type=ValidationType.TIER_COMPLIANCE,
                            severity=ValidationSeverity.ERROR,
                            field_name="base_price",
                            message=f"Base price exceeds tier limit of ${tier_limits['max_base_price']}",
                            details={
                                'tier': tier.tier_name,
                                'limit': float(tier_limits['max_base_price']),
                                'provided': float(base_price)
                            },
                            suggested_fix="Reduce price or upgrade tier",
                            validation_timestamp=datetime.utcnow()
                        ))
        
        # Platform-specific business rules
        platform_rules = self.validation_rules.get('platform_rules', {}).get(platform.lower(), {})
        
        # Check minimum price requirements
        min_price = platform_rules.get('min_price', Decimal('0'))
        if base_price < min_price:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.BUSINESS_RULES,
                severity=ValidationSeverity.ERROR,
                field_name="base_price",
                message=f"Price below platform minimum of ${min_price}",
                details={'platform': platform, 'minimum': float(min_price), 'provided': float(base_price)},
                suggested_fix=f"Increase price to at least ${min_price}",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Check maximum price recommendations
        max_recommended = platform_rules.get('max_recommended_price', Decimal('10000'))
        if base_price > max_recommended:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.BUSINESS_RULES,
                severity=ValidationSeverity.WARNING,
                field_name="base_price",
                message=f"Price above platform recommended maximum of ${max_recommended}",
                details={'platform': platform, 'recommended_max': float(max_recommended), 'provided': float(base_price)},
                suggested_fix="Consider if high pricing is appropriate for target audience",
                validation_timestamp=datetime.utcnow()
            ))
        
        return results
        
    async def _validate_market_reasonableness(
        self,
        platform: str,
        content_type: str,
        base_price: Decimal,
        pricing_factors: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate market reasonableness of pricing"""
        
        results = []
        
        # Get market data for comparison (mock implementation)
        market_ranges = await self._get_market_price_ranges(platform, content_type)
        
        # Check if price is within reasonable market range
        market_min = market_ranges.get('min', Decimal('1'))
        market_max = market_ranges.get('max', Decimal('1000'))
        market_avg = market_ranges.get('average', Decimal('50'))
        
        if base_price < market_min:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.MARKET_REASONABLENESS,
                severity=ValidationSeverity.WARNING,
                field_name="base_price",
                message=f"Price significantly below market minimum (${market_min})",
                details={
                    'market_min': float(market_min),
                    'market_avg': float(market_avg),
                    'provided': float(base_price),
                    'deviation_percent': float(((base_price - market_avg) / market_avg) * 100)
                },
                suggested_fix="Consider if underpricing is intentional or adjust to market rates",
                validation_timestamp=datetime.utcnow()
            ))
        elif base_price > market_max:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.MARKET_REASONABLENESS,
                severity=ValidationSeverity.WARNING,
                field_name="base_price",
                message=f"Price significantly above market maximum (${market_max})",
                details={
                    'market_max': float(market_max),
                    'market_avg': float(market_avg),
                    'provided': float(base_price),
                    'deviation_percent': float(((base_price - market_avg) / market_avg) * 100)
                },
                suggested_fix="Ensure premium pricing is justified by unique value proposition",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Check price deviation from market average
        deviation_percent = abs(((base_price - market_avg) / market_avg) * 100)
        if deviation_percent > 200:  # More than 200% deviation
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.MARKET_REASONABLENESS,
                severity=ValidationSeverity.INFO,
                field_name="base_price",
                message=f"Price deviates {deviation_percent:.1f}% from market average",
                details={
                    'market_avg': float(market_avg),
                    'deviation_percent': float(deviation_percent),
                    'is_above_average': base_price > market_avg
                },
                suggested_fix="Review pricing strategy and market positioning",
                validation_timestamp=datetime.utcnow()
            ))
        
        return results
        
    async def _validate_platform_compliance(
        self,
        platform: str,
        content_type: str,
        base_price: Decimal,
        pricing_factors: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate platform-specific compliance requirements"""
        
        results = []
        
        # Platform-specific validation rules
        platform_lower = platform.lower()
        
        if platform_lower == 'spotify':
            # Spotify-specific validations
            if content_type not in ['audio', 'course']:
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.PLATFORM_COMPLIANCE,
                    severity=ValidationSeverity.WARNING,
                    field_name="content_type",
                    message="Spotify primarily supports audio content",
                    details={'platform': platform, 'content_type': content_type},
                    suggested_fix="Consider if content type is appropriate for platform",
                    validation_timestamp=datetime.utcnow()
                ))
        
        elif platform_lower == 'youtube':
            # YouTube-specific validations
            if base_price > Decimal('500') and content_type == 'video':
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.PLATFORM_COMPLIANCE,
                    severity=ValidationSeverity.INFO,
                    field_name="base_price",
                    message="High pricing for YouTube video content",
                    details={'platform': platform, 'price': float(base_price)},
                    suggested_fix="Verify pricing aligns with YouTube audience expectations",
                    validation_timestamp=datetime.utcnow()
                ))
        
        elif platform_lower in ['onlyfans', 'patreon']:
            # Subscription platform validations
            if base_price < Decimal('5'):
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.PLATFORM_COMPLIANCE,
                    severity=ValidationSeverity.WARNING,
                    field_name="base_price",
                    message=f"{platform} typically has higher minimum pricing",
                    details={'platform': platform, 'price': float(base_price)},
                    suggested_fix="Consider platform fee structure in pricing",
                    validation_timestamp=datetime.utcnow()
                ))
        
        return results
        
    async def _validate_security_requirements(
        self,
        creator_id: str,
        pricing_factors: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validate security requirements"""
        
        results = []
        
        # Check for sensitive data in pricing factors
        sensitive_patterns = [
            r'password', r'token', r'secret', r'key', r'credential',
            r'ssn', r'social.*security', r'credit.*card', r'bank.*account'
        ]
        
        for key, value in pricing_factors.items():
            if isinstance(value, str):
                for pattern in sensitive_patterns:
                    if re.search(pattern, key.lower()) or re.search(pattern, value.lower()):
                        results.append(ValidationResult(
                            validation_id=str(uuid.uuid4()),
                            validation_type=ValidationType.SECURITY_CHECKS,
                            severity=ValidationSeverity.ERROR,
                            field_name=key,
                            message="Potentially sensitive data detected in pricing factors",
                            details={'field': key, 'pattern_matched': pattern},
                            suggested_fix="Remove sensitive information from pricing data",
                            validation_timestamp=datetime.utcnow()
                        ))
        
        # Validate request origin if provided
        if context and 'request_origin' in context:
            origin = context['request_origin']
            if not self._is_valid_origin(origin):
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.SECURITY_CHECKS,
                    severity=ValidationSeverity.WARNING,
                    field_name="request_origin",
                    message="Request from unverified origin",
                    details={'origin': origin},
                    suggested_fix="Verify request origin is authorized",
                    validation_timestamp=datetime.utcnow()
                ))
        
        return results
        
    async def _validate_performance_bounds(
        self,
        creator_id: str,
        base_price: Decimal,
        pricing_factors: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate performance bounds and limits"""
        
        results = []
        
        # Check pricing factors complexity
        factors_count = len(pricing_factors)
        if factors_count > 50:
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.PERFORMANCE_BOUNDS,
                severity=ValidationSeverity.WARNING,
                field_name="pricing_factors",
                message=f"High number of pricing factors ({factors_count}) may impact performance",
                details={'factor_count': factors_count, 'recommended_max': 50},
                suggested_fix="Consider reducing number of pricing factors",
                validation_timestamp=datetime.utcnow()
            ))
        
        # Check for extremely large price values that might cause overflow
        if base_price > Decimal('1000000'):
            results.append(ValidationResult(
                validation_id=str(uuid.uuid4()),
                validation_type=ValidationType.PERFORMANCE_BOUNDS,
                severity=ValidationSeverity.WARNING,
                field_name="base_price",
                message="Extremely high price value may cause calculation issues",
                details={'price': float(base_price), 'recommended_max': 1000000},
                suggested_fix="Verify price is in correct currency and scale",
                validation_timestamp=datetime.utcnow()
            ))
        
        return results
        
    async def _validate_tier_compliance(
        self,
        creator_id: str,
        pricing_factors: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validate tier-specific compliance"""
        
        results = []
        
        # Get creator's tier information
        async with self.db_manager.get_session() as session:
            subscription = session.query(UserSubscription).filter(
                UserSubscription.user_id == creator_id,
                UserSubscription.status == 'active'
            ).first()
            
            if subscription and subscription.tier:
                tier_name = subscription.tier.tier_name
                tier_limits = await self._get_tier_limits(tier_name)
                
                # Check advanced features usage
                advanced_features = pricing_factors.get('advanced_features', [])
                if isinstance(advanced_features, list) and advanced_features:
                    allowed_features = tier_limits.get('allowed_features', [])
                    
                    for feature in advanced_features:
                        if feature not in allowed_features:
                            results.append(ValidationResult(
                                validation_id=str(uuid.uuid4()),
                                validation_type=ValidationType.TIER_COMPLIANCE,
                                severity=ValidationSeverity.ERROR,
                                field_name="advanced_features",
                                message=f"Feature '{feature}' not available in {tier_name} tier",
                                details={
                                    'tier': tier_name,
                                    'feature': feature,
                                    'allowed_features': allowed_features
                                },
                                suggested_fix=f"Upgrade tier or remove '{feature}' feature",
                                validation_timestamp=datetime.utcnow()
                            ))
                
                # Check calculation frequency limits
                calculation_count = await self._get_recent_calculation_count(creator_id)
                max_calculations = tier_limits.get('max_calculations_per_hour', 100)
                
                if calculation_count >= max_calculations:
                    results.append(ValidationResult(
                        validation_id=str(uuid.uuid4()),
                        validation_type=ValidationType.TIER_COMPLIANCE,
                        severity=ValidationSeverity.ERROR,
                        field_name="calculation_frequency",
                        message=f"Calculation limit exceeded ({calculation_count}/{max_calculations})",
                        details={
                            'tier': tier_name,
                            'current_count': calculation_count,
                            'limit': max_calculations
                        },
                        suggested_fix="Wait for limit reset or upgrade tier",
                        validation_timestamp=datetime.utcnow()
                    ))
        
        return results
    
    # Calculation validation methods
    async def _validate_calculation_structure(
        self,
        calculation: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate calculation result structure"""
        
        results = []
        required_fields = [
            'creator_id', 'base_price', 'optimized_price', 
            'confidence_score', 'pricing_strategy'
        ]
        
        for field in required_fields:
            if field not in calculation:
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.DATA_INTEGRITY,
                    severity=ValidationSeverity.ERROR,
                    field_name=field,
                    message=f"Required field '{field}' missing from calculation",
                    details={'required_fields': required_fields},
                    suggested_fix=f"Include '{field}' in calculation result",
                    validation_timestamp=datetime.utcnow()
                ))
        
        return results
        
    async def _validate_calculation_logic(
        self,
        calculation: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate calculation logic and consistency"""
        
        results = []
        
        base_price = calculation.get('base_price')
        optimized_price = calculation.get('optimized_price')
        
        if base_price and optimized_price:
            try:
                base_decimal = Decimal(str(base_price))
                optimized_decimal = Decimal(str(optimized_price))
                
                # Check for reasonable price changes
                if optimized_decimal < Decimal('0'):
                    results.append(ValidationResult(
                        validation_id=str(uuid.uuid4()),
                        validation_type=ValidationType.DATA_INTEGRITY,
                        severity=ValidationSeverity.ERROR,
                        field_name="optimized_price",
                        message="Optimized price cannot be negative",
                        details={'optimized_price': float(optimized_decimal)},
                        suggested_fix="Review calculation algorithm",
                        validation_timestamp=datetime.utcnow()
                    ))
                
                # Check for extreme price changes
                if base_decimal > 0:
                    change_percent = ((optimized_decimal - base_decimal) / base_decimal) * 100
                    if abs(change_percent) > 500:  # 500% change
                        results.append(ValidationResult(
                            validation_id=str(uuid.uuid4()),
                            validation_type=ValidationType.MARKET_REASONABLENESS,
                            severity=ValidationSeverity.WARNING,
                            field_name="price_change",
                            message=f"Extreme price change detected ({change_percent:.1f}%)",
                            details={
                                'base_price': float(base_decimal),
                                'optimized_price': float(optimized_decimal),
                                'change_percent': float(change_percent)
                            },
                            suggested_fix="Verify calculation parameters and algorithm",
                            validation_timestamp=datetime.utcnow()
                        ))
                
            except (InvalidOperation, ValueError) as e:
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.DATA_INTEGRITY,
                    severity=ValidationSeverity.ERROR,
                    field_name="price_calculation",
                    message=f"Invalid price values in calculation: {e}",
                    details={'base_price': base_price, 'optimized_price': optimized_price},
                    suggested_fix="Ensure price values are valid decimal numbers",
                    validation_timestamp=datetime.utcnow()
                ))
        
        return results
        
    async def _validate_result_consistency(
        self,
        calculation: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate internal consistency of calculation results"""
        
        results = []
        
        # Check confidence score consistency with price changes
        confidence_score = calculation.get('confidence_score', 0)
        base_price = calculation.get('base_price')
        optimized_price = calculation.get('optimized_price')
        
        if base_price and optimized_price and confidence_score:
            try:
                base_decimal = Decimal(str(base_price))
                optimized_decimal = Decimal(str(optimized_price))
                
                if base_decimal > 0:
                    change_magnitude = abs((optimized_decimal - base_decimal) / base_decimal)
                    
                    # High confidence should not have extreme changes
                    if confidence_score > 0.9 and change_magnitude > 2.0:  # >200% change
                        results.append(ValidationResult(
                            validation_id=str(uuid.uuid4()),
                            validation_type=ValidationType.DATA_INTEGRITY,
                            severity=ValidationSeverity.WARNING,
                            field_name="confidence_consistency",
                            message="High confidence score with extreme price change",
                            details={
                                'confidence_score': confidence_score,
                                'change_magnitude': float(change_magnitude),
                                'expected_low_change': True
                            },
                            suggested_fix="Review confidence calculation or price optimization logic",
                            validation_timestamp=datetime.utcnow()
                        ))
                    
                    # Low confidence should not have minimal changes
                    elif confidence_score < 0.3 and change_magnitude < 0.05:  # <5% change
                        results.append(ValidationResult(
                            validation_id=str(uuid.uuid4()),
                            validation_type=ValidationType.DATA_INTEGRITY,
                            severity=ValidationSeverity.INFO,
                            field_name="confidence_consistency",
                            message="Low confidence score with minimal price change",
                            details={
                                'confidence_score': confidence_score,
                                'change_magnitude': float(change_magnitude),
                                'expected_more_change': True
                            },
                            suggested_fix="Consider if low confidence reflects calculation uncertainty",
                            validation_timestamp=datetime.utcnow()
                        ))
                
            except (InvalidOperation, ValueError, TypeError):
                pass  # Already handled in other validations
        
        return results
        
    async def _validate_confidence_scores(
        self,
        calculation: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate confidence scores"""
        
        results = []
        
        confidence_score = calculation.get('confidence_score')
        
        if confidence_score is not None:
            try:
                score_float = float(confidence_score)
                
                if not (0 <= score_float <= 1):
                    results.append(ValidationResult(
                        validation_id=str(uuid.uuid4()),
                        validation_type=ValidationType.DATA_INTEGRITY,
                        severity=ValidationSeverity.ERROR,
                        field_name="confidence_score",
                        message="Confidence score must be between 0 and 1",
                        details={'provided_score': score_float, 'valid_range': '0-1'},
                        suggested_fix="Normalize confidence score to 0-1 range",
                        validation_timestamp=datetime.utcnow()
                    ))
                elif score_float < 0.1:
                    results.append(ValidationResult(
                        validation_id=str(uuid.uuid4()),
                        validation_type=ValidationType.DATA_INTEGRITY,
                        severity=ValidationSeverity.WARNING,
                        field_name="confidence_score",
                        message="Very low confidence score indicates unreliable calculation",
                        details={'confidence_score': score_float, 'threshold': 0.1},
                        suggested_fix="Review calculation inputs and algorithm",
                        validation_timestamp=datetime.utcnow()
                    ))
                
            except (ValueError, TypeError):
                results.append(ValidationResult(
                    validation_id=str(uuid.uuid4()),
                    validation_type=ValidationType.DATA_INTEGRITY,
                    severity=ValidationSeverity.ERROR,
                    field_name="confidence_score",
                    message="Confidence score must be a numeric value",
                    details={'provided_type': type(confidence_score).__name__},
                    suggested_fix="Provide confidence score as float between 0 and 1",
                    validation_timestamp=datetime.utcnow()
                ))
        
        return results
    
    # Helper methods
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration"""
        
        return {
            'platform_rules': {
                'spotify': {
                    'min_price': Decimal('0.99'),
                    'max_recommended_price': Decimal('99.99'),
                    'supported_content_types': ['audio', 'course']
                },
                'youtube': {
                    'min_price': Decimal('0.00'),
                    'max_recommended_price': Decimal('499.99'),
                    'supported_content_types': ['video', 'live_stream', 'course']
                },
                'instagram': {
                    'min_price': Decimal('1.00'),
                    'max_recommended_price': Decimal('199.99'),
                    'supported_content_types': ['image', 'video', 'live_stream']
                },
                'tiktok': {
                    'min_price': Decimal('0.99'),
                    'max_recommended_price': Decimal('99.99'),
                    'supported_content_types': ['video', 'live_stream']
                },
                'onlyfans': {
                    'min_price': Decimal('4.99'),
                    'max_recommended_price': Decimal('999.99'),
                    'supported_content_types': ['image', 'video', 'text', 'subscription']
                },
                'patreon': {
                    'min_price': Decimal('1.00'),
                    'max_recommended_price': Decimal('999.99'),
                    'supported_content_types': ['subscription', 'course', 'text', 'image', 'video']
                }
            },
            'tier_limits': {
                'starter': {
                    'max_base_price': Decimal('99.99'),
                    'max_calculations_per_hour': 10,
                    'allowed_features': ['basic_pricing', 'single_platform']
                },
                'professional': {
                    'max_base_price': Decimal('499.99'),
                    'max_calculations_per_hour': 50,
                    'allowed_features': ['basic_pricing', 'multi_platform', 'analytics']
                },
                'premium': {
                    'max_base_price': Decimal('1999.99'),
                    'max_calculations_per_hour': 200,
                    'allowed_features': ['all_pricing', 'multi_platform', 'analytics', 'ai_optimization']
                },
                'enterprise': {
                    'max_base_price': Decimal('9999.99'),
                    'max_calculations_per_hour': 1000,
                    'allowed_features': ['all_features']
                },
                'celebrity': {
                    'max_base_price': Decimal('99999.99'),
                    'max_calculations_per_hour': 10000,
                    'allowed_features': ['all_features', 'custom_features']
                }
            }
        }
        
    async def _get_tier_limits(self, tier_name: str) -> Dict[str, Any]:
        """Get limits for a specific tier"""
        
        return self.validation_rules.get('tier_limits', {}).get(tier_name.lower(), {
            'max_base_price': Decimal('99.99'),
            'max_calculations_per_hour': 10,
            'allowed_features': ['basic_pricing']
        })
        
    async def _get_market_price_ranges(
        self,
        platform: str,
        content_type: str
    ) -> Dict[str, Decimal]:
        """Get market price ranges for validation (mock implementation)"""
        
        # Mock market data - replace with real market intelligence
        base_ranges = {
            'audio': {'min': Decimal('0.99'), 'max': Decimal('99.99'), 'average': Decimal('19.99')},
            'video': {'min': Decimal('1.99'), 'max': Decimal('199.99'), 'average': Decimal('39.99')},
            'image': {'min': Decimal('0.99'), 'max': Decimal('49.99'), 'average': Decimal('9.99')},
            'course': {'min': Decimal('9.99'), 'max': Decimal('999.99'), 'average': Decimal('99.99')},
            'subscription': {'min': Decimal('4.99'), 'max': Decimal('99.99'), 'average': Decimal('19.99')}
        }
        
        return base_ranges.get(content_type.lower(), {
            'min': Decimal('1.00'),
            'max': Decimal('100.00'),
            'average': Decimal('25.00')
        })
        
    async def _get_recent_calculation_count(self, creator_id: str) -> int:
        """Get recent calculation count for rate limiting"""
        
        try:
            cache_key = f"calculation_count:{creator_id}:{datetime.utcnow().hour}"
            count = await self.cache_manager.get(cache_key)
            return int(count) if count else 0
        except Exception:
            return 0
            
    def _is_valid_origin(self, origin: str) -> bool:
        """Validate request origin"""
        
        valid_origins = [
            'localhost',
            'ia-influencer.com',
            'app.ia-influencer.com',
            'api.ia-influencer.com'
        ]
        
        return any(valid_origin in origin for valid_origin in valid_origins)
        
    async def _generate_validation_summary(
        self,
        validation_results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        
        return {
            'validation_types': {
                vtype.value: len([r for r in validation_results if r.validation_type == vtype])
                for vtype in ValidationType
            },
            'severity_distribution': {
                severity.value: len([r for r in validation_results if r.severity == severity])
                for severity in ValidationSeverity
            },
            'field_issues': {
                result.field_name: len([r for r in validation_results if r.field_name == result.field_name])
                for result in validation_results
                if result.field_name
            },
            'has_blocking_errors': any(r.severity == ValidationSeverity.ERROR for r in validation_results),
            'recommendation': self._get_validation_recommendation(validation_results)
        }
        
    def _get_validation_recommendation(
        self,
        validation_results: List[ValidationResult]
    ) -> str:
        """Get overall validation recommendation"""
        
        errors = [r for r in validation_results if r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in validation_results if r.severity == ValidationSeverity.WARNING]
        
        if errors:
            return f"Fix {len(errors)} error(s) before proceeding with pricing calculation"
        elif len(warnings) > 5:
            return f"Review {len(warnings)} warnings to improve pricing quality"
        elif warnings:
            return "Minor issues detected - proceed with caution"
        else:
            return "All validation checks passed - ready for pricing optimization"
