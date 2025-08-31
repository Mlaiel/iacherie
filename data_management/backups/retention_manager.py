"""🗄️ Retention Manager - Advanced Backup Retention System
======================================================
Module: backend/data_management/backups/retention_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Retention System - Enterprise Production-Ready
Responsibility: Gestion intelligente de la rétention des sauvegardes
====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""import asyncio
import logging
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import calendar

from .models import BackupMetadata, BackupStatus, BackupType
from .exceptions import RetentionException
from .storage import BackupStorage

logger = logging.getLogger(__name__)


class RetentionStrategy(Enum):
    """Stratégies de rétention"""    SIMPLE_TIME = "simple_time"           # Basé sur l'âge uniquement
    GRANDFATHER_FATHER_SON = "gfs"        # Stratégie GFS classique
    TOWER_OF_HANOI = "tower_of_hanoi"     # Algorithme Tour de Hanoï
    FIBONACCI = "fibonacci"               # Séquence de Fibonacci
    CUSTOM_SCHEDULE = "custom_schedule"   # Planning personnalisé
    SMART_ADAPTIVE = "smart_adaptive"     # Adaptatif intelligent


class RetentionAction(Enum):
    """Actions de rétention"""    KEEP = "keep"                # Conserver
    DELETE = "delete"            # Supprimer
    ARCHIVE = "archive"          # Archiver
    COMPRESS = "compress"        # Compresser davantage
    MIGRATE = "migrate"          # Migrer vers stockage froid


@dataclass
class RetentionRule:
    """Règle de rétention"""    rule_id: str
    name: str
    strategy: RetentionStrategy
    backup_types: List[BackupType] = field(default_factory=list)
    
    # Paramètres de temps
    daily_keep: int = 7           # Jours à garder (quotidien)
    weekly_keep: int = 4          # Semaines à garder
    monthly_keep: int = 12        # Mois à garder
    yearly_keep: int = 3          # Années à garder
    
    # Paramètres avancés
    min_backups: int = 3          # Minimum à toujours garder
    max_backups: Optional[int] = None  # Maximum absolu
    size_limit_gb: Optional[float] = None  # Limite de taille totale
    
    # Actions
    default_action: RetentionAction = RetentionAction.DELETE
    archive_action: RetentionAction = RetentionAction.ARCHIVE
    
    # Critères spéciaux
    protect_patterns: List[str] = field(default_factory=list)  # Patterns à protéger
    priority_users: List[str] = field(default_factory=list)   # Utilisateurs prioritaires
    
    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "strategy": self.strategy.value,
            "backup_types": [bt.value for bt in self.backup_types],
            "daily_keep": self.daily_keep,
            "weekly_keep": self.weekly_keep,
            "monthly_keep": self.monthly_keep,
            "yearly_keep": self.yearly_keep,
            "min_backups": self.min_backups,
            "max_backups": self.max_backups,
            "size_limit_gb": self.size_limit_gb,
            "default_action": self.default_action.value,
            "archive_action": self.archive_action.value,
            "protect_patterns": self.protect_patterns,
            "priority_users": self.priority_users,
            "created_at": self.created_at.isoformat(),
            "enabled": self.enabled,
            "metadata": self.metadata
        }


@dataclass
class RetentionPlan:
    """Plan d'exécution de rétention"""    plan_id: str
    rule_id: str
    backups_to_process: List[BackupMetadata]
    actions: Dict[str, RetentionAction] = field(default_factory=dict)  # backup_id -> action
    estimated_space_freed: int = 0  # bytes
    created_at: datetime = field(default_factory=datetime.now)
    executed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "plan_id": self.plan_id,
            "rule_id": self.rule_id,
            "backups_to_process": [b.to_dict() for b in self.backups_to_process],
            "actions": {bid: action.value for bid, action in self.actions.items()},
            "estimated_space_freed": self.estimated_space_freed,
            "created_at": self.created_at.isoformat(),
            "executed": self.executed
        }


@dataclass
class RetentionStats:
    """Statistiques de rétention"""    total_backups: int = 0
    backups_deleted: int = 0
    backups_archived: int = 0
    backups_compressed: int = 0
    space_freed_gb: float = 0.0
    space_archived_gb: float = 0.0
    last_execution: Optional[datetime] = None
    average_execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""        return {
            "total_backups": self.total_backups,
            "backups_deleted": self.backups_deleted,
            "backups_archived": self.backups_archived,
            "backups_compressed": self.backups_compressed,
            "space_freed_gb": self.space_freed_gb,
            "space_archived_gb": self.space_archived_gb,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "average_execution_time": self.average_execution_time
        }


class RetentionManager:
    """    Gestionnaire intelligent de rétention des sauvegardes
    
    Fonctionnalités:
    - Stratégies de rétention multiples
    - Planification automatique
    - Optimisation espace de stockage
    - Protection des sauvegardes critiques
    - Analytics et reporting
    - Actions graduelles (archive -> compression -> suppression)
    """    
    def __init__(self, storage: Optional[BackupStorage] = None):
        self.storage = storage
        
        # Règles de rétention
        self.retention_rules: Dict[str, RetentionRule] = {}
        
        # Historique des plans et exécutions
        self.execution_history: List[Dict[str, Any]] = []
        
        # Statistiques
        self.retention_stats = RetentionStats()
        
        # Cache des métadonnées de sauvegarde
        self.backup_cache: Dict[str, BackupMetadata] = {}
        
        # Configuration par défaut
        self._setup_default_rules()
        
        logger.info("RetentionManager initialized")
    
    def _setup_default_rules(self):
        """Configure les règles de rétention par défaut"""        # Règle standard GFS
        gfs_rule = RetentionRule(
            rule_id="default_gfs",
            name="Default GFS Strategy",
            strategy=RetentionStrategy.GRANDFATHER_FATHER_SON,
            backup_types=[BackupType.FULL, BackupType.INCREMENTAL, BackupType.DIFFERENTIAL],
            daily_keep=7,
            weekly_keep=4,
            monthly_keep=12,
            yearly_keep=3,
            min_backups=3
        )
        
        # Règle simple pour tests/dev
        simple_rule = RetentionRule(
            rule_id="simple_time",
            name="Simple Time-based Retention",
            strategy=RetentionStrategy.SIMPLE_TIME,
            backup_types=[BackupType.FULL],
            daily_keep=30,
            min_backups=2
        )
        
        self.retention_rules[gfs_rule.rule_id] = gfs_rule
        self.retention_rules[simple_rule.rule_id] = simple_rule
    
    def add_retention_rule(self, rule: RetentionRule):
        """        Ajoute une règle de rétention
        
        Args:
            rule: Règle à ajouter
        """        self.retention_rules[rule.rule_id] = rule
        logger.info(f"Added retention rule: {rule.name}")
    
    def remove_retention_rule(self, rule_id: str) -> bool:
        """        Supprime une règle de rétention
        
        Args:
            rule_id: ID de la règle
            
        Returns:
            bool: True si suppression réussie
        """        if rule_id in self.retention_rules:
            del self.retention_rules[rule_id]
            logger.info(f"Removed retention rule: {rule_id}")
            return True
        
        return False
    
    async def create_retention_plan(
        self,
        rule_id: str,
        backups: List[BackupMetadata],
        dry_run: bool = False
    ) -> RetentionPlan:
        """        Crée un plan de rétention
        
        Args:
            rule_id: ID de la règle à appliquer
            backups: Liste des sauvegardes
            dry_run: Mode simulation
            
        Returns:
            RetentionPlan: Plan de rétention
        """        try:
            if rule_id not in self.retention_rules:
                raise RetentionException(f"Retention rule not found: {rule_id}")
            
            rule = self.retention_rules[rule_id]
            
            if not rule.enabled:
                raise RetentionException(f"Retention rule is disabled: {rule_id}")
            
            # Filtrage des sauvegardes applicables
            applicable_backups = self._filter_applicable_backups(backups, rule)
            
            # Génération plan selon stratégie
            plan = await self._generate_plan_by_strategy(rule, applicable_backups)
            
            # Optimisations et validations
            await self._optimize_retention_plan(plan, rule)
            await self._validate_retention_plan(plan, rule)
            
            logger.info(f"Created retention plan {plan.plan_id} with {len(plan.actions)} actions")
            
            if not dry_run:
                # Sauvegarde du plan pour exécution ultérieure
                await self._save_retention_plan(plan)
            
            return plan
            
        except Exception as e:
            logger.error(f"Retention plan creation failed: {e}")
            raise RetentionException(f"Retention plan creation failed: {e}")
    
    def _filter_applicable_backups(
        self,
        backups: List[BackupMetadata],
        rule: RetentionRule
    ) -> List[BackupMetadata]:
        """Filtre les sauvegardes applicables à une règle"""        applicable = []
        
        for backup in backups:
            # Filtre par type de sauvegarde
            if rule.backup_types and backup.backup_type not in rule.backup_types:
                continue
            
            # Filtre par patterns de protection
            if self._is_protected_backup(backup, rule.protect_patterns):
                continue
            
            # Filtre par utilisateurs prioritaires
            if rule.priority_users and backup.user_id not in rule.priority_users:
                continue
            
            # Filtre par statut (seulement sauvegardes complètes)
            if backup.status != BackupStatus.COMPLETED:
                continue
            
            applicable.append(backup)
        
        return applicable
    
    def _is_protected_backup(self, backup: BackupMetadata, patterns: List[str]) -> bool:
        """Vérifie si une sauvegarde est protégée par un pattern"""        if not patterns:
            return False
        
        import fnmatch
        
        backup_identifier = f"{backup.backup_id}:{backup.user_id}"
        
        for pattern in patterns:
            if fnmatch.fnmatch(backup_identifier, pattern):
                return True
        
        return False
    
    async def _generate_plan_by_strategy(
        self,
        rule: RetentionRule,
        backups: List[BackupMetadata]
    ) -> RetentionPlan:
        """Génère un plan selon la stratégie de rétention"""        plan_id = self._generate_plan_id()
        
        plan = RetentionPlan(
            plan_id=plan_id,
            rule_id=rule.rule_id,
            backups_to_process=backups.copy()
        )
        
        if rule.strategy == RetentionStrategy.SIMPLE_TIME:
            await self._apply_simple_time_strategy(plan, rule)
        elif rule.strategy == RetentionStrategy.GRANDFATHER_FATHER_SON:
            await self._apply_gfs_strategy(plan, rule)
        elif rule.strategy == RetentionStrategy.TOWER_OF_HANOI:
            await self._apply_tower_of_hanoi_strategy(plan, rule)
        elif rule.strategy == RetentionStrategy.FIBONACCI:
            await self._apply_fibonacci_strategy(plan, rule)
        elif rule.strategy == RetentionStrategy.SMART_ADAPTIVE:
            await self._apply_smart_adaptive_strategy(plan, rule)
        else:
            raise RetentionException(f"Unsupported retention strategy: {rule.strategy}")
        
        return plan
    
    def _generate_plan_id(self) -> str:
        """Génère un ID unique pour un plan"""        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import secrets
        return f"plan_{timestamp}_{secrets.token_hex(8)}"
    
    async def _apply_simple_time_strategy(self, plan: RetentionPlan, rule: RetentionRule):
        """Applique la stratégie simple basée sur le temps"""        cutoff_date = datetime.now() - timedelta(days=rule.daily_keep)
        
        # Tri par date (plus ancien en premier)
        backups_sorted = sorted(plan.backups_to_process, key=lambda x: x.created_at)
        
        kept_count = 0
        
        for backup in backups_sorted:
            if backup.created_at > cutoff_date or kept_count < rule.min_backups:
                plan.actions[backup.backup_id] = RetentionAction.KEEP
                kept_count += 1
            else:
                # Vérification limite maximale
                if rule.max_backups and kept_count >= rule.max_backups:
                    plan.actions[backup.backup_id] = rule.default_action
                    plan.estimated_space_freed += backup.total_size
                else:
                    plan.actions[backup.backup_id] = RetentionAction.KEEP
                    kept_count += 1
    
    async def _apply_gfs_strategy(self, plan: RetentionPlan, rule: RetentionRule):
        """Applique la stratégie Grandfather-Father-Son"""        now = datetime.now()
        
        # Catégorisation des sauvegardes
        daily_backups = []
        weekly_backups = []
        monthly_backups = []
        yearly_backups = []
        
        # Classification par période
        for backup in plan.backups_to_process:
            age = now - backup.created_at
            
            if age <= timedelta(days=rule.daily_keep):
                daily_backups.append(backup)
            elif age <= timedelta(weeks=rule.weekly_keep):
                weekly_backups.append(backup)
            elif age <= timedelta(days=rule.monthly_keep * 30):
                monthly_backups.append(backup)
            elif age <= timedelta(days=rule.yearly_keep * 365):
                yearly_backups.append(backup)
        
        # Application règles GFS
        self._apply_gfs_category(plan, daily_backups, "daily", 1)  # 1 par jour
        self._apply_gfs_category(plan, weekly_backups, "weekly", 7)  # 1 par semaine
        self._apply_gfs_category(plan, monthly_backups, "monthly", 30)  # 1 par mois
        self._apply_gfs_category(plan, yearly_backups, "yearly", 365)  # 1 par an
        
        # Suppression des sauvegardes trop anciennes
        for backup in plan.backups_to_process:
            if backup.backup_id not in plan.actions:
                age = now - backup.created_at
                
                if age > timedelta(days=rule.yearly_keep * 365):
                    plan.actions[backup.backup_id] = rule.default_action
                    plan.estimated_space_freed += backup.total_size
    
    def _apply_gfs_category(
        self,
        plan: RetentionPlan,
        backups: List[BackupMetadata],
        category: str,
        interval_days: int
    ):
        """Applique les règles GFS pour une catégorie"""        if not backups:
            return
        
        # Tri par date
        backups_sorted = sorted(backups, key=lambda x: x.created_at, reverse=True)
        
        # Groupement par intervalle
        kept_periods = set()
        
        for backup in backups_sorted:
            # Calcul de la période
            period_key = backup.created_at.date() // interval_days
            
            if period_key not in kept_periods:
                # Premier de cette période - garder
                plan.actions[backup.backup_id] = RetentionAction.KEEP
                kept_periods.add(period_key)
            else:
                # Dupliquer dans cette période - supprimer ou archiver
                if category in ["monthly", "yearly"]:
                    plan.actions[backup.backup_id] = RetentionAction.ARCHIVE
                else:
                    plan.actions[backup.backup_id] = RetentionAction.DELETE
                    plan.estimated_space_freed += backup.total_size
    
    async def _apply_tower_of_hanoi_strategy(self, plan: RetentionPlan, rule: RetentionRule):
        """Applique la stratégie Tour de Hanoï"""        # Tri par date (plus récent en premier)
        backups_sorted = sorted(plan.backups_to_process, key=lambda x: x.created_at, reverse=True)
        
        kept_count = 0
        
        for i, backup in enumerate(backups_sorted):
            # Algorithme Tour de Hanoï : garder si i & (i+1) == 0
            if (i & (i + 1)) == 0 or kept_count < rule.min_backups:
                plan.actions[backup.backup_id] = RetentionAction.KEEP
                kept_count += 1
            else:
                plan.actions[backup.backup_id] = rule.default_action
                plan.estimated_space_freed += backup.total_size
    
    async def _apply_fibonacci_strategy(self, plan: RetentionPlan, rule: RetentionRule):
        """Applique la stratégie basée sur Fibonacci"""        # Génération séquence Fibonacci
        fib_sequence = [1, 1]
        while fib_sequence[-1] < len(plan.backups_to_process):
            fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
        
        # Tri par date (plus récent en premier)
        backups_sorted = sorted(plan.backups_to_process, key=lambda x: x.created_at, reverse=True)
        
        # Indices Fibonacci à garder
        keep_indices = set(fib_sequence[:rule.daily_keep])
        
        for i, backup in enumerate(backups_sorted):
            if i in keep_indices or i < rule.min_backups:
                plan.actions[backup.backup_id] = RetentionAction.KEEP
            else:
                plan.actions[backup.backup_id] = rule.default_action
                plan.estimated_space_freed += backup.total_size
    
    async def _apply_smart_adaptive_strategy(self, plan: RetentionPlan, rule: RetentionRule):
        """Applique la stratégie adaptative intelligente"""        # Analyse des patterns d'utilisation
        usage_patterns = await self._analyze_backup_usage_patterns(plan.backups_to_process)
        
        # Tri par score d'importance
        backups_with_scores = []
        
        for backup in plan.backups_to_process:
            score = self._calculate_backup_importance_score(backup, usage_patterns)
            backups_with_scores.append((backup, score))
        
        # Tri par score décroissant
        backups_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Application règles adaptatives
        kept_count = 0
        total_size = 0
        
        for backup, score in backups_with_scores:
            should_keep = (
                kept_count < rule.min_backups or
                score > 0.7 or  # Score élevé
                (rule.size_limit_gb is None or total_size < rule.size_limit_gb * 1024**3)
            )
            
            if should_keep and (rule.max_backups is None or kept_count < rule.max_backups):
                plan.actions[backup.backup_id] = RetentionAction.KEEP
                kept_count += 1
                total_size += backup.total_size
            else:
                # Action graduée selon score
                if score > 0.4:
                    plan.actions[backup.backup_id] = RetentionAction.ARCHIVE
                elif score > 0.2:
                    plan.actions[backup.backup_id] = RetentionAction.COMPRESS
                else:
                    plan.actions[backup.backup_id] = RetentionAction.DELETE
                    plan.estimated_space_freed += backup.total_size
    
    async def _analyze_backup_usage_patterns(
        self,
        backups: List[BackupMetadata]
    ) -> Dict[str, Any]:
        """Analyse les patterns d'utilisation des sauvegardes"""        # En production: analyse des logs d'accès, restaurations, etc.
        # Ici: simulation basique
        
        patterns = {
            "access_frequency": {},
            "restoration_count": {},
            "user_preferences": {},
            "content_types": {}
        }
        
        for backup in backups:
            # Simulation fréquence d'accès
            age_days = (datetime.now() - backup.created_at).days
            access_freq = max(0, 1.0 - (age_days / 365))  # Décroît avec l'âge
            patterns["access_frequency"][backup.backup_id] = access_freq
        
        return patterns
    
    def _calculate_backup_importance_score(
        self,
        backup: BackupMetadata,
        usage_patterns: Dict[str, Any]
    ) -> float:
        """Calcule un score d'importance pour une sauvegarde"""        score = 0.0
        
        # Facteur âge (plus récent = plus important)
        age_days = (datetime.now() - backup.created_at).days
        age_factor = max(0, 1.0 - (age_days / 365))
        score += age_factor * 0.3
        
        # Facteur type de sauvegarde
        if backup.backup_type == BackupType.FULL:
            score += 0.4
        elif backup.backup_type == BackupType.INCREMENTAL:
            score += 0.2
        elif backup.backup_type == BackupType.DIFFERENTIAL:
            score += 0.3
        
        # Facteur fréquence d'accès
        access_freq = usage_patterns["access_frequency"].get(backup.backup_id, 0)
        score += access_freq * 0.3
        
        # Facteur taille (plus petit = plus facile à garder)
        size_gb = backup.total_size / (1024**3)
        size_factor = max(0, 1.0 - (size_gb / 100))  # Pénalise les gros fichiers
        score += size_factor * 0.1
        
        return min(1.0, score)
    
    async def _optimize_retention_plan(self, plan: RetentionPlan, rule: RetentionRule):
        """Optimise un plan de rétention"""        # Vérification limites de taille
        if rule.size_limit_gb:
            await self._enforce_size_limit(plan, rule)
        
        # Optimisation actions graduelles
        await self._optimize_gradual_actions(plan, rule)
        
        # Vérification cohérence
        await self._ensure_plan_coherence(plan, rule)
    
    async def _enforce_size_limit(self, plan: RetentionPlan, rule: RetentionRule):
        """Applique les limites de taille"""        size_limit_bytes = rule.size_limit_gb * 1024**3
        
        # Calcul taille actuelle des sauvegardes à garder
        current_size = 0
        kept_backups = []
        
        for backup in plan.backups_to_process:
            action = plan.actions.get(backup.backup_id, RetentionAction.KEEP)
            
            if action == RetentionAction.KEEP:
                current_size += backup.total_size
                kept_backups.append(backup)
        
        # Si dépassement, archiver ou supprimer les plus anciennes
        if current_size > size_limit_bytes:
            # Tri par date (plus ancien en premier)
            kept_backups.sort(key=lambda x: x.created_at)
            
            for backup in kept_backups:
                if current_size <= size_limit_bytes:
                    break
                
                # Change action de KEEP vers ARCHIVE ou DELETE
                plan.actions[backup.backup_id] = rule.archive_action
                current_size -= backup.total_size
                
                if rule.archive_action == RetentionAction.DELETE:
                    plan.estimated_space_freed += backup.total_size
    
    async def _optimize_gradual_actions(self, plan: RetentionPlan, rule: RetentionRule):
        """Optimise les actions graduelles"""        # Conversion DELETE -> ARCHIVE pour sauvegardes importantes
        for backup in plan.backups_to_process:
            action = plan.actions.get(backup.backup_id, RetentionAction.KEEP)
            
            if action == RetentionAction.DELETE:
                # Critères pour archivage au lieu de suppression
                if (backup.backup_type == BackupType.FULL or
                    backup.total_size < 100 * 1024 * 1024):  # < 100MB
                    
                    plan.actions[backup.backup_id] = RetentionAction.ARCHIVE
                    plan.estimated_space_freed -= backup.total_size
    
    async def _ensure_plan_coherence(self, plan: RetentionPlan, rule: RetentionRule):
        """Assure la cohérence du plan"""        # Vérification minimum de sauvegardes
        keep_count = sum(1 for action in plan.actions.values() if action == RetentionAction.KEEP)
        
        if keep_count < rule.min_backups:
            # Conversion d'actions vers KEEP pour respecter le minimum
            backups_by_date = sorted(
                plan.backups_to_process,
                key=lambda x: x.created_at,
                reverse=True
            )
            
            converted = 0
            needed = rule.min_backups - keep_count
            
            for backup in backups_by_date:
                if converted >= needed:
                    break
                
                action = plan.actions.get(backup.backup_id, RetentionAction.KEEP)
                
                if action != RetentionAction.KEEP:
                    plan.actions[backup.backup_id] = RetentionAction.KEEP
                    
                    if action == RetentionAction.DELETE:
                        plan.estimated_space_freed -= backup.total_size
                    
                    converted += 1
    
    async def _validate_retention_plan(self, plan: RetentionPlan, rule: RetentionRule):
        """Valide un plan de rétention"""        # Vérification actions valides
        for backup_id, action in plan.actions.items():
            if not isinstance(action, RetentionAction):
                raise RetentionException(f"Invalid retention action for {backup_id}: {action}")
        
        # Vérification minimum respecté
        keep_count = sum(1 for action in plan.actions.values() if action == RetentionAction.KEEP)
        
        if keep_count < rule.min_backups:
            raise RetentionException(
                f"Plan violates minimum backup rule: {keep_count} < {rule.min_backups}"
            )
        
        # Vérification maximum respecté
        if rule.max_backups and keep_count > rule.max_backups:
            raise RetentionException(
                f"Plan violates maximum backup rule: {keep_count} > {rule.max_backups}"
            )
    
    async def _save_retention_plan(self, plan: RetentionPlan):
        """Sauvegarde un plan de rétention"""        # En production: sauvegarde en base de données
        # Ici: sauvegarde fichier JSON
        plan_file = Path(f"/tmp/retention_plan_{plan.plan_id}.json")
        
        try:
            with open(plan_file, 'w') as f:
                json.dump(plan.to_dict(), f, indent=2)
            
            logger.debug(f"Retention plan saved: {plan_file}")
            
        except Exception as e:
            logger.error(f"Failed to save retention plan: {e}")
    
    async def execute_retention_plan(self, plan: RetentionPlan) -> Dict[str, Any]:
        """        Exécute un plan de rétention
        
        Args:
            plan: Plan à exécuter
            
        Returns:
            Dict[str, Any]: Résultats d'exécution
        """        try:
            if plan.executed:
                raise RetentionException("Plan already executed")
            
            start_time = datetime.now()
            execution_results = {
                "plan_id": plan.plan_id,
                "started_at": start_time.isoformat(),
                "actions_executed": {},
                "errors": [],
                "space_freed": 0,
                "space_archived": 0
            }
            
            # Exécution des actions
            for backup_id, action in plan.actions.items():
                try:
                    result = await self._execute_retention_action(backup_id, action)
                    execution_results["actions_executed"][backup_id] = {
                        "action": action.value,
                        "success": result["success"],
                        "space_changed": result.get("space_changed", 0)
                    }
                    
                    if action == RetentionAction.DELETE:
                        execution_results["space_freed"] += result.get("space_changed", 0)
                    elif action == RetentionAction.ARCHIVE:
                        execution_results["space_archived"] += result.get("space_changed", 0)
                        
                except Exception as e:
                    error_msg = f"Action failed for {backup_id}: {e}"
                    execution_results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Finalisation
            plan.executed = True
            end_time = datetime.now()
            execution_duration = (end_time - start_time).total_seconds()
            
            execution_results["completed_at"] = end_time.isoformat()
            execution_results["duration_seconds"] = execution_duration
            
            # Mise à jour statistiques
            self._update_retention_stats(execution_results)
            
            # Ajout à l'historique
            self.execution_history.append(execution_results)
            
            logger.info(f"Retention plan {plan.plan_id} executed successfully")
            return execution_results
            
        except Exception as e:
            logger.error(f"Retention plan execution failed: {e}")
            raise RetentionException(f"Retention plan execution failed: {e}")
    
    async def _execute_retention_action(
        self,
        backup_id: str,
        action: RetentionAction
    ) -> Dict[str, Any]:
        """Exécute une action de rétention"""        try:
            if action == RetentionAction.KEEP:
                return {"success": True, "space_changed": 0}
            
            elif action == RetentionAction.DELETE:
                space_freed = await self._delete_backup(backup_id)
                return {"success": True, "space_changed": space_freed}
            
            elif action == RetentionAction.ARCHIVE:
                space_changed = await self._archive_backup(backup_id)
                return {"success": True, "space_changed": space_changed}
            
            elif action == RetentionAction.COMPRESS:
                space_saved = await self._compress_backup(backup_id)
                return {"success": True, "space_changed": space_saved}
            
            elif action == RetentionAction.MIGRATE:
                space_migrated = await self._migrate_backup(backup_id)
                return {"success": True, "space_changed": space_migrated}
            
            else:
                raise RetentionException(f"Unknown retention action: {action}")
                
        except Exception as e:
            logger.error(f"Retention action {action} failed for {backup_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_backup(self, backup_id: str) -> int:
        """Supprime une sauvegarde"""        if self.storage:
            result = await self.storage.delete_backup(backup_id)
            return result.get("space_freed", 0)
        else:
            # Simulation
            backup_size = 1024 * 1024 * 100  # 100MB simulé
            logger.info(f"Simulated deletion of backup {backup_id}")
            return backup_size
    
    async def _archive_backup(self, backup_id: str) -> int:
        """Archive une sauvegarde"""        if self.storage:
            # Migration vers stockage d'archive
            result = await self.storage.move_to_archive(backup_id)
            return result.get("space_changed", 0)
        else:
            # Simulation
            logger.info(f"Simulated archiving of backup {backup_id}")
            return 0
    
    async def _compress_backup(self, backup_id: str) -> int:
        """Compresse davantage une sauvegarde"""        if self.storage:
            result = await self.storage.recompress_backup(backup_id)
            return result.get("space_saved", 0)
        else:
            # Simulation
            space_saved = 1024 * 1024 * 20  # 20MB économisés simulés
            logger.info(f"Simulated compression of backup {backup_id}")
            return space_saved
    
    async def _migrate_backup(self, backup_id: str) -> int:
        """Migre une sauvegarde vers stockage froid"""        if self.storage:
            result = await self.storage.migrate_to_cold_storage(backup_id)
            return result.get("space_migrated", 0)
        else:
            # Simulation
            logger.info(f"Simulated migration of backup {backup_id}")
            return 0
    
    def _update_retention_stats(self, execution_results: Dict[str, Any]):
        """Met à jour les statistiques de rétention"""        self.retention_stats.last_execution = datetime.now()
        
        for backup_id, result in execution_results["actions_executed"].items():
            if not result["success"]:
                continue
            
            action = result["action"]
            
            if action == "delete":
                self.retention_stats.backups_deleted += 1
                self.retention_stats.space_freed_gb += result["space_changed"] / (1024**3)
            elif action == "archive":
                self.retention_stats.backups_archived += 1
                self.retention_stats.space_archived_gb += result["space_changed"] / (1024**3)
            elif action == "compress":
                self.retention_stats.backups_compressed += 1
        
        # Mise à jour temps moyen
        duration = execution_results.get("duration_seconds", 0)
        current_avg = self.retention_stats.average_execution_time
        
        if current_avg == 0:
            self.retention_stats.average_execution_time = duration
        else:
            self.retention_stats.average_execution_time = (current_avg + duration) / 2
    
    async def schedule_retention_cleanup(self, rule_id: str, cron_expression: str):
        """        Programme le nettoyage automatique selon une règle
        
        Args:
            rule_id: ID de la règle de rétention
            cron_expression: Expression cron pour la planification
        """        # En production: intégration avec scheduler (Celery, APScheduler, etc.)
        logger.info(f"Scheduled retention cleanup for rule {rule_id}: {cron_expression}")
    
    def get_retention_stats(self) -> Dict[str, Any]:
        """        Récupère les statistiques de rétention
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """        stats = self.retention_stats.to_dict()
        
        # Statistiques additionnelles
        stats["total_rules"] = len(self.retention_rules)
        stats["active_rules"] = sum(1 for rule in self.retention_rules.values() if rule.enabled)
        stats["total_executions"] = len(self.execution_history)
        
        return stats
    
    def list_retention_rules(self) -> List[RetentionRule]:
        """        Liste toutes les règles de rétention
        
        Returns:
            List[RetentionRule]: Liste des règles
        """        return list(self.retention_rules.values())
    
    def get_retention_rule(self, rule_id: str) -> Optional[RetentionRule]:
        """        Récupère une règle de rétention spécifique
        
        Args:
            rule_id: ID de la règle
            
        Returns:
            Optional[RetentionRule]: Règle ou None
        """        return self.retention_rules.get(rule_id)


# Export des classes principales
__all__ = [
    'RetentionManager',
    'RetentionRule',
    'RetentionPlan',
    'RetentionStats',
    'RetentionStrategy',
    'RetentionAction'
]
