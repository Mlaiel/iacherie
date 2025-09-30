#!/usr/bin/env python3
"""
📋 BUSINESS RULES VALIDATOR - AINFLUE QUALITY MODULE
===================================================

Validateur règles métier enterprise pour l'écosystème IA Influencer Agent.
Validation logique business complexe avec patterns DBA et rules engine.

© 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
Contact: mlaiel@live.de

🎖️ EXPERTS RESPONSABLES:
- DBA: Validation règles données et intégrité business
- Backend Senior: Infrastructure validation robuste et patterns
- Lead Dev IA: Orchestration règles métier intelligentes

🚀 FONCTIONNALITÉS ENTERPRISE:
- Validation règles métier configurable
- Moteur de règles dynamique avec DSL
- Validation workflow business Ainflue
- Validation contraintes créateurs/contenu
- Audit conformité business automatisé
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import re
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Types de règles business"""
    VALIDATION = "validation"
    CONSTRAINT = "constraint"
    TRIGGER = "trigger"
    CONDITIONAL = "conditional"
    WORKFLOW = "workflow"
    COMPLIANCE = "compliance"

class RuleSeverity(Enum):
    """Sévérité des violations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WARNING = "warning"

class RuleStatus(Enum):
    """Status des règles"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"

@dataclass
class BusinessRule:
    """Règle métier enterprise"""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    severity: RuleSeverity
    status: RuleStatus = RuleStatus.ACTIVE
    condition: str = ""  # Expression à évaluer
    action: str = ""  # Action si condition vraie
    error_message: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RuleViolation:
    """Violation de règle métier"""
    violation_id: str
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    context: Dict[str, Any]
    suggested_fix: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationResult:
    """Résultat validation règles métier"""
    passed: bool
    score: float
    violations: List[RuleViolation]
    rules_checked: int
    rules_passed: int
    execution_time_ms: float
    context: Dict[str, Any] = field(default_factory=dict)

class BusinessRulesValidator:
    """
    🎯 Validateur règles métier enterprise
    
    Moteur de validation des règles business spécifiques à Ainflue,
    incluant validation créateurs, contenu, workflow, et conformité
    avec patterns DBA et enterprise rules engine.
    
    **Expertise DBA + Backend Senior + Lead Dev IA**
    """
    
    def __init__(self):
        """Initialize business rules validator"""
        self.logger = logging.getLogger(__name__ + '.BusinessRulesValidator')
        self.rules = {}
        self.rule_cache = {}
        self.violation_history = []
        
        # Règles par défaut Ainflue
        self._initialize_default_rules()
        
        # Statistiques
        self.total_validations = 0
        self.total_violations = 0
        
        self.logger.info("📋 Business Rules Validator enterprise initialisé")
    
    def _initialize_default_rules(self):
        """
        Initialiser règles métier par défaut Ainflue
        
        **DBA Expert**: Règles intégrité données business
        """
        default_rules = [
            # Règles Créateurs
            BusinessRule(
                rule_id="creator_content_minimum",
                name="Contenu Minimum Créateur",
                description="Un créateur doit avoir au moins 5 contenus validés",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.MEDIUM,
                condition="creator.validated_content_count >= 5",
                error_message="Créateur doit avoir au moins 5 contenus validés"
            ),
            BusinessRule(
                rule_id="creator_profile_complete",
                name="Profil Créateur Complet",
                description="Profil créateur doit être complet pour monétisation",
                rule_type=RuleType.CONSTRAINT,
                severity=RuleSeverity.HIGH,
                condition="creator.profile_completion >= 80",
                error_message="Profil créateur incomplet pour monétisation"
            ),
            
            # Règles Contenu
            BusinessRule(
                rule_id="content_quality_threshold",
                name="Seuil Qualité Contenu",
                description="Contenu doit avoir score qualité minimum 70%",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.HIGH,
                condition="content.quality_score >= 70",
                error_message="Qualité contenu insuffisante"
            ),
            BusinessRule(
                rule_id="content_copyright_check",
                name="Vérification Copyright",
                description="Contenu ne doit pas violer de copyright",
                rule_type=RuleType.COMPLIANCE,
                severity=RuleSeverity.CRITICAL,
                condition="content.copyright_violation == false",
                error_message="Violation copyright détectée"
            ),
            
            # Règles Monétisation
            BusinessRule(
                rule_id="monetization_eligibility",
                name="Éligibilité Monétisation",
                description="Créateur éligible pour monétisation si conditions remplies",
                rule_type=RuleType.WORKFLOW,
                severity=RuleSeverity.HIGH,
                condition="creator.followers >= 1000 AND creator.engagement_rate >= 5",
                error_message="Critères monétisation non atteints"
            ),
            BusinessRule(
                rule_id="revenue_sharing_valid",
                name="Partage Revenus Valide",
                description="Pourcentage partage revenus dans limites acceptables",
                rule_type=RuleType.CONSTRAINT,
                severity=RuleSeverity.MEDIUM,
                condition="revenue.creator_share >= 60 AND revenue.creator_share <= 90",
                error_message="Pourcentage partage revenus invalide"
            ),
            
            # Règles Collaboration
            BusinessRule(
                rule_id="collaboration_compatibility",
                name="Compatibilité Collaboration",
                description="Créateurs doivent être compatibles pour collaboration",
                rule_type=RuleType.VALIDATION,
                severity=RuleSeverity.MEDIUM,
                condition="abs(creator1.engagement_rate - creator2.engagement_rate) <= 10",
                error_message="Créateurs incompatibles pour collaboration"
            ),
            
            # Règles Compliance
            BusinessRule(
                rule_id="gdpr_consent_required",
                name="Consentement GDPR Requis",
                description="Consentement utilisateur requis pour traitement données",
                rule_type=RuleType.COMPLIANCE,
                severity=RuleSeverity.CRITICAL,
                condition="user.gdpr_consent == true",
                error_message="Consentement GDPR manquant"
            ),
            BusinessRule(
                rule_id="age_restriction_content",
                name="Restriction Âge Contenu",
                description="Contenu approprié selon restrictions d'âge",
                rule_type=RuleType.COMPLIANCE,
                severity=RuleSeverity.HIGH,
                condition="content.age_rating <= user.age OR user.age >= 18",
                error_message="Contenu non approprié pour l'âge utilisateur"
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
        
        self.logger.info(f"📊 {len(default_rules)} règles métier par défaut configurées")
    
    def add_rule(self, rule: BusinessRule) -> bool:
        """
        Ajouter règle métier
        
        **Backend Senior**: Gestion lifecycle règles
        """
        try:
            # Validation de la règle
            if not rule.rule_id or not rule.name:
                raise ValueError("ID et nom de règle requis")
            
            # Vérifier condition syntax (basique)
            if rule.condition and not self._validate_condition_syntax(rule.condition):
                raise ValueError(f"Syntaxe condition invalide: {rule.condition}")
            
            self.rules[rule.rule_id] = rule
            
            # Invalider cache si règle existe
            if rule.rule_id in self.rule_cache:
                del self.rule_cache[rule.rule_id]
            
            self.logger.info(f"➕ Règle ajoutée: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur ajout règle {rule.rule_id}: {e}")
            return False
    
    def _validate_condition_syntax(self, condition: str) -> bool:
        """Validation basique syntaxe condition"""
        try:
            # Vérifications basiques
            if not condition:
                return True
            
            # Vérifier parenthèses équilibrées
            if condition.count('(') != condition.count(')'):
                return False
            
            # Vérifier opérateurs valides
            invalid_chars = ['exec', 'eval', 'import', '__']
            for invalid in invalid_chars:
                if invalid in condition.lower():
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def validate(self, data: Dict[str, Any], 
                      rule_types: Optional[List[RuleType]] = None) -> ValidationResult:
        """
        Valider données contre règles métier
        
        **DBA Expert**: Validation logique business complexe
        """
        start_time = time.time()
        violations = []
        rules_checked = 0
        
        try:
            # Filtrer règles selon type si spécifié
            rules_to_check = self._filter_rules(rule_types)
            
            for rule in rules_to_check:
                if rule.status != RuleStatus.ACTIVE:
                    continue
                
                rules_checked += 1
                
                # Évaluer condition
                violation = await self._evaluate_rule(rule, data)
                if violation:
                    violations.append(violation)
            
            # Calculer score
            rules_passed = rules_checked - len(violations)
            score = (rules_passed / max(rules_checked, 1)) * 100
            
            # Mettre à jour statistiques
            self.total_validations += 1
            self.total_violations += len(violations)
            
            # Ajouter à l'historique
            self.violation_history.extend(violations)
            
            # Garder seulement les 1000 dernières violations
            if len(self.violation_history) > 1000:
                self.violation_history = self.violation_history[-1000:]
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ValidationResult(
                passed=len(violations) == 0,
                score=score,
                violations=violations,
                rules_checked=rules_checked,
                rules_passed=rules_passed,
                execution_time_ms=execution_time,
                context={"total_rules": len(self.rules)}
            )
            
            self.logger.debug(f"📋 Validation: {rules_passed}/{rules_checked} règles passées")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur validation règles: {e}")
            return ValidationResult(
                passed=False,
                score=0.0,
                violations=[RuleViolation(
                    violation_id="validation_error",
                    rule_id="system",
                    rule_name="System Error",
                    severity=RuleSeverity.CRITICAL,
                    message=f"Erreur validation: {str(e)}"
                )],
                rules_checked=0,
                rules_passed=0,
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _filter_rules(self, rule_types: Optional[List[RuleType]]) -> List[BusinessRule]:
        """Filtrer règles selon types"""
        if not rule_types:
            return list(self.rules.values())
        
        return [rule for rule in self.rules.values() if rule.rule_type in rule_types]
    
    async def _evaluate_rule(self, rule: BusinessRule, data: Dict[str, Any]) -> Optional[RuleViolation]:
        """
        Évaluer règle métier contre données
        
        **Lead Dev IA**: Intelligence évaluation règles
        """
        try:
            if not rule.condition:
                return None
            
            # Évaluation sécurisée de la condition
            result = self._safe_evaluate_condition(rule.condition, data)
            
            if not result:
                # Violation détectée
                violation = RuleViolation(
                    violation_id=f"violation_{int(time.time())}_{rule.rule_id}",
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=rule.error_message or f"Violation règle: {rule.name}",
                    context=data,
                    suggested_fix=self._generate_suggested_fix(rule, data)
                )
                
                return violation
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erreur évaluation règle {rule.rule_id}: {e}")
            return RuleViolation(
                violation_id=f"error_{int(time.time())}_{rule.rule_id}",
                rule_id=rule.rule_id,
                rule_name=rule.name,
                severity=RuleSeverity.CRITICAL,
                message=f"Erreur évaluation règle: {str(e)}",
                context=data
            )
    
    def _safe_evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """
        Évaluation sécurisée condition
        
        **Backend Senior**: Sécurité et sandboxing
        """
        try:
            # Remplacer variables dans condition
            processed_condition = self._process_condition_variables(condition, data)
            
            # Évaluation sécurisée (simulation)
            # En production, utiliser un parser plus sophistiqué
            return self._simple_condition_evaluator(processed_condition, data)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur évaluation condition: {e}")
            return False
    
    def _process_condition_variables(self, condition: str, data: Dict[str, Any]) -> str:
        """Traiter variables dans condition"""
        # Remplacements simples pour simulation
        replacements = {
            'creator.validated_content_count': str(data.get('creator', {}).get('validated_content_count', 0)),
            'creator.profile_completion': str(data.get('creator', {}).get('profile_completion', 0)),
            'creator.followers': str(data.get('creator', {}).get('followers', 0)),
            'creator.engagement_rate': str(data.get('creator', {}).get('engagement_rate', 0)),
            'content.quality_score': str(data.get('content', {}).get('quality_score', 0)),
            'content.copyright_violation': str(data.get('content', {}).get('copyright_violation', False)).lower(),
            'content.age_rating': str(data.get('content', {}).get('age_rating', 0)),
            'user.gdpr_consent': str(data.get('user', {}).get('gdpr_consent', False)).lower(),
            'user.age': str(data.get('user', {}).get('age', 0)),
            'revenue.creator_share': str(data.get('revenue', {}).get('creator_share', 0))
        }
        
        processed = condition
        for var, value in replacements.items():
            processed = processed.replace(var, value)
        
        return processed
    
    def _simple_condition_evaluator(self, condition: str, data: Dict[str, Any]) -> bool:
        """Évaluateur simple de conditions"""
        try:
            # Simulation basique - en production, utiliser un parser AST
            
            # Gestion AND/OR
            if ' AND ' in condition:
                parts = condition.split(' AND ')
                return all(self._evaluate_simple_expression(part.strip(), data) for part in parts)
            
            if ' OR ' in condition:
                parts = condition.split(' OR ')
                return any(self._evaluate_simple_expression(part.strip(), data) for part in parts)
            
            return self._evaluate_simple_expression(condition, data)
            
        except Exception:
            return False
    
    def _evaluate_simple_expression(self, expr: str, data: Dict[str, Any]) -> bool:
        """Évaluer expression simple"""
        try:
            # Opérateurs supportés
            if '>=' in expr:
                left, right = expr.split('>=')
                return float(left.strip()) >= float(right.strip())
            elif '<=' in expr:
                left, right = expr.split('<=')
                return float(left.strip()) <= float(right.strip())
            elif '>' in expr:
                left, right = expr.split('>')
                return float(left.strip()) > float(right.strip())
            elif '<' in expr:
                left, right = expr.split('<')
                return float(left.strip()) < float(right.strip())
            elif '==' in expr:
                left, right = expr.split('==')
                left_val = left.strip()
                right_val = right.strip()
                
                # Gestion boolean
                if left_val.lower() in ['true', 'false']:
                    return left_val.lower() == right_val.lower()
                
                # Gestion numérique
                try:
                    return float(left_val) == float(right_val)
                except ValueError:
                    return left_val == right_val
            
            return True
            
        except Exception:
            return False
    
    def _generate_suggested_fix(self, rule: BusinessRule, data: Dict[str, Any]) -> str:
        """
        Générer suggestion correction
        
        **Lead Dev IA**: Intelligence recommandations
        """
        # Suggestions basées sur type de règle
        if rule.rule_id == "creator_content_minimum":
            current = data.get('creator', {}).get('validated_content_count', 0)
            needed = 5 - current
            return f"Publier {needed} contenus supplémentaires de qualité"
        
        elif rule.rule_id == "creator_profile_complete":
            completion = data.get('creator', {}).get('profile_completion', 0)
            missing = 80 - completion
            return f"Compléter {missing}% du profil restant"
        
        elif rule.rule_id == "content_quality_threshold":
            score = data.get('content', {}).get('quality_score', 0)
            needed = 70 - score
            return f"Améliorer qualité contenu de {needed} points"
        
        elif rule.rule_id == "monetization_eligibility":
            followers = data.get('creator', {}).get('followers', 0)
            engagement = data.get('creator', {}).get('engagement_rate', 0)
            suggestions = []
            if followers < 1000:
                suggestions.append(f"Augmenter followers de {1000 - followers}")
            if engagement < 5:
                suggestions.append(f"Améliorer engagement de {5 - engagement}%")
            return " et ".join(suggestions)
        
        elif rule.rule_id == "gdpr_consent_required":
            return "Obtenir consentement explicite utilisateur pour GDPR"
        
        elif rule.rule_id == "content_copyright_check":
            return "Vérifier et corriger violations copyright détectées"
        
        return "Corriger selon exigences de la règle métier"
    
    def get_rules_statistics(self) -> Dict[str, Any]:
        """Récupérer statistiques règles"""
        active_rules = sum(1 for rule in self.rules.values() if rule.status == RuleStatus.ACTIVE)
        
        rules_by_type = {}
        for rule in self.rules.values():
            rule_type = rule.rule_type.value
            rules_by_type[rule_type] = rules_by_type.get(rule_type, 0) + 1
        
        recent_violations = [v for v in self.violation_history 
                           if v.timestamp > datetime.now() - timedelta(hours=24)]
        
        return {
            "total_rules": len(self.rules),
            "active_rules": active_rules,
            "rules_by_type": rules_by_type,
            "total_validations": self.total_validations,
            "total_violations": self.total_violations,
            "recent_violations_24h": len(recent_violations)
        }
    
    def get_rule_by_id(self, rule_id: str) -> Optional[BusinessRule]:
        """Récupérer règle par ID"""
        return self.rules.get(rule_id)
    
    def remove_rule(self, rule_id: str) -> bool:
        """Supprimer règle"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"🗑️ Règle supprimée: {rule_id}")
            return True
        return False
    
    def update_rule_status(self, rule_id: str, status: RuleStatus) -> bool:
        """Mettre à jour status règle"""
        if rule_id in self.rules:
            self.rules[rule_id].status = status
            self.rules[rule_id].updated_at = datetime.now()
            self.logger.info(f"🔄 Status règle {rule_id} mis à jour: {status.value}")
            return True
        return False

# Instance globale
business_rules_validator = BusinessRulesValidator()

async def validate_business_rules(data: Dict[str, Any], 
                                rule_types: Optional[List[RuleType]] = None) -> ValidationResult:
    """Valider règles métier enterprise"""
    return await business_rules_validator.validate(data, rule_types)

async def validate_creator_rules(creator_data: Dict[str, Any]) -> ValidationResult:
    """Valider règles spécifiques créateurs"""
    return await business_rules_validator.validate(
        {"creator": creator_data}, 
        [RuleType.VALIDATION, RuleType.CONSTRAINT]
    )

async def validate_content_rules(content_data: Dict[str, Any]) -> ValidationResult:
    """Valider règles spécifiques contenu"""
    return await business_rules_validator.validate(
        {"content": content_data}, 
        [RuleType.VALIDATION, RuleType.COMPLIANCE]
    )

async def validate_monetization_rules(creator_data: Dict[str, Any], 
                                    revenue_data: Dict[str, Any]) -> ValidationResult:
    """Valider règles monétisation"""
    return await business_rules_validator.validate(
        {"creator": creator_data, "revenue": revenue_data}, 
        [RuleType.WORKFLOW, RuleType.CONSTRAINT]
    )

# Exports principaux
__all__ = [
    'BusinessRulesValidator',
    'BusinessRule',
    'RuleViolation', 
    'ValidationResult',
    'RuleType',
    'RuleSeverity',
    'RuleStatus',
    'business_rules_validator',
    'validate_business_rules',
    'validate_creator_rules',
    'validate_content_rules',
    'validate_monetization_rules'
]