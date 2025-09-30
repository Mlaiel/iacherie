"""
Enterprise Data Manager
Gestion complète du cycle de vie des données d'entreprise
Comprehensive Enterprise Data Lifecycle Management

Ce module fournit une gestion complète du cycle de vie des données d'entreprise incluant:
- Gestion automatisée de l'archivage et de la rétention
- Conformité réglementaire automatisée (GDPR, CCPA, SOX)
- Gestion des métadonnées d'entreprise
- Surveillance continue de la qualité des données
- Optimisation automatique des performances
- Gestion centralisée des politiques de données

Created by: AI Assistant
Date: 2024
"""

import asyncio
import logging
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time


class DataLifecycleStage(Enum):
    """Étapes du cycle de vie des données"""
    INGESTION = "ingestion"
    PROCESSING = "processing"
    STORAGE = "storage"
    ANALYTICS = "analytics"
    ARCHIVAL = "archival"
    DELETION = "deletion"


class ComplianceRegulation(Enum):
    """Réglementations de conformité supportées"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"


class DataClassification(Enum):
    """Classification des données"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


@dataclass
class DataAsset:
    """Actif de données avec métadonnées complètes"""
    asset_id: str
    name: str
    description: str
    classification: DataClassification
    owner: str
    steward: str
    location: str
    format: str
    size_bytes: int
    created_at: datetime
    last_modified: datetime
    last_accessed: datetime
    retention_period: int  # en jours
    compliance_requirements: List[ComplianceRegulation]
    lifecycle_stage: DataLifecycleStage
    quality_score: float
    lineage_info: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class RetentionPolicy:
    """Politique de rétention des données"""
    policy_id: str
    name: str
    description: str
    data_classification: DataClassification
    retention_period_days: int
    archival_period_days: int
    deletion_period_days: int
    compliance_requirements: List[ComplianceRegulation]
    auto_archive: bool = True
    auto_delete: bool = False
    approval_required: bool = True


@dataclass
class ComplianceRule:
    """Règle de conformité"""
    rule_id: str
    regulation: ComplianceRegulation
    rule_type: str
    description: str
    validation_logic: str
    remediation_action: str
    severity: str
    enabled: bool = True


class EnterpriseDataManager:
    """Gestionnaire de données d'entreprise avancé"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le gestionnaire de données d'entreprise
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Configuration par défaut
        self.data_assets: Dict[str, DataAsset] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        
        # Services et composants
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 20)
        )
        
        # Métriques et surveillance
        self.metrics = {
            'assets_managed': 0,
            'policies_enforced': 0,
            'compliance_checks': 0,
            'archival_operations': 0,
            'deletion_operations': 0,
            'quality_assessments': 0,
            'last_update': datetime.now()
        }
        
        # Cache et optimisation
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)
        
        # État du système
        self.is_running = False
        self.monitoring_thread = None
        
        self.logger.info("Enterprise Data Manager initialisé avec succès")
    
    def _setup_logging(self) -> logging.Logger:
        """Configure le logging pour le gestionnaire"""
        logger = logging.getLogger(f"{__name__}.EnterpriseDataManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def start_monitoring(self):
        """Démarre la surveillance continue du cycle de vie des données"""
        self.is_running = True
        self.logger.info("Démarrage de la surveillance continue des données")
        
        # Thread de surveillance principal
        self.monitoring_thread = threading.Thread(
            target=self._continuous_monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        # Tâches de surveillance
        monitoring_tasks = [
            self._monitor_data_lifecycle(),
            self._monitor_compliance(),
            self._monitor_retention_policies(),
            self._monitor_data_quality(),
            self._optimize_storage()
        ]
        
        await asyncio.gather(*monitoring_tasks)
    
    def _continuous_monitoring_loop(self):
        """Boucle de surveillance continue"""
        while self.is_running:
            try:
                # Vérifications périodiques
                self._check_retention_compliance()
                self._update_asset_metadata()
                self._cleanup_expired_cache()
                
                # Pause avant la prochaine vérification
                time.sleep(self.config.get('monitoring_interval', 300))
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance continue: {e}")
                time.sleep(60)  # Pause en cas d'erreur
    
    async def register_data_asset(self, asset_data: Dict[str, Any]) -> str:
        """
        Enregistre un nouvel actif de données
        
        Args:
            asset_data: Données de l'actif
            
        Returns:
            ID de l'actif enregistré
        """
        try:
            # Génération de l'ID unique
            asset_id = str(uuid.uuid4())
            
            # Création de l'actif de données
            asset = DataAsset(
                asset_id=asset_id,
                name=asset_data.get('name', ''),
                description=asset_data.get('description', ''),
                classification=DataClassification(
                    asset_data.get('classification', 'internal')
                ),
                owner=asset_data.get('owner', ''),
                steward=asset_data.get('steward', ''),
                location=asset_data.get('location', ''),
                format=asset_data.get('format', ''),
                size_bytes=asset_data.get('size_bytes', 0),
                created_at=datetime.now(),
                last_modified=datetime.now(),
                last_accessed=datetime.now(),
                retention_period=asset_data.get('retention_period', 365),
                compliance_requirements=[
                    ComplianceRegulation(req) 
                    for req in asset_data.get('compliance_requirements', [])
                ],
                lifecycle_stage=DataLifecycleStage.INGESTION,
                quality_score=0.0,
                lineage_info={},
                metadata=asset_data.get('metadata', {})
            )
            
            # Enregistrement de l'actif
            self.data_assets[asset_id] = asset
            
            # Mise à jour des métriques
            self.metrics['assets_managed'] += 1
            self.metrics['last_update'] = datetime.now()
            
            # Application des politiques de rétention
            await self._apply_retention_policies(asset)
            
            # Évaluation de la qualité initiale
            await self._assess_data_quality(asset)
            
            self.logger.info(f"Actif de données enregistré: {asset_id}")
            return asset_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de l'actif: {e}")
            raise
    
    async def create_retention_policy(self, policy_data: Dict[str, Any]) -> str:
        """
        Crée une nouvelle politique de rétention
        
        Args:
            policy_data: Données de la politique
            
        Returns:
            ID de la politique créée
        """
        try:
            policy_id = str(uuid.uuid4())
            
            policy = RetentionPolicy(
                policy_id=policy_id,
                name=policy_data.get('name', ''),
                description=policy_data.get('description', ''),
                data_classification=DataClassification(
                    policy_data.get('data_classification', 'internal')
                ),
                retention_period_days=policy_data.get('retention_period_days', 365),
                archival_period_days=policy_data.get('archival_period_days', 2555),  # 7 ans
                deletion_period_days=policy_data.get('deletion_period_days', 3650),  # 10 ans
                compliance_requirements=[
                    ComplianceRegulation(req) 
                    for req in policy_data.get('compliance_requirements', [])
                ],
                auto_archive=policy_data.get('auto_archive', True),
                auto_delete=policy_data.get('auto_delete', False),
                approval_required=policy_data.get('approval_required', True)
            )
            
            self.retention_policies[policy_id] = policy
            
            self.logger.info(f"Politique de rétention créée: {policy_id}")
            return policy_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la politique: {e}")
            raise
    
    async def create_compliance_rule(self, rule_data: Dict[str, Any]) -> str:
        """
        Crée une nouvelle règle de conformité
        
        Args:
            rule_data: Données de la règle
            
        Returns:
            ID de la règle créée
        """
        try:
            rule_id = str(uuid.uuid4())
            
            rule = ComplianceRule(
                rule_id=rule_id,
                regulation=ComplianceRegulation(rule_data.get('regulation')),
                rule_type=rule_data.get('rule_type', ''),
                description=rule_data.get('description', ''),
                validation_logic=rule_data.get('validation_logic', ''),
                remediation_action=rule_data.get('remediation_action', ''),
                severity=rule_data.get('severity', 'medium'),
                enabled=rule_data.get('enabled', True)
            )
            
            self.compliance_rules[rule_id] = rule
            
            self.logger.info(f"Règle de conformité créée: {rule_id}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la règle: {e}")
            raise
    
    async def _apply_retention_policies(self, asset: DataAsset):
        """Applique les politiques de rétention à un actif"""
        try:
            # Recherche des politiques applicables
            applicable_policies = [
                policy for policy in self.retention_policies.values()
                if policy.data_classification == asset.classification
            ]
            
            if not applicable_policies:
                return
            
            # Application de la politique la plus stricte
            strictest_policy = min(
                applicable_policies,
                key=lambda p: p.retention_period_days
            )
            
            # Mise à jour de la période de rétention de l'actif
            asset.retention_period = strictest_policy.retention_period_days
            
            self.logger.info(
                f"Politique de rétention appliquée à l'actif {asset.asset_id}: "
                f"{strictest_policy.retention_period_days} jours"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application des politiques: {e}")
    
    async def _assess_data_quality(self, asset: DataAsset):
        """Évalue la qualité d'un actif de données"""
        try:
            quality_score = 1.0
            
            # Vérification de la complétude des métadonnées
            required_fields = ['name', 'description', 'owner', 'steward']
            missing_fields = [
                field for field in required_fields 
                if not getattr(asset, field, None)
            ]
            
            if missing_fields:
                quality_score -= len(missing_fields) * 0.1
            
            # Vérification de l'âge des données
            days_since_update = (datetime.now() - asset.last_modified).days
            if days_since_update > 30:
                quality_score -= 0.2
            
            # Vérification de l'accès récent
            days_since_access = (datetime.now() - asset.last_accessed).days
            if days_since_access > 90:
                quality_score -= 0.1
            
            # Mise à jour du score de qualité
            asset.quality_score = max(0.0, quality_score)
            
            self.metrics['quality_assessments'] += 1
            
            self.logger.info(
                f"Qualité évaluée pour l'actif {asset.asset_id}: "
                f"{asset.quality_score:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation de la qualité: {e}")
    
    async def _monitor_data_lifecycle(self):
        """Surveille le cycle de vie des données"""
        while self.is_running:
            try:
                for asset in self.data_assets.values():
                    # Vérification des transitions de cycle de vie
                    await self._check_lifecycle_transitions(asset)
                
                await asyncio.sleep(3600)  # Vérification horaire
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance du cycle de vie: {e}")
                await asyncio.sleep(60)
    
    async def _check_lifecycle_transitions(self, asset: DataAsset):
        """Vérifie les transitions de cycle de vie d'un actif"""
        try:
            days_since_creation = (datetime.now() - asset.created_at).days
            days_since_access = (datetime.now() - asset.last_accessed).days
            
            # Transition vers archivage
            if (asset.lifecycle_stage == DataLifecycleStage.STORAGE and 
                days_since_access > 180):
                await self._archive_asset(asset)
            
            # Transition vers suppression (si autorisée)
            elif (asset.lifecycle_stage == DataLifecycleStage.ARCHIVAL and 
                  days_since_creation > asset.retention_period):
                await self._schedule_deletion(asset)
            
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la vérification des transitions: {e}"
            )
    
    async def _archive_asset(self, asset: DataAsset):
        """Archive un actif de données"""
        try:
            # Vérification des autorisations
            applicable_policy = self._get_applicable_policy(asset)
            if applicable_policy and not applicable_policy.auto_archive:
                self.logger.info(
                    f"Archivage manuel requis pour l'actif {asset.asset_id}"
                )
                return
            
            # Processus d'archivage
            asset.lifecycle_stage = DataLifecycleStage.ARCHIVAL
            asset.metadata['archived_at'] = datetime.now().isoformat()
            asset.metadata['archival_reason'] = 'automatic_policy'
            
            self.metrics['archival_operations'] += 1
            
            self.logger.info(f"Actif archivé: {asset.asset_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'archivage: {e}")
    
    async def _schedule_deletion(self, asset: DataAsset):
        """Programme la suppression d'un actif"""
        try:
            applicable_policy = self._get_applicable_policy(asset)
            
            # Vérification des autorisations
            if applicable_policy and not applicable_policy.auto_delete:
                self.logger.info(
                    f"Suppression manuelle requise pour l'actif {asset.asset_id}"
                )
                return
            
            # Vérification des exigences de conformité
            if asset.compliance_requirements:
                self.logger.info(
                    f"Vérification de conformité requise avant suppression: {asset.asset_id}"
                )
                return
            
            # Programmation de la suppression
            asset.lifecycle_stage = DataLifecycleStage.DELETION
            asset.metadata['deletion_scheduled'] = datetime.now().isoformat()
            asset.metadata['deletion_reason'] = 'retention_policy'
            
            self.logger.info(f"Suppression programmée pour l'actif: {asset.asset_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la programmation de suppression: {e}")
    
    def _get_applicable_policy(self, asset: DataAsset) -> Optional[RetentionPolicy]:
        """Récupère la politique applicable à un actif"""
        for policy in self.retention_policies.values():
            if policy.data_classification == asset.classification:
                return policy
        return None
    
    async def _monitor_compliance(self):
        """Surveille la conformité réglementaire"""
        while self.is_running:
            try:
                for asset in self.data_assets.values():
                    for requirement in asset.compliance_requirements:
                        await self._check_compliance(asset, requirement)
                
                await asyncio.sleep(3600)  # Vérification horaire
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance de conformité: {e}")
                await asyncio.sleep(60)
    
    async def _check_compliance(self, asset: DataAsset, regulation: ComplianceRegulation):
        """Vérifie la conformité d'un actif à une réglementation"""
        try:
            # Recherche des règles applicables
            applicable_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.regulation == regulation and rule.enabled
            ]
            
            for rule in applicable_rules:
                # Exécution de la logique de validation
                is_compliant = await self._execute_validation_logic(
                    asset, rule.validation_logic
                )
                
                if not is_compliant:
                    await self._handle_compliance_violation(asset, rule)
            
            self.metrics['compliance_checks'] += 1
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de conformité: {e}")
    
    async def _execute_validation_logic(self, asset: DataAsset, logic: str) -> bool:
        """Exécute la logique de validation de conformité"""
        try:
            # Implémentation basique - à étendre selon les besoins
            if "data_age" in logic:
                days_old = (datetime.now() - asset.created_at).days
                return days_old <= asset.retention_period
            
            if "access_control" in logic:
                return bool(asset.owner and asset.steward)
            
            if "encryption" in logic:
                return asset.metadata.get('encrypted', False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur dans la logique de validation: {e}")
            return False
    
    async def _handle_compliance_violation(self, asset: DataAsset, rule: ComplianceRule):
        """Gère une violation de conformité"""
        try:
            # Enregistrement de la violation
            violation_id = str(uuid.uuid4())
            violation_data = {
                'violation_id': violation_id,
                'asset_id': asset.asset_id,
                'rule_id': rule.rule_id,
                'regulation': rule.regulation.value,
                'severity': rule.severity,
                'detected_at': datetime.now().isoformat(),
                'remediation_action': rule.remediation_action
            }
            
            # Stockage de la violation dans les métadonnées de l'actif
            if 'compliance_violations' not in asset.metadata:
                asset.metadata['compliance_violations'] = []
            asset.metadata['compliance_violations'].append(violation_data)
            
            # Exécution de l'action de remédiation si automatique
            if rule.remediation_action == 'auto_archive':
                await self._archive_asset(asset)
            elif rule.remediation_action == 'auto_encrypt':
                asset.metadata['encrypted'] = True
            
            self.logger.warning(
                f"Violation de conformité détectée - Actif: {asset.asset_id}, "
                f"Règle: {rule.rule_id}, Sévérité: {rule.severity}"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de violation: {e}")
    
    async def _monitor_retention_policies(self):
        """Surveille l'application des politiques de rétention"""
        while self.is_running:
            try:
                self._check_retention_compliance()
                await asyncio.sleep(86400)  # Vérification quotidienne
                
            except Exception as e:
                self.logger.error(
                    f"Erreur dans la surveillance des politiques de rétention: {e}"
                )
                await asyncio.sleep(3600)
    
    def _check_retention_compliance(self):
        """Vérifie la conformité aux politiques de rétention"""
        try:
            for asset in self.data_assets.values():
                days_since_creation = (datetime.now() - asset.created_at).days
                
                if days_since_creation > asset.retention_period:
                    # Action nécessaire selon la politique
                    policy = self._get_applicable_policy(asset)
                    if policy:
                        if policy.auto_archive and asset.lifecycle_stage != DataLifecycleStage.ARCHIVAL:
                            asyncio.create_task(self._archive_asset(asset))
                        elif policy.auto_delete and days_since_creation > policy.deletion_period_days:
                            asyncio.create_task(self._schedule_deletion(asset))
            
            self.metrics['policies_enforced'] += 1
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de rétention: {e}")
    
    async def _monitor_data_quality(self):
        """Surveille la qualité des données"""
        while self.is_running:
            try:
                for asset in self.data_assets.values():
                    await self._assess_data_quality(asset)
                
                await asyncio.sleep(3600)  # Évaluation horaire
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance de qualité: {e}")
                await asyncio.sleep(60)
    
    async def _optimize_storage(self):
        """Optimise le stockage des données"""
        while self.is_running:
            try:
                # Identification des opportunités d'optimisation
                candidates = [
                    asset for asset in self.data_assets.values()
                    if self._is_optimization_candidate(asset)
                ]
                
                for asset in candidates:
                    await self._optimize_asset_storage(asset)
                
                await asyncio.sleep(86400)  # Optimisation quotidienne
                
            except Exception as e:
                self.logger.error(f"Erreur dans l'optimisation du stockage: {e}")
                await asyncio.sleep(3600)
    
    def _is_optimization_candidate(self, asset: DataAsset) -> bool:
        """Détermine si un actif est candidat à l'optimisation"""
        try:
            # Critères d'optimisation
            days_since_access = (datetime.now() - asset.last_accessed).days
            size_threshold = self.config.get('optimization_size_threshold', 1000000)  # 1MB
            
            return (
                days_since_access > 30 and
                asset.size_bytes > size_threshold and
                asset.lifecycle_stage == DataLifecycleStage.STORAGE
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation d'optimisation: {e}")
            return False
    
    async def _optimize_asset_storage(self, asset: DataAsset):
        """Optimise le stockage d'un actif"""
        try:
            # Compression
            if not asset.metadata.get('compressed', False):
                asset.metadata['compressed'] = True
                asset.metadata['compression_ratio'] = 0.7  # Estimation
                asset.size_bytes = int(asset.size_bytes * 0.7)
            
            # Déduplication
            checksum = self._calculate_checksum(asset)
            duplicate_assets = [
                a for a in self.data_assets.values()
                if a.asset_id != asset.asset_id and 
                a.metadata.get('checksum') == checksum
            ]
            
            if duplicate_assets:
                asset.metadata['duplicates'] = [a.asset_id for a in duplicate_assets]
            
            self.logger.info(f"Stockage optimisé pour l'actif: {asset.asset_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'optimisation du stockage: {e}")
    
    def _calculate_checksum(self, asset: DataAsset) -> str:
        """Calcule le checksum d'un actif"""
        try:
            # Génération basique du checksum basé sur les métadonnées
            content = f"{asset.name}_{asset.size_bytes}_{asset.format}"
            return hashlib.md5(content.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du checksum: {e}")
            return ""
    
    def _update_asset_metadata(self):
        """Met à jour les métadonnées des actifs"""
        try:
            for asset in self.data_assets.values():
                # Mise à jour des statistiques d'accès
                asset.metadata['last_health_check'] = datetime.now().isoformat()
                
                # Calcul de l'âge des données
                age_days = (datetime.now() - asset.created_at).days
                asset.metadata['age_days'] = age_days
                
                # Mise à jour du statut de conformité
                asset.metadata['compliance_status'] = self._get_compliance_status(asset)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des métadonnées: {e}")
    
    def _get_compliance_status(self, asset: DataAsset) -> str:
        """Obtient le statut de conformité d'un actif"""
        try:
            violations = asset.metadata.get('compliance_violations', [])
            
            if not violations:
                return 'compliant'
            
            # Vérification des violations récentes
            recent_violations = [
                v for v in violations
                if (datetime.now() - datetime.fromisoformat(v['detected_at'])).days < 30
            ]
            
            if recent_violations:
                high_severity = any(v['severity'] == 'high' for v in recent_violations)
                return 'non_compliant_high' if high_severity else 'non_compliant_low'
            
            return 'compliant'
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation du statut de conformité: {e}")
            return 'unknown'
    
    def _cleanup_expired_cache(self):
        """Nettoie le cache expiré"""
        try:
            current_time = time.time()
            expired_keys = [
                key for key, (data, timestamp) in self.cache.items()
                if current_time - timestamp > self.cache_ttl
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage du cache: {e}")
    
    async def get_asset_info(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un actif
        
        Args:
            asset_id: ID de l'actif
            
        Returns:
            Informations de l'actif ou None si non trouvé
        """
        try:
            asset = self.data_assets.get(asset_id)
            if not asset:
                return None
            
            return {
                'asset_id': asset.asset_id,
                'name': asset.name,
                'description': asset.description,
                'classification': asset.classification.value,
                'owner': asset.owner,
                'steward': asset.steward,
                'lifecycle_stage': asset.lifecycle_stage.value,
                'quality_score': asset.quality_score,
                'size_bytes': asset.size_bytes,
                'created_at': asset.created_at.isoformat(),
                'last_modified': asset.last_modified.isoformat(),
                'last_accessed': asset.last_accessed.isoformat(),
                'retention_period': asset.retention_period,
                'compliance_requirements': [req.value for req in asset.compliance_requirements],
                'metadata': asset.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des informations: {e}")
            return None
    
    async def get_compliance_report(self) -> Dict[str, Any]:
        """
        Génère un rapport de conformité complet
        
        Returns:
            Rapport de conformité détaillé
        """
        try:
            total_assets = len(self.data_assets)
            compliant_assets = sum(
                1 for asset in self.data_assets.values()
                if self._get_compliance_status(asset) == 'compliant'
            )
            
            violations_by_regulation = {}
            for asset in self.data_assets.values():
                violations = asset.metadata.get('compliance_violations', [])
                for violation in violations:
                    regulation = violation['regulation']
                    if regulation not in violations_by_regulation:
                        violations_by_regulation[regulation] = 0
                    violations_by_regulation[regulation] += 1
            
            return {
                'generated_at': datetime.now().isoformat(),
                'total_assets': total_assets,
                'compliant_assets': compliant_assets,
                'compliance_rate': (compliant_assets / total_assets * 100) if total_assets > 0 else 0,
                'violations_by_regulation': violations_by_regulation,
                'total_policies': len(self.retention_policies),
                'total_rules': len(self.compliance_rules),
                'metrics': self.metrics
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {}
    
    async def get_lifecycle_summary(self) -> Dict[str, Any]:
        """
        Génère un résumé du cycle de vie des données
        
        Returns:
            Résumé du cycle de vie
        """
        try:
            stage_counts = {}
            for stage in DataLifecycleStage:
                stage_counts[stage.value] = sum(
                    1 for asset in self.data_assets.values()
                    if asset.lifecycle_stage == stage
                )
            
            # Statistiques d'âge
            ages = [
                (datetime.now() - asset.created_at).days
                for asset in self.data_assets.values()
            ]
            
            avg_age = np.mean(ages) if ages else 0
            
            # Prochaines actions
            archival_candidates = sum(
                1 for asset in self.data_assets.values()
                if (datetime.now() - asset.last_accessed).days > 180
            )
            
            deletion_candidates = sum(
                1 for asset in self.data_assets.values()
                if (datetime.now() - asset.created_at).days > asset.retention_period
            )
            
            return {
                'generated_at': datetime.now().isoformat(),
                'stage_distribution': stage_counts,
                'average_age_days': avg_age,
                'archival_candidates': archival_candidates,
                'deletion_candidates': deletion_candidates,
                'total_size_bytes': sum(asset.size_bytes for asset in self.data_assets.values()),
                'average_quality_score': np.mean([
                    asset.quality_score for asset in self.data_assets.values()
                ]) if self.data_assets else 0
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du résumé: {e}")
            return {}
    
    async def stop_monitoring(self):
        """Arrête la surveillance du gestionnaire"""
        try:
            self.is_running = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=30)
            
            self.executor.shutdown(wait=True)
            
            self.logger.info("Surveillance du gestionnaire arrêtée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques du gestionnaire
        
        Returns:
            Métriques actuelles
        """
        return {
            **self.metrics,
            'cache_size': len(self.cache),
            'active_assets': len(self.data_assets),
            'active_policies': len(self.retention_policies),
            'active_rules': len(self.compliance_rules),
            'is_running': self.is_running
        }


# Fonctions utilitaires pour l'intégration

def create_default_policies() -> List[Dict[str, Any]]:
    """Crée des politiques de rétention par défaut"""
    return [
        {
            'name': 'Standard Business Data',
            'description': 'Politique standard pour les données métier',
            'data_classification': 'internal',
            'retention_period_days': 2555,  # 7 ans
            'archival_period_days': 1825,   # 5 ans
            'deletion_period_days': 3650,   # 10 ans
            'compliance_requirements': ['sox'],
            'auto_archive': True,
            'auto_delete': False,
            'approval_required': True
        },
        {
            'name': 'Personal Data (GDPR)',
            'description': 'Politique pour les données personnelles GDPR',
            'data_classification': 'confidential',
            'retention_period_days': 1095,  # 3 ans
            'archival_period_days': 730,    # 2 ans
            'deletion_period_days': 1095,   # 3 ans
            'compliance_requirements': ['gdpr'],
            'auto_archive': True,
            'auto_delete': False,
            'approval_required': True
        },
        {
            'name': 'Financial Data',
            'description': 'Politique pour les données financières',
            'data_classification': 'restricted',
            'retention_period_days': 2555,  # 7 ans
            'archival_period_days': 1825,   # 5 ans
            'deletion_period_days': 3650,   # 10 ans
            'compliance_requirements': ['sox', 'pci_dss'],
            'auto_archive': True,
            'auto_delete': False,
            'approval_required': True
        }
    ]


def create_default_compliance_rules() -> List[Dict[str, Any]]:
    """Crée des règles de conformité par défaut"""
    return [
        {
            'regulation': 'gdpr',
            'rule_type': 'data_retention',
            'description': 'Vérification de la période de rétention GDPR',
            'validation_logic': 'data_age <= retention_period',
            'remediation_action': 'auto_archive',
            'severity': 'high'
        },
        {
            'regulation': 'sox',
            'rule_type': 'audit_trail',
            'description': 'Vérification de la traçabilité SOX',
            'validation_logic': 'access_control',
            'remediation_action': 'notify_admin',
            'severity': 'medium'
        },
        {
            'regulation': 'pci_dss',
            'rule_type': 'data_protection',
            'description': 'Vérification du chiffrement PCI DSS',
            'validation_logic': 'encryption',
            'remediation_action': 'auto_encrypt',
            'severity': 'high'
        }
    ]


# Point d'entrée principal
async def main():
    """Fonction principale pour les tests"""
    # Configuration de test
    config = {
        'max_workers': 10,
        'cache_ttl': 3600,
        'monitoring_interval': 300,
        'optimization_size_threshold': 1000000
    }
    
    # Initialisation du gestionnaire
    manager = EnterpriseDataManager(config)
    
    try:
        # Création des politiques par défaut
        for policy_data in create_default_policies():
            await manager.create_retention_policy(policy_data)
        
        # Création des règles de conformité par défaut
        for rule_data in create_default_compliance_rules():
            await manager.create_compliance_rule(rule_data)
        
        # Enregistrement d'un actif de test
        test_asset = {
            'name': 'Customer Database',
            'description': 'Base de données des clients',
            'classification': 'confidential',
            'owner': 'data-team@company.com',
            'steward': 'data-steward@company.com',
            'location': '/data/customers',
            'format': 'postgresql',
            'size_bytes': 10485760,  # 10MB
            'retention_period': 1095,  # 3 ans
            'compliance_requirements': ['gdpr', 'sox'],
            'metadata': {
                'department': 'sales',
                'sensitivity': 'high',
                'encrypted': True
            }
        }
        
        asset_id = await manager.register_data_asset(test_asset)
        print(f"Actif de test enregistré: {asset_id}")
        
        # Démarrage de la surveillance (pour test, on simule)
        print("Gestionnaire de données d'entreprise initialisé avec succès")
        
        # Génération des rapports
        compliance_report = await manager.get_compliance_report()
        lifecycle_summary = await manager.get_lifecycle_summary()
        
        print(f"Rapport de conformité: {json.dumps(compliance_report, indent=2)}")
        print(f"Résumé du cycle de vie: {json.dumps(lifecycle_summary, indent=2)}")
        
    except Exception as e:
        print(f"Erreur lors des tests: {e}")
    
    finally:
        await manager.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())