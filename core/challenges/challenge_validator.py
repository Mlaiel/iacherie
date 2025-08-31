"""✅ Challenge Validator - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/core/challenges/challenge_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Challenge Validation System - Production-Ready
Responsibility: Enterprise challenge validation, compliance, and fraud detection
=============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Challenge Submission → Multi-Layer Validation → Compliance Checking → 
Fraud Detection → Quality Assessment → Progress Verification → Approval/Rejection

VALIDATION ARCHITECTURE:
Input Sanitization → Business Rules → Compliance Engine → 
Fraud Detection → Quality Gates → Performance Validation → Security Audit
"""from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import logging
import asyncio
import re
import json
from abc import ABC, abstractmethod

class ValidationSeverity(Enum):
    """Validation issue severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class ValidationCategory(Enum):
    """Validation categories"""    BUSINESS_RULES = "business_rules"
    DATA_INTEGRITY = "data_integrity"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    FRAUD_DETECTION = "fraud_detection"
    CONTENT_POLICY = "content_policy"

class ValidationStatus(Enum):
    """Validation result status"""    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"
    FLAGGED = "flagged"
    APPROVED = "approved"
    REJECTED = "rejected"

class FraudRiskLevel(Enum):
    """Fraud risk assessment levels"""    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationRule:
    """Individual validation rule specification"""    rule_id: str
    rule_name: str
    description: str
    category: ValidationCategory
    severity: ValidationSeverity
    validation_function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_enabled: bool = True
    requires_human_review: bool = False
    auto_fix_possible: bool = False
    error_message_template: str = ""
    
@dataclass
class ValidationIssue:
    """Individual validation issue"""    issue_id: str
    rule_id: str
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    field_path: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    requires_human_review: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Complete validation result"""    validation_id: str
    status: ValidationStatus
    overall_score: float  # 0.0 to 100.0
    fraud_risk_level: FraudRiskLevel
    issues: List[ValidationIssue]
    passed_rules: List[str]
    failed_rules: List[str]
    security_flags: List[str]
    compliance_status: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    validation_timestamp: datetime
    processing_time_ms: float
    validator_version: str = "1.0"

class ComplianceChecker:
    """Enterprise compliance validation system"""    
    def __init__(self):
        """Initialize compliance checker"""        self.logger = logging.getLogger(__name__)
        
        # Compliance frameworks
        self._compliance_frameworks = {
            "GDPR": {
                "data_protection": True,
                "user_consent": True,
                "data_minimization": True,
                "right_to_erasure": True
            },
            "COPPA": {
                "age_verification": True,
                "parental_consent": True,
                "data_collection_limits": True
            },
            "CCPA": {
                "privacy_rights": True,
                "data_transparency": True,
                "opt_out_rights": True
            },
            "PLATFORM_POLICIES": {
                "content_guidelines": True,
                "community_standards": True,
                "monetization_policies": True,
                "copyright_compliance": True
            }
        }
        
        # Content policy rules
        self._content_policies = {
            "inappropriate_content": {
                "adult_content": False,
                "violence": False,
                "hate_speech": False,
                "harassment": False
            },
            "copyright": {
                "original_content": True,
                "proper_attribution": True,
                "fair_use_compliance": True
            },
            "quality_standards": {
                "minimum_duration": 10,  # seconds
                "minimum_resolution": "720p",
                "audio_quality": "acceptable"
            }
        }
    
    async def check_compliance(self, 
                             challenge_data: Dict[str, Any],
                             user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive compliance checking"""        try:
            compliance_results = {
                "overall_compliant": True,
                "framework_results": {},
                "policy_violations": [],
                "recommendations": [],
                "risk_assessment": "low"
            }
            
            # Check each compliance framework
            for framework, requirements in self._compliance_frameworks.items():
                framework_result = await self._check_framework_compliance(
                    framework, requirements, challenge_data, user_context
                )
                compliance_results["framework_results"][framework] = framework_result
                
                if not framework_result["compliant"]:
                    compliance_results["overall_compliant"] = False
                    compliance_results["policy_violations"].extend(
                        framework_result.get("violations", [])
                    )
            
            # Content policy check
            content_check = await self._check_content_policies(challenge_data)
            if not content_check["compliant"]:
                compliance_results["overall_compliant"] = False
                compliance_results["policy_violations"].extend(
                    content_check.get("violations", [])
                )
            
            # Risk assessment
            compliance_results["risk_assessment"] = self._assess_compliance_risk(
                compliance_results
            )
            
            # Generate recommendations
            compliance_results["recommendations"] = self._generate_compliance_recommendations(
                compliance_results
            )
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            return {
                "overall_compliant": False,
                "error": str(e),
                "risk_assessment": "high"
            }
    
    async def _check_framework_compliance(self,
                                        framework: str,
                                        requirements: Dict[str, Any],
                                        challenge_data: Dict[str, Any],
                                        user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with specific framework"""        result = {
            "framework": framework,
            "compliant": True,
            "violations": [],
            "requirements_met": [],
            "score": 100.0
        }
        
        if framework == "GDPR":
            # GDPR specific checks
            if not user_context.get("consent_given", False):
                result["compliant"] = False
                result["violations"].append("Missing user consent for data processing")
            
            if challenge_data.get("collects_personal_data", False):
                if not challenge_data.get("data_purpose_specified", False):
                    result["compliant"] = False
                    result["violations"].append("Data collection purpose not specified")
        
        elif framework == "COPPA":
            # COPPA specific checks
            user_age = user_context.get("age", 18)
            if user_age < 13:
                if not user_context.get("parental_consent", False):
                    result["compliant"] = False
                    result["violations"].append("Parental consent required for users under 13")
        
        elif framework == "PLATFORM_POLICIES":
            # Platform policy checks
            if challenge_data.get("monetization_enabled", False):
                if not challenge_data.get("monetization_compliant", True):
                    result["compliant"] = False
                    result["violations"].append("Monetization policy violation")
        
        # Calculate compliance score
        if result["violations"]:
            violation_penalty = len(result["violations"]) * 20
            result["score"] = max(0, 100 - violation_penalty)
        
        return result
    
    async def _check_content_policies(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check content policy compliance"""        result = {
            "compliant": True,
            "violations": [],
            "quality_score": 100.0
        }
        
        # Check for inappropriate content flags
        content_flags = challenge_data.get("content_flags", [])
        inappropriate_flags = ["adult_content", "violence", "hate_speech", "harassment"]
        
        for flag in content_flags:
            if flag in inappropriate_flags:
                result["compliant"] = False
                result["violations"].append(f"Inappropriate content detected: {flag}")
        
        # Check copyright compliance
        if not challenge_data.get("original_content", True):
            if not challenge_data.get("proper_attribution", False):
                result["compliant"] = False
                result["violations"].append("Copyright attribution missing")
        
        # Quality standards check
        duration = challenge_data.get("content_duration", 0)
        if duration < self._content_policies["quality_standards"]["minimum_duration"]:
            result["violations"].append("Content duration below minimum requirement")
        
        return result
    
    def _assess_compliance_risk(self, compliance_results: Dict[str, Any]) -> str:
        """Assess overall compliance risk level"""        violations = len(compliance_results.get("policy_violations", []))
        
        if violations == 0:
            return "minimal"
        elif violations <= 2:
            return "low"
        elif violations <= 5:
            return "medium"
        elif violations <= 10:
            return "high"
        else:
            return "critical"
    
    def _generate_compliance_recommendations(self, 
                                           compliance_results: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations"""        recommendations = []
        
        violations = compliance_results.get("policy_violations", [])
        
        for violation in violations:
            if "consent" in violation.lower():
                recommendations.append("Implement proper user consent mechanisms")
            elif "attribution" in violation.lower():
                recommendations.append("Add proper copyright attribution to content")
            elif "inappropriate" in violation.lower():
                recommendations.append("Review and remove inappropriate content")
            elif "quality" in violation.lower():
                recommendations.append("Improve content quality to meet standards")
        
        # Add general recommendations
        if len(violations) > 5:
            recommendations.append("Consider comprehensive compliance audit")
        
        return list(set(recommendations))  # Remove duplicates

class RequirementValidator:
    """Challenge requirement validation system"""    
    def __init__(self):
        """Initialize requirement validator"""        self.logger = logging.getLogger(__name__)
        
        # Validation thresholds
        self._thresholds = {
            "content_quality_min": 5.0,
            "engagement_rate_min": 1.0,
            "upload_count_max_daily": 50,
            "collaboration_count_max_daily": 20,
            "revenue_threshold_suspicious": 10000.0,
            "view_count_max_hourly": 1000000
        }
        
        # Requirement types and their validators
        self._requirement_validators = {
            "upload_count": self._validate_upload_count,
            "quality_score": self._validate_quality_score,
            "engagement_rate": self._validate_engagement_rate,
            "collaboration_count": self._validate_collaboration_count,
            "revenue_generated": self._validate_revenue_generated,
            "view_count": self._validate_view_count,
            "completion_time": self._validate_completion_time
        }
    
    async def validate_requirements(self, 
                                  challenge_requirements: List[Dict[str, Any]],
                                  user_progress: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate challenge requirements against user progress"""        try:
            validation_results = {
                "overall_valid": True,
                "requirements_met": [],
                "requirements_failed": [],
                "suspicious_activities": [],
                "completion_percentage": 0.0,
                "fraud_indicators": []
            }
            
            total_requirements = len(challenge_requirements)
            met_requirements = 0
            
            for requirement in challenge_requirements:
                requirement_type = requirement.get("metric_type")
                target_value = requirement.get("target_value", 0)
                current_value = user_progress.get(requirement_type, 0)
                
                # Validate requirement
                validator = self._requirement_validators.get(requirement_type)
                if validator:
                    validation_result = await validator(
                        requirement, current_value, context
                    )
                    
                    if validation_result["valid"]:
                        validation_results["requirements_met"].append({
                            "requirement": requirement_type,
                            "target": target_value,
                            "achieved": current_value,
                            "validation": validation_result
                        })
                        met_requirements += 1
                    else:
                        validation_results["requirements_failed"].append({
                            "requirement": requirement_type,
                            "target": target_value,
                            "achieved": current_value,
                            "validation": validation_result
                        })
                        validation_results["overall_valid"] = False
                    
                    # Check for suspicious activity
                    if validation_result.get("suspicious", False):
                        validation_results["suspicious_activities"].append({
                            "requirement": requirement_type,
                            "reason": validation_result.get("suspicious_reason"),
                            "severity": validation_result.get("severity", "medium")
                        })
                    
                    # Check for fraud indicators
                    fraud_indicators = validation_result.get("fraud_indicators", [])
                    validation_results["fraud_indicators"].extend(fraud_indicators)
            
            # Calculate completion percentage
            validation_results["completion_percentage"] = (
                met_requirements / total_requirements * 100 if total_requirements > 0 else 0
            )
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Requirement validation failed: {str(e)}")
            return {
                "overall_valid": False,
                "error": str(e),
                "completion_percentage": 0.0
            }
    
    async def _validate_upload_count(self, 
                                   requirement: Dict[str, Any],
                                   current_value: Union[int, float],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate upload count requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value >= target
        
        # Check for suspicious activity
        time_window = context.get("time_window_hours", 24)
        uploads_per_hour = current_value / time_window if time_window > 0 else 0
        
        suspicious = False
        fraud_indicators = []
        
        if uploads_per_hour > 10:  # More than 10 uploads per hour
            suspicious = True
            fraud_indicators.append("Unusually high upload frequency")
        
        if current_value > self._thresholds["upload_count_max_daily"]:
            suspicious = True
            fraud_indicators.append("Upload count exceeds daily maximum")
        
        return {
            "valid": is_met,
            "target": target,
            "achieved": current_value,
            "percentage": (current_value / target * 100) if target > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators,
            "suspicious_reason": "Abnormal upload patterns" if suspicious else None
        }
    
    async def _validate_quality_score(self, 
                                    requirement: Dict[str, Any],
                                    current_value: Union[int, float],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality score requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value >= target
        
        # Check minimum quality threshold
        below_minimum = current_value < self._thresholds["content_quality_min"]
        
        suspicious = False
        fraud_indicators = []
        
        # Check for artificially high scores
        if current_value > 9.5 and context.get("sample_size", 1) < 10:
            suspicious = True
            fraud_indicators.append("Suspiciously high quality score with low sample size")
        
        return {
            "valid": is_met and not below_minimum,
            "target": target,
            "achieved": current_value,
            "percentage": (current_value / target * 100) if target > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators,
            "quality_issues": ["Below minimum quality threshold"] if below_minimum else []
        }
    
    async def _validate_engagement_rate(self, 
                                      requirement: Dict[str, Any],
                                      current_value: Union[int, float],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate engagement rate requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value >= target
        
        suspicious = False
        fraud_indicators = []
        
        # Check for unrealistic engagement rates
        if current_value > 50:  # More than 50% engagement rate
            suspicious = True
            fraud_indicators.append("Unusually high engagement rate")
        
        # Check engagement consistency
        engagement_history = context.get("engagement_history", [])
        if engagement_history:
            avg_historical = sum(engagement_history) / len(engagement_history)
            if current_value > avg_historical * 3:  # 3x historical average
                suspicious = True
                fraud_indicators.append("Engagement rate spike inconsistent with history")
        
        return {
            "valid": is_met,
            "target": target,
            "achieved": current_value,
            "percentage": (current_value / target * 100) if target > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }
    
    async def _validate_collaboration_count(self, 
                                          requirement: Dict[str, Any],
                                          current_value: Union[int, float],
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate collaboration count requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value >= target
        
        suspicious = False
        fraud_indicators = []
        
        # Check for collaboration spam
        time_window = context.get("time_window_hours", 24)
        if current_value > self._thresholds["collaboration_count_max_daily"]:
            suspicious = True
            fraud_indicators.append("Excessive collaboration count")
        
        return {
            "valid": is_met,
            "target": target,
            "achieved": current_value,
            "percentage": (current_value / target * 100) if target > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }
    
    async def _validate_revenue_generated(self, 
                                        requirement: Dict[str, Any],
                                        current_value: Union[int, float],
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate revenue generation requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value >= target
        
        suspicious = False
        fraud_indicators = []
        
        # Check for suspicious revenue patterns
        if current_value > self._thresholds["revenue_threshold_suspicious"]:
            suspicious = True
            fraud_indicators.append("Revenue amount exceeds normal thresholds")
        
        # Check revenue consistency with other metrics
        view_count = context.get("view_count", 0)
        if view_count > 0:
            revenue_per_view = current_value / view_count
            if revenue_per_view > 1.0:  # More than $1 per view
                suspicious = True
                fraud_indicators.append("Revenue per view ratio suspicious")
        
        return {
            "valid": is_met,
            "target": target,
            "achieved": current_value,
            "percentage": (current_value / target * 100) if target > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }
    
    async def _validate_view_count(self, 
                                 requirement: Dict[str, Any],
                                 current_value: Union[int, float],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate view count requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value >= target
        
        suspicious = False
        fraud_indicators = []
        
        # Check for bot views or view manipulation
        time_window = context.get("time_window_hours", 24)
        views_per_hour = current_value / time_window if time_window > 0 else 0
        
        if views_per_hour > self._thresholds["view_count_max_hourly"]:
            suspicious = True
            fraud_indicators.append("View count growth rate suspicious")
        
        # Check view-to-engagement ratio
        engagement_count = context.get("engagement_count", 0)
        if current_value > 0:
            engagement_ratio = engagement_count / current_value
            if engagement_ratio < 0.001:  # Less than 0.1% engagement
                suspicious = True
                fraud_indicators.append("Suspiciously low engagement relative to views")
        
        return {
            "valid": is_met,
            "target": target,
            "achieved": current_value,
            "percentage": (current_value / target * 100) if target > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }
    
    async def _validate_completion_time(self, 
                                      requirement: Dict[str, Any],
                                      current_value: Union[int, float],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completion time requirement"""        target = requirement.get("target_value", 0)
        is_met = current_value <= target  # For time, lower is better
        
        suspicious = False
        fraud_indicators = []
        
        # Check for unreasonably fast completion
        challenge_complexity = context.get("challenge_complexity", "medium")
        minimum_time_thresholds = {
            "easy": 300,    # 5 minutes
            "medium": 900,  # 15 minutes
            "hard": 1800    # 30 minutes
        }
        
        min_time = minimum_time_thresholds.get(challenge_complexity, 900)
        if current_value < min_time:
            suspicious = True
            fraud_indicators.append("Completion time unreasonably fast")
        
        return {
            "valid": is_met,
            "target": target,
            "achieved": current_value,
            "percentage": (target / current_value * 100) if current_value > 0 else 100,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }

class ProgressValidator:
    """Progress validation and tracking system"""    
    def __init__(self):
        """Initialize progress validator"""        self.logger = logging.getLogger(__name__)
        
        # Progress validation rules
        self._progress_rules = {
            "max_progress_jump": 25,  # Maximum percentage jump per update
            "min_time_between_updates": 60,  # Minimum seconds between updates
            "consistency_threshold": 0.8,  # Progress consistency requirement
            "max_daily_progress": 90  # Maximum daily progress percentage
        }
    
    async def validate_progress_update(self, 
                                     current_progress: Dict[str, Any],
                                     new_progress: Dict[str, Any],
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate progress update for anomalies and fraud"""        try:
            validation_result = {
                "valid": True,
                "issues": [],
                "fraud_indicators": [],
                "recommended_actions": [],
                "confidence_score": 100.0
            }
            
            # Validate progress increment
            increment_validation = await self._validate_progress_increment(
                current_progress, new_progress, context
            )
            
            if not increment_validation["valid"]:
                validation_result["valid"] = False
                validation_result["issues"].extend(increment_validation["issues"])
                validation_result["fraud_indicators"].extend(
                    increment_validation.get("fraud_indicators", [])
                )
            
            # Validate timing
            timing_validation = await self._validate_progress_timing(
                current_progress, new_progress, context
            )
            
            if not timing_validation["valid"]:
                validation_result["issues"].extend(timing_validation["issues"])
                if timing_validation.get("suspicious", False):
                    validation_result["fraud_indicators"].extend(
                        timing_validation.get("fraud_indicators", [])
                    )
            
            # Validate consistency
            consistency_validation = await self._validate_progress_consistency(
                current_progress, new_progress, context
            )
            
            validation_result["confidence_score"] = consistency_validation["confidence_score"]
            
            if consistency_validation.get("suspicious", False):
                validation_result["fraud_indicators"].extend(
                    consistency_validation.get("fraud_indicators", [])
                )
            
            # Generate recommended actions
            validation_result["recommended_actions"] = self._generate_progress_recommendations(
                validation_result
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Progress validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e),
                "confidence_score": 0.0
            }
    
    async def _validate_progress_increment(self, 
                                         current_progress: Dict[str, Any],
                                         new_progress: Dict[str, Any],
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate progress increment for suspicious jumps"""        current_percentage = current_progress.get("completion_percentage", 0.0)
        new_percentage = new_progress.get("completion_percentage", 0.0)
        
        increment = new_percentage - current_percentage
        
        issues = []
        fraud_indicators = []
        
        # Check for excessive progress jump
        if increment > self._progress_rules["max_progress_jump"]:
            issues.append(f"Progress jump of {increment}% exceeds maximum allowed")
            fraud_indicators.append("Suspicious progress acceleration")
        
        # Check for negative progress (should not happen)
        if increment < 0:
            issues.append("Progress cannot go backwards")
            fraud_indicators.append("Invalid progress update")
        
        # Check progress beyond 100%
        if new_percentage > 100:
            issues.append("Progress cannot exceed 100%")
            fraud_indicators.append("Invalid progress value")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "fraud_indicators": fraud_indicators,
            "increment": increment
        }
    
    async def _validate_progress_timing(self, 
                                      current_progress: Dict[str, Any],
                                      new_progress: Dict[str, Any],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate timing of progress updates"""        last_update = current_progress.get("last_updated")
        current_time = datetime.now(timezone.utc)
        
        issues = []
        fraud_indicators = []
        suspicious = False
        
        if last_update:
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            
            time_diff = (current_time - last_update).total_seconds()
            
            # Check minimum time between updates
            if time_diff < self._progress_rules["min_time_between_updates"]:
                issues.append("Updates too frequent")
                suspicious = True
                fraud_indicators.append("Automated progress updates suspected")
        
        # Check for off-hours activity (potential bot activity)
        if current_time.hour < 6 or current_time.hour > 23:
            if context.get("user_timezone_offset"):
                # Adjust for user timezone
                user_hour = (current_time.hour + context["user_timezone_offset"]) % 24
                if user_hour < 6 or user_hour > 23:
                    suspicious = True
                    fraud_indicators.append("Off-hours activity pattern")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }
    
    async def _validate_progress_consistency(self, 
                                           current_progress: Dict[str, Any],
                                           new_progress: Dict[str, Any],
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate progress consistency with historical patterns"""        progress_history = context.get("progress_history", [])
        
        confidence_score = 100.0
        fraud_indicators = []
        suspicious = False
        
        if len(progress_history) >= 3:
            # Analyze progress patterns
            increments = []
            for i in range(1, len(progress_history)):
                prev_pct = progress_history[i-1].get("completion_percentage", 0)
                curr_pct = progress_history[i].get("completion_percentage", 0)
                increments.append(curr_pct - prev_pct)
            
            if increments:
                avg_increment = sum(increments) / len(increments)
                current_increment = (
                    new_progress.get("completion_percentage", 0) - 
                    current_progress.get("completion_percentage", 0)
                )
                
                # Check for inconsistent patterns
                if abs(current_increment - avg_increment) > avg_increment * 2:
                    confidence_score -= 30
                    suspicious = True
                    fraud_indicators.append("Progress pattern inconsistent with history")
        
        # Check progress velocity consistency
        time_intervals = []
        if len(progress_history) >= 2:
            for i in range(1, len(progress_history)):
                prev_time = progress_history[i-1].get("timestamp")
                curr_time = progress_history[i].get("timestamp")
                
                if prev_time and curr_time:
                    if isinstance(prev_time, str):
                        prev_time = datetime.fromisoformat(prev_time.replace('Z', '+00:00'))
                    if isinstance(curr_time, str):
                        curr_time = datetime.fromisoformat(curr_time.replace('Z', '+00:00'))
                    
                    interval = (curr_time - prev_time).total_seconds()
                    time_intervals.append(interval)
            
            if time_intervals:
                avg_interval = sum(time_intervals) / len(time_intervals)
                current_interval = context.get("time_since_last_update", avg_interval)
                
                # Check for unusual timing patterns
                if current_interval < avg_interval * 0.1:  # 10x faster than usual
                    confidence_score -= 40
                    suspicious = True
                    fraud_indicators.append("Unusually fast progress updates")
        
        return {
            "confidence_score": max(0, confidence_score),
            "suspicious": suspicious,
            "fraud_indicators": fraud_indicators
        }
    
    def _generate_progress_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""        recommendations = []
        
        if validation_result.get("fraud_indicators"):
            recommendations.append("Flag for manual review due to fraud indicators")
            recommendations.append("Implement additional verification steps")
        
        if validation_result["confidence_score"] < 70:
            recommendations.append("Request additional verification from user")
            recommendations.append("Implement photo/video proof requirements")
        
        if "Automated progress updates suspected" in validation_result.get("fraud_indicators", []):
            recommendations.append("Implement CAPTCHA verification")
            recommendations.append("Add random verification challenges")
        
        return recommendations

class ChallengeValidator:
    """Main challenge validation orchestrator"""    
    def __init__(self,
                 analytics_service=None,
                 user_service=None,
                 content_service=None,
                 fraud_detection_service=None):
        """Initialize challenge validator"""        self.analytics_service = analytics_service
        self.user_service = user_service
        self.content_service = content_service
        self.fraud_detection_service = fraud_detection_service
        
        # Initialize validation components
        self.compliance_checker = ComplianceChecker()
        self.requirement_validator = RequirementValidator()
        self.progress_validator = ProgressValidator()
        
        self.logger = logging.getLogger(__name__)
        
        # Validation rules registry
        self._validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> List[ValidationRule]:
        """Initialize comprehensive validation rules"""        return [
            ValidationRule(
                rule_id="business_001",
                rule_name="Challenge Title Length",
                description="Challenge title must be between 3 and 100 characters",
                category=ValidationCategory.BUSINESS_RULES,
                severity=ValidationSeverity.ERROR,
                validation_function=self._validate_title_length,
                parameters={"min_length": 3, "max_length": 100}
            ),
            ValidationRule(
                rule_id="security_001",
                rule_name="Content Security Scan",
                description="Scan content for malicious elements",
                category=ValidationCategory.SECURITY,
                severity=ValidationSeverity.CRITICAL,
                validation_function=self._validate_content_security,
                requires_human_review=True
            ),
            ValidationRule(
                rule_id="fraud_001",
                rule_name="Progress Anomaly Detection",
                description="Detect unusual progress patterns",
                category=ValidationCategory.FRAUD_DETECTION,
                severity=ValidationSeverity.WARNING,
                validation_function=self._validate_progress_anomalies
            ),
            ValidationRule(
                rule_id="quality_001",
                rule_name="Content Quality Standards",
                description="Ensure content meets quality standards",
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.WARNING,
                validation_function=self._validate_content_quality
            ),
            ValidationRule(
                rule_id="compliance_001",
                rule_name="Platform Policy Compliance",
                description="Verify compliance with platform policies",
                category=ValidationCategory.COMPLIANCE,
                severity=ValidationSeverity.ERROR,
                validation_function=self._validate_policy_compliance,
                requires_human_review=True
            )
        ]
    
    async def validate_challenge_submission(self, 
                                          challenge_data: Dict[str, Any],
                                          user_context: Dict[str, Any]) -> ValidationResult:
        """Perform comprehensive challenge validation"""        start_time = datetime.now()
        validation_id = f"val_{int(start_time.timestamp())}"
        
        try:
            issues = []
            passed_rules = []
            failed_rules = []
            security_flags = []
            
            # Run all validation rules
            for rule in self._validation_rules:
                if not rule.is_enabled:
                    continue
                
                try:
                    rule_result = await rule.validation_function(
                        challenge_data, user_context, rule.parameters
                    )
                    
                    if rule_result.get("passed", False):
                        passed_rules.append(rule.rule_id)
                    else:
                        failed_rules.append(rule.rule_id)
                        
                        # Create validation issue
                        issue = ValidationIssue(
                            issue_id=f"{validation_id}_{rule.rule_id}",
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            category=rule.category,
                            message=rule_result.get("message", rule.description),
                            field_path=rule_result.get("field_path"),
                            suggested_fix=rule_result.get("suggested_fix"),
                            auto_fixable=rule.auto_fix_possible,
                            requires_human_review=rule.requires_human_review,
                            metadata=rule_result.get("metadata", {})
                        )
                        
                        issues.append(issue)
                        
                        # Collect security flags
                        if rule.category == ValidationCategory.SECURITY:
                            security_flags.extend(
                                rule_result.get("security_flags", [])
                            )
                
                except Exception as e:
                    self.logger.error(f"Validation rule {rule.rule_id} failed: {str(e)}")
                    failed_rules.append(rule.rule_id)
            
            # Perform compliance check
            compliance_result = await self.compliance_checker.check_compliance(
                challenge_data, user_context
            )
            
            # Determine overall status
            status = self._determine_validation_status(issues, compliance_result)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                len(passed_rules), len(failed_rules), issues
            )
            
            # Assess fraud risk
            fraud_risk_level = self._assess_fraud_risk(issues, compliance_result)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ValidationResult(
                validation_id=validation_id,
                status=status,
                overall_score=overall_score,
                fraud_risk_level=fraud_risk_level,
                issues=issues,
                passed_rules=passed_rules,
                failed_rules=failed_rules,
                security_flags=security_flags,
                compliance_status=compliance_result,
                performance_metrics={
                    "rules_executed": len(self._validation_rules),
                    "processing_time_ms": processing_time
                },
                validation_timestamp=datetime.now(timezone.utc),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Challenge validation failed: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ValidationResult(
                validation_id=validation_id,
                status=ValidationStatus.FAILED,
                overall_score=0.0,
                fraud_risk_level=FraudRiskLevel.HIGH,
                issues=[ValidationIssue(
                    issue_id=f"{validation_id}_system_error",
                    rule_id="system_error",
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.SECURITY,
                    message=f"System validation error: {str(e)}",
                    requires_human_review=True
                )],
                passed_rules=[],
                failed_rules=["system_error"],
                security_flags=["system_error"],
                compliance_status={"error": str(e)},
                performance_metrics={"error": True},
                validation_timestamp=datetime.now(timezone.utc),
                processing_time_ms=processing_time
            )
    
    # Validation rule implementations
    
    async def _validate_title_length(self, 
                                   challenge_data: Dict[str, Any],
                                   user_context: Dict[str, Any],
                                   parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate challenge title length"""        title = challenge_data.get("title", "")
        min_length = parameters.get("min_length", 3)
        max_length = parameters.get("max_length", 100)
        
        if len(title) < min_length:
            return {
                "passed": False,
                "message": f"Title too short (minimum {min_length} characters)",
                "field_path": "title",
                "suggested_fix": f"Add at least {min_length - len(title)} more characters"
            }
        
        if len(title) > max_length:
            return {
                "passed": False,
                "message": f"Title too long (maximum {max_length} characters)",
                "field_path": "title",
                "suggested_fix": f"Remove at least {len(title) - max_length} characters"
            }
        
        return {"passed": True}
    
    async def _validate_content_security(self, 
                                       challenge_data: Dict[str, Any],
                                       user_context: Dict[str, Any],
                                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content security"""        content = challenge_data.get("content", "")
        security_flags = []
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'data:.*base64',           # Base64 data URIs
            r'<iframe.*?>',             # Iframe tags
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_flags.append(f"Suspicious pattern detected: {pattern}")
        
        # Check for external links to suspicious domains
        suspicious_domains = ['bit.ly', 'tinyurl.com', 'goo.gl']
        for domain in suspicious_domains:
            if domain in content.lower():
                security_flags.append(f"Link to suspicious domain: {domain}")
        
        if security_flags:
            return {
                "passed": False,
                "message": "Security scan detected potential threats",
                "security_flags": security_flags,
                "suggested_fix": "Remove suspicious content elements"
            }
        
        return {"passed": True}
    
    async def _validate_progress_anomalies(self, 
                                         challenge_data: Dict[str, Any],
                                         user_context: Dict[str, Any],
                                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate progress for anomalies"""        progress_data = challenge_data.get("progress", {})
        
        # Use progress validator
        if "current_progress" in user_context and "new_progress" in challenge_data:
            validation_result = await self.progress_validator.validate_progress_update(
                user_context["current_progress"],
                challenge_data["new_progress"],
                user_context
            )
            
            if not validation_result["valid"] or validation_result["fraud_indicators"]:
                return {
                    "passed": False,
                    "message": "Progress anomalies detected",
                    "metadata": validation_result,
                    "suggested_fix": "Review progress updates for accuracy"
                }
        
        return {"passed": True}
    
    async def _validate_content_quality(self, 
                                      challenge_data: Dict[str, Any],
                                      user_context: Dict[str, Any],
                                      parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content quality standards"""        quality_score = challenge_data.get("content_quality_score", 0)
        
        if quality_score < 5.0:
            return {
                "passed": False,
                "message": "Content quality below acceptable standards",
                "field_path": "content_quality_score",
                "suggested_fix": "Improve content quality before submission"
            }
        
        return {"passed": True}
    
    async def _validate_policy_compliance(self, 
                                        challenge_data: Dict[str, Any],
                                        user_context: Dict[str, Any],
                                        parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate policy compliance"""        compliance_result = await self.compliance_checker.check_compliance(
            challenge_data, user_context
        )
        
        if not compliance_result.get("overall_compliant", False):
            return {
                "passed": False,
                "message": "Policy compliance violations detected",
                "metadata": compliance_result,
                "suggested_fix": "Address policy violations before proceeding"
            }
        
        return {"passed": True}
    
    # Helper methods
    
    def _determine_validation_status(self, 
                                   issues: List[ValidationIssue],
                                   compliance_result: Dict[str, Any]) -> ValidationStatus:
        """Determine overall validation status"""        # Check for critical issues
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            return ValidationStatus.FAILED
        
        # Check for security issues
        security_issues = [i for i in issues if i.severity == ValidationSeverity.SECURITY]
        if security_issues:
            return ValidationStatus.FLAGGED
        
        # Check compliance
        if not compliance_result.get("overall_compliant", False):
            return ValidationStatus.REQUIRES_REVIEW
        
        # Check for error issues
        error_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
        if error_issues:
            return ValidationStatus.FAILED
        
        # Check for human review requirements
        review_required = any(i.requires_human_review for i in issues)
        if review_required:
            return ValidationStatus.REQUIRES_REVIEW
        
        # Check for warnings
        warning_issues = [i for i in issues if i.severity == ValidationSeverity.WARNING]
        if warning_issues:
            return ValidationStatus.REQUIRES_REVIEW
        
        return ValidationStatus.PASSED
    
    def _calculate_overall_score(self, 
                               passed_count: int,
                               failed_count: int,
                               issues: List[ValidationIssue]) -> float:
        """Calculate overall validation score"""        total_rules = passed_count + failed_count
        if total_rules == 0:
            return 0.0
        
        base_score = (passed_count / total_rules) * 100
        
        # Apply penalties for severity
        severity_penalties = {
            ValidationSeverity.CRITICAL: 30,
            ValidationSeverity.SECURITY: 25,
            ValidationSeverity.ERROR: 15,
            ValidationSeverity.WARNING: 5,
            ValidationSeverity.INFO: 1
        }
        
        total_penalty = sum(
            severity_penalties.get(issue.severity, 0) for issue in issues
        )
        
        return max(0.0, base_score - total_penalty)
    
    def _assess_fraud_risk(self, 
                          issues: List[ValidationIssue],
                          compliance_result: Dict[str, Any]) -> FraudRiskLevel:
        """Assess fraud risk level"""        fraud_indicators = 0
        
        # Count fraud-related issues
        fraud_issues = [
            i for i in issues 
            if i.category == ValidationCategory.FRAUD_DETECTION
        ]
        fraud_indicators += len(fraud_issues)
        
        # Check security issues
        security_issues = [
            i for i in issues 
            if i.category == ValidationCategory.SECURITY
        ]
        fraud_indicators += len(security_issues) * 2  # Higher weight
        
        # Check compliance risk
        compliance_risk = compliance_result.get("risk_assessment", "low")
        if compliance_risk in ["high", "critical"]:
            fraud_indicators += 3
        elif compliance_risk == "medium":
            fraud_indicators += 1
        
        # Determine risk level
        if fraud_indicators >= 5:
            return FraudRiskLevel.CRITICAL
        elif fraud_indicators >= 3:
            return FraudRiskLevel.HIGH
        elif fraud_indicators >= 2:
            return FraudRiskLevel.MEDIUM
        elif fraud_indicators >= 1:
            return FraudRiskLevel.LOW
        else:
            return FraudRiskLevel.MINIMAL