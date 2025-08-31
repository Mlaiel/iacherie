"""
 Validation Rules Engine - IA Influencer Agent Platform Enterprise
=================================================================
Module: backend/data_management/validation/rules_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 MOTEUR DE RÈGLES DE VALIDATION CONFIGURABLE
Système de règles flexibles pour validation personnalisée
- Règles configurables par type de créateur
- Moteur d'évaluation dynamique
- Support conditions complexes
- Gestion des exceptions et cas spéciaux
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import os
import json
import re
from abc import ABC, abstractmethod

# Rule evaluation
import ast
import operator
from collections import defaultdict

logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Types de règles de validation"""
    FILE_SIZE = "file_size"
    FILE_FORMAT = "file_format"
    CONTENT_QUALITY = "content_quality"
    METADATA = "metadata"
    BUSINESS_LOGIC = "business_logic"
    SECURITY = "security"
    CUSTOM = "custom"

class RuleOperator(Enum):
    """Opérateurs pour les règles"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX_MATCH = "regex_match"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"

class RuleCondition(Enum):
    """Conditions de combinaison des règles"""
    AND = "and"
    OR = "or"
    NOT = "not"

class RuleSeverity(Enum):
    """Niveaux de sévérité des règles"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationRule:
    """Définition d'une règle de validation"""
    id: str
    name: str
    description: str
    rule_type: RuleType
    field_path: str  # Chemin vers le champ à valider (ex: "metadata.duration")
    operator: RuleOperator
    expected_value: Any
    severity: RuleSeverity
    enabled: bool = True
    creator_types: List[str] = field(default_factory=list)  # Types de créateurs concernés
    content_types: List[str] = field(default_factory=list)  # Types de contenu concernés
    conditions: List['ValidationRule'] = field(default_factory=list)  # Sous-règles
    condition_operator: RuleCondition = RuleCondition.AND
    custom_function: Optional[str] = None  # Nom de fonction personnalisée
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RuleEvaluationResult:
    """Résultat d'évaluation d'une règle"""
    rule_id: str
    rule_name: str
    passed: bool
    severity: RuleSeverity
    message: str
    field_path: str
    actual_value: Any
    expected_value: Any
    evaluation_time: float

@dataclass
class RulesEvaluationResult:
    """Résultat global d'évaluation des règles"""
    is_valid: bool
    total_rules: int
    passed_rules: int
    failed_rules: int
    rule_results: List[RuleEvaluationResult]
    errors: List[str]
    warnings: List[str]
    info_messages: List[str]
    evaluation_summary: Dict[str, Any]

class RuleEvaluator:
    """Évaluateur de règles"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.RuleEvaluator")
        
        # Mapping des opérateurs
        self.operators = {
            RuleOperator.EQUALS: operator.eq,
            RuleOperator.NOT_EQUALS: operator.ne,
            RuleOperator.GREATER_THAN: operator.gt,
            RuleOperator.LESS_THAN: operator.lt,
            RuleOperator.GREATER_EQUAL: operator.ge,
            RuleOperator.LESS_EQUAL: operator.le,
        }
        
        # Fonctions personnalisées disponibles
        self.custom_functions = {}
        self._register_builtin_functions()
    
    def evaluate_rule(self, rule: ValidationRule, data: Dict[str, Any]) -> RuleEvaluationResult:
        """Évalue une règle individuelle"""
        start_time = datetime.now()
        
        try:
            # Extraction de la valeur du champ
            actual_value = self._extract_field_value(data, rule.field_path)
            
            # Évaluation selon l'opérateur
            passed = self._evaluate_operator(rule.operator, actual_value, rule.expected_value)
            
            # Évaluation des sous-conditions si présentes
            if rule.conditions:
                sub_results = [self.evaluate_rule(sub_rule, data) for sub_rule in rule.conditions]
                
                if rule.condition_operator == RuleCondition.AND:
                    passed = passed and all(result.passed for result in sub_results)
                elif rule.condition_operator == RuleCondition.OR:
                    passed = passed or any(result.passed for result in sub_results)
                elif rule.condition_operator == RuleCondition.NOT:
                    passed = not passed
            
            # Évaluation fonction personnalisée
            if rule.custom_function and rule.custom_function in self.custom_functions:
                custom_result = self.custom_functions[rule.custom_function](actual_value, rule.expected_value, data)
                passed = passed and custom_result
            
            # Message d'erreur
            if not passed and rule.error_message:
                message = rule.error_message.format(
                    actual=actual_value,
                    expected=rule.expected_value,
                    field=rule.field_path
                )
            else:
                message = self._generate_default_message(rule, actual_value, passed)
            
            evaluation_time = (datetime.now() - start_time).total_seconds()
            
            return RuleEvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                passed=passed,
                severity=rule.severity,
                message=message,
                field_path=rule.field_path,
                actual_value=actual_value,
                expected_value=rule.expected_value,
                evaluation_time=evaluation_time
            )
            
        except Exception as e:
            self.logger.error(f"Erreur évaluation règle {rule.id}: {e}")
            evaluation_time = (datetime.now() - start_time).total_seconds()
            
            return RuleEvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                passed=False,
                severity=RuleSeverity.ERROR,
                message=f"Erreur d'évaluation: {str(e)}",
                field_path=rule.field_path,
                actual_value=None,
                expected_value=rule.expected_value,
                evaluation_time=evaluation_time
            )
    
    def _extract_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Extrait une valeur depuis un chemin de champ"""



        try:
            parts = field_path.split('.')
            value = data
            
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and part.isdigit():
                    index = int(part)
                    value = value[index] if index < len(value) else None
                else:
                    return None
                
                if value is None:
                    break
            
            return value
            
        except Exception as e:
            self.logger.debug(f"Erreur extraction champ {field_path}: {e}")
            return None
    
    def _evaluate_operator(self, op: RuleOperator, actual: Any, expected: Any) -> bool:
        """Évalue un opérateur"""



        try:
            if op in self.operators:
                return self.operators[op](actual, expected)
            
            elif op == RuleOperator.CONTAINS:
                return expected in actual if actual else False
            
            elif op == RuleOperator.NOT_CONTAINS:
                return expected not in actual if actual else True
            
            elif op == RuleOperator.STARTS_WITH:
                return str(actual).startswith(str(expected)) if actual else False
            
            elif op == RuleOperator.ENDS_WITH:
                return str(actual).endswith(str(expected)) if actual else False
            
            elif op == RuleOperator.REGEX_MATCH:
                return bool(re.match(str(expected), str(actual))) if actual else False
            
            elif op == RuleOperator.IN_LIST:
                return actual in expected if expected else False
            
            elif op == RuleOperator.NOT_IN_LIST:
                return actual not in expected if expected else True
            
            elif op == RuleOperator.IS_EMPTY:
                return not actual or len(str(actual)) == 0
            
            elif op == RuleOperator.IS_NOT_EMPTY:
                return bool(actual) and len(str(actual)) > 0
            
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur évaluation opérateur {op}: {e}")
            return False
    
    def _generate_default_message(self, rule: ValidationRule, actual_value: Any, passed: bool) -> str:
        """Génère un message par défaut"""
        if passed:
            return f"Rule '{rule.name}' passed"
        else:
            return f"Rule '{rule.name}' failed: expected {rule.expected_value}, got {actual_value}"
    
    def _register_builtin_functions(self):
        """Enregistre les fonctions intégrées"""
        
        def validate_audio_duration(actual, expected, data):
            """Valide la durée audio selon le type de créateur"""
            creator_type = data.get('creator_type', '')
            
            if creator_type == 'musician':
                return 10 <= actual <= 3600  # 10s à 1h
            elif creator_type == 'comedian':
                return 30 <= actual <= 1800  # 30s à 30min
            else:
                return actual <= expected
        
        def validate_image_resolution(actual, expected, data):
            """Valide la résolution image selon le type de créateur"""
            if not isinstance(actual, (list, tuple)) or len(actual) != 2:
                return False
            
            width, height = actual
            min_width, min_height = expected if isinstance(expected, (list, tuple)) else [expected, expected]
            
            creator_type = data.get('creator_type', '')
            
            if creator_type == 'photographer':
                return width >= 2000 and height >= 1333  # Minimum professionnel
            elif creator_type == 'influencer':
                return width >= 1080 and height >= 1080  # Instagram standard
            else:
                return width >= min_width and height >= min_height
        
        def validate_file_extension_coherence(actual, expected, data):
            """Valide la cohérence extension/type de contenu"""
            file_extension = data.get('file_extension', '').lower()
            content_type = data.get('content_type', '')
            
            coherence_map = {
                'audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a'],
                'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
                'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
                'document': ['.txt', '.md', '.pdf', '.docx']
            }
            
            return file_extension in coherence_map.get(content_type, [])
        
        self.custom_functions = {
            'validate_audio_duration': validate_audio_duration,
            'validate_image_resolution': validate_image_resolution,
            'validate_file_extension_coherence': validate_file_extension_coherence
        }

class RuleSetManager:
    """Gestionnaire de jeux de règles"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.RuleSetManager")
        self.rule_sets: Dict[str, List[ValidationRule]] = {}
        self.evaluator = RuleEvaluator()
        
        # Chargement des règles par défaut
        self._load_default_rules()
    
    def load_rules_from_config(self, config_path: str) -> bool:
        """Charge les règles depuis un fichier de configuration"""



        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for rule_set_name, rules_data in config.items():
                rules = []
                for rule_data in rules_data:
                    rule = self._create_rule_from_dict(rule_data)
                    rules.append(rule)
                
                self.rule_sets[rule_set_name] = rules
            
            self.logger.info(f"Loaded {len(config)} rule sets from {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur chargement règles {config_path}: {e}")
            return False
    
    def save_rules_to_config(self, config_path: str) -> bool:
        """Sauvegarde les règles dans un fichier de configuration"""



        try:
            config = {}
            
            for rule_set_name, rules in self.rule_sets.items():
                config[rule_set_name] = [self._rule_to_dict(rule) for rule in rules]
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
            
            self.logger.info(f"Saved {len(config)} rule sets to {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde règles {config_path}: {e}")
            return False
    
    def add_rule(self, rule_set_name: str, rule: ValidationRule):
        """Ajoute une règle à un jeu de règles"""
        if rule_set_name not in self.rule_sets:
            self.rule_sets[rule_set_name] = []
        
        # Vérification unicité ID
        existing_ids = [r.id for r in self.rule_sets[rule_set_name]]
        if rule.id in existing_ids:
            rule.id = f"{rule.id}_{len(existing_ids)}"
        
        self.rule_sets[rule_set_name].append(rule)
        self.logger.info(f"Added rule {rule.id} to set {rule_set_name}")
    
    def remove_rule(self, rule_set_name: str, rule_id: str) -> bool:
        """Supprime une règle d'un jeu de règles"""
        if rule_set_name not in self.rule_sets:
            return False
        
        original_count = len(self.rule_sets[rule_set_name])
        self.rule_sets[rule_set_name] = [r for r in self.rule_sets[rule_set_name] if r.id != rule_id]
        
        removed = len(self.rule_sets[rule_set_name]) < original_count
        if removed:
            self.logger.info(f"Removed rule {rule_id} from set {rule_set_name}")
        
        return removed
    
    def get_applicable_rules(self, rule_set_name: str, creator_type: str, content_type: str) -> List[ValidationRule]:
        """Récupère les règles applicables selon le contexte"""
        if rule_set_name not in self.rule_sets:
            return []
        
        applicable_rules = []
        
        for rule in self.rule_sets[rule_set_name]:
            if not rule.enabled:
                continue
            
            # Vérification type de créateur
            if rule.creator_types and creator_type not in rule.creator_types:
                continue
            
            # Vérification type de contenu
            if rule.content_types and content_type not in rule.content_types:
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    def evaluate_rules(self, rule_set_name: str, data: Dict[str, Any], creator_type: str = "", content_type: str = "") -> RulesEvaluationResult:
        """Évalue un jeu de règles contre des données"""
        
        applicable_rules = self.get_applicable_rules(rule_set_name, creator_type, content_type)
        
        if not applicable_rules:
            return RulesEvaluationResult(
                is_valid=True,
                total_rules=0,
                passed_rules=0,
                failed_rules=0,
                rule_results=[],
                errors=[],
                warnings=[],
                info_messages=["No applicable rules found"],
                evaluation_summary={}
            )
        
        # Évaluation des règles
        rule_results = []
        errors = []
        warnings = []
        info_messages = []
        
        for rule in applicable_rules:
            result = self.evaluator.evaluate_rule(rule, data)
            rule_results.append(result)
            
            # Classification des messages
            if not result.passed:
                if result.severity == RuleSeverity.CRITICAL or result.severity == RuleSeverity.ERROR:
                    errors.append(result.message)
                elif result.severity == RuleSeverity.WARNING:
                    warnings.append(result.message)
                else:
                    info_messages.append(result.message)
        
        # Calcul des statistiques
        total_rules = len(rule_results)
        passed_rules = sum(1 for r in rule_results if r.passed)
        failed_rules = total_rules - passed_rules
        
        # Validation globale (aucune erreur critique)
        critical_errors = [r for r in rule_results if not r.passed and r.severity in [RuleSeverity.CRITICAL, RuleSeverity.ERROR]]
        is_valid = len(critical_errors) == 0
        
        # Résumé détaillé
        evaluation_summary = {
            'success_rate': (passed_rules / total_rules) * 100 if total_rules > 0 else 100,
            'critical_failures': len([r for r in rule_results if not r.passed and r.severity == RuleSeverity.CRITICAL]),
            'error_failures': len([r for r in rule_results if not r.passed and r.severity == RuleSeverity.ERROR]),
            'warning_failures': len([r for r in rule_results if not r.passed and r.severity == RuleSeverity.WARNING]),
            'total_evaluation_time': sum(r.evaluation_time for r in rule_results),
            'rule_types_evaluated': list(set(r.rule_name.split('_')[0] for r in rule_results if '_' in r.rule_name))
        }
        
        return RulesEvaluationResult(
            is_valid=is_valid,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            rule_results=rule_results,
            errors=errors,
            warnings=warnings,
            info_messages=info_messages,
            evaluation_summary=evaluation_summary
        )
    
    def _create_rule_from_dict(self, rule_data: Dict[str, Any]) -> ValidationRule:
        """Crée une règle depuis un dictionnaire"""



        return ValidationRule(
            id=rule_data['id'],
            name=rule_data['name'],
            description=rule_data.get('description', ''),
            rule_type=RuleType(rule_data['rule_type']),
            field_path=rule_data['field_path'],
            operator=RuleOperator(rule_data['operator']),
            expected_value=rule_data['expected_value'],
            severity=RuleSeverity(rule_data.get('severity', 'error')),
            enabled=rule_data.get('enabled', True),
            creator_types=rule_data.get('creator_types', []),
            content_types=rule_data.get('content_types', []),
            custom_function=rule_data.get('custom_function'),
            error_message=rule_data.get('error_message', ''),
            created_at=datetime.fromisoformat(rule_data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(rule_data.get('updated_at', datetime.now().isoformat()))
        )
    
    def _rule_to_dict(self, rule: ValidationRule) -> Dict[str, Any]:
        """Convertit une règle en dictionnaire"""



        return {
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'rule_type': rule.rule_type.value,
            'field_path': rule.field_path,
            'operator': rule.operator.value,
            'expected_value': rule.expected_value,
            'severity': rule.severity.value,
            'enabled': rule.enabled,
            'creator_types': rule.creator_types,
            'content_types': rule.content_types,
            'custom_function': rule.custom_function,
            'error_message': rule.error_message,
            'created_at': rule.created_at.isoformat(),
            'updated_at': rule.updated_at.isoformat()
        }
    
    def _load_default_rules(self):
        """Charge les règles par défaut"""
        
        # Règles générales de taille de fichier
        file_size_rules = [
            ValidationRule(
                id="file_size_max_general",
                name="Maximum File Size",
                description="Limite de taille générale des fichiers",
                rule_type=RuleType.FILE_SIZE,
                field_path="file_size",
                operator=RuleOperator.LESS_EQUAL,
                expected_value=100 * 1024 * 1024,  # 100MB
                severity=RuleSeverity.ERROR,
                error_message="File size {actual} exceeds maximum allowed {expected} bytes"
            ),
            ValidationRule(
                id="file_size_min_general",
                name="Minimum File Size",
                description="Taille minimale des fichiers",
                rule_type=RuleType.FILE_SIZE,
                field_path="file_size",
                operator=RuleOperator.GREATER_THAN,
                expected_value=0,
                severity=RuleSeverity.ERROR,
                error_message="File cannot be empty"
            )
        ]
        
        # Règles spécifiques aux musiciens
        musician_rules = [
            ValidationRule(
                id="audio_duration_musician",
                name="Audio Duration for Musicians",
                description="Durée audio pour musiciens",
                rule_type=RuleType.CONTENT_QUALITY,
                field_path="duration",
                operator=RuleOperator.GREATER_THAN,
                expected_value=10,
                severity=RuleSeverity.WARNING,
                creator_types=["musician"],
                content_types=["audio"],
                custom_function="validate_audio_duration",
                error_message="Audio too short for music content: {actual}s"
            ),
            ValidationRule(
                id="audio_quality_musician",
                name="Audio Quality for Musicians",
                description="Qualité audio pour musiciens",
                rule_type=RuleType.CONTENT_QUALITY,
                field_path="audio_bitrate",
                operator=RuleOperator.GREATER_EQUAL,
                expected_value=192,
                severity=RuleSeverity.WARNING,
                creator_types=["musician"],
                content_types=["audio"],
                error_message="Audio bitrate {actual} below recommended {expected} for music"
            )
        ]
        
        # Règles spécifiques aux photographes
        photographer_rules = [
            ValidationRule(
                id="image_resolution_photographer",
                name="Image Resolution for Photographers",
                description="Résolution image pour photographes",
                rule_type=RuleType.CONTENT_QUALITY,
                field_path="resolution",
                operator=RuleOperator.CUSTOM,
                expected_value=[2000, 1333],
                severity=RuleSeverity.WARNING,
                creator_types=["photographer"],
                content_types=["image"],
                custom_function="validate_image_resolution",
                error_message="Image resolution {actual} below professional standards"
            ),
            ValidationRule(
                id="image_format_photographer",
                name="Image Format for Photographers",
                description="Formats d'image acceptés pour photographes",
                rule_type=RuleType.FILE_FORMAT,
                field_path="file_extension",
                operator=RuleOperator.IN_LIST,
                expected_value=[".jpg", ".jpeg", ".png", ".tiff", ".raw"],
                severity=RuleSeverity.ERROR,
                creator_types=["photographer"],
                content_types=["image"],
                error_message="Image format {actual} not suitable for professional photography"
            )
        ]
        
        # Règles de sécurité
        security_rules = [
            ValidationRule(
                id="file_extension_coherence",
                name="File Extension Coherence",
                description="Cohérence extension/contenu",
                rule_type=RuleType.SECURITY,
                field_path="file_extension",
                operator=RuleOperator.CUSTOM,
                expected_value=True,
                severity=RuleSeverity.ERROR,
                custom_function="validate_file_extension_coherence",
                error_message="File extension {actual} does not match content type"
            ),
            ValidationRule(
                id="malware_scan_clean",
                name="Malware Scan Clean",
                description="Fichier exempt de malwares",
                rule_type=RuleType.SECURITY,
                field_path="malware_detected",
                operator=RuleOperator.EQUALS,
                expected_value=False,
                severity=RuleSeverity.CRITICAL,
                error_message="SECURITY ALERT: Malware detected in file"
            )
        ]
        
        # Ajout des règles aux jeux
        self.rule_sets["general"] = file_size_rules + security_rules
        self.rule_sets["musician"] = musician_rules
        self.rule_sets["photographer"] = photographer_rules
        self.rule_sets["security"] = security_rules

class RulesEngine:
    """Moteur principal de règles de validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(f"{__name__}.RulesEngine")
        self.rule_set_manager = RuleSetManager()
        
        # Chargement configuration personnalisée
        if config_path and os.path.exists(config_path):
            self.rule_set_manager.load_rules_from_config(config_path)
        
        # Cache des résultats d'évaluation
        self._evaluation_cache = {}
    
    def validate_with_rules(
        self,
        data: Dict[str, Any],
        rule_sets: List[str],
        creator_type: str = "",
        content_type: str = "",
        use_cache: bool = True
    ) -> RulesEvaluationResult:
        """Valide des données avec des jeux de règles spécifiques"""
        
        # Vérification cache
        cache_key = self._generate_cache_key(data, rule_sets, creator_type, content_type)
        if use_cache and cache_key in self._evaluation_cache:
            return self._evaluation_cache[cache_key]
        
        # Compilation des résultats de tous les jeux de règles
        all_results = []
        all_errors = []
        all_warnings = []
        all_info = []
        
        for rule_set_name in rule_sets:
            result = self.rule_set_manager.evaluate_rules(rule_set_name, data, creator_type, content_type)
            
            all_results.extend(result.rule_results)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            all_info.extend(result.info_messages)
        
        # Résultat consolidé
        total_rules = len(all_results)
        passed_rules = sum(1 for r in all_results if r.passed)
        failed_rules = total_rules - passed_rules
        
        # Validation globale
        critical_errors = [r for r in all_results if not r.passed and r.severity in [RuleSeverity.CRITICAL, RuleSeverity.ERROR]]
        is_valid = len(critical_errors) == 0
        
        # Résumé consolidé
        evaluation_summary = {
            'rule_sets_evaluated': rule_sets,
            'creator_type': creator_type,
            'content_type': content_type,
            'success_rate': (passed_rules / total_rules) * 100 if total_rules > 0 else 100,
            'critical_failures': len([r for r in all_results if not r.passed and r.severity == RuleSeverity.CRITICAL]),
            'error_failures': len([r for r in all_results if not r.passed and r.severity == RuleSeverity.ERROR]),
            'warning_failures': len([r for r in all_results if not r.passed and r.severity == RuleSeverity.WARNING]),
            'total_evaluation_time': sum(r.evaluation_time for r in all_results)
        }
        
        consolidated_result = RulesEvaluationResult(
            is_valid=is_valid,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            rule_results=all_results,
            errors=list(set(all_errors)),  # Dédoublonnage
            warnings=list(set(all_warnings)),
            info_messages=list(set(all_info)),
            evaluation_summary=evaluation_summary
        )
        
        # Mise en cache
        if use_cache:
            self._evaluation_cache[cache_key] = consolidated_result
        
        return consolidated_result
    
    def validate_file_with_rules(
        self,
        file_path: str,
        creator_type: str,
        content_type: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> RulesEvaluationResult:
        """Valide un fichier avec les règles appropriées"""
        
        # Compilation des données de base
        data = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'file_extension': Path(file_path).suffix.lower(),
            'creator_type': creator_type,
            'content_type': content_type
        }
        
        # Ajout des données supplémentaires
        if additional_data:
            data.update(additional_data)
        
        # Sélection des jeux de règles appropriés
        rule_sets = ['general']  # Toujours inclure les règles générales
        
        if creator_type:
            rule_sets.append(creator_type)
        
        rule_sets.append('security')  # Toujours inclure la sécurité
        
        # Validation
        return self.validate_with_rules(data, rule_sets, creator_type, content_type)
    
    def add_custom_rule(self, rule_set_name: str, rule_config: Dict[str, Any]) -> bool:
        """Ajoute une règle personnalisée"""



        try:
            rule = ValidationRule(
                id=rule_config['id'],
                name=rule_config['name'],
                description=rule_config.get('description', ''),
                rule_type=RuleType(rule_config['rule_type']),
                field_path=rule_config['field_path'],
                operator=RuleOperator(rule_config['operator']),
                expected_value=rule_config['expected_value'],
                severity=RuleSeverity(rule_config.get('severity', 'error')),
                enabled=rule_config.get('enabled', True),
                creator_types=rule_config.get('creator_types', []),
                content_types=rule_config.get('content_types', []),
                custom_function=rule_config.get('custom_function'),
                error_message=rule_config.get('error_message', '')
            )
            
            self.rule_set_manager.add_rule(rule_set_name, rule)
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur ajout règle personnalisée: {e}")
            return False
    
    def get_validation_summary(self, result: RulesEvaluationResult) -> Dict[str, Any]:
        """Génère un résumé de validation formaté"""



        return {
            'status': 'VALID' if result.is_valid else 'INVALID',
            'overall_score': (result.passed_rules / result.total_rules) * 100 if result.total_rules > 0 else 100,
            'rules_summary': {
                'total': result.total_rules,
                'passed': result.passed_rules,
                'failed': result.failed_rules
            },
            'issues_summary': {
                'critical_errors': result.evaluation_summary.get('critical_failures', 0),
                'errors': result.evaluation_summary.get('error_failures', 0),
                'warnings': result.evaluation_summary.get('warning_failures', 0)
            },
            'messages': {
                'errors': result.errors[:5],  # Limiter à 5 pour affichage
                'warnings': result.warnings[:5],
                'info': result.info_messages[:3]
            },
            'performance': {
                'evaluation_time': result.evaluation_summary.get('total_evaluation_time', 0),
                'rule_sets_used': result.evaluation_summary.get('rule_sets_evaluated', [])
            }
        }
    
    def _generate_cache_key(self, data: Dict[str, Any], rule_sets: List[str], creator_type: str, content_type: str) -> str:
        """Génère une clé de cache pour les résultats"""
        import hashlib
        
        # Création d'une signature des données importantes
        key_data = {
            'file_path': data.get('file_path', ''),
            'file_size': data.get('file_size', 0),
            'rule_sets': sorted(rule_sets),
            'creator_type': creator_type,
            'content_type': content_type
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

class AsyncRulesEngine:
    """Version asynchrone du moteur de règles"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.sync_engine = RulesEngine(config_path)
        self.logger = logging.getLogger(f"{__name__}.AsyncRulesEngine")
    
    async def validate_with_rules(
        self,
        data: Dict[str, Any],
        rule_sets: List[str],
        creator_type: str = "",
        content_type: str = "",
        use_cache: bool = True
    ) -> RulesEvaluationResult:
        """Valide avec des règles de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_engine.validate_with_rules,
            data,
            rule_sets,
            creator_type,
            content_type,
            use_cache
        )
        
        return result
    
    async def validate_file_with_rules(
        self,
        file_path: str,
        creator_type: str,
        content_type: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> RulesEvaluationResult:
        """Valide un fichier avec des règles de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_engine.validate_file_with_rules,
            file_path,
            creator_type,
            content_type,
            additional_data
        )
        
        return result

# Export des classes principales
__all__ = [
    'RulesEngine',
    'AsyncRulesEngine',
    'RuleSetManager',
    'RuleEvaluator',
    'ValidationRule',
    'RulesEvaluationResult',
    'RuleEvaluationResult',
    'RuleType',
    'RuleOperator',
    'RuleCondition',
    'RuleSeverity'
]
