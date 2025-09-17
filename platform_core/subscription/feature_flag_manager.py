"""🚀 Platform Core Subscription - Feature Flag Manager
======================================================
Module: backend/platform_core/subscription/feature_flag_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 GESTIONNAIRE FEATURE FLAGS DYNAMIQUES
Gestion avancée des fonctionnalités par abonnement
- Feature flags dynamiques par plan subscription
- A/B testing automatique des nouvelles fonctionnalités
- Rollout progressif et canary deployments
- Analytics et métriques d'adoption des features
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
import logging
import asyncio
import json
import hashlib
from decimal import Decimal
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class FeatureStatus(Enum):
    """Statuts des feature flags"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    TESTING = "testing"
    ROLLOUT = "rollout"
    DEPRECATED = "deprecated"


class RolloutStrategy(Enum):
    """Stratégies de déploiement"""
    INSTANT = "instant"
    GRADUAL = "gradual"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    A_B_TEST = "a_b_test"


class TargetingType(Enum):
    """Types de ciblage"""
    ALL_USERS = "all_users"
    SUBSCRIPTION_TIER = "subscription_tier"
    CREATOR_TYPE = "creator_type"
    USAGE_LEVEL = "usage_level"
    GEOGRAPHIC = "geographic"
    COHORT = "cohort"
    CUSTOM = "custom"


@dataclass
class FeatureFlag:
    """Feature flag avec configuration avancée"""
    flag_id: str
    name: str
    description: str
    status: FeatureStatus
    rollout_strategy: RolloutStrategy
    rollout_percentage: float
    targeting_rules: List[Dict[str, Any]]
    subscription_tiers: List[str]
    creator_types: List[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureEvaluation:
    """Résultat d'évaluation d'un feature flag"""
    flag_id: str
    user_id: str
    enabled: bool
    reason: str
    evaluation_time: datetime
    experiment_group: Optional[str]
    targeting_matched: List[str]


@dataclass
class ABTestConfig:
    """Configuration A/B test"""
    test_id: str
    flag_id: str
    variant_a_percentage: float
    variant_b_percentage: float
    control_group_percentage: float
    success_metrics: List[str]
    min_sample_size: int
    max_duration_days: int
    confidence_level: float


class FeatureFlagManager:
    """🚀 Gestionnaire Feature Flags Dynamiques Enterprise
    
    Système avancé de gestion des fonctionnalités avec
    A/B testing, rollout progressif et analytics.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de feature flags"""
        self.feature_flags = {}
        self.user_assignments = {}
        self.evaluation_cache = {}
        self.ab_tests = {}
        self.metrics_data = {}
        
        # Configuration par défaut
        self.cache_ttl = 300  # 5 minutes
        self.default_rollout_percentage = 100.0
        
        # Initialisation des flags de base
        self._initialize_default_flags()
        
        logger.info("🚀 Feature Flag Manager initialized")
    
    def _initialize_default_flags(self):
        """Initialise les feature flags par défaut"""
        
        # Features Premium pour musiciens
        self.feature_flags['premium_audio_processing'] = FeatureFlag(
            flag_id='premium_audio_processing',
            name='Premium Audio Processing',
            description='Traitement audio avancé avec IA',
            status=FeatureStatus.ENABLED,
            rollout_strategy=RolloutStrategy.INSTANT,
            rollout_percentage=100.0,
            targeting_rules=[{
                'type': TargetingType.SUBSCRIPTION_TIER.value,
                'values': ['musician_professional', 'musician_star']
            }],
            subscription_tiers=['musician_professional', 'musician_star'],
            creator_types=['musician'],
            start_date=datetime.now(),
            end_date=None,
            created_by='system',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Features collaboration avancée
        self.feature_flags['advanced_collaboration'] = FeatureFlag(
            flag_id='advanced_collaboration',
            name='Advanced Collaboration Tools',
            description='Outils de collaboration temps réel',
            status=FeatureStatus.ROLLOUT,
            rollout_strategy=RolloutStrategy.GRADUAL,
            rollout_percentage=50.0,
            targeting_rules=[{
                'type': TargetingType.SUBSCRIPTION_TIER.value,
                'values': ['professional', 'enterprise', 'star']
            }],
            subscription_tiers=['professional', 'enterprise', 'star'],
            creator_types=['musician', 'blogger', 'photographer'],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            created_by='system',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Features analytics avancées
        self.feature_flags['advanced_analytics'] = FeatureFlag(
            flag_id='advanced_analytics',
            name='Advanced Analytics Dashboard',
            description='Analytics et insights avancés',
            status=FeatureStatus.TESTING,
            rollout_strategy=RolloutStrategy.A_B_TEST,
            rollout_percentage=25.0,
            targeting_rules=[{
                'type': TargetingType.USAGE_LEVEL.value,
                'values': ['high', 'medium']
            }],
            subscription_tiers=['pro', 'enterprise'],
            creator_types=['blogger', 'photographer'],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14),
            created_by='system',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    async def evaluate_feature_flag(
        self,
        flag_id: str,
        user_id: str,
        user_context: Dict[str, Any]
    ) -> FeatureEvaluation:
        """Évalue un feature flag pour un utilisateur"""
        try:
            # Vérification du cache
            cache_key = f"{flag_id}_{user_id}_{hash(str(user_context))}"
            if cache_key in self.evaluation_cache:
                cached_result, cache_time = self.evaluation_cache[cache_key]
                if (datetime.now() - cache_time).seconds < self.cache_ttl:
                    return cached_result
            
            # Récupération du flag
            flag = self.feature_flags.get(flag_id)
            if not flag:
                return FeatureEvaluation(
                    flag_id=flag_id,
                    user_id=user_id,
                    enabled=False,
                    reason="Flag not found",
                    evaluation_time=datetime.now(),
                    experiment_group=None,
                    targeting_matched=[]
                )
            
            # Évaluation des conditions
            evaluation_result = await self._evaluate_flag_conditions(flag, user_id, user_context)
            
            # Mise en cache
            self.evaluation_cache[cache_key] = (evaluation_result, datetime.now())
            
            # Logging pour analytics
            await self._log_flag_evaluation(evaluation_result, user_context)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"❌ Error evaluating feature flag {flag_id}: {e}")
            return FeatureEvaluation(
                flag_id=flag_id,
                user_id=user_id,
                enabled=False,
                reason=f"Evaluation error: {e}",
                evaluation_time=datetime.now(),
                experiment_group=None,
                targeting_matched=[]
            )
    
    async def _evaluate_flag_conditions(
        self,
        flag: FeatureFlag,
        user_id: str,
        user_context: Dict[str, Any]
    ) -> FeatureEvaluation:
        """Évalue les conditions d'un feature flag"""
        
        # Vérification du statut
        if flag.status == FeatureStatus.DISABLED:
            return FeatureEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                enabled=False,
                reason="Flag disabled",
                evaluation_time=datetime.now(),
                experiment_group=None,
                targeting_matched=[]
            )
        
        # Vérification des dates
        now = datetime.now()
        if flag.start_date and now < flag.start_date:
            return FeatureEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                enabled=False,
                reason="Flag not yet active",
                evaluation_time=datetime.now(),
                experiment_group=None,
                targeting_matched=[]
            )
        
        if flag.end_date and now > flag.end_date:
            return FeatureEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                enabled=False,
                reason="Flag expired",
                evaluation_time=datetime.now(),
                experiment_group=None,
                targeting_matched=[]
            )
        
        # Évaluation du ciblage
        targeting_matched = await self._evaluate_targeting_rules(flag, user_context)
        
        if not targeting_matched:
            return FeatureEvaluation(
                flag_id=flag.flag_id,
                user_id=user_id,
                enabled=False,
                reason="Targeting criteria not met",
                evaluation_time=datetime.now(),
                experiment_group=None,
                targeting_matched=[]
            )
        
        # Évaluation du rollout
        enabled, experiment_group = await self._evaluate_rollout_strategy(flag, user_id, user_context)
        
        return FeatureEvaluation(
            flag_id=flag.flag_id,
            user_id=user_id,
            enabled=enabled,
            reason="Evaluation successful" if enabled else "Rollout percentage not met",
            evaluation_time=datetime.now(),
            experiment_group=experiment_group,
            targeting_matched=targeting_matched
        )
    
    async def _evaluate_targeting_rules(
        self,
        flag: FeatureFlag,
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Évalue les règles de ciblage"""
        matched_rules = []
        
        try:
            for rule in flag.targeting_rules:
                rule_type = rule.get('type')
                rule_values = rule.get('values', [])
                
                if rule_type == TargetingType.SUBSCRIPTION_TIER.value:
                    user_tier = user_context.get('subscription_tier')
                    if user_tier in rule_values:
                        matched_rules.append(f"subscription_tier:{user_tier}")
                
                elif rule_type == TargetingType.CREATOR_TYPE.value:
                    user_creator_type = user_context.get('creator_type')
                    if user_creator_type in rule_values:
                        matched_rules.append(f"creator_type:{user_creator_type}")
                
                elif rule_type == TargetingType.USAGE_LEVEL.value:
                    user_usage_level = user_context.get('usage_level')
                    if user_usage_level in rule_values:
                        matched_rules.append(f"usage_level:{user_usage_level}")
                
                elif rule_type == TargetingType.GEOGRAPHIC.value:
                    user_country = user_context.get('country')
                    if user_country in rule_values:
                        matched_rules.append(f"geographic:{user_country}")
                
                elif rule_type == TargetingType.COHORT.value:
                    user_cohorts = user_context.get('cohorts', [])
                    for cohort in user_cohorts:
                        if cohort in rule_values:
                            matched_rules.append(f"cohort:{cohort}")
                
                elif rule_type == TargetingType.ALL_USERS.value:
                    matched_rules.append("all_users")
                
                elif rule_type == TargetingType.CUSTOM.value:
                    # Évaluation de règles personnalisées
                    custom_result = await self._evaluate_custom_rule(rule, user_context)
                    if custom_result:
                        matched_rules.append(f"custom:{rule.get('name', 'unnamed')}")
            
            return matched_rules
            
        except Exception as e:
            logger.error(f"❌ Error evaluating targeting rules: {e}")
            return []
    
    async def _evaluate_custom_rule(self, rule: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """Évalue une règle personnalisée"""
        try:
            # Exemple d'évaluation de règles complexes
            condition = rule.get('condition', {})
            
            if condition.get('type') == 'revenue_threshold':
                user_revenue = user_context.get('monthly_revenue', 0)
                threshold = condition.get('value', 0)
                return user_revenue >= threshold
            
            elif condition.get('type') == 'engagement_score':
                user_engagement = user_context.get('engagement_score', 0)
                min_score = condition.get('min_value', 0)
                return user_engagement >= min_score
            
            elif condition.get('type') == 'collaboration_count':
                user_collaborations = user_context.get('collaboration_count', 0)
                min_count = condition.get('min_value', 0)
                return user_collaborations >= min_count
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error evaluating custom rule: {e}")
            return False
    
    async def _evaluate_rollout_strategy(
        self,
        flag: FeatureFlag,
        user_id: str,
        user_context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Évalue la stratégie de rollout"""
        
        if flag.rollout_strategy == RolloutStrategy.INSTANT:
            return True, None
        
        elif flag.rollout_strategy == RolloutStrategy.GRADUAL:
            # Rollout basé sur hash de l'ID utilisateur
            user_hash = self._calculate_user_hash(user_id, flag.flag_id)
            return user_hash < flag.rollout_percentage, None
        
        elif flag.rollout_strategy == RolloutStrategy.CANARY:
            # Rollout canary pour utilisateurs spécifiques
            canary_users = flag.metadata.get('canary_users', [])
            if user_id in canary_users:
                return True, "canary"
            
            user_hash = self._calculate_user_hash(user_id, flag.flag_id)
            return user_hash < flag.rollout_percentage, "general" if user_hash < flag.rollout_percentage else None
        
        elif flag.rollout_strategy == RolloutStrategy.A_B_TEST:
            # Assignment A/B test
            return await self._assign_ab_test_group(flag, user_id, user_context)
        
        elif flag.rollout_strategy == RolloutStrategy.BLUE_GREEN:
            # Blue-green basé sur version ou autre critère
            deployment_version = flag.metadata.get('deployment_version', 'blue')
            user_version = user_context.get('deployment_version', 'blue')
            return deployment_version == user_version, deployment_version
        
        else:
            return True, None
    
    def _calculate_user_hash(self, user_id: str, flag_id: str) -> float:
        """Calcule un hash consistant pour un utilisateur et flag"""
        hash_input = f"{user_id}:{flag_id}".encode('utf-8')
        hash_value = hashlib.md5(hash_input).hexdigest()
        # Convertit en pourcentage (0-100)
        return (int(hash_value[:8], 16) % 10000) / 100.0
    
    async def _assign_ab_test_group(
        self,
        flag: FeatureFlag,
        user_id: str,
        user_context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Assigne un groupe A/B test"""
        try:
            # Recherche du test A/B associé
            ab_test = None
            for test in self.ab_tests.values():
                if test.flag_id == flag.flag_id:
                    ab_test = test
                    break
            
            if not ab_test:
                # Configuration A/B par défaut
                user_hash = self._calculate_user_hash(user_id, flag.flag_id)
                if user_hash < 50:
                    return True, "variant_a"
                else:
                    return False, "variant_b"
            
            # Assignment basé sur configuration A/B
            user_hash = self._calculate_user_hash(user_id, ab_test.test_id)
            
            if user_hash < ab_test.variant_a_percentage:
                return True, "variant_a"
            elif user_hash < ab_test.variant_a_percentage + ab_test.variant_b_percentage:
                return False, "variant_b"
            else:
                return False, "control"
                
        except Exception as e:
            logger.error(f"❌ Error in A/B test assignment: {e}")
            return False, "error"
    
    async def _log_flag_evaluation(self, evaluation: FeatureEvaluation, user_context: Dict[str, Any]):
        """Log l'évaluation pour analytics"""
        try:
            log_entry = {
                'timestamp': evaluation.evaluation_time.isoformat(),
                'flag_id': evaluation.flag_id,
                'user_id': evaluation.user_id,
                'enabled': evaluation.enabled,
                'reason': evaluation.reason,
                'experiment_group': evaluation.experiment_group,
                'targeting_matched': evaluation.targeting_matched,
                'user_context': user_context
            }
            
            # Stockage pour analytics (à remplacer par système de logging réel)
            if evaluation.flag_id not in self.metrics_data:
                self.metrics_data[evaluation.flag_id] = []
            
            self.metrics_data[evaluation.flag_id].append(log_entry)
            
            # Garde seulement les 1000 dernières évaluations par flag
            if len(self.metrics_data[evaluation.flag_id]) > 1000:
                self.metrics_data[evaluation.flag_id] = self.metrics_data[evaluation.flag_id][-1000:]
                
        except Exception as e:
            logger.error(f"❌ Error logging flag evaluation: {e}")
    
    async def create_feature_flag(self, flag_config: Dict[str, Any]) -> bool:
        """Crée un nouveau feature flag"""
        try:
            flag = FeatureFlag(
                flag_id=flag_config['flag_id'],
                name=flag_config['name'],
                description=flag_config['description'],
                status=FeatureStatus(flag_config.get('status', 'disabled')),
                rollout_strategy=RolloutStrategy(flag_config.get('rollout_strategy', 'instant')),
                rollout_percentage=flag_config.get('rollout_percentage', 100.0),
                targeting_rules=flag_config.get('targeting_rules', []),
                subscription_tiers=flag_config.get('subscription_tiers', []),
                creator_types=flag_config.get('creator_types', []),
                start_date=flag_config.get('start_date'),
                end_date=flag_config.get('end_date'),
                created_by=flag_config.get('created_by', 'system'),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=flag_config.get('metadata', {})
            )
            
            self.feature_flags[flag.flag_id] = flag
            
            logger.info(f"✅ Feature flag created: {flag.flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating feature flag: {e}")
            return False
    
    async def update_feature_flag(self, flag_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un feature flag"""
        try:
            if flag_id not in self.feature_flags:
                logger.warning(f"Feature flag not found: {flag_id}")
                return False
            
            flag = self.feature_flags[flag_id]
            
            # Mise à jour des attributs
            for key, value in updates.items():
                if hasattr(flag, key):
                    if key == 'status' and isinstance(value, str):
                        setattr(flag, key, FeatureStatus(value))
                    elif key == 'rollout_strategy' and isinstance(value, str):
                        setattr(flag, key, RolloutStrategy(value))
                    else:
                        setattr(flag, key, value)
            
            flag.updated_at = datetime.now()
            
            # Invalidation du cache
            self._invalidate_cache_for_flag(flag_id)
            
            logger.info(f"✅ Feature flag updated: {flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating feature flag {flag_id}: {e}")
            return False
    
    def _invalidate_cache_for_flag(self, flag_id: str):
        """Invalide le cache pour un flag spécifique"""
        keys_to_remove = [key for key in self.evaluation_cache.keys() if key.startswith(f"{flag_id}_")]
        for key in keys_to_remove:
            del self.evaluation_cache[key]
    
    async def create_ab_test(self, test_config: Dict[str, Any]) -> bool:
        """Crée un test A/B"""
        try:
            ab_test = ABTestConfig(
                test_id=test_config['test_id'],
                flag_id=test_config['flag_id'],
                variant_a_percentage=test_config.get('variant_a_percentage', 50.0),
                variant_b_percentage=test_config.get('variant_b_percentage', 50.0),
                control_group_percentage=test_config.get('control_group_percentage', 0.0),
                success_metrics=test_config.get('success_metrics', []),
                min_sample_size=test_config.get('min_sample_size', 1000),
                max_duration_days=test_config.get('max_duration_days', 30),
                confidence_level=test_config.get('confidence_level', 0.95)
            )
            
            self.ab_tests[ab_test.test_id] = ab_test
            
            # Mise à jour du flag associé
            if ab_test.flag_id in self.feature_flags:
                await self.update_feature_flag(ab_test.flag_id, {
                    'rollout_strategy': 'a_b_test',
                    'status': 'testing'
                })
            
            logger.info(f"✅ A/B test created: {ab_test.test_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating A/B test: {e}")
            return False
    
    async def get_flag_analytics(self, flag_id: str, days: int = 7) -> Dict[str, Any]:
        """Récupère les analytics d'un feature flag"""
        try:
            if flag_id not in self.metrics_data:
                return {
                    'flag_id': flag_id,
                    'total_evaluations': 0,
                    'enabled_percentage': 0,
                    'user_adoption': {},
                    'experiment_groups': {}
                }
            
            # Filtrage par période
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = [
                entry for entry in self.metrics_data[flag_id]
                if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
            ]
            
            if not recent_data:
                return {
                    'flag_id': flag_id,
                    'total_evaluations': 0,
                    'enabled_percentage': 0,
                    'user_adoption': {},
                    'experiment_groups': {}
                }
            
            # Calcul des métriques
            total_evaluations = len(recent_data)
            enabled_count = sum(1 for entry in recent_data if entry['enabled'])
            enabled_percentage = (enabled_count / total_evaluations) * 100 if total_evaluations > 0 else 0
            
            # Adoption par type d'utilisateur
            user_adoption = {}
            for entry in recent_data:
                creator_type = entry['user_context'].get('creator_type', 'unknown')
                if creator_type not in user_adoption:
                    user_adoption[creator_type] = {'total': 0, 'enabled': 0}
                user_adoption[creator_type]['total'] += 1
                if entry['enabled']:
                    user_adoption[creator_type]['enabled'] += 1
            
            # Calcul des pourcentages d'adoption
            for creator_type in user_adoption:
                total = user_adoption[creator_type]['total']
                enabled = user_adoption[creator_type]['enabled']
                user_adoption[creator_type]['percentage'] = (enabled / total) * 100 if total > 0 else 0
            
            # Groupes d'expérimentation
            experiment_groups = {}
            for entry in recent_data:
                group = entry.get('experiment_group')
                if group:
                    if group not in experiment_groups:
                        experiment_groups[group] = {'count': 0, 'enabled': 0}
                    experiment_groups[group]['count'] += 1
                    if entry['enabled']:
                        experiment_groups[group]['enabled'] += 1
            
            return {
                'flag_id': flag_id,
                'period_days': days,
                'total_evaluations': total_evaluations,
                'enabled_percentage': enabled_percentage,
                'unique_users': len(set(entry['user_id'] for entry in recent_data)),
                'user_adoption': user_adoption,
                'experiment_groups': experiment_groups,
                'daily_breakdown': self._calculate_daily_breakdown(recent_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting flag analytics for {flag_id}: {e}")
            return {}
    
    def _calculate_daily_breakdown(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule la répartition quotidienne des évaluations"""
        daily_data = {}
        
        for entry in data:
            date = datetime.fromisoformat(entry['timestamp']).date().isoformat()
            if date not in daily_data:
                daily_data[date] = {'total': 0, 'enabled': 0}
            
            daily_data[date]['total'] += 1
            if entry['enabled']:
                daily_data[date]['enabled'] += 1
        
        # Calcul des pourcentages
        for date in daily_data:
            total = daily_data[date]['total']
            enabled = daily_data[date]['enabled']
            daily_data[date]['percentage'] = (enabled / total) * 100 if total > 0 else 0
        
        return daily_data
    
    async def list_active_flags(self) -> List[Dict[str, Any]]:
        """Liste tous les feature flags actifs"""
        try:
            active_flags = []
            
            for flag in self.feature_flags.values():
                if flag.status != FeatureStatus.DISABLED:
                    flag_info = {
                        'flag_id': flag.flag_id,
                        'name': flag.name,
                        'status': flag.status.value,
                        'rollout_strategy': flag.rollout_strategy.value,
                        'rollout_percentage': flag.rollout_percentage,
                        'subscription_tiers': flag.subscription_tiers,
                        'creator_types': flag.creator_types,
                        'start_date': flag.start_date.isoformat() if flag.start_date else None,
                        'end_date': flag.end_date.isoformat() if flag.end_date else None,
                        'updated_at': flag.updated_at.isoformat()
                    }
                    active_flags.append(flag_info)
            
            return sorted(active_flags, key=lambda x: x['updated_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Error listing active flags: {e}")
            return []
    
    async def bulk_evaluate_flags(
        self,
        user_id: str,
        user_context: Dict[str, Any],
        flag_ids: Optional[List[str]] = None
    ) -> Dict[str, FeatureEvaluation]:
        """Évalue plusieurs feature flags en une fois"""
        try:
            if flag_ids is None:
                flag_ids = list(self.feature_flags.keys())
            
            evaluations = {}
            
            # Évaluation parallèle
            tasks = []
            for flag_id in flag_ids:
                task = self.evaluate_feature_flag(flag_id, user_id, user_context)
                tasks.append((flag_id, task))
            
            # Collecte des résultats
            for flag_id, task in tasks:
                try:
                    evaluation = await task
                    evaluations[flag_id] = evaluation
                except Exception as e:
                    logger.error(f"❌ Error evaluating flag {flag_id}: {e}")
            
            return evaluations
            
        except Exception as e:
            logger.error(f"❌ Error in bulk flag evaluation: {e}")
            return {}


# Instance globale
feature_flag_manager = FeatureFlagManager()

# Export des classes principales
__all__ = [
    'FeatureFlagManager',
    'FeatureFlag',
    'FeatureEvaluation',
    'ABTestConfig',
    'FeatureStatus',
    'RolloutStrategy',
    'TargetingType',
    'feature_flag_manager'
]