"""
✅ Data Validation Framework - Enterprise MLOps
Expert DBA + Data Engineering: Framework validation données enterprise

🎯 EXPERTISE DÉMONTRÉ:
- DBA: Contraintes intégrité + validation schémas
- Data Engineering: Pipeline validation automatique
- Backend Senior: Validation <100ms + architecture robuste
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Niveaux de sévérité des violations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationType(Enum):
    """Types de validations"""
    SCHEMA = "schema"
    DATA_TYPE = "data_type"
    RANGE = "range"
    FORMAT = "format"
    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    BUSINESS_RULE = "business_rule"

@dataclass
class ValidationRule:
    """Règle de validation"""
    id: str
    name: str
    validation_type: ValidationType
    severity: ValidationSeverity
    validator_function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    error_message: str = ""
    active: bool = True

@dataclass
class ValidationViolation:
    """Violation d'une règle de validation"""
    rule_id: str
    severity: ValidationSeverity
    message: str
    field_name: Optional[str] = None
    record_index: Optional[int] = None
    actual_value: Any = None
    expected_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Résultat de validation"""
    dataset_id: str
    validation_date: datetime
    total_records: int
    total_fields: int
    total_violations: int
    violations_by_severity: Dict[str, int]
    violations: List[ValidationViolation]
    passed: bool
    validation_score: float  # 0-100
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataValidationFramework:
    """
    ✅ Framework Enterprise de Validation de Données
    
    Expertise DBA + Data Engineering:
    - Validation schémas et contraintes intégrité
    - Règles business automatiques
    - Performance validation <100ms
    - Reporting complet violations
    """
    
    def __init__(self):
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
        self.schema_cache: Dict[str, Dict] = {}
        
        # Enregistrer les validations intégrées
        self._register_builtin_validators()
    
    def _register_builtin_validators(self):
        """Enregistre les validateurs intégrés"""
        
        # Validation type de données
        self.register_rule(ValidationRule(
            id="data_type_check",
            name="Data Type Validation",
            validation_type=ValidationType.DATA_TYPE,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_data_type,
            description="Validates data types match expected schema"
        ))
        
        # Validation valeurs nulles
        self.register_rule(ValidationRule(
            id="null_check",
            name="Null Value Check",
            validation_type=ValidationType.COMPLETENESS,
            severity=ValidationSeverity.WARNING,
            validator_function=self._validate_not_null,
            description="Validates required fields are not null"
        ))
        
        # Validation plage de valeurs
        self.register_rule(ValidationRule(
            id="range_check",
            name="Value Range Check",
            validation_type=ValidationType.RANGE,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_range,
            description="Validates numeric values are within expected range"
        ))
        
        # Validation format
        self.register_rule(ValidationRule(
            id="format_check",
            name="Format Validation",
            validation_type=ValidationType.FORMAT,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_format,
            description="Validates field formats match expected patterns"
        ))
        
        # Validation unicité
        self.register_rule(ValidationRule(
            id="uniqueness_check", 
            name="Uniqueness Check",
            validation_type=ValidationType.UNIQUENESS,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_uniqueness,
            description="Validates field values are unique"
        ))
    
    def register_rule(self, rule: ValidationRule) -> bool:
        """Enregistre une règle de validation"""
        try:
            if not callable(rule.validator_function):
                raise ValueError(f"Validator function for rule {rule.id} is not callable")
            
            self.validation_rules[rule.id] = rule
            logger.info(f"Registered validation rule: {rule.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register validation rule {rule.id}: {str(e)}")
            return False
    
    async def validate_dataset(
        self,
        dataset_id: str,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]] = None,
        rules_to_apply: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Valide un dataset complet
        
        Expertise DBA: Validation intégrité + contraintes
        """
        start_time = datetime.utcnow()
        violations = []
        
        total_records = len(next(iter(data.values()))) if data else 0
        total_fields = len(data)
        
        # Déterminer les règles à appliquer
        if rules_to_apply is None:
            active_rules = [rule for rule in self.validation_rules.values() if rule.active]
        else:
            active_rules = [
                self.validation_rules[rule_id] 
                for rule_id in rules_to_apply 
                if rule_id in self.validation_rules
            ]
        
        # Validation par règle
        for rule in active_rules:
            try:
                rule_violations = await self._apply_rule(rule, data, schema)
                violations.extend(rule_violations)
            except Exception as e:
                logger.error(f"Error applying rule {rule.id}: {str(e)}")
                # Ajouter une violation pour l'erreur de validation
                violations.append(ValidationViolation(
                    rule_id=rule.id,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation rule execution failed: {str(e)}"
                ))
        
        # Calcul des métriques
        violations_by_severity = {
            "info": sum(1 for v in violations if v.severity == ValidationSeverity.INFO),
            "warning": sum(1 for v in violations if v.severity == ValidationSeverity.WARNING),
            "error": sum(1 for v in violations if v.severity == ValidationSeverity.ERROR),
            "critical": sum(1 for v in violations if v.severity == ValidationSeverity.CRITICAL)
        }
        
        # Score de validation (100 - pénalités)
        validation_score = self._calculate_validation_score(
            violations_by_severity, total_records, total_fields
        )
        
        # Détermine si la validation est passée
        passed = (violations_by_severity["error"] == 0 and 
                 violations_by_severity["critical"] == 0)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = ValidationResult(
            dataset_id=dataset_id,
            validation_date=start_time,
            total_records=total_records,
            total_fields=total_fields,
            total_violations=len(violations),
            violations_by_severity=violations_by_severity,
            violations=violations,
            passed=passed,
            validation_score=validation_score,
            execution_time=execution_time
        )
        
        # Stockage de l'historique
        self.validation_history.append(result)
        
        logger.info(f"Dataset validation completed for {dataset_id}: "
                   f"Score {validation_score:.1f}, {len(violations)} violations in {execution_time*1000:.2f}ms")
        
        return result
    
    async def _apply_rule(
        self,
        rule: ValidationRule,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]]
    ) -> List[ValidationViolation]:
        """Applique une règle de validation"""
        violations = []
        
        try:
            if asyncio.iscoroutinefunction(rule.validator_function):
                rule_violations = await rule.validator_function(data, schema, rule.parameters)
            else:
                rule_violations = rule.validator_function(data, schema, rule.parameters)
            
            # Assurer que les violations ont le bon rule_id
            for violation in rule_violations:
                violation.rule_id = rule.id
                violations.append(violation)
                
        except Exception as e:
            violations.append(ValidationViolation(
                rule_id=rule.id,
                severity=ValidationSeverity.CRITICAL,
                message=f"Rule execution error: {str(e)}"
            ))
        
        return violations
    
    def _calculate_validation_score(
        self,
        violations_by_severity: Dict[str, int],
        total_records: int,
        total_fields: int
    ) -> float:
        """Calcule le score de validation"""
        base_score = 100.0
        
        # Pénalités par sévérité
        penalties = {
            "critical": 50,  # Très grave
            "error": 20,     # Grave
            "warning": 5,    # Modéré
            "info": 1        # Faible
        }
        
        total_penalty = 0
        for severity, count in violations_by_severity.items():
            if count > 0:
                penalty_per_violation = penalties.get(severity, 0)
                # Normaliser par rapport au nombre total d'éléments
                normalized_penalty = (penalty_per_violation * count) / (total_records * total_fields) * 100
                total_penalty += normalized_penalty
        
        final_score = max(0.0, base_score - total_penalty)
        return round(final_score, 2)
    
    # Validateurs intégrés
    
    def _validate_data_type(
        self,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> List[ValidationViolation]:
        """Valide les types de données"""
        violations = []
        
        if not schema:
            return violations
        
        for field_name, values in data.items():
            if field_name in schema:
                expected_type = schema[field_name].get("type")
                if expected_type:
                    for i, value in enumerate(values):
                        if value is not None:
                            actual_type = type(value).__name__
                            
                            # Mapping des types
                            type_mapping = {
                                "string": ["str"],
                                "integer": ["int"],
                                "number": ["int", "float"],
                                "boolean": ["bool"]
                            }
                            
                            valid_types = type_mapping.get(expected_type, [expected_type])
                            
                            if actual_type not in valid_types:
                                violations.append(ValidationViolation(
                                    rule_id="data_type_check",
                                    severity=ValidationSeverity.ERROR,
                                    message=f"Invalid data type for field {field_name}",
                                    field_name=field_name,
                                    record_index=i,
                                    actual_value=actual_type,
                                    expected_value=expected_type
                                ))
        
        return violations
    
    def _validate_not_null(
        self,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> List[ValidationViolation]:
        """Valide l'absence de valeurs nulles pour champs requis"""
        violations = []
        
        required_fields = parameters.get("required_fields", [])
        if schema:
            # Ajouter les champs marqués comme requis dans le schéma
            for field_name, field_schema in schema.items():
                if field_schema.get("required", False):
                    required_fields.append(field_name)
        
        for field_name in required_fields:
            if field_name in data:
                values = data[field_name]
                for i, value in enumerate(values):
                    if value is None or value == "":
                        violations.append(ValidationViolation(
                            rule_id="null_check",
                            severity=ValidationSeverity.WARNING,
                            message=f"Required field {field_name} is null or empty",
                            field_name=field_name,
                            record_index=i,
                            actual_value=value
                        ))
        
        return violations
    
    def _validate_range(
        self,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> List[ValidationViolation]:
        """Valide les plages de valeurs numériques"""
        violations = []
        
        range_constraints = parameters.get("ranges", {})
        
        # Ajouter contraintes du schéma
        if schema:
            for field_name, field_schema in schema.items():
                if "minimum" in field_schema or "maximum" in field_schema:
                    range_constraints[field_name] = {
                        "min": field_schema.get("minimum"),
                        "max": field_schema.get("maximum")
                    }
        
        for field_name, constraints in range_constraints.items():
            if field_name in data:
                min_val = constraints.get("min")
                max_val = constraints.get("max")
                
                for i, value in enumerate(data[field_name]):
                    if value is not None and isinstance(value, (int, float)):
                        if min_val is not None and value < min_val:
                            violations.append(ValidationViolation(
                                rule_id="range_check",
                                severity=ValidationSeverity.ERROR,
                                message=f"Value {value} below minimum {min_val} for field {field_name}",
                                field_name=field_name,
                                record_index=i,
                                actual_value=value,
                                expected_value=f">={min_val}"
                            ))
                        
                        if max_val is not None and value > max_val:
                            violations.append(ValidationViolation(
                                rule_id="range_check",
                                severity=ValidationSeverity.ERROR,
                                message=f"Value {value} above maximum {max_val} for field {field_name}",
                                field_name=field_name,
                                record_index=i,
                                actual_value=value,
                                expected_value=f"<={max_val}"
                            ))
        
        return violations
    
    def _validate_format(
        self,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> List[ValidationViolation]:
        """Valide les formats avec expressions régulières"""
        violations = []
        
        format_patterns = parameters.get("patterns", {})
        
        # Patterns prédéfinis
        predefined_patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone": r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
            "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        }
        
        # Ajouter formats du schéma
        if schema:
            for field_name, field_schema in schema.items():
                format_name = field_schema.get("format")
                if format_name in predefined_patterns:
                    format_patterns[field_name] = predefined_patterns[format_name]
                elif "pattern" in field_schema:
                    format_patterns[field_name] = field_schema["pattern"]
        
        for field_name, pattern in format_patterns.items():
            if field_name in data:
                compiled_pattern = re.compile(pattern)
                
                for i, value in enumerate(data[field_name]):
                    if value is not None:
                        str_value = str(value)
                        if not compiled_pattern.match(str_value):
                            violations.append(ValidationViolation(
                                rule_id="format_check",
                                severity=ValidationSeverity.ERROR,
                                message=f"Value '{str_value}' does not match expected format for field {field_name}",
                                field_name=field_name,
                                record_index=i,
                                actual_value=str_value,
                                expected_value=f"Pattern: {pattern}"
                            ))
        
        return violations
    
    def _validate_uniqueness(
        self,
        data: Dict[str, List[Any]],
        schema: Optional[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> List[ValidationViolation]:
        """Valide l'unicité des valeurs"""
        violations = []
        
        unique_fields = parameters.get("unique_fields", [])
        
        # Ajouter champs uniques du schéma
        if schema:
            for field_name, field_schema in schema.items():
                if field_schema.get("unique", False):
                    unique_fields.append(field_name)
        
        for field_name in unique_fields:
            if field_name in data:
                values = data[field_name]
                seen_values = set()
                
                for i, value in enumerate(values):
                    if value is not None:
                        if value in seen_values:
                            violations.append(ValidationViolation(
                                rule_id="uniqueness_check",
                                severity=ValidationSeverity.ERROR,
                                message=f"Duplicate value '{value}' found in unique field {field_name}",
                                field_name=field_name,
                                record_index=i,
                                actual_value=value
                            ))
                        else:
                            seen_values.add(value)
        
        return violations
    
    async def validate_schema_compatibility(
        self,
        new_schema: Dict[str, Any],
        existing_schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Valide la compatibilité entre schémas
        
        Expertise DBA: Evolution schéma sans rupture
        """
        violations = []
        
        # Vérifier les champs supprimés
        for field_name in existing_schema:
            if field_name not in new_schema:
                violations.append(ValidationViolation(
                    rule_id="schema_compatibility",
                    severity=ValidationSeverity.ERROR,
                    message=f"Field {field_name} removed from schema",
                    field_name=field_name
                ))
        
        # Vérifier les changements de type
        for field_name in new_schema:
            if field_name in existing_schema:
                old_type = existing_schema[field_name].get("type")
                new_type = new_schema[field_name].get("type")
                
                if old_type != new_type:
                    violations.append(ValidationViolation(
                        rule_id="schema_compatibility",
                        severity=ValidationSeverity.WARNING,
                        message=f"Type change for field {field_name}: {old_type} -> {new_type}",
                        field_name=field_name,
                        actual_value=new_type,
                        expected_value=old_type
                    ))
        
        # Résultat de validation schéma
        violations_by_severity = {
            "info": sum(1 for v in violations if v.severity == ValidationSeverity.INFO),
            "warning": sum(1 for v in violations if v.severity == ValidationSeverity.WARNING),
            "error": sum(1 for v in violations if v.severity == ValidationSeverity.ERROR),
            "critical": sum(1 for v in violations if v.severity == ValidationSeverity.CRITICAL)
        }
        
        passed = violations_by_severity["error"] == 0 and violations_by_severity["critical"] == 0
        
        return ValidationResult(
            dataset_id="schema_compatibility",
            validation_date=datetime.utcnow(),
            total_records=1,
            total_fields=len(new_schema),
            total_violations=len(violations),
            violations_by_severity=violations_by_severity,
            violations=violations,
            passed=passed,
            validation_score=100.0 if passed else 50.0,
            execution_time=0.001
        )
    
    async def get_validation_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de validation"""
        if not self.validation_history:
            return {"total_validations": 0}
        
        total_validations = len(self.validation_history)
        passed_validations = sum(1 for r in self.validation_history if r.passed)
        
        avg_score = sum(r.validation_score for r in self.validation_history) / total_validations
        avg_execution_time = sum(r.execution_time for r in self.validation_history) / total_validations
        
        return {
            "total_validations": total_validations,
            "pass_rate": passed_validations / total_validations,
            "average_validation_score": avg_score,
            "average_execution_time": avg_execution_time,
            "registered_rules": len(self.validation_rules)
        }

# Exemple d'utilisation
async def demo_data_validation():
    """Démo du framework de validation"""
    framework = DataValidationFramework()
    
    # Schéma d'exemple
    schema = {
        "user_id": {"type": "integer", "unique": True, "required": True},
        "email": {"type": "string", "format": "email", "required": True},
        "age": {"type": "integer", "minimum": 0, "maximum": 120},
        "salary": {"type": "number", "minimum": 0}
    }
    
    # Données avec violations
    sample_data = {
        "user_id": [1, 2, 2, 4],  # Violation: doublon
        "email": ["user1@test.com", "invalid-email", "user3@test.com", None],  # Violations: format et null
        "age": [25, -5, 30, 150],  # Violations: valeurs hors limites
        "salary": [50000, 60000, -1000, 80000]  # Violation: valeur négative
    }
    
    # Validation
    result = await framework.validate_dataset("test_dataset", sample_data, schema)
    
    print(f"Validation result:")
    print(f"  Passed: {result.passed}")
    print(f"  Score: {result.validation_score}")
    print(f"  Total violations: {result.total_violations}")
    print(f"  By severity: {result.violations_by_severity}")
    
    # Afficher quelques violations
    for violation in result.violations[:3]:
        print(f"  - {violation.severity.value}: {violation.message}")

if __name__ == "__main__":
    asyncio.run(demo_data_validation())