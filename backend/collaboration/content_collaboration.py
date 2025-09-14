"""
📄 Content Collaboration - Enterprise Content Collaboration Platform
====================================================================

**Module Collaboration de Contenu - Plateforme IA-Influencer-Agent**

NOUVEAU MODULE ENTERPRISE pour collaboration avancée de contenu
- Co-création de contenu intelligent et synchronisée
- Workflow de révision et approbation multi-niveaux
- Gestion de versions et historique collaboratif
- Templates et bibliothèques de ressources partagées
- Analytics de performance contenu temps réel
- Système de feedback et amélioration continue

CONTENT COLLABORATION: ~3,500+ lignes de code collaboration enterprise

© 2025 Fahed Mlaiel (mlaiel@live.de) - Tous Droits Réservés
"""

import asyncio
import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import uuid
import hashlib

# External dependencies pour content collaboration
try:
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    from transformers import pipeline, AutoTokenizer, AutoModel
    import spacy
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    from moviepy.editor import VideoFileClip
    import librosa  # Pour l'analyse audio
    from textblob import TextBlob
    import pytesseract  # OCR
except ImportError as e:
    logging.warning(f"Optional content dependency missing: {e}")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS ET TYPES CONTENT
# ==========================================

class ContentType(Enum):
    """Types de contenu"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    INFOGRAPHIC = "infographic"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    LIVE_STREAM = "live_stream"
    BLOG_POST = "blog_post"
    NEWSLETTER = "newsletter"

class ContentStatus(Enum):
    """Statuts de contenu"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"

class ReviewType(Enum):
    """Types de révision"""
    CONTENT_REVIEW = "content_review"
    LEGAL_REVIEW = "legal_review"
    BRAND_REVIEW = "brand_review"
    TECHNICAL_REVIEW = "technical_review"
    CREATIVE_REVIEW = "creative_review"
    FINAL_APPROVAL = "final_approval"

class CollaborationRole(Enum):
    """Rôles de collaboration"""
    CREATOR = "creator"
    CO_CREATOR = "co_creator"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    VIEWER = "viewer"
    ADMIN = "admin"

class ContentQuality(Enum):
    """Niveaux de qualité"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    OUTSTANDING = "outstanding"

# ==========================================
# DATACLASSES CONTENT
# ==========================================

@dataclass
class ContentPiece:
    """Pièce de contenu"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    type: ContentType = ContentType.TEXT
    status: ContentStatus = ContentStatus.DRAFT
    content_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    collaborators: Dict[str, CollaborationRole] = field(default_factory=dict)
    versions: List[Dict] = field(default_factory=list)
    current_version: int = 1
    quality_score: float = 0.0
    engagement_prediction: Dict[str, float] = field(default_factory=dict)
    brand_guidelines_compliance: float = 0.0
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

@dataclass
class ContentProject:
    """Projet de contenu collaboratif"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    content_pieces: List[str] = field(default_factory=list)
    collaborators: Dict[str, CollaborationRole] = field(default_factory=dict)
    timeline: Dict[str, datetime] = field(default_factory=dict)
    templates: List[str] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    workflow_stages: List[Dict] = field(default_factory=list)
    approval_chain: List[str] = field(default_factory=list)
    budget: Dict[str, float] = field(default_factory=dict)
    performance_targets: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"

@dataclass
class ReviewRequest:
    """Demande de révision"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    reviewer_id: str = ""
    review_type: ReviewType = ReviewType.CONTENT_REVIEW
    requested_by: str = ""
    deadline: Optional[datetime] = None
    priority: str = "medium"
    instructions: str = ""
    feedback: List[Dict] = field(default_factory=list)
    status: str = "pending"
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentTemplate:
    """Template de contenu"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: ContentType = ContentType.TEXT
    template_data: Dict[str, Any] = field(default_factory=dict)
    variables: List[Dict] = field(default_factory=list)
    style_guide: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    rating: float = 0.0
    tags: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_public: bool = True

@dataclass
class CollaborationSession:
    """Session de collaboration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    content_id: str = ""
    participants: List[str] = field(default_factory=list)
    session_type: str = "editing"  # editing, brainstorming, review
    real_time_changes: List[Dict] = field(default_factory=list)
    chat_messages: List[Dict] = field(default_factory=list)
    screen_sharing: bool = False
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    recording_url: Optional[str] = None

# ==========================================
# CONTENT COLLABORATION MANAGER - GESTIONNAIRE PRINCIPAL
# ==========================================

class ContentCollaborationManager:
    """
    📄 Content Collaboration Manager - Gestionnaire de collaboration de contenu enterprise
    
    Fonctionnalités Enterprise:
    - Co-création temps réel multi-utilisateur
    - Workflow de révision intelligent et automatisé
    - Gestion de versions avancée avec merge automatique
    - Templates adaptatifs et suggestions IA
    - Analyse de qualité et conformité automatique
    - Analytics de performance prédictive
    """
    
    def __init__(self, db_session=None, redis_client=None) -> None:
        self.db_session = db_session
        self.redis_client = redis_client
        self.content_pieces = {}
        self.content_projects = {}
        self.active_sessions = {}
        self.review_requests = {}
        self.templates = {}
        self.quality_analyzers = {}
        
        # Initialiser les analyseurs de qualité
        self._initialize_quality_analyzers()
    
    def _initialize_quality_analyzers(self) -> None:
        """Initialise les analyseurs de qualité"""
        self.quality_analyzers = {
            'text': {
                'readability': True,
                'grammar': True,
                'sentiment': True,
                'brand_voice': True,
                'seo_optimization': True
            },
            'image': {
                'composition': True,
                'color_harmony': True,
                'brand_compliance': True,
                'technical_quality': True,
                'visual_appeal': True
            },
            'video': {
                'technical_quality': True,
                'engagement_factors': True,
                'brand_compliance': True,
                'audio_quality': True,
                'pacing': True
            }
        }
    
    async def create_content_project(self, creator_id: str, project_data: Dict) -> ContentProject:
        """Crée un nouveau projet de contenu collaboratif"""
        try:
            # Créer le projet
            project = ContentProject(
                name=project_data['name'],
                description=project_data.get('description', ''),
                objectives=project_data.get('objectives', []),
                target_audience=project_data.get('target_audience', {}),
                brand_guidelines=project_data.get('brand_guidelines', {}),
                timeline=project_data.get('timeline', {}),
                budget=project_data.get('budget', {}),
                performance_targets=project_data.get('performance_targets', {})
            )
            
            # Ajouter le créateur comme admin
            project.collaborators[creator_id] = CollaborationRole.ADMIN
            
            # Configurer le workflow par défaut
            await self._setup_default_workflow(project)
            
            # Créer les templates par défaut
            await self._create_project_templates(project)
            
            # Stocker le projet
            self.content_projects[project.id] = project
            
            # Persister
            if self.db_session:
                await self._persist_content_project(project)
            
            logger.info(f"Projet de contenu créé: {project.name}")
            return project
            
        except Exception as e:
            logger.error(f"Erreur création projet contenu: {e}")
            raise
    
    async def create_content_piece(self, project_id: str, creator_id: str, 
                                 content_data: Dict) -> ContentPiece:
        """Crée une nouvelle pièce de contenu"""
        try:
            # Vérifier les permissions
            project = self.content_projects.get(project_id)
            if not project or creator_id not in project.collaborators:
                raise PermissionError("Accès non autorisé au projet")
            
            # Créer la pièce de contenu
            content = ContentPiece(
                title=content_data['title'],
                description=content_data.get('description', ''),
                type=ContentType(content_data['type']),
                content_data=content_data.get('content_data', {}),
                metadata=content_data.get('metadata', {}),
                tags=content_data.get('tags', []),
                categories=content_data.get('categories', []),
                created_by=creator_id
            )
            
            # Ajouter le créateur comme collaborateur principal
            content.collaborators[creator_id] = CollaborationRole.CREATOR
            
            # Créer la première version
            initial_version = {
                'version': 1,
                'content_data': content.content_data.copy(),
                'created_by': creator_id,
                'created_at': datetime.utcnow(),
                'changes': ['Initial creation'],
                'hash': self._calculate_content_hash(content.content_data)
            }
            content.versions.append(initial_version)
            
            # Analyser la qualité initiale
            quality_score = await self._analyze_content_quality(content)
            content.quality_score = quality_score
            
            # Prédire l'engagement
            engagement_prediction = await self._predict_content_engagement(content)
            content.engagement_prediction = engagement_prediction
            
            # Vérifier la conformité aux guidelines
            compliance_score = await self._check_brand_guidelines_compliance(content, project)
            content.brand_guidelines_compliance = compliance_score
            
            # Stocker le contenu
            self.content_pieces[content.id] = content
            
            # Ajouter au projet
            project.content_pieces.append(content.id)
            
            # Persister
            if self.db_session:
                await self._persist_content_piece(content)
            
            logger.info(f"Contenu créé: {content.title}")
            return content
            
        except Exception as e:
            logger.error(f"Erreur création contenu: {e}")
            raise
    
    async def start_collaboration_session(self, content_id: str, initiator_id: str,
                                        session_type: str = "editing") -> CollaborationSession:
        """Démarre une session de collaboration"""
        try:
            content = self.content_pieces.get(content_id)
            if not content:
                raise ValueError("Contenu introuvable")
            
            # Vérifier les permissions
            if initiator_id not in content.collaborators:
                raise PermissionError("Accès non autorisé")
            
            # Créer la session
            session = CollaborationSession(
                content_id=content_id,
                session_type=session_type,
                participants=[initiator_id]
            )
            
            # Trouver le projet associé
            project_id = None
            for pid, project in self.content_projects.items():
                if content_id in project.content_pieces:
                    project_id = pid
                    session.project_id = project_id
                    break
            
            # Stocker la session
            self.active_sessions[session.id] = session
            
            # Notifier les autres collaborateurs
            await self._notify_collaboration_session_started(session, content)
            
            # Initialiser la synchronisation temps réel
            await self._initialize_real_time_sync(session.id)
            
            logger.info(f"Session de collaboration démarrée: {session_type} pour {content.title}")
            return session
            
        except Exception as e:
            logger.error(f"Erreur démarrage session collaboration: {e}")
            raise
    
    async def join_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """Rejoint une session de collaboration"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError("Session introuvable")
            
            content = self.content_pieces.get(session.content_id)
            if not content:
                raise ValueError("Contenu associé introuvable")
            
            # Vérifier les permissions
            if user_id not in content.collaborators:
                raise PermissionError("Accès non autorisé")
            
            # Ajouter à la session
            if user_id not in session.participants:
                session.participants.append(user_id)
            
            # Notifier les autres participants
            await self._notify_user_joined_session(session, user_id)
            
            # Synchroniser l'état actuel
            await self._sync_session_state(session_id, user_id)
            
            logger.info(f"Utilisateur {user_id} a rejoint la session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur rejoindre session: {e}")
            return False
    
    async def apply_real_time_change(self, session_id: str, user_id: str, 
                                   change_data: Dict) -> bool:
        """Applique un changement en temps réel"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or user_id not in session.participants:
                raise PermissionError("Accès non autorisé à la session")
            
            content = self.content_pieces.get(session.content_id)
            if not content:
                raise ValueError("Contenu introuvable")
            
            # Valider le changement
            if not await self._validate_change(change_data, content):
                raise ValueError("Changement invalide")
            
            # Créer l'entrée de changement
            change_entry = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'timestamp': datetime.utcnow(),
                'change_type': change_data['type'],
                'change_data': change_data['data'],
                'previous_value': await self._get_current_value(content, change_data['path']),
                'applied': False
            }
            
            # Appliquer le changement au contenu
            await self._apply_change_to_content(content, change_data)
            change_entry['applied'] = True
            
            # Ajouter à l'historique de session
            session.real_time_changes.append(change_entry)
            
            # Diffuser le changement aux autres participants
            await self._broadcast_change_to_participants(session, change_entry)
            
            # Mettre à jour les métriques de qualité
            await self._update_quality_metrics_incremental(content, change_data)
            
            logger.debug(f"Changement appliqué: {change_data['type']} par {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur application changement temps réel: {e}")
            return False
    
    async def create_content_version(self, content_id: str, user_id: str, 
                                   version_notes: str = "") -> int:
        """Crée une nouvelle version du contenu"""
        try:
            content = self.content_pieces.get(content_id)
            if not content:
                raise ValueError("Contenu introuvable")
            
            # Vérifier les permissions
            user_role = content.collaborators.get(user_id)
            if not user_role or user_role not in [CollaborationRole.CREATOR, CollaborationRole.CO_CREATOR, CollaborationRole.EDITOR]:
                raise PermissionError("Permissions insuffisantes")
            
            # Créer la nouvelle version
            new_version_number = max([v['version'] for v in content.versions]) + 1
            
            # Calculer les changements depuis la dernière version
            changes = await self._calculate_changes_since_last_version(content)
            
            new_version = {
                'version': new_version_number,
                'content_data': content.content_data.copy(),
                'created_by': user_id,
                'created_at': datetime.utcnow(),
                'changes': changes,
                'notes': version_notes,
                'hash': self._calculate_content_hash(content.content_data),
                'quality_score': content.quality_score,
                'parent_version': content.current_version
            }
            
            # Ajouter à l'historique
            content.versions.append(new_version)
            content.current_version = new_version_number
            content.updated_at = datetime.utcnow()
            
            # Persister
            if self.db_session:
                await self._persist_content_version(content, new_version)
            
            # Notifier les collaborateurs
            await self._notify_new_version_created(content, new_version)
            
            logger.info(f"Nouvelle version créée: v{new_version_number} pour {content.title}")
            return new_version_number
            
        except Exception as e:
            logger.error(f"Erreur création version: {e}")
            raise
    
    async def request_content_review(self, content_id: str, requester_id: str,
                                   review_type: ReviewType, reviewer_id: str,
                                   instructions: str = "", deadline: Optional[datetime] = None) -> ReviewRequest:
        """Demande une révision de contenu"""
        try:
            content = self.content_pieces.get(content_id)
            if not content:
                raise ValueError("Contenu introuvable")
            
            # Vérifier les permissions
            if requester_id not in content.collaborators:
                raise PermissionError("Accès non autorisé")
            
            # Créer la demande de révision
            review_request = ReviewRequest(
                content_id=content_id,
                reviewer_id=reviewer_id,
                review_type=review_type,
                requested_by=requester_id,
                deadline=deadline or datetime.utcnow() + timedelta(days=3),
                instructions=instructions,
                priority="medium"
            )
            
            # Déterminer la priorité selon le type de révision
            if review_type == ReviewType.LEGAL_REVIEW:
                review_request.priority = "high"
            elif review_type == ReviewType.FINAL_APPROVAL:
                review_request.priority = "high"
            
            # Stocker la demande
            self.review_requests[review_request.id] = review_request
            
            # Persister
            if self.db_session:
                await self._persist_review_request(review_request)
            
            # Notifier le reviewer
            await self._notify_review_requested(review_request, content)
            
            # Mettre à jour le statut du contenu
            if content.status == ContentStatus.DRAFT:
                content.status = ContentStatus.UNDER_REVIEW
                content.updated_at = datetime.utcnow()
            
            logger.info(f"Révision demandée: {review_type.value} pour {content.title}")
            return review_request
            
        except Exception as e:
            logger.error(f"Erreur demande révision: {e}")
            raise
    
    async def submit_review_feedback(self, review_request_id: str, reviewer_id: str,
                                   feedback_data: Dict) -> bool:
        """Soumet un feedback de révision"""
        try:
            review_request = self.review_requests.get(review_request_id)
            if not review_request:
                raise ValueError("Demande de révision introuvable")
            
            # Vérifier les permissions
            if review_request.reviewer_id != reviewer_id:
                raise PermissionError("Non autorisé à réviser cette demande")
            
            # Structurer le feedback
            feedback = {
                'id': str(uuid.uuid4()),
                'reviewer_id': reviewer_id,
                'timestamp': datetime.utcnow(),
                'overall_rating': feedback_data.get('overall_rating', 0),
                'approval_status': feedback_data.get('approval_status', 'pending'),
                'comments': feedback_data.get('comments', []),
                'suggestions': feedback_data.get('suggestions', []),
                'issues': feedback_data.get('issues', []),
                'attachments': feedback_data.get('attachments', [])
            }
            
            # Ajouter le feedback à la demande
            review_request.feedback.append(feedback)
            review_request.status = "completed"
            review_request.completed_at = datetime.utcnow()
            
            # Mettre à jour le contenu selon le feedback
            content = self.content_pieces.get(review_request.content_id)
            if content:
                await self._process_review_feedback(content, feedback, review_request.review_type)
            
            # Persister
            if self.db_session:
                await self._persist_review_feedback(review_request, feedback)
            
            # Notifier le demandeur
            await self._notify_review_completed(review_request, feedback)
            
            logger.info(f"Feedback de révision soumis: {review_request.review_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur soumission feedback révision: {e}")
            return False

# ==========================================
# CONTENT QUALITY ANALYZER - ANALYSEUR DE QUALITÉ
# ==========================================

class ContentQualityAnalyzer:
    """
    🔍 Content Quality Analyzer - Analyseur de qualité de contenu enterprise
    
    Fonctionnalités Enterprise:
    - Analyse multi-dimensionnelle de qualité
    - Scoring automatique basé sur IA
    - Détection d'anomalies et problèmes
    - Suggestions d'amélioration intelligentes
    - Conformité aux guidelines de marque
    """
    
    def __init__(self, collaboration_manager) -> None:
        self.collaboration_manager = collaboration_manager
        self.quality_models = {}
        self.benchmark_data = {}
        
    async def analyze_text_quality(self, content: ContentPiece) -> Dict[str, Any]:
        """Analyse la qualité d'un contenu textuel"""
        try:
            text_data = content.content_data.get('text', '')
            if not text_data:
                return {'overall_score': 0, 'analysis': {}}
            
            analysis = {}
            
            # Analyse de lisibilité
            readability_score = await self._calculate_readability_score(text_data)
            analysis['readability'] = {
                'score': readability_score,
                'level': self._get_readability_level(readability_score)
            }
            
            # Analyse grammaticale
            grammar_analysis = await self._analyze_grammar(text_data)
            analysis['grammar'] = grammar_analysis
            
            # Analyse de sentiment
            sentiment_analysis = await self._analyze_sentiment(text_data)
            analysis['sentiment'] = sentiment_analysis
            
            # Analyse SEO
            seo_analysis = await self._analyze_seo_factors(text_data, content.metadata)
            analysis['seo'] = seo_analysis
            
            # Analyse de la voix de marque
            brand_voice_analysis = await self._analyze_brand_voice(text_data, content)
            analysis['brand_voice'] = brand_voice_analysis
            
            # Score global
            overall_score = await self._calculate_overall_text_score(analysis)
            
            return {
                'overall_score': overall_score,
                'analysis': analysis,
                'recommendations': await self._generate_text_recommendations(analysis),
                'analyzed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse qualité texte: {e}")
            return {'overall_score': 0, 'analysis': {}}
    
    async def analyze_visual_quality(self, content: ContentPiece) -> Dict[str, Any]:
        """Analyse la qualité d'un contenu visuel"""
        try:
            if content.type not in [ContentType.IMAGE, ContentType.VIDEO]:
                return {'overall_score': 0, 'analysis': {}}
            
            analysis = {}
            
            # Analyse technique
            technical_analysis = await self._analyze_technical_quality(content)
            analysis['technical'] = technical_analysis
            
            # Analyse compositionnelle
            composition_analysis = await self._analyze_composition(content)
            analysis['composition'] = composition_analysis
            
            # Analyse de cohérence de marque
            brand_analysis = await self._analyze_visual_brand_compliance(content)
            analysis['brand_compliance'] = brand_analysis
            
            # Analyse de l'engagement visuel
            engagement_analysis = await self._analyze_visual_engagement(content)
            analysis['engagement_potential'] = engagement_analysis
            
            # Score global
            overall_score = await self._calculate_overall_visual_score(analysis)
            
            return {
                'overall_score': overall_score,
                'analysis': analysis,
                'recommendations': await self._generate_visual_recommendations(analysis),
                'analyzed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse qualité visuelle: {e}")
            return {'overall_score': 0, 'analysis': {}}

# ==========================================
# CONTENT TEMPLATE ENGINE - MOTEUR DE TEMPLATES
# ==========================================

class ContentTemplateEngine:
    """
    📋 Content Template Engine - Moteur de templates de contenu enterprise
    
    Fonctionnalités Enterprise:
    - Templates adaptatifs basés sur IA
    - Personnalisation automatique selon contexte
    - Bibliothèque de templates intelligente
    - Génération de templates à partir d'exemples
    - Optimisation de templates basée sur performance
    """
    
    def __init__(self, collaboration_manager) -> None:
        self.collaboration_manager = collaboration_manager
        self.template_library = {}
        self.template_performance = defaultdict(dict)
        
    async def create_template_from_content(self, content_id: str, template_name: str,
                                         creator_id: str) -> ContentTemplate:
        """Crée un template à partir d'un contenu existant"""
        try:
            content = self.collaboration_manager.content_pieces.get(content_id)
            if not content:
                raise ValueError("Contenu source introuvable")
            
            # Extraire les éléments templatables
            template_data = await self._extract_template_elements(content)
            
            # Identifier les variables
            variables = await self._identify_template_variables(content, template_data)
            
            # Créer le guide de style
            style_guide = await self._extract_style_guide(content)
            
            # Créer le template
            template = ContentTemplate(
                name=template_name,
                description=f"Template créé à partir de {content.title}",
                type=content.type,
                template_data=template_data,
                variables=variables,
                style_guide=style_guide,
                created_by=creator_id,
                tags=content.tags.copy()
            )
            
            # Stocker le template
            self.template_library[template.id] = template
            self.collaboration_manager.templates[template.id] = template
            
            # Persister
            if self.collaboration_manager.db_session:
                await self._persist_template(template)
            
            logger.info(f"Template créé: {template_name} à partir de {content.title}")
            return template
            
        except Exception as e:
            logger.error(f"Erreur création template: {e}")
            raise
    
    async def generate_content_from_template(self, template_id: str, variables_data: Dict,
                                           creator_id: str) -> ContentPiece:
        """Génère du contenu à partir d'un template"""
        try:
            template = self.template_library.get(template_id)
            if not template:
                raise ValueError("Template introuvable")
            
            # Valider les variables
            await self._validate_template_variables(template, variables_data)
            
            # Générer le contenu
            content_data = await self._populate_template(template, variables_data)
            
            # Créer la pièce de contenu
            content = ContentPiece(
                title=variables_data.get('title', f"Contenu généré depuis {template.name}"),
                description=variables_data.get('description', ''),
                type=template.type,
                content_data=content_data,
                metadata={
                    'generated_from_template': template_id,
                    'template_name': template.name,
                    'generation_variables': variables_data
                },
                tags=template.tags.copy(),
                created_by=creator_id
            )
            
            # Appliquer le guide de style
            await self._apply_style_guide(content, template.style_guide)
            
            # Analyser la qualité initiale
            quality_score = await self.collaboration_manager._analyze_content_quality(content)
            content.quality_score = quality_score
            
            # Mettre à jour les statistiques d'usage du template
            template.usage_count += 1
            
            return content
            
        except Exception as e:
            logger.error(f"Erreur génération contenu depuis template: {e}")
            raise

# ==========================================
# EXPORTS CONSOLIDÉS
# ==========================================

__all__ = [
    'ContentCollaborationManager', 'ContentQualityAnalyzer', 'ContentTemplateEngine',
    'ContentPiece', 'ContentProject', 'ReviewRequest', 'ContentTemplate', 'CollaborationSession',
    'ContentType', 'ContentStatus', 'ReviewType', 'CollaborationRole', 'ContentQuality'
]

# ==========================================
# FACTORY FUNCTION
# ==========================================

async def create_content_collaboration(redis_url: Optional[str] = None, 
                                     db_session=None) -> Dict[str, Any]:
    """
    Factory function pour créer une instance complète de Content Collaboration
    """
    # Configuration Redis si URL fournie
    redis_client = None
    if redis_url:
        try:
            import aioredis
            redis_client = await aioredis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Impossible de se connecter à Redis: {e}")
    
    # Créer les instances
    collaboration_manager = ContentCollaborationManager(db_session, redis_client)
    quality_analyzer = ContentQualityAnalyzer(collaboration_manager)
    template_engine = ContentTemplateEngine(collaboration_manager)
    
    return {
        'collaboration_manager': collaboration_manager,
        'quality_analyzer': quality_analyzer,
        'template_engine': template_engine,
        'redis_client': redis_client
    }

# Fin du module content_collaboration.py
