"""
Collaboration Network Database Models and Operations

Gestion complète du réseau de collaboration entre créateurs avec 
matching IA et distribution multi-plateformes.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer & Network Specialist

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle de Fahed Mlaiel.
Toute utilisation, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de 
poursuites judiciaires selon la loi allemande.
Email: mlaiel@live.de pour autorisation d'utilisation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey, Decimal, Table
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum as PyEnum
import logging
import uuid
import json

logger = logging.getLogger(__name__)

Base = declarative_base()


class CollaborationType(PyEnum):
    """Types de collaboration supportés."""
    MUSIC_FEATURE = "music_feature"
    PODCAST_GUEST = "podcast_guest"
    CONTENT_CROSS_PROMOTION = "content_cross_promotion"
    JOINT_PROJECT = "joint_project"
    MENTOR_MENTEE = "mentor_mentee"
    BRAND_PARTNERSHIP = "brand_partnership"
    LIVE_PERFORMANCE = "live_performance"
    REMIX_REMIX = "remix_remix"


class CollaborationStatus(PyEnum):
    """Statuts des collaborations."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class NetworkTier(PyEnum):
    """Niveaux du réseau de collaboration."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class MatchingAlgorithm(PyEnum):
    """Algorithmes de matching IA disponibles."""
    CONTENT_SIMILARITY = "content_similarity"
    AUDIENCE_OVERLAP = "audience_overlap"
    GENRE_COMPATIBILITY = "genre_compatibility"
    ENGAGEMENT_SCORE = "engagement_score"
    LOCATION_PROXIMITY = "location_proximity"
    COLLABORATION_HISTORY = "collaboration_history"


# Table d'association pour les collaborations many-to-many
collaboration_participants = Table(
    'collaboration_participants',
    Base.metadata,
    Column('collaboration_id', String, ForeignKey('collaborations.id'), primary_key=True),
    Column('creator_id', String, ForeignKey('creator_accounts.id'), primary_key=True),
    Column('role', String, nullable=False),
    Column('contribution_percentage', Decimal(5, 2), default=0.00),
    Column('joined_at', DateTime, default=datetime.utcnow)
)


class CollaborationNetwork(Base):
    """
    Réseau principal de collaboration entre créateurs.
    Utilise l'IA pour le matching intelligent et l'optimisation.
    """
    __tablename__ = "collaboration_networks"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    network_uuid = Column(String, unique=True, nullable=False)
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Configuration réseau
    network_tier = Column(Enum(NetworkTier), default=NetworkTier.STARTER)
    is_active = Column(Boolean, default=True)
    max_collaborations = Column(Integer, default=5)
    current_collaborations = Column(Integer, default=0)
    
    # Préférences de matching
    preferred_collaboration_types = Column(JSON)  # ["music_feature", "podcast_guest"]
    preferred_genres = Column(JSON)  # ["pop", "rock", "jazz"]
    preferred_languages = Column(JSON)  # ["en", "fr", "de"]
    preferred_regions = Column(JSON)  # ["US", "EU", "ASIA"]
    
    # Critères de matching IA
    matching_algorithms = Column(JSON)  # Configuration des algorithmes
    minimum_match_score = Column(Decimal(3, 2), default=0.70)
    auto_accept_threshold = Column(Decimal(3, 2), default=0.95)
    
    # Métriques de performance
    total_collaborations = Column(Integer, default=0)
    successful_collaborations = Column(Integer, default=0)
    average_collaboration_rating = Column(Decimal(3, 2), default=0.00)
    network_influence_score = Column(Decimal(5, 2), default=0.00)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        self.network_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class Collaboration(Base):
    """
    Modèle de collaboration entre créateurs avec suivi complet.
    """
    __tablename__ = "collaborations"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_uuid = Column(String, unique=True, nullable=False)
    initiator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Informations de base
    title = Column(String(300), nullable=False)
    description = Column(Text)
    collaboration_type = Column(Enum(CollaborationType), nullable=False)
    status = Column(Enum(CollaborationStatus), default=CollaborationStatus.PENDING)
    
    # Configuration technique
    expected_deliverables = Column(JSON)  # ["audio_file", "video_content", "social_media"]
    technical_requirements = Column(JSON)  # Specs techniques requises
    platform_distribution = Column(JSON)  # Plateformes de distribution
    
    # Timeline et planning
    start_date = Column(DateTime)
    expected_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    milestone_dates = Column(JSON)  # Dates clés du projet
    
    # Aspects financiers
    budget_range = Column(JSON)  # {"min": 1000, "max": 5000, "currency": "EUR"}
    revenue_sharing = Column(JSON)  # Répartition des revenus
    payment_terms = Column(JSON)  # Conditions de paiement
    
    # Métriques et évaluation
    match_score = Column(Decimal(3, 2))  # Score de compatibilité IA
    collaboration_rating = Column(Decimal(3, 2))  # Évaluation finale
    success_metrics = Column(JSON)  # Métriques de succès définies
    actual_results = Column(JSON)  # Résultats obtenus
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relations
    participants = relationship(
        "CreatorAccount",
        secondary=collaboration_participants,
        back_populates="collaborations"
    )

    def __init__(self, **kwargs):
        super().__init__()
        self.collaboration_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class CollaborationInvitation(Base):
    """
    Invitations de collaboration avec gestion intelligente.
    """
    __tablename__ = "collaboration_invitations"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invitation_uuid = Column(String, unique=True, nullable=False)
    collaboration_id = Column(String, ForeignKey("collaborations.id"), nullable=False)
    
    # Participants
    sender_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False)
    
    # Contenu invitation
    subject = Column(String(200), nullable=False)
    message = Column(Text)
    proposed_role = Column(String(100))
    proposed_contribution = Column(Decimal(5, 2))
    
    # Statut et réponse
    status = Column(Enum(CollaborationStatus), default=CollaborationStatus.PENDING)
    response_message = Column(Text)
    response_date = Column(DateTime)
    
    # Timeline
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    sent_at = Column(DateTime, default=datetime.utcnow)
    viewed_at = Column(DateTime)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        self.invitation_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class CollaborationMatchingProfile(Base):
    """
    Profil de matching IA pour optimiser les collaborations.
    """
    __tablename__ = "collaboration_matching_profiles"

    # Identifiants principaux
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, ForeignKey("creator_accounts.id"), nullable=False, unique=True)
    profile_uuid = Column(String, unique=True, nullable=False)
    
    # Vecteurs de features IA
    content_embedding = Column(JSON)  # Embedding du contenu créé
    style_features = Column(JSON)  # Caractéristiques stylistiques
    audience_demographics = Column(JSON)  # Démographie de l'audience
    engagement_patterns = Column(JSON)  # Patterns d'engagement
    
    # Préférences comportementales
    collaboration_frequency = Column(String(50))  # "weekly", "monthly", "occasional"
    commitment_level = Column(String(50))  # "casual", "professional", "exclusive"
    communication_style = Column(String(50))  # "formal", "casual", "creative"
    
    # Historique et réputation
    collaboration_success_rate = Column(Decimal(3, 2), default=0.00)
    average_project_duration = Column(Integer)  # En jours
    reliability_score = Column(Decimal(3, 2), default=0.00)
    creativity_score = Column(Decimal(3, 2), default=0.00)
    
    # Configuration IA
    matching_weights = Column(JSON)  # Poids des différents critères
    exclusion_criteria = Column(JSON)  # Critères d'exclusion
    boost_criteria = Column(JSON)  # Critères de boost
    
    # Métadonnées
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile_completeness = Column(Decimal(3, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        self.profile_uuid = str(uuid.uuid4())
        for key, value in kwargs.items():
            setattr(self, key, value)


class CollaborationNetworkRepository:
    """
    Repository pour la gestion des réseaux de collaboration.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_network(self, creator_id: str, network_data: Dict[str, Any]) -> CollaborationNetwork:
        """Créer un nouveau réseau de collaboration."""



        try:
            network = CollaborationNetwork(
                creator_id=creator_id,
                **network_data
            )
            self.db.add(network)
            self.db.commit()
            self.db.refresh(network)
            
            logger.info(f"Réseau de collaboration créé: {network.network_uuid}")
            return network
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création réseau: {str(e)}")
            raise

    def find_matches(self, creator_id: str, collaboration_type: CollaborationType, 
                    min_score: float = 0.70) -> List[Dict[str, Any]]:
        """Trouver des matches de collaboration via IA."""



        try:
            # Logique de matching IA sophistiquée
            network = self.db.query(CollaborationNetwork).filter(
                CollaborationNetwork.creator_id == creator_id
            ).first()
            
            if not network:
                return []
            
            # Algorithme de matching basé sur plusieurs critères
            potential_matches = []
            
            # Récupérer les autres créateurs actifs
            other_networks = self.db.query(CollaborationNetwork).filter(
                CollaborationNetwork.creator_id != creator_id,
                CollaborationNetwork.is_active == True
            ).all()
            
            for other_network in other_networks:
                match_score = self._calculate_match_score(network, other_network, collaboration_type)
                
                if match_score >= min_score:
                    potential_matches.append({
                        "creator_id": other_network.creator_id,
                        "network_id": other_network.id,
                        "match_score": float(match_score),
                        "collaboration_type": collaboration_type.value,
                        "compatibility_factors": self._get_compatibility_factors(network, other_network)
                    })
            
            # Trier par score décroissant
            potential_matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            logger.info(f"Trouvé {len(potential_matches)} matches pour {creator_id}")
            return potential_matches
            
        except Exception as e:
            logger.error(f"Erreur recherche matches: {str(e)}")
            return []

    def create_collaboration(self, collaboration_data: Dict[str, Any]) -> Collaboration:
        """Créer une nouvelle collaboration."""



        try:
            collaboration = Collaboration(**collaboration_data)
            self.db.add(collaboration)
            self.db.commit()
            self.db.refresh(collaboration)
            
            logger.info(f"Collaboration créée: {collaboration.collaboration_uuid}")
            return collaboration
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur création collaboration: {str(e)}")
            raise

    def send_invitation(self, invitation_data: Dict[str, Any]) -> CollaborationInvitation:
        """Envoyer une invitation de collaboration."""



        try:
            invitation = CollaborationInvitation(**invitation_data)
            self.db.add(invitation)
            self.db.commit()
            self.db.refresh(invitation)
            
            logger.info(f"Invitation envoyée: {invitation.invitation_uuid}")
            return invitation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur envoi invitation: {str(e)}")
            raise

    def update_matching_profile(self, creator_id: str, profile_data: Dict[str, Any]) -> CollaborationMatchingProfile:
        """Mettre à jour le profil de matching IA."""



        try:
            profile = self.db.query(CollaborationMatchingProfile).filter(
                CollaborationMatchingProfile.creator_id == creator_id
            ).first()
            
            if not profile:
                profile = CollaborationMatchingProfile(
                    creator_id=creator_id,
                    **profile_data
                )
                self.db.add(profile)
            else:
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.last_updated = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"Profil matching mis à jour: {creator_id}")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur mise à jour profil: {str(e)}")
            raise

    def get_collaboration_analytics(self, creator_id: str, timeframe_days: int = 30) -> Dict[str, Any]:
        """Obtenir les analytics de collaboration."""



        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=timeframe_days)
            
            # Collaborations dans la période
            collaborations = self.db.query(Collaboration).join(
                collaboration_participants,
                Collaboration.id == collaboration_participants.c.collaboration_id
            ).filter(
                collaboration_participants.c.creator_id == creator_id,
                Collaboration.created_at >= start_date
            ).all()
            
            # Calcul des métriques
            total_collaborations = len(collaborations)
            completed_collaborations = len([c for c in collaborations if c.status == CollaborationStatus.COMPLETED])
            
            success_rate = (completed_collaborations / total_collaborations * 100) if total_collaborations > 0 else 0
            
            avg_rating = 0
            if completed_collaborations > 0:
                ratings = [c.collaboration_rating for c in collaborations if c.collaboration_rating and c.status == CollaborationStatus.COMPLETED]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            return {
                "timeframe_days": timeframe_days,
                "total_collaborations": total_collaborations,
                "completed_collaborations": completed_collaborations,
                "success_rate": round(success_rate, 2),
                "average_rating": round(float(avg_rating), 2),
                "collaboration_types": self._get_collaboration_type_breakdown(collaborations),
                "monthly_trend": self._get_monthly_trend(creator_id, timeframe_days)
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics collaboration: {str(e)}")
            return {}

    def _calculate_match_score(self, network1: CollaborationNetwork, network2: CollaborationNetwork, 
                             collaboration_type: CollaborationType) -> float:
        """Calculer le score de compatibilité entre deux créateurs."""
        score = 0.0
        
        # Vérifier les types de collaboration préférés
        if network1.preferred_collaboration_types and network2.preferred_collaboration_types:
            if collaboration_type.value in network1.preferred_collaboration_types and \
               collaboration_type.value in network2.preferred_collaboration_types:
                score += 0.3
        
        # Vérifier la compatibilité des genres
        if network1.preferred_genres and network2.preferred_genres:
            common_genres = set(network1.preferred_genres) & set(network2.preferred_genres)
            if common_genres:
                score += 0.25 * (len(common_genres) / max(len(network1.preferred_genres), len(network2.preferred_genres)))
        
        # Vérifier les régions
        if network1.preferred_regions and network2.preferred_regions:
            common_regions = set(network1.preferred_regions) & set(network2.preferred_regions)
            if common_regions:
                score += 0.2
        
        # Prendre en compte les scores de performance
        avg_performance = (network1.network_influence_score + network2.network_influence_score) / 2
        score += 0.25 * min(float(avg_performance) / 100, 1.0)
        
        return min(score, 1.0)

    def _get_compatibility_factors(self, network1: CollaborationNetwork, network2: CollaborationNetwork) -> List[str]:
        """Obtenir les facteurs de compatibilité."""
        factors = []
        
        if network1.preferred_genres and network2.preferred_genres:
            common_genres = set(network1.preferred_genres) & set(network2.preferred_genres)
            if common_genres:
                factors.append(f"Genres communs: {', '.join(common_genres)}")
        
        if network1.preferred_regions and network2.preferred_regions:
            common_regions = set(network1.preferred_regions) & set(network2.preferred_regions)
            if common_regions:
                factors.append(f"Régions communes: {', '.join(common_regions)}")
        
        return factors

    def _get_collaboration_type_breakdown(self, collaborations: List[Collaboration]) -> Dict[str, int]:
        """Répartition par type de collaboration."""
        breakdown = {}
        for collaboration in collaborations:
            type_name = collaboration.collaboration_type.value
            breakdown[type_name] = breakdown.get(type_name, 0) + 1
        return breakdown

    def _get_monthly_trend(self, creator_id: str, timeframe_days: int) -> List[Dict[str, Any]]:
        """Tendance mensuelle des collaborations."""
        # Implémentation simplifiée - à enrichir selon les besoins
        return []
