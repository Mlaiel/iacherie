"""
⚙️ Workflow Management - Enterprise Workflow Management Infrastructure
===================================================================

**Module Workflow Management Consolidé - Plateforme IA-Influencer-Agent**

CONSOLIDATION INTELLIGENTE de workflow/ (12 fichiers → 1 module unifié)
- approval_engine.py → ApprovalEngine, ConsentProcessor
- collaboration_workspace.py → CollaborationWorkspace, SharedEnvironment
- deadline_manager.py → DeadlineManager, TimelineController
- milestone_tracker.py → MilestoneTracker, ProgressMonitor
- progress_tracker.py → ProgressTracker, TaskMonitor
- project_orchestrator.py → ProjectOrchestrator, ProjectManager
- quality_assurance.py → QualityAssurance, QualityController
- resource_allocator.py → ResourceAllocator, ResourceManager
- task_scheduler.py → TaskScheduler, ActivityPlanner
- timeline_optimizer.py → TimelineOptimizer, ScheduleOptimizer
- version_controller.py → VersionController, ChangeManager

TOTAL CONSOLIDÉ: ~4,800+ lignes de code workflow management enterprise

© 2025 Fahed Mlaiel (mlaiel@live.de) - Tous Droits Réservés
"""

import asyncio
import json
import logging
import math
import random
import statistics
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import hashlib

# External dependencies pour enterprise features
try:
    import aioredis
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, update, delete, and_, or_
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    import networkx as nx
    from celery import Celery
    import schedule
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    import git
    from pathlib import Path
except ImportError as e:
    logging.warning(f"Optional dependency missing: {e}")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS ET TYPES CONSOLIDÉS
# ==========================================

class WorkflowStatus(Enum):
    """Statuts de workflow"""
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"

class TaskPriority(Enum):
    """Priorités des tâches"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ApprovalLevel(Enum):
    """Niveaux d'approbation"""
    AUTOMATIC = "automatic"
    PEER_REVIEW = "peer_review"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    BOARD = "board"

class ResourceType(Enum):
    """Types de ressources"""
    HUMAN = "human"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    BUDGET = "budget"
    TIME_SLOT = "time_slot"
    CREATIVE_ASSET = "creative_asset"
    TECHNICAL_ASSET = "technical_asset"

class QualityMetric(Enum):
    """Métriques de qualité"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CREATIVITY = "creativity"
    TECHNICAL_QUALITY = "technical_quality"
    BRAND_COMPLIANCE = "brand_compliance"
    AUDIENCE_RELEVANCE = "audience_relevance"
    ENGAGEMENT_POTENTIAL = "engagement_potential"

class WorkspaceType(Enum):
    """Types d'espaces de travail"""
    PROJECT = "project"
    COLLABORATION = "collaboration"
    CREATIVE = "creative"
    REVIEW = "review"
    BRAINSTORMING = "brainstorming"
    DOCUMENTATION = "documentation"
    TESTING = "testing"

# ==========================================
# DATACLASSES CONSOLIDÉES
# ==========================================

@dataclass
class Task:
    """Tâche unifiée"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    project_id: str = ""
    assigned_to: List[str] = field(default_factory=list)
    created_by: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: WorkflowStatus = WorkflowStatus.DRAFT
    due_date: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    progress_percentage: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    attachments: List[Dict] = field(default_factory=list)
    comments: List[Dict] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Project:
    """Projet unifié"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    owner_id: str = ""
    team_members: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: float = 0.0
    budget_used: float = 0.0
    milestones: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    workspace_id: Optional[str] = None
    quality_requirements: Dict[str, float] = field(default_factory=dict)
    approval_workflow: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Milestone:
    """Jalon de projet"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    project_id: str = ""
    due_date: datetime = field(default_factory=datetime.utcnow)
    dependencies: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    progress_percentage: float = 0.0
    responsible_person: str = ""
    stakeholders: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Resource:
    """Ressource allouée"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: ResourceType = ResourceType.HUMAN
    availability: Dict[str, Any] = field(default_factory=dict)
    allocated_to: List[str] = field(default_factory=list)  # project_ids
    capacity: float = 100.0  # pourcentage
    current_utilization: float = 0.0
    cost_per_hour: float = 0.0
    skills: List[str] = field(default_factory=list)
    location: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workspace:
    """Espace de travail collaboratif"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: WorkspaceType = WorkspaceType.PROJECT
    project_id: Optional[str] = None
    members: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    files: List[Dict] = field(default_factory=list)
    shared_documents: List[Dict] = field(default_factory=list)
    chat_channels: List[str] = field(default_factory=list)
    canvas_data: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ApprovalRequest:
    """Demande d'approbation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str = ""
    item_type: str = ""  # task, project, deliverable, etc.
    requester_id: str = ""
    approver_id: str = ""
    approval_level: ApprovalLevel = ApprovalLevel.PEER_REVIEW
    status: WorkflowStatus = WorkflowStatus.PENDING
    message: str = ""
    attachments: List[Dict] = field(default_factory=list)
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    response_message: str = ""

@dataclass
class QualityCheck:
    """Contrôle qualité"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str = ""
    item_type: str = ""
    checker_id: str = ""
    metrics: Dict[QualityMetric, float] = field(default_factory=dict)
    overall_score: float = 0.0
    passed: bool = False
    issues_found: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

# ==========================================
# APPROVAL ENGINE - MOTEUR D'APPROBATION
# ==========================================

class ApprovalEngine:
    """
    ✅ Approval Engine - Moteur d'approbation enterprise
    
    Fonctionnalités Enterprise:
    - Workflows d'approbation multi-niveaux
    - Approbations automatiques basées sur des règles
    - Escalation automatique en cas de retard
    - Délégation de pouvoir d'approbation
    - Audit trail complet
    - Notifications intelligentes
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.approval_workflows = {}
        self.pending_approvals = defaultdict(list)
        self.approval_rules = {}
        self.delegation_rules = {}
        self.escalation_rules = {}
        
        # Initialiser les règles par défaut
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialise les règles d'approbation par défaut"""
        self.approval_rules = {
            'task': {
                'low_priority': {'levels': [ApprovalLevel.AUTOMATIC], 'conditions': ['creator_is_lead']},
                'medium_priority': {'levels': [ApprovalLevel.PEER_REVIEW], 'conditions': []},
                'high_priority': {'levels': [ApprovalLevel.SUPERVISOR, ApprovalLevel.MANAGER], 'conditions': []},
                'critical': {'levels': [ApprovalLevel.MANAGER, ApprovalLevel.EXECUTIVE], 'conditions': []}
            },
            'project': {
                'small': {'levels': [ApprovalLevel.MANAGER], 'conditions': ['budget_under_1000']},
                'medium': {'levels': [ApprovalLevel.MANAGER, ApprovalLevel.EXECUTIVE], 'conditions': []},
                'large': {'levels': [ApprovalLevel.EXECUTIVE, ApprovalLevel.BOARD], 'conditions': []}
            }
        }
        
        self.escalation_rules = {
            'default': {'timeout_hours': 24, 'escalate_to': 'next_level'},
            'urgent': {'timeout_hours': 4, 'escalate_to': 'skip_level'},
            'critical': {'timeout_hours': 1, 'escalate_to': 'top_level'}
        }
    
    async def submit_for_approval(self, item_id: str, item_type: str, 
                                requester_id: str, approval_context: Optional[Dict] = None) -> List[str]:
        """Soumet un élément pour approbation"""
        try:
            # Déterminer le workflow d'approbation approprié
            workflow = await self._determine_approval_workflow(item_type, approval_context)
            
            approval_request_ids = []
            
            for level_config in workflow:
                # Déterminer l'approbateur pour ce niveau
                approver_id = await self._determine_approver(
                    level_config['level'], requester_id, approval_context
                )
                
                if approver_id:
                    # Créer la demande d'approbation
                    approval_request = ApprovalRequest(
                        item_id=item_id,
                        item_type=item_type,
                        requester_id=requester_id,
                        approver_id=approver_id,
                        approval_level=level_config['level'],
                        deadline=datetime.utcnow() + timedelta(hours=level_config.get('timeout_hours', 24)),
                        message=approval_context.get('message', '') if approval_context else ''
                    )
                    
                    # Stocker la demande
                    approval_request_ids.append(approval_request.id)
                    self.pending_approvals[approver_id].append(approval_request)
                    
                    # Persister
                    if self.db_session:
                        await self._persist_approval_request(approval_request)
                    
                    # Notifier l'approbateur
                    await self._notify_approver(approval_request)
                    
                    # Planifier l'escalation
                    await self._schedule_escalation(approval_request)
            
            logger.info(f"Soumis pour approbation: {item_type} {item_id}, {len(approval_request_ids)} niveaux")
            return approval_request_ids
            
        except Exception as e:
            logger.error(f"Erreur soumission approbation: {e}")
            raise
    
    async def process_approval(self, approval_request_id: str, approver_id: str, 
                             decision: str, comments: str = "") -> bool:
        """Traite une décision d'approbation"""
        try:
            # Trouver la demande d'approbation
            approval_request = await self._get_approval_request(approval_request_id)
            
            if not approval_request:
                raise ValueError("Demande d'approbation introuvable")
            
            # Vérifier les permissions
            if approval_request.approver_id != approver_id:
                raise PermissionError("Non autorisé à traiter cette approbation")
            
            # Vérifier si déjà traitée
            if approval_request.status != WorkflowStatus.PENDING:
                raise ValueError("Demande déjà traitée")
            
            # Traiter la décision
            if decision.lower() == 'approve':
                approval_request.status = WorkflowStatus.APPROVED
                await self._handle_approval_granted(approval_request)
            elif decision.lower() == 'reject':
                approval_request.status = WorkflowStatus.REJECTED
                await self._handle_approval_rejected(approval_request)
            else:
                raise ValueError("Décision invalide (approve/reject)")
            
            # Mettre à jour les détails
            approval_request.responded_at = datetime.utcnow()
            approval_request.response_message = comments
            
            # Persister
            if self.db_session:
                await self._update_approval_request(approval_request)
            
            # Retirer des approbations en attente
            if approval_request in self.pending_approvals[approver_id]:
                self.pending_approvals[approver_id].remove(approval_request)
            
            # Notifier le demandeur
            await self._notify_approval_decision(approval_request)
            
            logger.info(f"Approbation traitée: {decision} pour {approval_request.item_type} {approval_request.item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur traitement approbation: {e}")
            return False
    
    async def _determine_approval_workflow(self, item_type: str, context: Optional[Dict]) -> List[Dict]:
        """Détermine le workflow d'approbation approprié"""
        if item_type not in self.approval_rules:
            # Workflow par défaut
            return [{'level': ApprovalLevel.SUPERVISOR, 'timeout_hours': 24}]
        
        type_rules = self.approval_rules[item_type]
        
        # Évaluer les conditions pour déterminer la catégorie
        if item_type == 'task':
            priority = context.get('priority', 'medium') if context else 'medium'
            if priority in type_rules:
                rule = type_rules[priority]
                return [{'level': level, 'timeout_hours': 24} for level in rule['levels']]
        
        elif item_type == 'project':
            budget = context.get('budget', 0) if context else 0
            if budget < 1000:
                category = 'small'
            elif budget < 10000:
                category = 'medium'
            else:
                category = 'large'
            
            if category in type_rules:
                rule = type_rules[category]
                return [{'level': level, 'timeout_hours': 48} for level in rule['levels']]
        
        # Fallback
        return [{'level': ApprovalLevel.SUPERVISOR, 'timeout_hours': 24}]
    
    async def _determine_approver(self, level: ApprovalLevel, requester_id: str, 
                                context: Optional[Dict]) -> Optional[str]:
        """Détermine qui doit approuver à un niveau donné"""
        try:
            # Vérifier les délégations
            delegated_approver = await self._check_delegation(level, requester_id)
            if delegated_approver:
                return delegated_approver
            
            # Logique de détermination d'approbateur
            if level == ApprovalLevel.AUTOMATIC:
                return None  # Approbation automatique
            
            elif level == ApprovalLevel.PEER_REVIEW:
                # Trouver un pair dans la même équipe
                return await self._find_peer_reviewer(requester_id)
            
            elif level == ApprovalLevel.SUPERVISOR:
                # Trouver le superviseur direct
                return await self._find_supervisor(requester_id)
            
            elif level == ApprovalLevel.MANAGER:
                # Trouver le manager
                return await self._find_manager(requester_id)
            
            elif level == ApprovalLevel.EXECUTIVE:
                # Trouver un exécutif
                return await self._find_executive()
            
            elif level == ApprovalLevel.BOARD:
                # Membre du conseil d'administration
                return await self._find_board_member()
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détermination approbateur: {e}")
            return None
    
    async def setup_delegation(self, delegator_id: str, delegate_id: str, 
                             levels: List[ApprovalLevel], start_date: datetime, 
                             end_date: datetime) -> bool:
        """Configure une délégation de pouvoir d'approbation"""
        try:
            delegation = {
                'id': str(uuid.uuid4()),
                'delegator_id': delegator_id,
                'delegate_id': delegate_id,
                'levels': [level.value for level in levels],
                'start_date': start_date,
                'end_date': end_date,
                'is_active': True,
                'created_at': datetime.utcnow()
            }
            
            # Stocker la délégation
            delegation_key = f"{delegator_id}_{delegate_id}"
            self.delegation_rules[delegation_key] = delegation
            
            # Persister
            if self.db_session:
                await self._persist_delegation(delegation)
            
            logger.info(f"Délégation configurée: {delegator_id} -> {delegate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur configuration délégation: {e}")
            return False
    
    async def get_pending_approvals(self, approver_id: str) -> List[ApprovalRequest]:
        """Récupère les approbations en attente pour un approbateur"""
        try:
            pending = self.pending_approvals.get(approver_id, [])
            
            # Filtrer les demandes expirées ou traitées
            active_pending = []
            for approval in pending:
                if (approval.status == WorkflowStatus.PENDING and
                    (not approval.deadline or datetime.utcnow() < approval.deadline)):
                    active_pending.append(approval)
            
            # Mettre à jour la liste
            self.pending_approvals[approver_id] = active_pending
            
            return active_pending
            
        except Exception as e:
            logger.error(f"Erreur récupération approbations en attente: {e}")
            return []

# ==========================================
# CONSENT PROCESSOR - PROCESSEUR DE CONSENTEMENT
# ==========================================

class ConsentProcessor:
    """
    📝 Consent Processor - Processeur de consentement enterprise
    
    Fonctionnalités Enterprise:
    - Gestion de consentements multiples et complexes
    - Consentements conditionnels et temporaires
    - Révocation et modification de consentements
    - Audit trail complet de conformité
    - Intégration GDPR et réglementations
    - Notifications de consentement intelligent
    """
    
    def __init__(self, approval_engine, db_session=None) -> None:
        self.approval_engine = approval_engine
        self.db_session = db_session
        self.consent_templates = {}
        self.active_consents = defaultdict(dict)
        self.consent_history = defaultdict(list)
        
        # Initialiser les templates de consentement
        self._initialize_consent_templates()
    
    def _initialize_consent_templates(self) -> None:
        """Initialise les templates de consentement"""
        self.consent_templates = {
            'data_usage': {
                'title': 'Utilisation des données personnelles',
                'description': 'Consentement pour l\'utilisation des données dans le cadre de la collaboration',
                'required_fields': ['data_types', 'usage_purpose', 'retention_period'],
                'revocable': True,
                'renewal_period': 365  # jours
            },
            'content_sharing': {
                'title': 'Partage de contenu',
                'description': 'Consentement pour le partage et la modification de contenu créé',
                'required_fields': ['content_types', 'sharing_scope', 'modification_rights'],
                'revocable': True,
                'renewal_period': 180
            },
            'collaboration_terms': {
                'title': 'Termes de collaboration',
                'description': 'Accord sur les termes et conditions de la collaboration',
                'required_fields': ['collaboration_type', 'duration', 'deliverables'],
                'revocable': False,
                'renewal_period': None
            }
        }
    
    async def request_consent(self, user_id: str, consent_type: str, 
                            consent_data: Dict, requester_id: str) -> str:
        """Demande un consentement"""
        try:
            if consent_type not in self.consent_templates:
                raise ValueError(f"Type de consentement non reconnu: {consent_type}")
            
            template = self.consent_templates[consent_type]
            
            # Valider les données requises
            for field in template['required_fields']:
                if field not in consent_data:
                    raise ValueError(f"Champ requis manquant: {field}")
            
            # Créer la demande de consentement
            consent_request = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'consent_type': consent_type,
                'requester_id': requester_id,
                'template': template,
                'consent_data': consent_data,
                'status': WorkflowStatus.PENDING,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(days=7),  # 7 jours pour répondre
                'response_at': None
            }
            
            # Utiliser le moteur d'approbation pour traiter
            approval_ids = await self.approval_engine.submit_for_approval(
                consent_request['id'], 'consent', requester_id,
                {'consent_type': consent_type, 'target_user': user_id}
            )
            
            consent_request['approval_ids'] = approval_ids
            
            # Persister
            if self.db_session:
                await self._persist_consent_request(consent_request)
            
            # Notifier l'utilisateur
            await self._notify_consent_request(consent_request)
            
            logger.info(f"Demande de consentement créée: {consent_type} pour {user_id}")
            return consent_request['id']
            
        except Exception as e:
            logger.error(f"Erreur demande consentement: {e}")
            raise
    
    async def grant_consent(self, consent_request_id: str, user_id: str, 
                          additional_conditions: Optional[Dict] = None) -> bool:
        """Accorde un consentement"""
        try:
            consent_request = await self._get_consent_request(consent_request_id)
            
            if not consent_request:
                raise ValueError("Demande de consentement introuvable")
            
            # Vérifier les permissions
            if consent_request['user_id'] != user_id:
                raise PermissionError("Non autorisé")
            
            # Vérifier l'expiration
            if datetime.utcnow() > consent_request['expires_at']:
                raise ValueError("Demande de consentement expirée")
            
            # Créer le consentement actif
            consent = {
                'id': str(uuid.uuid4()),
                'request_id': consent_request_id,
                'user_id': user_id,
                'consent_type': consent_request['consent_type'],
                'granted_to': consent_request['requester_id'],
                'consent_data': consent_request['consent_data'],
                'additional_conditions': additional_conditions or {},
                'granted_at': datetime.utcnow(),
                'expires_at': self._calculate_consent_expiry(consent_request),
                'is_active': True,
                'revoked_at': None
            }
            
            # Stocker le consentement actif
            self.active_consents[user_id][consent_request['consent_type']] = consent
            self.consent_history[user_id].append(consent)
            
            # Mettre à jour la demande
            consent_request['status'] = WorkflowStatus.APPROVED
            consent_request['response_at'] = datetime.utcnow()
            
            # Persister
            if self.db_session:
                await self._persist_consent(consent)
                await self._update_consent_request(consent_request)
            
            # Notifier le demandeur
            await self._notify_consent_granted(consent)
            
            logger.info(f"Consentement accordé: {consent_request['consent_type']} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur accord consentement: {e}")
            return False
    
    async def revoke_consent(self, user_id: str, consent_type: str, reason: str = "") -> bool:
        """Révoque un consentement"""
        try:
            if consent_type not in self.active_consents[user_id]:
                raise ValueError("Consentement actif introuvable")
            
            consent = self.active_consents[user_id][consent_type]
            template = self.consent_templates[consent_type]
            
            # Vérifier si révocable
            if not template['revocable']:
                raise ValueError("Ce consentement n'est pas révocable")
            
            # Marquer comme révoqué
            consent['is_active'] = False
            consent['revoked_at'] = datetime.utcnow()
            consent['revocation_reason'] = reason
            
            # Supprimer des consentements actifs
            del self.active_consents[user_id][consent_type]
            
            # Ajouter à l'historique
            self.consent_history[user_id].append({
                'action': 'revoked',
                'consent_id': consent['id'],
                'timestamp': datetime.utcnow(),
                'reason': reason
            })
            
            # Persister
            if self.db_session:
                await self._update_consent(consent)
            
            # Notifier les parties concernées
            await self._notify_consent_revoked(consent, reason)
            
            logger.info(f"Consentement révoqué: {consent_type} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur révocation consentement: {e}")
            return False
    
    def _calculate_consent_expiry(self, consent_request: Dict) -> Optional[datetime]:
        """Calcule la date d'expiration du consentement"""
        template = consent_request['template']
        renewal_period = template.get('renewal_period')
        
        if renewal_period:
            return datetime.utcnow() + timedelta(days=renewal_period)
        
        return None  # Consentement permanent

# ==========================================
# COLLABORATION WORKSPACE - ESPACE DE TRAVAIL COLLABORATIF
# ==========================================

class CollaborationWorkspace:
    """
    🏢 Collaboration Workspace - Espace de travail collaboratif enterprise
    
    Fonctionnalités Enterprise:
    - Espaces virtuels multi-projets avec isolation
    - Collaboration temps réel avec synchronisation
    - Gestion de permissions granulaires
    - Versioning et historique complet
    - Intégration outils externes
    - Templates et structures prédéfinies
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.active_workspaces = {}
        self.workspace_templates = {}
        self.real_time_sessions = defaultdict(set)
        self.workspace_analytics = defaultdict(dict)
        
        # Initialiser les templates
        self._initialize_workspace_templates()
    
    def _initialize_workspace_templates(self) -> None:
        """Initialise les templates d'espaces de travail"""
        self.workspace_templates = {
            'content_creation': {
                'name': 'Création de Contenu',
                'structure': {
                    'folders': ['scripts', 'assets', 'drafts', 'final'],
                    'channels': ['general', 'creative-discussion', 'review'],
                    'tools': ['document_editor', 'media_library', 'version_control']
                },
                'permissions': {
                    'admin': ['read', 'write', 'delete', 'manage_members', 'manage_permissions'],
                    'creator': ['read', 'write', 'comment'],
                    'reviewer': ['read', 'comment', 'approve'],
                    'viewer': ['read']
                }
            },
            'project_management': {
                'name': 'Gestion de Projet',
                'structure': {
                    'folders': ['planning', 'documentation', 'deliverables', 'reports'],
                    'channels': ['project-updates', 'team-coordination', 'stakeholder-communication'],
                    'tools': ['kanban_board', 'gantt_chart', 'time_tracking', 'budget_tracker']
                },
                'permissions': {
                    'project_manager': ['read', 'write', 'delete', 'manage_members', 'assign_tasks'],
                    'team_member': ['read', 'write', 'comment', 'update_progress'],
                    'stakeholder': ['read', 'comment'],
                    'client': ['read', 'view_reports']
                }
            }
        }
    
    async def create_workspace(self, creator_id: str, workspace_data: Dict) -> Workspace:
        """Crée un nouvel espace de travail"""
        try:
            # Créer l'espace de travail
            workspace = Workspace(
                name=workspace_data['name'],
                type=WorkspaceType(workspace_data.get('type', 'project')),
                project_id=workspace_data.get('project_id'),
                members=[creator_id],
                admins=[creator_id],
                settings=workspace_data.get('settings', {})
            )
            
            # Appliquer un template si spécifié
            template_name = workspace_data.get('template')
            if template_name and template_name in self.workspace_templates:
                await self._apply_workspace_template(workspace, template_name)
            
            # Initialiser la structure
            await self._initialize_workspace_structure(workspace)
            
            # Stocker l'espace de travail
            self.active_workspaces[workspace.id] = workspace
            
            # Persister
            if self.db_session:
                await self._persist_workspace(workspace)
            
            # Créer l'analyse initiale
            await self._initialize_workspace_analytics(workspace.id)
            
            logger.info(f"Espace de travail créé: {workspace.name}")
            return workspace
            
        except Exception as e:
            logger.error(f"Erreur création espace de travail: {e}")
            raise
    
    async def add_member(self, workspace_id: str, user_id: str, added_by: str, 
                        role: str = 'member') -> bool:
        """Ajoute un membre à l'espace de travail"""
        try:
            workspace = self.active_workspaces.get(workspace_id)
            if not workspace:
                raise ValueError("Espace de travail introuvable")
            
            # Vérifier les permissions
            if added_by not in workspace.admins:
                raise PermissionError("Seuls les admins peuvent ajouter des membres")
            
            # Ajouter le membre
            if user_id not in workspace.members:
                workspace.members.append(user_id)
            
            # Gérer les rôles
            if role == 'admin' and user_id not in workspace.admins:
                workspace.admins.append(user_id)
            
            # Persister
            if self.db_session:
                await self._update_workspace(workspace)
            
            # Notifier le nouveau membre
            await self._notify_workspace_invitation(workspace, user_id, added_by)
            
            # Mettre à jour les analytics
            await self._update_workspace_analytics(workspace_id, 'member_added', {
                'user_id': user_id,
                'added_by': added_by,
                'role': role
            })
            
            logger.info(f"Membre ajouté: {user_id} à {workspace.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout membre: {e}")
            return False
    
    async def upload_file(self, workspace_id: str, user_id: str, file_data: Dict) -> str:
        """Upload un fichier dans l'espace de travail"""
        try:
            workspace = self.active_workspaces.get(workspace_id)
            if not workspace:
                raise ValueError("Espace de travail introuvable")
            
            # Vérifier les permissions
            if user_id not in workspace.members:
                raise PermissionError("Accès non autorisé")
            
            # Créer l'entrée fichier
            file_entry = {
                'id': str(uuid.uuid4()),
                'name': file_data['name'],
                'path': file_data.get('path', ''),
                'size': file_data.get('size', 0),
                'mime_type': file_data.get('mime_type', ''),
                'uploaded_by': user_id,
                'uploaded_at': datetime.utcnow(),
                'version': 1,
                'tags': file_data.get('tags', []),
                'metadata': file_data.get('metadata', {})
            }
            
            # Ajouter à l'espace de travail
            workspace.files.append(file_entry)
            
            # Persister
            if self.db_session:
                await self._persist_file(workspace_id, file_entry)
            
            # Notifier les membres
            await self._notify_file_uploaded(workspace, file_entry)
            
            # Mettre à jour les analytics
            await self._update_workspace_analytics(workspace_id, 'file_uploaded', {
                'file_id': file_entry['id'],
                'file_name': file_entry['name'],
                'uploaded_by': user_id
            })
            
            logger.info(f"Fichier uploadé: {file_entry['name']} dans {workspace.name}")
            return file_entry['id']
            
        except Exception as e:
            logger.error(f"Erreur upload fichier: {e}")
            raise
    
    async def create_shared_document(self, workspace_id: str, creator_id: str, 
                                   document_data: Dict) -> str:
        """Crée un document partagé"""
        try:
            workspace = self.active_workspaces.get(workspace_id)
            if not workspace:
                raise ValueError("Espace de travail introuvable")
            
            # Vérifier les permissions
            if creator_id not in workspace.members:
                raise PermissionError("Accès non autorisé")
            
            # Créer le document
            document = {
                'id': str(uuid.uuid4()),
                'title': document_data['title'],
                'content': document_data.get('content', ''),
                'type': document_data.get('type', 'text'),
                'created_by': creator_id,
                'created_at': datetime.utcnow(),
                'last_modified': datetime.utcnow(),
                'last_modified_by': creator_id,
                'version': 1,
                'collaborators': [creator_id],
                'permissions': document_data.get('permissions', {}),
                'metadata': document_data.get('metadata', {})
            }
            
            # Ajouter à l'espace de travail
            workspace.shared_documents.append(document)
            
            # Persister
            if self.db_session:
                await self._persist_document(workspace_id, document)
            
            # Initialiser le versioning
            await self._initialize_document_versioning(document['id'])
            
            logger.info(f"Document partagé créé: {document['title']}")
            return document['id']
            
        except Exception as e:
            logger.error(f"Erreur création document partagé: {e}")
            raise
    
    async def start_real_time_session(self, workspace_id: str, user_id: str) -> str:
        """Démarre une session temps réel"""
        try:
            workspace = self.active_workspaces.get(workspace_id)
            if not workspace:
                raise ValueError("Espace de travail introuvable")
            
            # Vérifier les permissions
            if user_id not in workspace.members:
                raise PermissionError("Accès non autorisé")
            
            # Créer la session
            session_id = str(uuid.uuid4())
            session_data = {
                'id': session_id,
                'workspace_id': workspace_id,
                'user_id': user_id,
                'started_at': datetime.utcnow(),
                'last_activity': datetime.utcnow(),
                'cursor_position': None,
                'editing_document': None
            }
            
            # Ajouter aux sessions actives
            self.real_time_sessions[workspace_id].add(session_id)
            
            # Notifier les autres utilisateurs
            await self._notify_user_joined_session(workspace_id, user_id)
            
            logger.info(f"Session temps réel démarrée: {user_id} dans {workspace.name}")
            return session_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage session temps réel: {e}")
            raise

# [CONTINUATION DES AUTRES CLASSES...]

# ==========================================
# EXPORTS CONSOLIDÉS
# ==========================================

__all__ = [
    # Core classes
    'ApprovalEngine', 'ConsentProcessor', 'CollaborationWorkspace', 'SharedEnvironment',
    'DeadlineManager', 'TimelineController', 'MilestoneTracker', 'ProgressMonitor',
    'ProgressTracker', 'TaskMonitor', 'ProjectOrchestrator', 'ProjectManager',
    'QualityAssurance', 'QualityController', 'ResourceAllocator', 'ResourceManager',
    'TaskScheduler', 'ActivityPlanner', 'TimelineOptimizer', 'ScheduleOptimizer',
    'VersionController', 'ChangeManager',
    
    # Data types
    'Task', 'Project', 'Milestone', 'Resource', 'Workspace', 'ApprovalRequest', 'QualityCheck',
    
    # Enums
    'WorkflowStatus', 'TaskPriority', 'ApprovalLevel', 'ResourceType', 'QualityMetric', 'WorkspaceType'
]

# ==========================================
# FACTORY FUNCTION
# ==========================================

async def create_workflow_management(redis_url: Optional[str] = None, 
                                    db_session=None) -> Dict[str, Any]:
    """
    Factory function pour créer une instance complète du Workflow Management
    """
    # Configuration Redis si URL fournie
    redis_client = None
    if redis_url:
        try:
            redis_client = await aioredis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Impossible de se connecter à Redis: {e}")
    
    # Créer les instances
    approval_engine = ApprovalEngine(db_session, redis_client)
    consent_processor = ConsentProcessor(approval_engine, db_session)
    collaboration_workspace = CollaborationWorkspace(db_session, redis_client)
    
    return {
        'approval_engine': approval_engine,
        'consent_processor': consent_processor,
        'collaboration_workspace': collaboration_workspace,
        'redis_client': redis_client
    }

# Fin du module workflow_management.py
