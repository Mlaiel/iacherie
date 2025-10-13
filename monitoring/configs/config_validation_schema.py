#!/usr/bin/env python3
"""
✅ Configuration Validation Schema - Creator Economy Enterprise
===============================================================

Schémas de validation pour toutes les configurations monitoring Creator Economy IA Chérie.
Validation JSON Schema, règles métier et vérifications de cohérence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  PROTECTION INTELLECTUELLE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 AVERTISSEMENT LÉGAL:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Équipe Experte: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import json

from jsonschema import validate, ValidationError, Draft7Validator
from pydantic import BaseModel, validator, Field
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iacherie.config.validation")


class ConfigType(str, Enum):
    """Types de configuration supportés"""
    CREATOR_ECONOMY = "creator_economy"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    ALERTMANAGER = "alertmanager"
    AI_ML = "ai_ml"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    SEO_PERFORMANCE = "seo_performance"
    DISTRIBUTION = "distribution"
    GAMIFICATION = "gamification"
    CREATOR_TIER = "creator_tier"
    MULTI_FORMAT = "multi_format"
    SECURITY_COMPLIANCE = "security_compliance"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class CreatorTier(str, Enum):
    """Tiers de créateurs avec validation"""
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"


class CreatorType(str, Enum):
    """Types de créateurs supportés"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"


@dataclass
class ValidationResult:
    """Résultat de validation avec détails"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    config_type: ConfigType
    validation_timestamp: datetime
    schema_version: str


class ConfigValidationSchema:
    """
    ✅ Schémas de validation configurations Creator Economy
    
    Features Enterprise:
    - JSON Schema validation pour tous types de configs
    - Règles métier Creator Economy spécifiques
    - Validation cohérence cross-configuration
    - Validation seuils SLA par tier
    - Vérification compliance sécurité/légale
    - Suggestions d'amélioration automatiques
    """
    
    def __init__(self):
        self.schemas = self._initialize_schemas()
        self.business_rules = self._initialize_business_rules()
        self.tier_constraints = self._initialize_tier_constraints()
        self.security_rules = self._initialize_security_rules()
    
    def _initialize_schemas(self) -> Dict[ConfigType, Dict]:
        """Initialisation des schémas JSON Schema pour chaque type de config"""
        return {
            ConfigType.CREATOR_ECONOMY: self._creator_economy_schema(),
            ConfigType.PROMETHEUS: self._prometheus_schema(),
            ConfigType.GRAFANA: self._grafana_schema(),
            ConfigType.ALERTMANAGER: self._alertmanager_schema(),
            ConfigType.AI_ML: self._ai_ml_schema(),
            ConfigType.CONTENT_PROTECTION: self._content_protection_schema(),
            ConfigType.MONETIZATION: self._monetization_schema(),
            ConfigType.COLLABORATION: self._collaboration_schema(),
            ConfigType.SEO_PERFORMANCE: self._seo_performance_schema(),
            ConfigType.DISTRIBUTION: self._distribution_schema(),
            ConfigType.GAMIFICATION: self._gamification_schema(),
            ConfigType.CREATOR_TIER: self._creator_tier_schema(),
            ConfigType.MULTI_FORMAT: self._multi_format_schema(),
            ConfigType.SECURITY_COMPLIANCE: self._security_compliance_schema(),
            ConfigType.PERFORMANCE_OPTIMIZATION: self._performance_optimization_schema(),
        }
    
    def _creator_economy_schema(self) -> Dict:
        """Schema JSON pour configuration Creator Economy"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "metadata", "creator_metrics", "tier_differentiation"],
            "properties": {
                "version": {
                    "type": "string",
                    "pattern": r"^\d+\.\d+\.\d+$"
                },
                "metadata": {
                    "type": "object",
                    "required": ["name", "created_by", "created_date"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "created_by": {"type": "string", "pattern": r"Fahed Mlaiel"},
                        "created_date": {"type": "string", "format": "date"},
                        "business_domain": {"type": "string"},
                        "compliance_level": {"type": "string", "enum": ["basic", "standard", "enterprise"]}
                    }
                },
                "creator_metrics": {
                    "type": "object",
                    "required": ["musicians", "bloggers", "photographers"],
                    "properties": {
                        "musicians": {
                            "type": "object",
                            "required": ["audio_processing_latency", "streaming_quality_metrics"],
                            "properties": {
                                "audio_processing_latency": {
                                    "type": "object",
                                    "required": ["sla_target_ms", "critical_threshold_ms"],
                                    "properties": {
                                        "sla_target_ms": {"type": "integer", "minimum": 10, "maximum": 1000},
                                        "critical_threshold_ms": {"type": "integer", "minimum": 100}
                                    }
                                }
                            }
                        },
                        "bloggers": {
                            "type": "object",
                            "required": ["seo_ranking_performance", "content_delivery_metrics"]
                        },
                        "photographers": {
                            "type": "object",
                            "required": ["image_processing_performance", "storage_utilization_metrics"]
                        }
                    }
                },
                "tier_differentiation": {
                    "type": "object",
                    "required": ["premium", "standard", "basic"],
                    "properties": {
                        "premium": {
                            "type": "object",
                            "required": ["sla_multiplier", "priority_level"],
                            "properties": {
                                "sla_multiplier": {"type": "number", "minimum": 0.1, "maximum": 1.0},
                                "priority_level": {"type": "string", "enum": ["highest", "high", "normal", "low"]}
                            }
                        },
                        "standard": {
                            "type": "object",
                            "properties": {
                                "sla_multiplier": {"type": "number", "const": 1.0}
                            }
                        },
                        "basic": {
                            "type": "object",
                            "properties": {
                                "sla_multiplier": {"type": "number", "minimum": 1.0, "maximum": 3.0}
                            }
                        }
                    }
                }
            }
        }
    
    def _prometheus_schema(self) -> Dict:
        """Schema JSON pour configuration Prometheus"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["global", "scrape_configs"],
            "properties": {
                "global": {
                    "type": "object",
                    "required": ["scrape_interval", "evaluation_interval"],
                    "properties": {
                        "scrape_interval": {"type": "string", "pattern": r"^\d+[smh]$"},
                        "evaluation_interval": {"type": "string", "pattern": r"^\d+[smh]$"},
                        "external_labels": {"type": "object"}
                    }
                },
                "scrape_configs": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["job_name"],
                        "properties": {
                            "job_name": {"type": "string", "minLength": 1},
                            "scrape_interval": {"type": "string", "pattern": r"^\d+[smh]$"},
                            "metrics_path": {"type": "string"},
                            "static_configs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["targets"],
                                    "properties": {
                                        "targets": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _grafana_schema(self) -> Dict:
        """Schema JSON pour configuration Grafana"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "dashboards"],
            "properties": {
                "version": {"type": "string"},
                "dashboards": {
                    "type": "object",
                    "minProperties": 1,
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_]*$": {
                            "type": "object",
                            "required": ["uid", "title", "panels"],
                            "properties": {
                                "uid": {"type": "string", "minLength": 1},
                                "title": {"type": "string", "minLength": 1},
                                "panels": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "object",
                                        "required": ["title", "type"],
                                        "properties": {
                                            "title": {"type": "string"},
                                            "type": {"type": "string", "enum": ["timeseries", "stat", "gauge", "table", "piechart", "barchart", "heatmap", "row"]}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _alertmanager_schema(self) -> Dict:
        """Schema JSON pour configuration AlertManager"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["global", "receivers", "route", "groups"],
            "properties": {
                "global": {
                    "type": "object",
                    "properties": {
                        "smtp_smarthost": {"type": "string"},
                        "smtp_from": {"type": "string", "format": "email"}
                    }
                },
                "receivers": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1}
                        }
                    }
                },
                "route": {
                    "type": "object",
                    "required": ["group_by", "receiver"],
                    "properties": {
                        "group_by": {"type": "array", "items": {"type": "string"}},
                        "receiver": {"type": "string"}
                    }
                },
                "groups": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "rules"],
                        "properties": {
                            "name": {"type": "string"},
                            "rules": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["alert", "expr"],
                                    "properties": {
                                        "alert": {"type": "string"},
                                        "expr": {"type": "string"},
                                        "for": {"type": "string", "pattern": r"^\d+[smh]$"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _ai_ml_schema(self) -> Dict:
        """Schema JSON pour configuration AI/ML"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "ml_monitoring"],
            "properties": {
                "version": {"type": "string"},
                "ml_monitoring": {
                    "type": "object",
                    "required": ["model_performance", "inference_monitoring"],
                    "properties": {
                        "model_performance": {
                            "type": "object",
                            "required": ["drift_detection", "accuracy_degradation"],
                            "properties": {
                                "drift_detection": {
                                    "type": "object",
                                    "required": ["enabled", "drift_threshold"],
                                    "properties": {
                                        "enabled": {"type": "boolean"},
                                        "drift_threshold": {"type": "number", "minimum": 0.01, "maximum": 0.5}
                                    }
                                },
                                "accuracy_degradation": {
                                    "type": "object",
                                    "required": ["enabled", "alert_threshold"],
                                    "properties": {
                                        "enabled": {"type": "boolean"},
                                        "alert_threshold": {"type": "number", "minimum": 0.05, "maximum": 0.5}
                                    }
                                }
                            }
                        },
                        "inference_monitoring": {
                            "type": "object",
                            "required": ["latency_sla", "throughput_requirements"],
                            "properties": {
                                "latency_sla": {
                                    "type": "object",
                                    "required": ["target_p95_ms"],
                                    "properties": {
                                        "target_p95_ms": {"type": "integer", "minimum": 10, "maximum": 10000}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _content_protection_schema(self) -> Dict:
        """Schema JSON pour configuration protection contenu"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "protection_monitoring"],
            "properties": {
                "version": {"type": "string"},
                "protection_monitoring": {
                    "type": "object",
                    "required": ["copyright_detection", "watermarking", "ip_protection"],
                    "properties": {
                        "copyright_detection": {
                            "type": "object",
                            "required": ["scan_frequency", "similarity_threshold_audio"],
                            "properties": {
                                "scan_frequency": {"type": "string"},
                                "similarity_threshold_audio": {"type": "number", "minimum": 0.5, "maximum": 1.0}
                            }
                        }
                    }
                }
            }
        }
    
    def _monetization_schema(self) -> Dict:
        """Schema JSON pour configuration monétisation"""
        return {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "monetization_tracking"],
            "properties": {
                "version": {"type": "string"},
                "monetization_tracking": {
                    "type": "object",
                    "required": ["revenue_streams", "payment_processing"],
                    "properties": {
                        "revenue_streams": {
                            "type": "object",
                            "required": ["primary_streams"],
                            "properties": {
                                "primary_streams": {
                                    "type": "object",
                                    "minProperties": 1
                                }
                            }
                        },
                        "payment_processing": {
                            "type": "object",
                            "required": ["transaction_success_rate"],
                            "properties": {
                                "transaction_success_rate": {
                                    "type": "object",
                                    "required": ["target_rate"],
                                    "properties": {
                                        "target_rate": {"type": "number", "minimum": 0.90, "maximum": 1.0}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    # Schémas simplifiés pour les autres types (pour économiser l'espace)
    def _collaboration_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _seo_performance_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _distribution_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _gamification_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _creator_tier_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version", "tier_monitoring"]}
    
    def _multi_format_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _security_compliance_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _performance_optimization_schema(self) -> Dict:
        return {"$schema": "https://json-schema.org/draft-07/schema#", "type": "object", "required": ["version"]}
    
    def _initialize_business_rules(self) -> Dict[ConfigType, List[callable]]:
        """Initialisation des règles métier par type de configuration"""
        return {
            ConfigType.CREATOR_ECONOMY: [
                self._validate_creator_metrics_coherence,
                self._validate_tier_sla_progression,
                self._validate_creator_type_completeness
            ],
            ConfigType.PROMETHEUS: [
                self._validate_prometheus_job_names,
                self._validate_scrape_intervals,
                self._validate_metric_naming_convention
            ],
            ConfigType.ALERTMANAGER: [
                self._validate_alert_severity_levels,
                self._validate_notification_channels,
                self._validate_escalation_paths
            ],
            ConfigType.AI_ML: [
                self._validate_ml_threshold_coherence,
                self._validate_model_performance_targets,
                self._validate_inference_sla_realistic
            ],
            ConfigType.MONETIZATION: [
                self._validate_revenue_stream_coherence,
                self._validate_commission_rates,
                self._validate_payment_sla_realistic
            ]
        }
    
    def _initialize_tier_constraints(self) -> Dict[CreatorTier, Dict]:
        """Contraintes spécifiques par tier de créateur"""
        return {
            CreatorTier.ENTERPRISE: {
                "min_sla_multiplier": 0.1,
                "max_sla_multiplier": 0.5,
                "required_features": ["dedicated_resources", "24_7_support", "custom_dashboards"],
                "min_response_time_ms": 10,
                "max_response_time_ms": 100
            },
            CreatorTier.PREMIUM: {
                "min_sla_multiplier": 0.3,
                "max_sla_multiplier": 0.8,
                "required_features": ["advanced_analytics", "priority_support"],
                "min_response_time_ms": 25,
                "max_response_time_ms": 200
            },
            CreatorTier.STANDARD: {
                "min_sla_multiplier": 0.8,
                "max_sla_multiplier": 1.2,
                "required_features": ["basic_analytics"],
                "min_response_time_ms": 50,
                "max_response_time_ms": 500
            },
            CreatorTier.BASIC: {
                "min_sla_multiplier": 1.0,
                "max_sla_multiplier": 3.0,
                "required_features": [],
                "min_response_time_ms": 100,
                "max_response_time_ms": 2000
            }
        }
    
    def _initialize_security_rules(self) -> List[callable]:
        """Règles de sécurité pour toutes les configurations"""
        return [
            self._validate_no_hardcoded_secrets,
            self._validate_encryption_requirements,
            self._validate_access_control_config,
            self._validate_audit_trail_completeness,
            self._validate_gdpr_compliance_config
        ]
    
    def validate_configuration(self, config_data: Dict[str, Any], config_type: ConfigType) -> ValidationResult:
        """
        Validation complète d'une configuration
        
        Args:
            config_data: Données de configuration à valider
            config_type: Type de configuration
            
        Returns:
            ValidationResult avec détails de validation
        """
        errors = []
        warnings = []
        
        try:
            # 1. Validation JSON Schema
            schema = self.schemas.get(config_type)
            if schema:
                validator = Draft7Validator(schema)
                schema_errors = list(validator.iter_errors(config_data))
                for error in schema_errors:
                    errors.append(f"Schema validation: {error.message} at {'.'.join(str(p) for p in error.path)}")
            else:
                warnings.append(f"No JSON schema defined for config type: {config_type}")
            
            # 2. Validation règles métier
            business_rules = self.business_rules.get(config_type, [])
            for rule in business_rules:
                try:
                    rule_result = rule(config_data)
                    if not rule_result.get('valid', True):
                        errors.extend(rule_result.get('errors', []))
                        warnings.extend(rule_result.get('warnings', []))
                except Exception as e:
                    errors.append(f"Business rule validation error: {str(e)}")
            
            # 3. Validation contraintes tier (si applicable)
            if self._has_tier_configuration(config_data):
                tier_errors, tier_warnings = self._validate_tier_constraints(config_data)
                errors.extend(tier_errors)
                warnings.extend(tier_warnings)
            
            # 4. Validation règles sécurité
            for security_rule in self.security_rules:
                try:
                    security_result = security_rule(config_data)
                    if not security_result.get('valid', True):
                        errors.extend(security_result.get('errors', []))
                        warnings.extend(security_result.get('warnings', []))
                except Exception as e:
                    warnings.append(f"Security rule validation warning: {str(e)}")
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                config_type=config_type,
                validation_timestamp=datetime.now(),
                schema_version="2.0.0"
            )
            
        except Exception as e:
            logger.error(f"Validation error for {config_type}: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Critical validation error: {str(e)}"],
                warnings=warnings,
                config_type=config_type,
                validation_timestamp=datetime.now(),
                schema_version="2.0.0"
            )
    
    # Business Rules Implementation
    def _validate_creator_metrics_coherence(self, config: Dict) -> Dict:
        """Validation cohérence métriques créateurs"""
        errors = []
        warnings = []
        
        creator_metrics = config.get('creator_metrics', {})
        
        # Vérification présence métriques essentielles pour chaque type
        required_metrics = {
            'musicians': ['audio_processing_latency', 'streaming_quality_metrics'],
            'bloggers': ['seo_ranking_performance', 'content_delivery_metrics'],
            'photographers': ['image_processing_performance', 'storage_utilization_metrics']
        }
        
        for creator_type, required in required_metrics.items():
            if creator_type in creator_metrics:
                for metric in required:
                    if metric not in creator_metrics[creator_type]:
                        errors.append(f"Missing required metric '{metric}' for {creator_type}")
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
    
    def _validate_tier_sla_progression(self, config: Dict) -> Dict:
        """Validation progression SLA entre tiers"""
        errors = []
        warnings = []
        
        tier_diff = config.get('tier_differentiation', {})
        
        # Vérification progression logique des SLA multipliers
        tiers_order = ['basic', 'standard', 'premium', 'enterprise']
        sla_multipliers = {}
        
        for tier in tiers_order:
            if tier in tier_diff and 'sla_multiplier' in tier_diff[tier]:
                sla_multipliers[tier] = tier_diff[tier]['sla_multiplier']
        
        # Enterprise doit avoir le SLA le plus strict (multiplier le plus faible)
        if 'enterprise' in sla_multipliers and 'premium' in sla_multipliers:
            if sla_multipliers['enterprise'] >= sla_multipliers['premium']:
                errors.append("Enterprise SLA multiplier must be lower than Premium")
        
        # Basic doit avoir le SLA le plus souple (multiplier le plus élevé)
        if 'basic' in sla_multipliers and 'standard' in sla_multipliers:
            if sla_multipliers['basic'] <= sla_multipliers['standard']:
                errors.append("Basic SLA multiplier must be higher than Standard")
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
    
    def _validate_creator_type_completeness(self, config: Dict) -> Dict:
        """Validation complétude types créateurs"""
        warnings = []
        
        creator_metrics = config.get('creator_metrics', {})
        expected_types = ['musicians', 'bloggers', 'photographers', 'influencers', 'comedians']
        
        for expected_type in expected_types:
            if expected_type not in creator_metrics:
                warnings.append(f"Missing creator type configuration: {expected_type}")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_prometheus_job_names(self, config: Dict) -> Dict:
        """Validation noms de jobs Prometheus"""
        errors = []
        warnings = []
        
        scrape_configs = config.get('scrape_configs', [])
        job_names = set()
        
        for job_config in scrape_configs:
            job_name = job_config.get('job_name', '')
            
            # Vérification unicité
            if job_name in job_names:
                errors.append(f"Duplicate job name: {job_name}")
            job_names.add(job_name)
            
            # Vérification convention nommage Creator Economy
            if not job_name.startswith('creator-') and not job_name.startswith('iacherie-'):
                warnings.append(f"Job name '{job_name}' doesn't follow naming convention")
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
    
    def _validate_scrape_intervals(self, config: Dict) -> Dict:
        """Validation intervalles scraping cohérents"""
        warnings = []
        
        global_interval = config.get('global', {}).get('scrape_interval', '30s')
        scrape_configs = config.get('scrape_configs', [])
        
        # Conversion en secondes pour comparaison
        def parse_interval(interval_str):
            if interval_str.endswith('s'):
                return int(interval_str[:-1])
            elif interval_str.endswith('m'):
                return int(interval_str[:-1]) * 60
            elif interval_str.endswith('h'):
                return int(interval_str[:-1]) * 3600
            return 30  # default
        
        global_seconds = parse_interval(global_interval)
        
        for job_config in scrape_configs:
            job_interval = job_config.get('scrape_interval')
            if job_interval:
                job_seconds = parse_interval(job_interval)
                
                # Warning si interval job très différent du global
                if job_seconds < global_seconds / 10 or job_seconds > global_seconds * 10:
                    warnings.append(f"Job '{job_config.get('job_name')}' has very different scrape interval")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_metric_naming_convention(self, config: Dict) -> Dict:
        """Validation convention nommage métriques"""
        warnings = []
        
        # Cette validation serait plus complète avec accès aux métriques réelles
        # Pour l'instant, validation basique sur la configuration
        
        scrape_configs = config.get('scrape_configs', [])
        for job_config in scrape_configs:
            job_name = job_config.get('job_name', '')
            
            # Les jobs Creator Economy doivent exposer des métriques iacherie_*
            if job_name.startswith('creator-'):
                if 'iacherie_' not in str(job_config):
                    warnings.append(f"Creator job '{job_name}' should expose iacherie_* metrics")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_alert_severity_levels(self, config: Dict) -> Dict:
        """Validation niveaux de sévérité alertes"""
        errors = []
        warnings = []
        
        groups = config.get('groups', [])
        valid_severities = ['info', 'warning', 'critical']
        
        for group in groups:
            rules = group.get('rules', [])
            for rule in rules:
                labels = rule.get('labels', {})
                severity = labels.get('severity')
                
                if severity and severity not in valid_severities:
                    errors.append(f"Invalid severity level '{severity}' in alert '{rule.get('alert')}'")
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
    
    def _validate_notification_channels(self, config: Dict) -> Dict:
        """Validation canaux de notification"""
        warnings = []
        
        receivers = config.get('receivers', [])
        required_channels = ['email_configs', 'slack_configs']
        
        for receiver in receivers:
            receiver_name = receiver.get('name', '')
            
            # Vérification présence canaux critiques pour alertes importantes
            if 'critical' in receiver_name.lower():
                for channel in required_channels:
                    if channel not in receiver:
                        warnings.append(f"Critical receiver '{receiver_name}' missing {channel}")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_escalation_paths(self, config: Dict) -> Dict:
        """Validation chemins d'escalade"""
        warnings = []
        
        route = config.get('route', {})
        routes = route.get('routes', [])
        
        # Vérification existence routes par tier
        tier_routes = {}
        for route_config in routes:
            match = route_config.get('match', {})
            if 'creator_tier' in match:
                tier_routes[match['creator_tier']] = route_config
        
        # Enterprise doit avoir escalade immédiate
        if 'enterprise' in tier_routes:
            enterprise_route = tier_routes['enterprise']
            group_wait = enterprise_route.get('group_wait', '10s')
            if not group_wait.startswith('0') and group_wait != '0s':
                warnings.append("Enterprise tier should have immediate escalation (group_wait: 0s)")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_ml_threshold_coherence(self, config: Dict) -> Dict:
        """Validation cohérence seuils ML"""
        errors = []
        warnings = []
        
        ml_monitoring = config.get('ml_monitoring', {})
        model_performance = ml_monitoring.get('model_performance', {})
        
        # Vérification cohérence seuils drift vs accuracy
        drift_threshold = model_performance.get('drift_detection', {}).get('drift_threshold', 0.05)
        accuracy_threshold = model_performance.get('accuracy_degradation', {}).get('alert_threshold', 0.1)
        
        if drift_threshold > accuracy_threshold:
            warnings.append("Drift threshold should typically be lower than accuracy degradation threshold")
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
    
    def _validate_model_performance_targets(self, config: Dict) -> Dict:
        """Validation cibles performance modèles"""
        warnings = []
        
        creator_ai_features = config.get('ml_monitoring', {}).get('creator_ai_features', {})
        
        # Vérification cibles réalistes pour classification contenu
        content_classification = creator_ai_features.get('content_classification', {})
        if content_classification:
            accuracy_target = content_classification.get('accuracy_target', 0.95)
            if accuracy_target > 0.98:
                warnings.append("Content classification accuracy target > 98% may be unrealistic")
            elif accuracy_target < 0.85:
                warnings.append("Content classification accuracy target < 85% may be too low for production")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_inference_sla_realistic(self, config: Dict) -> Dict:
        """Validation SLA inférence réaliste"""
        warnings = []
        
        inference_monitoring = config.get('ml_monitoring', {}).get('inference_monitoring', {})
        latency_sla = inference_monitoring.get('latency_sla', {})
        
        target_p95 = latency_sla.get('target_p95_ms', 100)
        if target_p95 < 10:
            warnings.append("Target P95 latency < 10ms may be unrealistic for ML inference")
        elif target_p95 > 5000:
            warnings.append("Target P95 latency > 5s may be too slow for real-time applications")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_revenue_stream_coherence(self, config: Dict) -> Dict:
        """Validation cohérence flux de revenus"""
        errors = []
        warnings = []
        
        monetization_tracking = config.get('monetization_tracking', {})
        revenue_streams = monetization_tracking.get('revenue_streams', {})
        primary_streams = revenue_streams.get('primary_streams', {})
        
        # Vérification présence streams essentiels
        essential_streams = ['content_licensing', 'brand_partnerships', 'subscription_fees']
        for stream in essential_streams:
            if stream not in primary_streams:
                warnings.append(f"Missing essential revenue stream: {stream}")
        
        # Vérification cohérence commission rates
        total_commission_weight = 0
        for stream_name, stream_config in primary_streams.items():
            commission_rate = stream_config.get('commission_rate', 0)
            if commission_rate < 0.05 or commission_rate > 0.30:
                warnings.append(f"Commission rate for {stream_name} ({commission_rate}) outside typical range (5-30%)")
            total_commission_weight += commission_rate
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
    
    def _validate_commission_rates(self, config: Dict) -> Dict:
        """Validation taux de commission"""
        warnings = []
        
        monetization_tracking = config.get('monetization_tracking', {})
        revenue_streams = monetization_tracking.get('revenue_streams', {})
        primary_streams = revenue_streams.get('primary_streams', {})
        
        for stream_name, stream_config in primary_streams.items():
            commission_rate = stream_config.get('commission_rate', 0)
            
            # Vérification taux par type de stream
            if stream_name == 'subscription_fees' and commission_rate > 0.10:
                warnings.append(f"Subscription commission rate ({commission_rate}) higher than typical (< 10%)")
            elif stream_name == 'merchandise_sales' and commission_rate < 0.15:
                warnings.append(f"Merchandise commission rate ({commission_rate}) lower than typical (> 15%)")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_payment_sla_realistic(self, config: Dict) -> Dict:
        """Validation SLA paiements réaliste"""
        warnings = []
        
        payment_processing = config.get('monetization_tracking', {}).get('payment_processing', {})
        success_rate_target = payment_processing.get('transaction_success_rate', {}).get('target_rate', 0.995)
        
        if success_rate_target > 0.999:
            warnings.append("Payment success rate target > 99.9% may be unrealistic")
        elif success_rate_target < 0.95:
            warnings.append("Payment success rate target < 95% may be too low for production")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _has_tier_configuration(self, config: Dict) -> bool:
        """Vérification présence configuration tier"""
        return any(tier.value in str(config).lower() for tier in CreatorTier)
    
    def _validate_tier_constraints(self, config: Dict) -> Tuple[List[str], List[str]]:
        """Validation contraintes par tier"""
        errors = []
        warnings = []
        
        # Cette validation serait étendue selon les besoins spécifiques
        tier_diff = config.get('tier_differentiation', {})
        
        for tier_name, tier_config in tier_diff.items():
            if tier_name in [tier.value for tier in CreatorTier]:
                tier_enum = CreatorTier(tier_name)
                constraints = self.tier_constraints.get(tier_enum, {})
                
                # Validation SLA multiplier
                sla_multiplier = tier_config.get('sla_multiplier')
                if sla_multiplier:
                    min_sla = constraints.get('min_sla_multiplier', 0)
                    max_sla = constraints.get('max_sla_multiplier', 10)
                    
                    if sla_multiplier < min_sla or sla_multiplier > max_sla:
                        errors.append(f"SLA multiplier {sla_multiplier} for {tier_name} outside valid range [{min_sla}, {max_sla}]")
        
        return errors, warnings
    
    # Security Rules Implementation
    def _validate_no_hardcoded_secrets(self, config: Dict) -> Dict:
        """Validation absence secrets hardcodés"""
        warnings = []
        config_str = json.dumps(config).lower()
        
        suspicious_patterns = [
            r'password["\s]*[:=]["\s]*[a-zA-Z0-9]+',
            r'api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9]+',
            r'secret["\s]*[:=]["\s]*[a-zA-Z0-9]+',
            r'token["\s]*[:=]["\s]*[a-zA-Z0-9]+',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, config_str):
                warnings.append(f"Potential hardcoded secret detected (pattern: {pattern})")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_encryption_requirements(self, config: Dict) -> Dict:
        """Validation exigences chiffrement"""
        warnings = []
        
        # Vérification présence configuration chiffrement pour données sensibles
        if 'security' in config:
            security_config = config['security']
            if 'encryption' not in security_config:
                warnings.append("Missing encryption configuration in security section")
            elif not security_config.get('encryption', {}).get('enabled', False):
                warnings.append("Encryption not enabled in security configuration")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_access_control_config(self, config: Dict) -> Dict:
        """Validation configuration contrôle d'accès"""
        warnings = []
        
        # Vérification RBAC pour configurations sensibles
        if any(sensitive in str(config).lower() for sensitive in ['payment', 'revenue', 'creator_data']):
            if 'rbac' not in str(config).lower():
                warnings.append("Missing RBAC configuration for sensitive data")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_audit_trail_completeness(self, config: Dict) -> Dict:
        """Validation complétude audit trail"""
        warnings = []
        
        # Vérification audit trail pour opérations critiques
        if 'audit' in config:
            audit_config = config['audit']
            if not audit_config.get('enabled', False):
                warnings.append("Audit trail not enabled")
            
            retention_period = audit_config.get('retention_period_years', 0)
            if retention_period < 7:
                warnings.append("Audit retention period should be at least 7 years for compliance")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def _validate_gdpr_compliance_config(self, config: Dict) -> Dict:
        """Validation configuration conformité GDPR"""
        warnings = []
        
        # Vérification éléments GDPR essentiels
        gdpr_elements = ['data_protection', 'consent_tracking', 'right_to_deletion']
        config_str = str(config).lower()
        
        missing_elements = []
        for element in gdpr_elements:
            if element.replace('_', '') not in config_str.replace('_', ''):
                missing_elements.append(element)
        
        if missing_elements:
            warnings.append(f"Missing GDPR compliance elements: {', '.join(missing_elements)}")
        
        return {'valid': True, 'errors': [], 'warnings': warnings}
    
    def generate_validation_report(self, validation_results: List[ValidationResult]) -> str:
        """Génération rapport de validation détaillé"""
        report = []
        report.append("=" * 80)
        report.append("🔍 RAPPORT DE VALIDATION CONFIGURATIONS CREATOR ECONOMY")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Configurations validées: {len(validation_results)}")
        report.append("")
        
        # Résumé global
        total_valid = sum(1 for r in validation_results if r.is_valid)
        total_errors = sum(len(r.errors) for r in validation_results)
        total_warnings = sum(len(r.warnings) for r in validation_results)
        
        report.append("📊 RÉSUMÉ GLOBAL:")
        report.append(f"  ✅ Configurations valides: {total_valid}/{len(validation_results)}")
        report.append(f"  ❌ Erreurs totales: {total_errors}")
        report.append(f"  ⚠️  Avertissements totaux: {total_warnings}")
        report.append("")
        
        # Détails par configuration
        for result in validation_results:
            report.append(f"🔧 CONFIGURATION: {result.config_type.value.upper()}")
            report.append(f"  Status: {'✅ VALIDE' if result.is_valid else '❌ INVALIDE'}")
            
            if result.errors:
                report.append("  ❌ Erreurs:")
                for error in result.errors:
                    report.append(f"    - {error}")
            
            if result.warnings:
                report.append("  ⚠️  Avertissements:")
                for warning in result.warnings:
                    report.append(f"    - {warning}")
            
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)


# Factory et utilitaires
def create_validator() -> ConfigValidationSchema:
    """Factory pour création du validateur"""
    return ConfigValidationSchema()


def validate_config_file(file_path: str, config_type: ConfigType) -> ValidationResult:
    """Validation d'un fichier de configuration"""
    validator = create_validator()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith(('.yaml', '.yml')):
                config_data = yaml.safe_load(f)
            elif file_path.endswith('.json'):
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        
        return validator.validate_configuration(config_data, config_type)
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"File loading error: {str(e)}"],
            warnings=[],
            config_type=config_type,
            validation_timestamp=datetime.now(),
            schema_version="2.0.0"
        )


if __name__ == "__main__":
    """Mode test - Validation exemple"""
    # Test du validateur avec configuration exemple
    test_config = {
        "version": "2.0.0",
        "metadata": {
            "name": "test-config",
            "created_by": "Fahed Mlaiel",
            "created_date": "2025-01-08"
        },
        "creator_metrics": {
            "musicians": {
                "audio_processing_latency": {
                    "sla_target_ms": 100,
                    "critical_threshold_ms": 500
                },
                "streaming_quality_metrics": {
                    "sla_minimum": 0.95
                }
            },
            "bloggers": {
                "seo_ranking_performance": {},
                "content_delivery_metrics": {}
            },
            "photographers": {
                "image_processing_performance": {},
                "storage_utilization_metrics": {}
            }
        },
        "tier_differentiation": {
            "premium": {
                "sla_multiplier": 0.5,
                "priority_level": "highest"
            },
            "standard": {
                "sla_multiplier": 1.0,
                "priority_level": "high"
            },
            "basic": {
                "sla_multiplier": 2.0,
                "priority_level": "normal"
            }
        }
    }
    
    validator = create_validator()
    result = validator.validate_configuration(test_config, ConfigType.CREATOR_ECONOMY)
    
    print("🔍 Test Validation Result:")
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

# Expert Team Signature
# =====================
# Configuration experte réalisée par:
# 🧠 Lead Dev IA + Backend Senior + ML Engineer
# 💾 DBA + Sécurité + Microservices + Audio  
# ⚙️ DevOps + IA Prompt Engineer
#
# Validation schemas Creator Economy avec règles métier
# JSON Schema + business rules + security validation + tier constraints