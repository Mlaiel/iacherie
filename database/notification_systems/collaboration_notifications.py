"""
Collaboration and Partnership Notification Manager

Gestionnaire spécialisé pour les notifications de collaboration et partenariats
dans l'écosystème IA Influencer Agent. Matching artistes, projets collaboratifs et réseautage.

Fonctionnalités:
- Notifications matching collaborateurs compatibles IA
- Alertes nouvelles opportunités de partenariat
- Gestion projets collaboratifs multi-artistes
- Système de recommandations intelligent
- Workflow approbation et négociation

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. Tous droits réservés.
AVERTISSEMENT LÉGAL STRICT:
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou tentative de reverse engineering
non autorisée par écrit est formellement interdite et passible de poursuites judiciaires
selon le droit allemand et international. Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
import asyncio
import logging
import json
import uuid
from decimal import Decimal
import aioredis
import asyncpg
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, DECIMAL, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, validator
import httpx
from jinja2 import Template
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types de collaborations possibles"""
    MUSIC_FEATURE = "music_feature"
    REMIX_COLLABORATION = "remix_collaboration"
    JOINT_RELEASE = "joint_release"
    LIVE_PERFORMANCE = "live_performance"
    VIDEO_COLLABORATION = "video_collaboration"
    PODCAST_GUEST = "podcast_guest"
    BRAND_PARTNERSHIP = "brand_partnership"
    SYNC_LICENSING = "sync_licensing"
    MENTORSHIP = "mentorship"
    CROSS_PROMOTION = "cross_promotion"
    LABEL_SIGNING = "label_signing"
    PLAYLIST_EXCHANGE = "playlist_exchange"


class CollaborationStatus(Enum):
    """États des collaborations"""
    SUGGESTED = "suggested"
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class MatchQuality(IntEnum):
    """Qualité du matching de collaboration"""
    POOR = 1        # <40% compatibilité
    FAIR = 2        # 40-60% compatibilité
    GOOD = 3        # 60-80% compatibilité
    EXCELLENT = 4   # 80-95% compatibilité
    PERFECT = 5     # >95% compatibilité


class Genre(Enum):
    """Genres musicaux pour matching"""
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    R_AND_B = "r_and_b"
    REGGAE = "reggae"
    BLUES = "blues"
    FOLK = "folk"
    AMBIENT = "ambient"
    TECHNO = "techno"
    HOUSE = "house"
    DRUM_AND_BASS = "drum_and_bass"
    TRAP = "trap"
    INDIE = "indie"
    ALTERNATIVE = "alternative"


@dataclass
class ArtistProfile:
    """Profil artiste pour matching collaborations"""
    user_id: str
    artist_name: str
    genres: List[Genre] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)  # vocals, guitar, production, mixing
    location: str = ""
    languages: List[str] = field(default_factory=list)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    past_collaborations: List[str] = field(default_factory=list)
    availability: Dict[str, Any] = field(default_factory=dict)
    social_metrics: Dict[str, int] = field(default_factory=dict)
    music_style_vector: List[float] = field(default_factory=list)
    reputation_score: float = 5.0
    response_rate: float = 1.0
    completion_rate: float = 1.0


@dataclass
class CollaborationOpportunity:
    """Opportunité de collaboration détectée"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initiator_id: str = None
    target_id: str = None
    collaboration_type: CollaborationType = CollaborationType.MUSIC_FEATURE
    match_quality: MatchQuality = MatchQuality.FAIR
    compatibility_score: float = 0.0
    mutual_benefits: List[str] = field(default_factory=list)
    project_description: str = ""
    estimated_timeline: str = ""
    proposed_terms: Dict[str, Any] = field(default_factory=dict)
    ai_reasoning: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = None
    status: CollaborationStatus = CollaborationStatus.SUGGESTED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationProject:
    """Projet de collaboration en cours"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    participants: List[str] = field(default_factory=list)
    collaboration_type: CollaborationType = CollaborationType.MUSIC_FEATURE
    description: str = ""
    timeline: Dict[str, datetime] = field(default_factory=dict)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    shared_resources: List[str] = field(default_factory=list)
    revenue_split: Dict[str, float] = field(default_factory=dict)
    contracts: List[str] = field(default_factory=list)
    status: CollaborationStatus = CollaborationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollaborationNotificationManager:
    """
    Gestionnaire avancé des notifications de collaboration
    
    Responsabilités:
    - Matching intelligent artistes compatibles via IA
    - Notifications opportunités de partenariat
    - Gestion workflow collaborations
    - Analytics performance collaborations
    - Système de réputation et recommandations
    """

    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis):
        self.db_pool = db_pool
        self.redis = redis_client
        self.ml_models = self._init_ml_models()
        self.notification_templates = self._load_collaboration_templates()
        self.matching_weights = self._load_matching_weights()
        
    def _init_ml_models(self) -> Dict[str, Any]:
        """Initialise les modèles ML pour le matching"""
        return {
            "tfidf_vectorizer": TfidfVectorizer(max_features=1000, stop_words='english'),
            "genre_similarity_matrix": self._build_genre_similarity_matrix(),
            "collaboration_success_predictor": None  # À charger depuis fichier modèle
        }

    def _build_genre_similarity_matrix(self) -> np.ndarray:
        """Construit matrice de similarité entre genres musicaux"""
        genres = list(Genre)
        # Matrice de similarité basée sur la proximité musicologique
        similarity_matrix = np.eye(len(genres))
        
        # Définition similarités inter-genres (simplifié)
        genre_clusters = {
            "electronic": [Genre.ELECTRONIC, Genre.TECHNO, Genre.HOUSE, Genre.AMBIENT],
            "urban": [Genre.HIP_HOP, Genre.R_AND_B, Genre.TRAP],
            "rock": [Genre.ROCK, Genre.ALTERNATIVE, Genre.INDIE],
            "traditional": [Genre.JAZZ, Genre.BLUES, Genre.FOLK, Genre.COUNTRY]
        }
        
        for cluster in genre_clusters.values():
            for i, genre1 in enumerate(genres):
                for j, genre2 in enumerate(genres):
                    if genre1 in cluster and genre2 in cluster and i != j:
                        similarity_matrix[i][j] = 0.7
        
        return similarity_matrix

    def _load_collaboration_templates(self) -> Dict[str, Template]:
        """Charge les templates de notification de collaboration"""
        templates = {
            "collaboration_suggestion": Template("""
                🤝 NOUVELLE OPPORTUNITÉ DE COLLABORATION!
                
                🎵 Artiste suggéré: {{ target_artist }}
                🎯 Type: {{ collaboration_type }}
                ⭐ Compatibilité: {{ compatibility_score }}% ({{ match_quality }})
                
                🔥 Pourquoi ce match?
                {{ ai_reasoning }}
                
                💎 Bénéfices mutuels:
                {{ mutual_benefits | join('\n• ') }}
                
                📊 Profil artiste:
                • Genres: {{ target_genres | join(', ') }}
                • Followers: {{ target_followers }}
                • Taux de réponse: {{ response_rate }}%
                
                🚀 Prêt à collaborer?
                
                ✅ Accepter collaboration: {{ accept_url }}
                📞 Contacter artiste: {{ contact_url }}
                👀 Voir profil complet: {{ profile_url }}
            """),
            
            "collaboration_request": Template("""
                🎼 DEMANDE DE COLLABORATION REÇUE
                
                👤 De: {{ initiator_name }}
                🎵 Projet: {{ project_title }}
                📅 Timeline: {{ timeline }}
                
                📝 Description:
                {{ project_description }}
                
                💰 Conditions proposées:
                {{ proposed_terms | join('\n• ') }}
                
                ⏰ Réponde avant: {{ expires_at }}
                
                🔍 Profil demandeur:
                • Expérience: {{ initiator_experience }}
                • Collaborations passées: {{ past_collaborations }}
                • Note réputation: {{ reputation_score }}/5
                
                📲 Actions:
                ✅ Accepter: {{ accept_url }}
                ❌ Décliner: {{ decline_url }}
                💬 Négocier: {{ negotiate_url }}
                👀 Voir portfolio: {{ portfolio_url }}
            """),
            
            "collaboration_accepted": Template("""
                🎉 COLLABORATION ACCEPTÉE!
                
                🎵 Projet: {{ project_title }}
                👥 Collaborateurs: {{ participants | join(', ') }}
                📅 Début: {{ start_date }}
                
                📋 Prochaines étapes:
                {{ next_steps | join('\n• ') }}
                
                📁 Espace de travail partagé créé:
                🔗 {{ workspace_url }}
                
                📞 Première réunion programmée:
                📅 {{ meeting_date }}
                🔗 {{ meeting_link }}
                
                💪 Faisons de la magie ensemble!
            """),
            
            "milestone_achieved": Template("""
                🏆 ÉTAPE FRANCHIE - {{ project_title }}
                
                ✅ Étape complétée: {{ milestone_name }}
                📈 Progression: {{ progress_percentage }}%
                
                🎯 Prochaine étape: {{ next_milestone }}
                📅 Échéance: {{ next_deadline }}
                
                💼 Livrables attendus:
                {{ next_deliverables | join('\n• ') }}
                
                🔥 Excellent travail d'équipe!
                
                📊 Tableau de bord: {{ dashboard_url }}
            """),
            
            "trending_opportunity": Template("""
                📈 OPPORTUNITÉ TRENDING DÉTECTÉE!
                
                🔥 {{ opportunity_type }} en tendance
                📊 Popularité: +{{ trend_percentage }}% cette semaine
                
                🎯 Artistes recommandés pour vous:
                {{ recommended_artists | join('\n• ') }}
                
                ⚡ Agissez vite - opportunité limitée!
                
                💡 Pourquoi maintenant?
                {{ trend_reasoning }}
                
                🚀 Démarrer collaboration: {{ start_url }}
            """)
        }
        
        return templates

    def _load_matching_weights(self) -> Dict[str, float]:
        """Charge les poids pour l'algorithme de matching"""
        return {
            "genre_compatibility": 0.25,
            "skill_complementarity": 0.20,
            "location_proximity": 0.10,
            "social_metrics": 0.15,
            "reputation_score": 0.15,
            "collaboration_history": 0.10,
            "response_rate": 0.05
        }

    async def discover_collaboration_opportunities(
        self,
        user_id: str,
        collaboration_types: List[CollaborationType] = None,
        max_suggestions: int = 10
    ) -> List[CollaborationOpportunity]:
        """
        Découvre et propose des opportunités de collaboration via IA
        
        Args:
            user_id: ID de l'utilisateur demandeur
            collaboration_types: Types de collaborations recherchées
            max_suggestions: Nombre maximum de suggestions
            
        Returns:
            Liste d'opportunités de collaboration classées par compatibilité
        """
        try:
            # Récupération profil utilisateur
            user_profile = await self._get_artist_profile(user_id)
            
            # Recherche candidats potentiels
            candidates = await self._find_collaboration_candidates(
                user_profile, collaboration_types
            )
            
            # Calcul scores de compatibilité
            scored_opportunities = []
            
            for candidate in candidates:
                for collab_type in (collaboration_types or list(CollaborationType)):
                    compatibility = await self._calculate_compatibility(
                        user_profile, candidate, collab_type
                    )
                    
                    if compatibility.compatibility_score > 0.4:  # Seuil minimum
                        opportunity = await self._create_collaboration_opportunity(
                            user_profile, candidate, collab_type, compatibility
                        )
                        scored_opportunities.append(opportunity)
            
            # Tri par score de compatibilité
            scored_opportunities.sort(
                key=lambda x: x.compatibility_score, 
                reverse=True
            )
            
            # Limitation du nombre
            final_opportunities = scored_opportunities[:max_suggestions]
            
            # Sauvegarde des suggestions
            await self._save_collaboration_suggestions(final_opportunities)
            
            # Envoi notifications
            await self._send_collaboration_suggestions(user_id, final_opportunities)
            
            logger.info(f"Découvert {len(final_opportunities)} opportunités pour {user_id}")
            
            return final_opportunities
            
        except Exception as e:
            logger.error(f"Erreur découverte collaborations: {str(e)}")
            raise

    async def process_collaboration_request(
        self,
        initiator_id: str,
        target_id: str,
        collaboration_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Traite une demande de collaboration entre artistes"""
        try:
            # Validation des participants
            initiator_profile = await self._get_artist_profile(initiator_id)
            target_profile = await self._get_artist_profile(target_id)
            
            # Création de la demande
            collaboration_request = CollaborationOpportunity(
                initiator_id=initiator_id,
                target_id=target_id,
                collaboration_type=CollaborationType(collaboration_details.get('type')),
                project_description=collaboration_details.get('description', ''),
                proposed_terms=collaboration_details.get('terms', {}),
                estimated_timeline=collaboration_details.get('timeline', ''),
                expires_at=datetime.now() + timedelta(days=7)
            )
            
            # Calcul compatibilité automatique
            compatibility = await self._calculate_compatibility(
                initiator_profile, target_profile, collaboration_request.collaboration_type
            )
            
            collaboration_request.compatibility_score = compatibility.compatibility_score
            collaboration_request.match_quality = compatibility.match_quality
            collaboration_request.ai_reasoning = compatibility.reasoning
            
            # Sauvegarde de la demande
            request_id = await self._save_collaboration_request(collaboration_request)
            
            # Notification au destinataire
            await self._send_collaboration_request_notification(collaboration_request)
            
            # Analytics
            await self._track_collaboration_request(collaboration_request)
            
            return {
                "request_id": request_id,
                "status": "sent",
                "compatibility_score": compatibility.compatibility_score,
                "expires_at": collaboration_request.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement demande collaboration: {str(e)}")
            raise

    async def manage_collaboration_project(
        self,
        project_id: str,
        action: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Gère un projet de collaboration (mise à jour, jalons, etc.)"""
        async with self.db_pool.acquire() as conn:
            project = await conn.fetchrow("""
                SELECT * FROM collaboration_projects 
                WHERE id = $1
            """, project_id)
            
            if not project:
                raise ValueError(f"Projet {project_id} non trouvé")
            
            result = {}
            
            if action == "update_milestone":
                result = await self._update_project_milestone(project, data)
            elif action == "add_resource":
                result = await self._add_shared_resource(project, data)
            elif action == "update_timeline":
                result = await self._update_project_timeline(project, data)
            elif action == "finalize":
                result = await self._finalize_collaboration(project)
            else:
                raise ValueError(f"Action {action} non supportée")
            
            # Notification participants
            await self._notify_project_participants(project, action, result)
            
            return result

    async def get_collaboration_analytics(self, user_id: str) -> Dict[str, Any]:
        """Récupère les analytics de collaboration pour un utilisateur"""
        async with self.db_pool.acquire() as conn:
            # Statistiques collaborations
            collab_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_collaborations,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'in_progress') as active,
                    AVG(
                        CASE 
                            WHEN status = 'completed' 
                            THEN EXTRACT(DAYS FROM completed_at - created_at)
                        END
                    ) as avg_completion_days
                FROM collaboration_projects 
                WHERE $1 = ANY(participants)
            """, user_id)
            
            # Types de collaboration préférés
            collab_types = await conn.fetch("""
                SELECT 
                    collaboration_type,
                    COUNT(*) as count,
                    AVG(compatibility_score) as avg_compatibility
                FROM collaboration_opportunities 
                WHERE (initiator_id = $1 OR target_id = $1)
                AND status = 'completed'
                GROUP BY collaboration_type
                ORDER BY count DESC
            """, user_id)
            
            # Partenaires fréquents
            frequent_partners = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN initiator_id = $1 THEN target_id 
                        ELSE initiator_id 
                    END as partner_id,
                    COUNT(*) as collaboration_count
                FROM collaboration_opportunities 
                WHERE (initiator_id = $1 OR target_id = $1)
                AND status = 'completed'
                GROUP BY partner_id
                HAVING COUNT(*) > 1
                ORDER BY collaboration_count DESC
                LIMIT 10
            """, user_id)
            
            # Score de réputation
            reputation = await self._calculate_reputation_score(user_id)
            
            return {
                "statistics": dict(collab_stats) if collab_stats else {},
                "preferred_types": [dict(ct) for ct in collab_types],
                "frequent_partners": [dict(fp) for fp in frequent_partners],
                "reputation_score": reputation,
                "success_rate": await self._calculate_success_rate(user_id),
                "network_reach": await self._calculate_network_reach(user_id)
            }

    # Méthodes utilitaires privées
    async def _get_artist_profile(self, user_id: str) -> ArtistProfile:
        """Récupère le profil artiste complet pour matching"""
        async with self.db_pool.acquire() as conn:
            profile_data = await conn.fetchrow("""
                SELECT 
                    u.id, u.username, u.location,
                    ap.genres, ap.skills, ap.languages,
                    ap.collaboration_preferences, ap.social_metrics,
                    ap.music_style_vector, ap.reputation_score,
                    ap.response_rate, ap.completion_rate
                FROM users u
                LEFT JOIN artist_profiles ap ON u.id = ap.user_id
                WHERE u.id = $1
            """, user_id)
            
            if not profile_data:
                raise ValueError(f"Profil artiste {user_id} non trouvé")
            
            return ArtistProfile(
                user_id=profile_data['id'],
                artist_name=profile_data['username'],
                genres=[Genre(g) for g in (profile_data['genres'] or [])],
                skills=profile_data['skills'] or [],
                location=profile_data['location'] or '',
                languages=profile_data['languages'] or [],
                collaboration_preferences=profile_data['collaboration_preferences'] or {},
                social_metrics=profile_data['social_metrics'] or {},
                music_style_vector=profile_data['music_style_vector'] or [],
                reputation_score=profile_data['reputation_score'] or 5.0,
                response_rate=profile_data['response_rate'] or 1.0,
                completion_rate=profile_data['completion_rate'] or 1.0
            )

    async def _calculate_compatibility(
        self,
        profile1: ArtistProfile,
        profile2: ArtistProfile,
        collaboration_type: CollaborationType
    ) -> Dict[str, Any]:
        """Calcule la compatibilité entre deux artistes pour un type de collaboration"""
        
        # Compatibilité genres
        genre_score = self._calculate_genre_compatibility(profile1.genres, profile2.genres)
        
        # Complémentarité compétences
        skill_score = self._calculate_skill_complementarity(profile1.skills, profile2.skills)
        
        # Proximité géographique
        location_score = self._calculate_location_proximity(profile1.location, profile2.location)
        
        # Métriques sociales
        social_score = self._calculate_social_compatibility(
            profile1.social_metrics, profile2.social_metrics
        )
        
        # Score de réputation
        reputation_score = min(profile1.reputation_score, profile2.reputation_score) / 5.0
        
        # Historique collaborations
        history_score = self._calculate_collaboration_history_score(profile1, profile2)
        
        # Score composite pondéré
        final_score = (
            genre_score * self.matching_weights["genre_compatibility"] +
            skill_score * self.matching_weights["skill_complementarity"] +
            location_score * self.matching_weights["location_proximity"] +
            social_score * self.matching_weights["social_metrics"] +
            reputation_score * self.matching_weights["reputation_score"] +
            history_score * self.matching_weights["collaboration_history"]
        )
        
        # Détermination qualité match
        if final_score >= 0.95:
            quality = MatchQuality.PERFECT
        elif final_score >= 0.80:
            quality = MatchQuality.EXCELLENT
        elif final_score >= 0.60:
            quality = MatchQuality.GOOD
        elif final_score >= 0.40:
            quality = MatchQuality.FAIR
        else:
            quality = MatchQuality.POOR
        
        # Génération raisonnement IA
        reasoning = self._generate_ai_reasoning(
            profile1, profile2, collaboration_type, {
                "genre": genre_score,
                "skills": skill_score,
                "location": location_score,
                "social": social_score,
                "reputation": reputation_score
            }
        )
        
        return {
            "compatibility_score": final_score,
            "match_quality": quality,
            "reasoning": reasoning,
            "score_breakdown": {
                "genre_compatibility": genre_score,
                "skill_complementarity": skill_score,
                "location_proximity": location_score,
                "social_compatibility": social_score,
                "reputation_score": reputation_score,
                "history_score": history_score
            }
        }

    def _calculate_genre_compatibility(self, genres1: List[Genre], genres2: List[Genre]) -> float:
        """Calcule la compatibilité entre genres musicaux"""
        if not genres1 or not genres2:
            return 0.5  # Score neutre
        
        max_similarity = 0.0
        
        for g1 in genres1:
            for g2 in genres2:
                if g1 == g2:
                    max_similarity = max(max_similarity, 1.0)
                else:
                    # Utilisation matrice de similarité
                    idx1 = list(Genre).index(g1)
                    idx2 = list(Genre).index(g2)
                    similarity = self.ml_models["genre_similarity_matrix"][idx1][idx2]
                    max_similarity = max(max_similarity, similarity)
        
        return max_similarity

    def _generate_ai_reasoning(
        self,
        profile1: ArtistProfile,
        profile2: ArtistProfile,
        collaboration_type: CollaborationType,
        scores: Dict[str, float]
    ) -> str:
        """Génère le raisonnement IA pour expliquer le matching"""
        
        strengths = []
        
        if scores["genre"] > 0.7:
            strengths.append("genres musicaux très compatibles")
        if scores["skills"] > 0.7:
            strengths.append("compétences complémentaires parfaites")
        if scores["location"] > 0.8:
            strengths.append("proximité géographique favorable")
        if scores["reputation"] > 0.8:
            strengths.append("excellente réputation mutuelle")
        
        if not strengths:
            strengths.append("potentiel d'exploration créative intéressant")
        
        return f"Match recommandé grâce à: {', '.join(strengths)}. " \
               f"Cette collaboration {collaboration_type.value} pourrait créer " \
               f"une synergie unique entre vos styles artistiques."


# Export des classes principales
__all__ = [
    "CollaborationNotificationManager",
    "CollaborationOpportunity",
    "CollaborationProject",
    "ArtistProfile",
    "CollaborationType",
    "CollaborationStatus",
    "MatchQuality",
    "Genre"
]
