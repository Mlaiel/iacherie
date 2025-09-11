"""
🔍 Backward Compatibility Validation System
Enterprise-grade compatibility checking and validation framework

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

🎯 DBA Expert Role: Advanced compatibility analysis and validation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
import json
from abc import ABC, abstractmethod

from .base import BaseSchema, TimestampSchema, UUIDSchema
from .schema_registry import SchemaVersion, SchemaMetadata
from .version_control import SchemaChange, ChangeType, CompatibilityLevel


class CompatibilityRule(str, Enum):
    """Compatibility validation rules"""
    NO_FIELD_REMOVAL = "no_field_removal"
    NO_REQUIRED_FIELDS = "no_required_fields"
    NO_TYPE_CHANGES = "no_type_changes"
    NO_CONSTRAINT_TIGHTENING = "no_constraint_tightening"
    MAINTAIN_DEFAULTS = "maintain_defaults"
    PRESERVE_ENUMS = "preserve_enums"
    KEEP_ARRAY_STRUCTURE = "keep_array_structure"
    MAINTAIN_OBJECT_SHAPE = "maintain_object_shape"


class CompatibilityViolationType(str, Enum):
    """Types of compatibility violations"""
    BREAKING_CHANGE = "breaking_change"
    DEPRECATION_WARNING = "deprecation_warning"
    BEHAVIORAL_CHANGE = "behavioral_change"
    PERFORMANCE_IMPACT = "performance_impact"
    SECURITY_CONCERN = "security_concern"


class ValidationSeverity(str, Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CompatibilityViolation(UUIDSchema, TimestampSchema):
    """Individual compatibility violation"""
    violation_type: CompatibilityViolationType = Field(description="Type of violation")
    severity: ValidationSeverity = Field(description="Violation severity")
    rule_violated: CompatibilityRule = Field(description="Compatibility rule that was violated")
    field_path: str = Field(description="Path to problematic field")
    violation_message: str = Field(description="Human-readable violation description")
    
    # Change details
    old_value: Optional[Any] = Field(None, description="Previous value")
    new_value: Optional[Any] = Field(None, description="New value")
    change_description: str = Field(description="Description of the change")
    
    # Impact assessment
    affected_consumers: List[str] = Field(default_factory=list, description="List of affected consumers")
    estimated_impact: str = Field(description="Estimated impact assessment")
    migration_effort: str = Field(description="Required migration effort")
    
    # Remediation
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for the violation")
    alternative_approaches: List[str] = Field(default_factory=list, description="Alternative approaches")
    can_be_automated: bool = Field(default=False, description="Whether fix can be automated")


class CompatibilityReport(UUIDSchema, TimestampSchema):
    """Comprehensive compatibility analysis report"""
    source_schema: str = Field(description="Source schema name")
    target_schema: str = Field(description="Target schema name")
    source_version: SchemaVersion = Field(description="Source schema version")
    target_version: SchemaVersion = Field(description="Target schema version")
    
    # Analysis results
    overall_compatibility: CompatibilityLevel = Field(description="Overall compatibility assessment")
    violations: List[CompatibilityViolation] = Field(default_factory=list, description="Compatibility violations")
    warnings: List[CompatibilityViolation] = Field(default_factory=list, description="Compatibility warnings")
    
    # Statistics
    total_changes: int = Field(default=0, ge=0, description="Total number of changes")
    breaking_changes: int = Field(default=0, ge=0, description="Number of breaking changes")
    safe_changes: int = Field(default=0, ge=0, description="Number of safe changes")
    
    # Recommendations
    migration_required: bool = Field(description="Whether migration is required")
    migration_complexity: str = Field(description="Migration complexity assessment")
    recommended_strategy: str = Field(description="Recommended migration strategy")
    estimated_effort_hours: Optional[float] = Field(None, ge=0, description="Estimated migration effort")
    
    # Consumer impact
    consumer_analysis: Dict[str, Any] = Field(default_factory=dict, description="Analysis of consumer impact")
    rollback_feasibility: str = Field(description="Rollback feasibility assessment")
    
    @property
    def violation_summary(self) -> Dict[str, int]:
        """Get summary of violations by severity"""
        summary = {}
        for violation in self.violations:
            severity = violation.severity.value
            summary[severity] = summary.get(severity, 0) + 1
        return summary
    
    @property
    def has_critical_violations(self) -> bool:
        """Check if report has critical violations"""
        return any(v.severity == ValidationSeverity.CRITICAL for v in self.violations)


class CompatibilityChecker(ABC):
    """Abstract base class for compatibility checkers"""
    
    @abstractmethod
    def check_compatibility(self, 
                          source_schema: SchemaMetadata, 
                          target_schema: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check compatibility between two schemas"""
        pass
    
    @abstractmethod
    def get_supported_rules(self) -> List[CompatibilityRule]:
        """Get list of supported compatibility rules"""
        pass


class JSONSchemaCompatibilityChecker(CompatibilityChecker):
    """JSON Schema specific compatibility checker"""
    
    def __init__(self):
        self.supported_rules = [
            CompatibilityRule.NO_FIELD_REMOVAL,
            CompatibilityRule.NO_REQUIRED_FIELDS,
            CompatibilityRule.NO_TYPE_CHANGES,
            CompatibilityRule.NO_CONSTRAINT_TIGHTENING,
            CompatibilityRule.MAINTAIN_DEFAULTS,
            CompatibilityRule.PRESERVE_ENUMS,
        ]
    
    def get_supported_rules(self) -> List[CompatibilityRule]:
        """Get supported compatibility rules"""
        return self.supported_rules
    
    def check_compatibility(self, 
                          source_schema: SchemaMetadata, 
                          target_schema: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check JSON Schema compatibility"""
        violations = []
        
        # Check each rule
        violations.extend(self._check_field_removal(source_schema, target_schema))
        violations.extend(self._check_required_fields(source_schema, target_schema))
        violations.extend(self._check_type_changes(source_schema, target_schema))
        violations.extend(self._check_constraint_tightening(source_schema, target_schema))
        violations.extend(self._check_default_values(source_schema, target_schema))
        violations.extend(self._check_enum_compatibility(source_schema, target_schema))
        
        return violations
    
    def _check_field_removal(self, source: SchemaMetadata, target: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check for removed fields"""
        violations = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in source_props:
            if field_name not in target_props:
                violations.append(CompatibilityViolation(
                    id=uuid4(),
                    violation_type=CompatibilityViolationType.BREAKING_CHANGE,
                    severity=ValidationSeverity.CRITICAL,
                    rule_violated=CompatibilityRule.NO_FIELD_REMOVAL,
                    field_path=f"properties.{field_name}",
                    violation_message=f"Field '{field_name}' was removed from schema",
                    old_value=source_props[field_name],
                    new_value=None,
                    change_description=f"Removed field '{field_name}'",
                    estimated_impact="High - existing consumers will fail",
                    migration_effort="Medium - consumers need to handle missing field",
                    suggested_fix=f"Deprecate field '{field_name}' instead of removing it"
                ))
        
        return violations
    
    def _check_required_fields(self, source: SchemaMetadata, target: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check for new required fields"""
        violations = []
        source_required = set(source.schema_content.get("required", []))
        target_required = set(target.schema_content.get("required", []))
        
        new_required = target_required - source_required
        
        for field_name in new_required:
            violations.append(CompatibilityViolation(
                id=uuid4(),
                violation_type=CompatibilityViolationType.BREAKING_CHANGE,
                severity=ValidationSeverity.HIGH,
                rule_violated=CompatibilityRule.NO_REQUIRED_FIELDS,
                field_path=f"required.{field_name}",
                violation_message=f"Field '{field_name}' is now required",
                old_value=False,
                new_value=True,
                change_description=f"Made field '{field_name}' required",
                estimated_impact="High - existing data without this field will be invalid",
                migration_effort="High - need to populate missing values",
                suggested_fix=f"Provide default value for '{field_name}' or make it optional"
            ))
        
        return violations
    
    def _check_type_changes(self, source: SchemaMetadata, target: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check for type changes"""
        violations = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in set(source_props.keys()) & set(target_props.keys()):
            source_type = source_props[field_name].get("type")
            target_type = target_props[field_name].get("type")
            
            if source_type != target_type:
                compatibility = self._assess_type_compatibility(source_type, target_type)
                
                if not compatibility["is_compatible"]:
                    violations.append(CompatibilityViolation(
                        id=uuid4(),
                        violation_type=CompatibilityViolationType.BREAKING_CHANGE,
                        severity=ValidationSeverity.CRITICAL,
                        rule_violated=CompatibilityRule.NO_TYPE_CHANGES,
                        field_path=f"properties.{field_name}.type",
                        violation_message=f"Type of '{field_name}' changed from {source_type} to {target_type}",
                        old_value=source_type,
                        new_value=target_type,
                        change_description=f"Changed type of '{field_name}'",
                        estimated_impact="Critical - data conversion required",
                        migration_effort="High - complex data transformation needed",
                        suggested_fix=compatibility["suggested_fix"]
                    ))
        
        return violations
    
    def _assess_type_compatibility(self, source_type: str, target_type: str) -> Dict[str, Any]:
        """Assess compatibility between two data types"""
        compatible_transitions = {
            ("integer", "number"): {"is_compatible": True, "reason": "Integer is subset of number"},
            ("string", "string"): {"is_compatible": True, "reason": "Same type"},
            # Add more compatible transitions
        }
        
        transition = (source_type, target_type)
        if transition in compatible_transitions:
            return {
                "is_compatible": True,
                "reason": compatible_transitions[transition]["reason"],
                "suggested_fix": None
            }
        
        return {
            "is_compatible": False,
            "reason": f"Incompatible type change from {source_type} to {target_type}",
            "suggested_fix": f"Use union type or create new field for {target_type}"
        }
    
    def _check_constraint_tightening(self, source: SchemaMetadata, target: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check for tightened constraints"""
        violations = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in set(source_props.keys()) & set(target_props.keys()):
            source_field = source_props[field_name]
            target_field = target_props[field_name]
            
            # Check string length constraints
            if (source_field.get("maxLength") is None and target_field.get("maxLength") is not None) or \
               (source_field.get("maxLength", float('inf')) > target_field.get("maxLength", float('inf'))):
                violations.append(CompatibilityViolation(
                    id=uuid4(),
                    violation_type=CompatibilityViolationType.BREAKING_CHANGE,
                    severity=ValidationSeverity.HIGH,
                    rule_violated=CompatibilityRule.NO_CONSTRAINT_TIGHTENING,
                    field_path=f"properties.{field_name}.maxLength",
                    violation_message=f"MaxLength constraint tightened for '{field_name}'",
                    old_value=source_field.get("maxLength"),
                    new_value=target_field.get("maxLength"),
                    change_description=f"Reduced maximum length for '{field_name}'",
                    estimated_impact="Medium - longer existing values may become invalid",
                    migration_effort="Medium - data validation and truncation needed",
                    suggested_fix="Gradually migrate data before applying constraint"
                ))
            
            # Check numeric constraints
            if (source_field.get("maximum") is None and target_field.get("maximum") is not None) or \
               (source_field.get("maximum", float('inf')) > target_field.get("maximum", float('inf'))):
                violations.append(CompatibilityViolation(
                    id=uuid4(),
                    violation_type=CompatibilityViolationType.BREAKING_CHANGE,
                    severity=ValidationSeverity.HIGH,
                    rule_violated=CompatibilityRule.NO_CONSTRAINT_TIGHTENING,
                    field_path=f"properties.{field_name}.maximum",
                    violation_message=f"Maximum value constraint tightened for '{field_name}'",
                    old_value=source_field.get("maximum"),
                    new_value=target_field.get("maximum"),
                    change_description=f"Reduced maximum value for '{field_name}'",
                    estimated_impact="Medium - larger existing values may become invalid",
                    migration_effort="Medium - data validation and adjustment needed",
                    suggested_fix="Validate existing data before applying constraint"
                ))
        
        return violations
    
    def _check_default_values(self, source: SchemaMetadata, target: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check for changed default values"""
        violations = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in set(source_props.keys()) & set(target_props.keys()):
            source_default = source_props[field_name].get("default")
            target_default = target_props[field_name].get("default")
            
            if source_default != target_default:
                severity = ValidationSeverity.MEDIUM if source_default is not None else ValidationSeverity.LOW
                
                violations.append(CompatibilityViolation(
                    id=uuid4(),
                    violation_type=CompatibilityViolationType.BEHAVIORAL_CHANGE,
                    severity=severity,
                    rule_violated=CompatibilityRule.MAINTAIN_DEFAULTS,
                    field_path=f"properties.{field_name}.default",
                    violation_message=f"Default value changed for '{field_name}'",
                    old_value=source_default,
                    new_value=target_default,
                    change_description=f"Changed default value for '{field_name}'",
                    estimated_impact="Low to Medium - behavior change for new instances",
                    migration_effort="Low - mainly affects new data",
                    suggested_fix="Document behavior change and consider gradual rollout"
                ))
        
        return violations
    
    def _check_enum_compatibility(self, source: SchemaMetadata, target: SchemaMetadata) -> List[CompatibilityViolation]:
        """Check for enum value changes"""
        violations = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in set(source_props.keys()) & set(target_props.keys()):
            source_enum = source_props[field_name].get("enum", [])
            target_enum = target_props[field_name].get("enum", [])
            
            if source_enum and target_enum:
                removed_values = set(source_enum) - set(target_enum)
                
                if removed_values:
                    violations.append(CompatibilityViolation(
                        id=uuid4(),
                        violation_type=CompatibilityViolationType.BREAKING_CHANGE,
                        severity=ValidationSeverity.HIGH,
                        rule_violated=CompatibilityRule.PRESERVE_ENUMS,
                        field_path=f"properties.{field_name}.enum",
                        violation_message=f"Enum values removed from '{field_name}': {removed_values}",
                        old_value=source_enum,
                        new_value=target_enum,
                        change_description=f"Removed enum values from '{field_name}'",
                        estimated_impact="High - existing data with removed values will be invalid",
                        migration_effort="High - data migration and consumer updates needed",
                        suggested_fix="Deprecate values instead of removing them immediately"
                    ))
        
        return violations


class BackwardCompatibilityValidator:
    """
    Enterprise-grade backward compatibility validation system
    Comprehensive analysis and reporting of schema compatibility
    """
    
    def __init__(self):
        self.checkers: Dict[str, CompatibilityChecker] = {
            "json_schema": JSONSchemaCompatibilityChecker()
        }
        self.validation_history: List[CompatibilityReport] = []
        self.custom_rules: Dict[str, Callable] = {}
    
    def register_checker(self, schema_type: str, checker: CompatibilityChecker):
        """Register custom compatibility checker"""
        self.checkers[schema_type] = checker
    
    def register_custom_rule(self, rule_name: str, rule_function: Callable):
        """Register custom compatibility rule"""
        self.custom_rules[rule_name] = rule_function
    
    def validate_compatibility(self, 
                             source_schema: SchemaMetadata, 
                             target_schema: SchemaMetadata,
                             schema_type: str = "json_schema") -> CompatibilityReport:
        """
        Perform comprehensive compatibility validation
        Returns detailed compatibility report
        """
        checker = self.checkers.get(schema_type)
        if not checker:
            raise ValueError(f"No checker registered for schema type: {schema_type}")
        
        # Run compatibility checks
        violations = checker.check_compatibility(source_schema, target_schema)
        
        # Apply custom rules
        custom_violations = self._apply_custom_rules(source_schema, target_schema)
        violations.extend(custom_violations)
        
        # Analyze consumer impact
        consumer_analysis = self._analyze_consumer_impact(violations)
        
        # Generate report
        report = self._generate_compatibility_report(
            source_schema, target_schema, violations, consumer_analysis
        )
        
        # Store validation history
        self.validation_history.append(report)
        
        return report
    
    def _apply_custom_rules(self, 
                           source_schema: SchemaMetadata, 
                           target_schema: SchemaMetadata) -> List[CompatibilityViolation]:
        """Apply custom compatibility rules"""
        violations = []
        
        for rule_name, rule_function in self.custom_rules.items():
            try:
                rule_violations = rule_function(source_schema, target_schema)
                if isinstance(rule_violations, list):
                    violations.extend(rule_violations)
                elif isinstance(rule_violations, CompatibilityViolation):
                    violations.append(rule_violations)
            except Exception as e:
                print(f"Error applying custom rule {rule_name}: {e}")
        
        return violations
    
    def _analyze_consumer_impact(self, violations: List[CompatibilityViolation]) -> Dict[str, Any]:
        """Analyze impact on schema consumers"""
        impact_analysis = {
            "affected_apis": set(),
            "breaking_change_count": 0,
            "migration_required": False,
            "risk_level": "low",
            "estimated_downtime": "none"
        }
        
        critical_violations = [v for v in violations if v.severity == ValidationSeverity.CRITICAL]
        breaking_violations = [v for v in violations 
                             if v.violation_type == CompatibilityViolationType.BREAKING_CHANGE]
        
        impact_analysis["breaking_change_count"] = len(breaking_violations)
        impact_analysis["migration_required"] = len(breaking_violations) > 0
        
        # Assess risk level
        if critical_violations:
            impact_analysis["risk_level"] = "critical"
            impact_analysis["estimated_downtime"] = "high"
        elif breaking_violations:
            impact_analysis["risk_level"] = "high"
            impact_analysis["estimated_downtime"] = "medium"
        elif len(violations) > 10:
            impact_analysis["risk_level"] = "medium"
            impact_analysis["estimated_downtime"] = "low"
        
        return impact_analysis
    
    def _generate_compatibility_report(self, 
                                     source_schema: SchemaMetadata,
                                     target_schema: SchemaMetadata,
                                     violations: List[CompatibilityViolation],
                                     consumer_analysis: Dict[str, Any]) -> CompatibilityReport:
        """Generate comprehensive compatibility report"""
        
        # Separate violations and warnings
        critical_violations = [v for v in violations if v.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
        warnings = [v for v in violations if v.severity in [ValidationSeverity.MEDIUM, ValidationSeverity.LOW]]
        
        # Assess overall compatibility
        overall_compatibility = self._assess_overall_compatibility(violations)
        
        # Calculate statistics
        breaking_changes = len([v for v in violations 
                               if v.violation_type == CompatibilityViolationType.BREAKING_CHANGE])
        safe_changes = len(violations) - breaking_changes
        
        # Determine migration strategy
        migration_complexity, recommended_strategy = self._determine_migration_strategy(violations)
        
        # Estimate effort
        estimated_effort = self._estimate_migration_effort(violations)
        
        return CompatibilityReport(
            id=uuid4(),
            source_schema=source_schema.name,
            target_schema=target_schema.name,
            source_version=source_schema.version,
            target_version=target_schema.version,
            overall_compatibility=overall_compatibility,
            violations=critical_violations,
            warnings=warnings,
            total_changes=len(violations),
            breaking_changes=breaking_changes,
            safe_changes=safe_changes,
            migration_required=breaking_changes > 0,
            migration_complexity=migration_complexity,
            recommended_strategy=recommended_strategy,
            estimated_effort_hours=estimated_effort,
            consumer_analysis=consumer_analysis,
            rollback_feasibility=self._assess_rollback_feasibility(violations)
        )
    
    def _assess_overall_compatibility(self, violations: List[CompatibilityViolation]) -> CompatibilityLevel:
        """Assess overall compatibility level"""
        if any(v.severity == ValidationSeverity.CRITICAL for v in violations):
            return CompatibilityLevel.BREAKING
        elif any(v.violation_type == CompatibilityViolationType.BREAKING_CHANGE for v in violations):
            return CompatibilityLevel.BREAKING
        elif any(v.severity == ValidationSeverity.HIGH for v in violations):
            return CompatibilityLevel.BACKWARD
        elif violations:
            return CompatibilityLevel.FORWARD
        else:
            return CompatibilityLevel.FULL
    
    def _determine_migration_strategy(self, violations: List[CompatibilityViolation]) -> Tuple[str, str]:
        """Determine migration complexity and recommended strategy"""
        critical_count = len([v for v in violations if v.severity == ValidationSeverity.CRITICAL])
        breaking_count = len([v for v in violations 
                            if v.violation_type == CompatibilityViolationType.BREAKING_CHANGE])
        
        if critical_count > 0:
            return "High", "Blue-Green deployment with extensive testing"
        elif breaking_count > 5:
            return "High", "Gradual migration with feature flags"
        elif breaking_count > 0:
            return "Medium", "Rolling deployment with rollback plan"
        else:
            return "Low", "Standard deployment"
    
    def _estimate_migration_effort(self, violations: List[CompatibilityViolation]) -> float:
        """Estimate migration effort in hours"""
        effort_weights = {
            ValidationSeverity.CRITICAL: 8.0,
            ValidationSeverity.HIGH: 4.0,
            ValidationSeverity.MEDIUM: 2.0,
            ValidationSeverity.LOW: 0.5,
        }
        
        total_effort = sum(effort_weights.get(v.severity, 1.0) for v in violations)
        return round(total_effort, 1)
    
    def _assess_rollback_feasibility(self, violations: List[CompatibilityViolation]) -> str:
        """Assess feasibility of rolling back changes"""
        data_loss_violations = [
            v for v in violations 
            if v.rule_violated in [CompatibilityRule.NO_FIELD_REMOVAL, CompatibilityRule.NO_TYPE_CHANGES]
        ]
        
        if data_loss_violations:
            return "Difficult - potential data loss"
        elif len(violations) > 10:
            return "Complex - extensive changes to revert"
        elif any(v.severity == ValidationSeverity.CRITICAL for v in violations):
            return "Moderate - careful planning required"
        else:
            return "Easy - straightforward rollback"
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics and trends"""
        if not self.validation_history:
            return {"message": "No validation history available"}
        
        total_validations = len(self.validation_history)
        compatibility_distribution = {}
        
        for report in self.validation_history:
            level = report.overall_compatibility.value
            compatibility_distribution[level] = compatibility_distribution.get(level, 0) + 1
        
        avg_violations = sum(len(r.violations) for r in self.validation_history) / total_validations
        avg_effort = sum(r.estimated_effort_hours or 0 for r in self.validation_history) / total_validations
        
        return {
            "total_validations": total_validations,
            "compatibility_distribution": compatibility_distribution,
            "average_violations_per_validation": round(avg_violations, 2),
            "average_migration_effort_hours": round(avg_effort, 2),
            "most_common_violations": self._get_most_common_violations(),
        }
    
    def _get_most_common_violations(self) -> Dict[str, int]:
        """Get most common violation types"""
        violation_counts = {}
        
        for report in self.validation_history:
            for violation in report.violations + report.warnings:
                rule = violation.rule_violated.value
                violation_counts[rule] = violation_counts.get(rule, 0) + 1
        
        # Return top 5 most common violations
        return dict(sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5])


# Export all classes
__all__ = [
    'CompatibilityRule',
    'CompatibilityViolationType',
    'ValidationSeverity',
    'CompatibilityViolation',
    'CompatibilityReport',
    'CompatibilityChecker',
    'JSONSchemaCompatibilityChecker',
    'BackwardCompatibilityValidator'
]