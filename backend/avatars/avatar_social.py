"""Avatar Social - Social & Collaboration

Système social et collaboration pour avatars avec réseau social,
collaborations multi-créateurs et communautés thématiques.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field


class RelationshipType(Enum):
    """Types de relations entre utilisateurs"""
    FOLLOWER = "follower"
    FOLLOWING = "following"
    FRIEND = "friend"
    COLLABORATOR = "collaborator"
    MENTOR = "mentor"
    MENTEE = "mentee"
    BUSINESS_PARTNER = "business_partner"
    BLOCKED = "blocked"


class CommunityType(Enum):
    """Types de communautés"""
    GENERAL = "general"
    FASHION = "fashion"
    MUSIC = "music"
    BUSINESS = "business"
    FITNESS = "fitness"
    TECHNOLOGY = "technology"
    ART = "art"
    GAMING = "gaming"
    EDUCATION = "education"
    LIFESTYLE = "lifestyle"


class CollaborationType(Enum):
    """Types de collaboration"""
    AVATAR_CREATION = "avatar_creation"
    CONTENT_CREATION = "content_creation"
    BRAND_PARTNERSHIP = "brand_partnership"
    EDUCATIONAL = "educational"
    CHARITY = "charity"
    COMPETITION = "competition"
    MENTORSHIP = "mentorship"
    RESEARCH = "research"


class ContentType(Enum):
    """Types de contenu social"""
    POST = "post"
    AVATAR_SHOWCASE = "avatar_showcase"
    TUTORIAL = "tutorial"
    COLLABORATION = "collaboration"
    REVIEW = "review"
    CHALLENGE = "challenge"
    LIVE_STREAM = "live_stream"
    STORY = "story"


class MatchingCriteria(Enum):
    """Critères de matching"""
    STYLE_SIMILARITY = "style_similarity"
    INTEREST_ALIGNMENT = "interest_alignment"
    SKILL_COMPLEMENT = "skill_complement"
    LOCATION_PROXIMITY = "location_proximity"
    LANGUAGE_MATCH = "language_match"
    EXPERIENCE_LEVEL = "experience_level"
    GOAL_ALIGNMENT = "goal_alignment"


@dataclass
class UserProfile:
    """Profil utilisateur social"""
    user_id: str
    username: str
    display_name: str
    bio: str = ""
    avatar_id: Optional[str] = None
    profile_image: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    location: Optional[str] = None
    experience_level: str = "beginner"
    goals: List[str] = field(default_factory=list)
    social_links: Dict[str, str] = field(default_factory=dict)
    verification_status: str = "unverified"
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    reputation_score: float = 0.0
    total_followers: int = 0
    total_following: int = 0


@dataclass 
class Relationship:
    """Relation entre utilisateurs"""
    relationship_id: str
    user_a_id: str
    user_b_id: str
    relationship_type: RelationshipType
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    notes: str = ""
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None


@dataclass
class Community:
    """Communauté d'utilisateurs"""
    community_id: str
    name: str
    description: str
    community_type: CommunityType
    creator_id: str
    moderators: List[str] = field(default_factory=list)
    members: Set[str] = field(default_factory=set)
    rules: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    privacy: str = "public"  # public, private, invite_only
    created_at: datetime = field(default_factory=datetime.now)
    member_count: int = 0
    activity_score: float = 0.0
    featured: bool = False


@dataclass
class SocialContent:
    """Contenu social"""
    content_id: str
    author_id: str
    community_id: Optional[str] = None
    content_type: ContentType = ContentType.POST
    title: str = ""
    description: str = ""
    media_urls: List[str] = field(default_factory=list)
    avatar_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    visibility: str = "public"
    collaboration_data: Optional[Dict[str, Any]] = None


@dataclass
class Collaboration:
    """Collaboration entre créateurs"""
    collaboration_id: str
    title: str
    description: str
    collaboration_type: CollaborationType
    creator_id: str
    participants: List[str] = field(default_factory=list)
    invited_users: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    timeline: Dict[str, str] = field(default_factory=dict)
    budget: Optional[float] = None
    status: str = "open"  # open, in_progress, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    collaboration_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchingProfile:
    """Profil pour le matching intelligent"""
    user_id: str
    style_preferences: Dict[str, float] = field(default_factory=dict)
    collaboration_interests: List[CollaborationType] = field(default_factory=list)
    preferred_community_types: List[CommunityType] = field(default_factory=list)
    matching_criteria: Dict[MatchingCriteria, float] = field(default_factory=dict)
    availability: Dict[str, bool] = field(default_factory=dict)
    portfolio_strength: float = 0.0
    communication_style: str = "balanced"
    preferred_project_size: str = "medium"


class AvatarSocialNetwork:
    """Réseau social avatars"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.users: Dict[str, UserProfile] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.content: Dict[str, SocialContent] = {}
        self.feed_cache: Dict[str, List[str]] = {}
    
    async def create_user_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Création d'un profil utilisateur"""
        try:
            profile = UserProfile(
                user_id=profile_data['user_id'],
                username=profile_data['username'],
                display_name=profile_data['display_name'],
                bio=profile_data.get('bio', ''),
                avatar_id=profile_data.get('avatar_id'),
                interests=profile_data.get('interests', []),
                skills=profile_data.get('skills', []),
                languages=profile_data.get('languages', ['en']),
                location=profile_data.get('location'),
                experience_level=profile_data.get('experience_level', 'beginner'),
                goals=profile_data.get('goals', []),
                social_links=profile_data.get('social_links', {}),
                privacy_settings=profile_data.get('privacy_settings', {
                    'profile_visible': True,
                    'allow_messages': True,
                    'show_activity': True
                })
            )
            
            self.users[profile.user_id] = profile
            self.logger.info(f"Profil créé: {profile.username} ({profile.user_id})")
            return profile
            
        except Exception as e:
            self.logger.error(f"Erreur création profil: {e}")
            raise
    
    async def follow_user(self, follower_id: str, following_id: str) -> Relationship:
        """Suivre un utilisateur"""
        try:
            if follower_id == following_id:
                raise ValueError("Un utilisateur ne peut pas se suivre lui-même")
            
            # Vérifier que les utilisateurs existent
            if follower_id not in self.users or following_id not in self.users:
                raise ValueError("Utilisateur non trouvé")
            
            # Vérifier si la relation existe déjà
            existing_rel = await self._find_relationship(follower_id, following_id, RelationshipType.FOLLOWING)
            if existing_rel:
                raise ValueError("Relation déjà existante")
            
            # Créer la relation de suivi
            follow_rel = Relationship(
                relationship_id=str(uuid.uuid4()),
                user_a_id=follower_id,
                user_b_id=following_id,
                relationship_type=RelationshipType.FOLLOWING
            )
            
            # Créer la relation inverse (follower)
            follower_rel = Relationship(
                relationship_id=str(uuid.uuid4()),
                user_a_id=following_id,
                user_b_id=follower_id,
                relationship_type=RelationshipType.FOLLOWER
            )
            
            self.relationships[follow_rel.relationship_id] = follow_rel
            self.relationships[follower_rel.relationship_id] = follower_rel
            
            # Mettre à jour les compteurs
            self.users[follower_id].total_following += 1
            self.users[following_id].total_followers += 1
            
            # Invalider le cache de feed
            if follower_id in self.feed_cache:
                del self.feed_cache[follower_id]
            
            self.logger.info(f"{follower_id} suit maintenant {following_id}")
            return follow_rel
            
        except Exception as e:
            self.logger.error(f"Erreur suivi utilisateur: {e}")
            raise
    
    async def _find_relationship(self, user_a: str, user_b: str, 
                               rel_type: RelationshipType) -> Optional[Relationship]:
        """Recherche d'une relation spécifique"""
        for rel in self.relationships.values():
            if (rel.user_a_id == user_a and rel.user_b_id == user_b and 
                rel.relationship_type == rel_type):
                return rel
        return None
    
    async def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Arrêter de suivre un utilisateur"""
        try:
            # Trouver les relations à supprimer
            follow_rel = await self._find_relationship(follower_id, following_id, RelationshipType.FOLLOWING)
            follower_rel = await self._find_relationship(following_id, follower_id, RelationshipType.FOLLOWER)
            
            if not follow_rel or not follower_rel:
                return False
            
            # Supprimer les relations
            del self.relationships[follow_rel.relationship_id]
            del self.relationships[follower_rel.relationship_id]
            
            # Mettre à jour les compteurs
            self.users[follower_id].total_following -= 1
            self.users[following_id].total_followers -= 1
            
            # Invalider le cache de feed
            if follower_id in self.feed_cache:
                del self.feed_cache[follower_id]
            
            self.logger.info(f"{follower_id} ne suit plus {following_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur arrêt suivi: {e}")
            return False
    
    async def create_content(self, content_data: Dict[str, Any]) -> SocialContent:
        """Création de contenu social"""
        try:
            content = SocialContent(
                content_id=str(uuid.uuid4()),
                author_id=content_data['author_id'],
                community_id=content_data.get('community_id'),
                content_type=ContentType(content_data.get('type', 'post')),
                title=content_data.get('title', ''),
                description=content_data['description'],
                media_urls=content_data.get('media_urls', []),
                avatar_id=content_data.get('avatar_id'),
                tags=content_data.get('tags', []),
                visibility=content_data.get('visibility', 'public'),
                collaboration_data=content_data.get('collaboration_data')
            )
            
            self.content[content.content_id] = content
            
            # Invalider les caches de feed des followers
            followers = await self.get_followers(content.author_id)
            for follower_id in followers:
                if follower_id in self.feed_cache:
                    del self.feed_cache[follower_id]
            
            self.logger.info(f"Contenu créé: {content.title} par {content.author_id}")
            return content
            
        except Exception as e:
            self.logger.error(f"Erreur création contenu: {e}")
            raise
    
    async def get_followers(self, user_id: str) -> List[str]:
        """Récupération des followers d'un utilisateur"""
        followers = []
        for rel in self.relationships.values():
            if (rel.user_b_id == user_id and 
                rel.relationship_type == RelationshipType.FOLLOWER and
                rel.status == "active"):
                followers.append(rel.user_a_id)
        return followers
    
    async def get_following(self, user_id: str) -> List[str]:
        """Récupération des utilisateurs suivis"""
        following = []
        for rel in self.relationships.values():
            if (rel.user_a_id == user_id and 
                rel.relationship_type == RelationshipType.FOLLOWING and
                rel.status == "active"):
                following.append(rel.user_b_id)
        return following
    
    async def generate_feed(self, user_id: str, limit: int = 20) -> List[SocialContent]:
        """Génération du feed personnalisé"""
        try:
            # Vérifier le cache
            if user_id in self.feed_cache:
                cached_content_ids = self.feed_cache[user_id][:limit]
                return [self.content[cid] for cid in cached_content_ids if cid in self.content]
            
            # Récupérer les utilisateurs suivis
            following = await self.get_following(user_id)
            following.append(user_id)  # Inclure son propre contenu
            
            # Récupérer le contenu pertinent
            relevant_content = []
            for content in self.content.values():
                if (content.author_id in following and 
                    content.visibility == "public" and
                    content.created_at > datetime.now() - timedelta(days=30)):
                    relevant_content.append(content)
            
            # Tri par pertinence (score basé sur interactions et date)
            def calculate_relevance_score(content: SocialContent) -> float:
                time_factor = 1.0 / (1 + (datetime.now() - content.created_at).days)
                interaction_factor = (content.likes_count * 1.0 + 
                                    content.comments_count * 2.0 + 
                                    content.shares_count * 3.0)
                return time_factor * (1 + interaction_factor)
            
            relevant_content.sort(key=calculate_relevance_score, reverse=True)
            
            # Mettre en cache
            self.feed_cache[user_id] = [c.content_id for c in relevant_content]
            
            return relevant_content[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur génération feed: {e}")
            return []
    
    async def like_content(self, user_id: str, content_id: str) -> bool:
        """Liker du contenu"""
        try:
            if content_id not in self.content:
                return False
            
            content = self.content[content_id]
            content.likes_count += 1
            
            # Enregistrer l'interaction dans la relation
            author_rel = await self._find_relationship(user_id, content.author_id, RelationshipType.FOLLOWING)
            if author_rel:
                author_rel.interaction_count += 1
                author_rel.last_interaction = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur like contenu: {e}")
            return False
    
    async def search_users(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[UserProfile]:
        """Recherche d'utilisateurs"""
        try:
            results = []
            query_lower = query.lower()
            
            for user in self.users.values():
                if not user.privacy_settings.get('profile_visible', True):
                    continue
                
                # Recherche dans nom d'utilisateur, nom d'affichage, bio
                if (query_lower in user.username.lower() or
                    query_lower in user.display_name.lower() or
                    query_lower in user.bio.lower() or
                    any(query_lower in interest.lower() for interest in user.interests) or
                    any(query_lower in skill.lower() for skill in user.skills)):
                    
                    # Application des filtres
                    if filters:
                        if 'experience_level' in filters and user.experience_level != filters['experience_level']:
                            continue
                        if 'location' in filters and user.location != filters['location']:
                            continue
                        if 'min_followers' in filters and user.total_followers < filters['min_followers']:
                            continue
                    
                    results.append(user)
            
            # Tri par pertinence (followers + reputation)
            results.sort(key=lambda u: u.total_followers + u.reputation_score * 100, reverse=True)
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur recherche utilisateurs: {e}")
            return []


class CollaborationEngine:
    """Moteur collaboration créateurs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collaborations: Dict[str, Collaboration] = {}
        self.collaboration_history: Dict[str, List[str]] = {}
    
    async def create_collaboration(self, collaboration_data: Dict[str, Any]) -> Collaboration:
        """Création d'une collaboration"""
        try:
            collaboration = Collaboration(
                collaboration_id=str(uuid.uuid4()),
                title=collaboration_data['title'],
                description=collaboration_data['description'],
                collaboration_type=CollaborationType(collaboration_data['type']),
                creator_id=collaboration_data['creator_id'],
                requirements=collaboration_data.get('requirements', []),
                deliverables=collaboration_data.get('deliverables', []),
                timeline=collaboration_data.get('timeline', {}),
                budget=collaboration_data.get('budget'),
                deadline=collaboration_data.get('deadline')
            )
            
            self.collaborations[collaboration.collaboration_id] = collaboration
            
            # Initialiser l'historique pour le créateur
            if collaboration.creator_id not in self.collaboration_history:
                self.collaboration_history[collaboration.creator_id] = []
            self.collaboration_history[collaboration.creator_id].append(collaboration.collaboration_id)
            
            self.logger.info(f"Collaboration créée: {collaboration.title}")
            return collaboration
            
        except Exception as e:
            self.logger.error(f"Erreur création collaboration: {e}")
            raise
    
    async def join_collaboration(self, collaboration_id: str, user_id: str) -> bool:
        """Rejoindre une collaboration"""
        try:
            if collaboration_id not in self.collaborations:
                return False
            
            collaboration = self.collaborations[collaboration_id]
            
            if collaboration.status != "open":
                return False
            
            if user_id in collaboration.participants:
                return False  # Déjà participant
            
            collaboration.participants.append(user_id)
            
            # Ajouter à l'historique
            if user_id not in self.collaboration_history:
                self.collaboration_history[user_id] = []
            self.collaboration_history[user_id].append(collaboration_id)
            
            self.logger.info(f"Utilisateur {user_id} a rejoint la collaboration {collaboration.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur rejoindre collaboration: {e}")
            return False
    
    async def invite_to_collaboration(self, collaboration_id: str, inviter_id: str, 
                                    invited_user_id: str) -> bool:
        """Inviter à une collaboration"""
        try:
            if collaboration_id not in self.collaborations:
                return False
            
            collaboration = self.collaborations[collaboration_id]
            
            # Vérifier que l'inviteur est le créateur ou un participant
            if inviter_id not in [collaboration.creator_id] + collaboration.participants:
                return False
            
            if invited_user_id not in collaboration.invited_users:
                collaboration.invited_users.append(invited_user_id)
            
            self.logger.info(f"Invitation envoyée à {invited_user_id} pour {collaboration.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur invitation collaboration: {e}")
            return False
    
    async def get_collaboration_opportunities(self, user_id: str) -> List[Collaboration]:
        """Récupération des opportunités de collaboration"""
        try:
            opportunities = []
            
            for collaboration in self.collaborations.values():
                if (collaboration.status == "open" and
                    collaboration.creator_id != user_id and
                    user_id not in collaboration.participants):
                    opportunities.append(collaboration)
            
            # Tri par date de création (plus récent en premier)
            opportunities.sort(key=lambda c: c.created_at, reverse=True)
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Erreur récupération opportunités: {e}")
            return []
    
    async def complete_collaboration(self, collaboration_id: str, 
                                   completion_data: Dict[str, Any]) -> bool:
        """Finaliser une collaboration"""
        try:
            if collaboration_id not in self.collaborations:
                return False
            
            collaboration = self.collaborations[collaboration_id]
            collaboration.status = "completed"
            collaboration.collaboration_data.update({
                'completion_date': datetime.now().isoformat(),
                'final_deliverables': completion_data.get('deliverables', []),
                'success_rating': completion_data.get('rating', 5.0),
                'feedback': completion_data.get('feedback', '')
            })
            
            self.logger.info(f"Collaboration complétée: {collaboration.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur finalisation collaboration: {e}")
            return False


class AvatarMatching:
    """Système matching intelligent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.matching_profiles: Dict[str, MatchingProfile] = {}
        self.match_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def create_matching_profile(self, profile_data: Dict[str, Any]) -> MatchingProfile:
        """Création d'un profil de matching"""
        try:
            profile = MatchingProfile(
                user_id=profile_data['user_id'],
                style_preferences=profile_data.get('style_preferences', {}),
                collaboration_interests=[
                    CollaborationType(t) for t in profile_data.get('collaboration_interests', [])
                ],
                preferred_community_types=[
                    CommunityType(t) for t in profile_data.get('community_types', [])
                ],
                matching_criteria={
                    MatchingCriteria(k): v for k, v in profile_data.get('criteria', {}).items()
                },
                availability=profile_data.get('availability', {}),
                portfolio_strength=profile_data.get('portfolio_strength', 0.0),
                communication_style=profile_data.get('communication_style', 'balanced'),
                preferred_project_size=profile_data.get('project_size', 'medium')
            )
            
            self.matching_profiles[profile.user_id] = profile
            return profile
            
        except Exception as e:
            self.logger.error(f"Erreur création profil matching: {e}")
            raise
    
    async def find_matches(self, user_id: str, match_type: str = "collaboration") -> List[Dict[str, Any]]:
        """Recherche de matches"""
        try:
            if user_id not in self.matching_profiles:
                return []
            
            user_profile = self.matching_profiles[user_id]
            matches = []
            
            for other_user_id, other_profile in self.matching_profiles.items():
                if other_user_id == user_id:
                    continue
                
                match_score = await self._calculate_match_score(user_profile, other_profile, match_type)
                
                if match_score > 0.3:  # Seuil de compatibilité
                    matches.append({
                        'user_id': other_user_id,
                        'match_score': match_score,
                        'match_reasons': await self._get_match_reasons(user_profile, other_profile),
                        'compatibility_breakdown': await self._get_compatibility_breakdown(
                            user_profile, other_profile
                        )
                    })
            
            # Tri par score de compatibilité
            matches.sort(key=lambda m: m['match_score'], reverse=True)
            return matches[:10]  # Top 10 matches
            
        except Exception as e:
            self.logger.error(f"Erreur recherche matches: {e}")
            return []
    
    async def _calculate_match_score(self, profile1: MatchingProfile, 
                                   profile2: MatchingProfile, match_type: str) -> float:
        """Calcul du score de compatibilité"""
        score = 0.0
        
        # Intérêts de collaboration communs
        common_interests = set(profile1.collaboration_interests) & set(profile2.collaboration_interests)
        if common_interests:
            score += len(common_interests) * 0.2
        
        # Complémentarité des compétences
        skill_complement = abs(profile1.portfolio_strength - profile2.portfolio_strength)
        if 0.2 <= skill_complement <= 0.6:  # Complémentarité idéale
            score += 0.3
        
        # Préférences de style similaires
        style_similarity = await self._calculate_style_similarity(profile1, profile2)
        score += style_similarity * 0.2
        
        # Disponibilité compatible
        availability_match = await self._check_availability_compatibility(profile1, profile2)
        score += availability_match * 0.15
        
        # Communication style compatible
        if profile1.communication_style == profile2.communication_style:
            score += 0.1
        elif abs(hash(profile1.communication_style) - hash(profile2.communication_style)) % 3 == 0:
            score += 0.05  # Styles complémentaires
        
        # Taille de projet préférée
        if profile1.preferred_project_size == profile2.preferred_project_size:
            score += 0.05
        
        return min(1.0, score)
    
    async def _calculate_style_similarity(self, profile1: MatchingProfile, 
                                        profile2: MatchingProfile) -> float:
        """Calcul de la similarité de style"""
        if not profile1.style_preferences or not profile2.style_preferences:
            return 0.0
        
        common_styles = set(profile1.style_preferences.keys()) & set(profile2.style_preferences.keys())
        if not common_styles:
            return 0.0
        
        similarity_sum = 0.0
        for style in common_styles:
            diff = abs(profile1.style_preferences[style] - profile2.style_preferences[style])
            similarity_sum += 1.0 - diff
        
        return similarity_sum / len(common_styles)
    
    async def _check_availability_compatibility(self, profile1: MatchingProfile, 
                                              profile2: MatchingProfile) -> float:
        """Vérification de la compatibilité de disponibilité"""
        if not profile1.availability or not profile2.availability:
            return 0.5  # Score neutre si pas d'info
        
        common_slots = 0
        total_slots = 0
        
        for time_slot in set(profile1.availability.keys()) | set(profile2.availability.keys()):
            total_slots += 1
            if (profile1.availability.get(time_slot, False) and 
                profile2.availability.get(time_slot, False)):
                common_slots += 1
        
        return common_slots / total_slots if total_slots > 0 else 0.0
    
    async def _get_match_reasons(self, profile1: MatchingProfile, 
                               profile2: MatchingProfile) -> List[str]:
        """Raisons du match"""
        reasons = []
        
        common_interests = set(profile1.collaboration_interests) & set(profile2.collaboration_interests)
        if common_interests:
            reasons.append(f"Intérêts communs: {', '.join([i.value for i in common_interests])}")
        
        skill_complement = abs(profile1.portfolio_strength - profile2.portfolio_strength)
        if 0.2 <= skill_complement <= 0.6:
            reasons.append("Compétences complémentaires")
        
        style_similarity = await self._calculate_style_similarity(profile1, profile2)
        if style_similarity > 0.7:
            reasons.append("Styles artistiques similaires")
        
        if profile1.communication_style == profile2.communication_style:
            reasons.append("Style de communication compatible")
        
        return reasons
    
    async def _get_compatibility_breakdown(self, profile1: MatchingProfile, 
                                         profile2: MatchingProfile) -> Dict[str, float]:
        """Détail de la compatibilité"""
        return {
            'style_similarity': await self._calculate_style_similarity(profile1, profile2),
            'availability_match': await self._check_availability_compatibility(profile1, profile2),
            'interest_overlap': len(set(profile1.collaboration_interests) & 
                                  set(profile2.collaboration_interests)) / 
                               max(1, len(profile1.collaboration_interests)),
            'skill_complementarity': 1.0 - abs(profile1.portfolio_strength - profile2.portfolio_strength)
        }


class CommunityManager:
    """Gestion communautés avatars"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.communities: Dict[str, Community] = {}
        self._initialize_default_communities()
    
    def _initialize_default_communities(self):
        """Initialisation des communautés par défaut"""
        default_communities = [
            {
                'name': 'Fashion Avatars',
                'description': 'Communauté dédiée aux avatars mode et lifestyle',
                'type': CommunityType.FASHION,
                'creator_id': 'system',
                'rules': [
                    'Respecter les autres membres',
                    'Partager uniquement du contenu original',
                    'Pas de spam ou publicité non autorisée'
                ],
                'featured': True
            },
            {
                'name': 'Business Professionals',
                'description': 'Réseau d\'avatars pour professionnels et entrepreneurs',
                'type': CommunityType.BUSINESS,
                'creator_id': 'system',
                'rules': [
                    'Contenu professionnel uniquement',
                    'Networking constructif',
                    'Partage d\'expériences et conseils'
                ],
                'featured': True
            },
            {
                'name': 'Creative Artists',
                'description': 'Espace pour artistes et créateurs d\'avatars',
                'type': CommunityType.ART,
                'creator_id': 'system',
                'rules': [
                    'Créativité et originalité encouragées',
                    'Feedback constructif',
                    'Respect de la propriété intellectuelle'
                ],
                'featured': True
            }
        ]
        
        for comm_data in default_communities:
            community = Community(
                community_id=str(uuid.uuid4()),
                name=comm_data['name'],
                description=comm_data['description'],
                community_type=comm_data['type'],
                creator_id=comm_data['creator_id'],
                rules=comm_data['rules'],
                featured=comm_data.get('featured', False)
            )
            self.communities[community.community_id] = community
    
    async def create_community(self, community_data: Dict[str, Any]) -> Community:
        """Création d'une communauté"""
        try:
            community = Community(
                community_id=str(uuid.uuid4()),
                name=community_data['name'],
                description=community_data['description'],
                community_type=CommunityType(community_data['type']),
                creator_id=community_data['creator_id'],
                moderators=community_data.get('moderators', []),
                rules=community_data.get('rules', []),
                tags=community_data.get('tags', []),
                privacy=community_data.get('privacy', 'public')
            )
            
            self.communities[community.community_id] = community
            self.logger.info(f"Communauté créée: {community.name}")
            return community
            
        except Exception as e:
            self.logger.error(f"Erreur création communauté: {e}")
            raise
    
    async def join_community(self, community_id: str, user_id: str) -> bool:
        """Rejoindre une communauté"""
        try:
            if community_id not in self.communities:
                return False
            
            community = self.communities[community_id]
            
            if user_id in community.members:
                return False  # Déjà membre
            
            community.members.add(user_id)
            community.member_count = len(community.members)
            
            self.logger.info(f"Utilisateur {user_id} a rejoint {community.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur rejoindre communauté: {e}")
            return False
    
    async def get_community_recommendations(self, user_id: str, 
                                          user_interests: List[str]) -> List[Community]:
        """Recommandations de communautés"""
        try:
            recommendations = []
            
            for community in self.communities.values():
                if user_id in community.members:
                    continue  # Déjà membre
                
                if community.privacy == "private":
                    continue  # Pas accessible
                
                # Score basé sur les intérêts et l'activité
                score = 0.0
                
                # Correspondance d'intérêts
                community_keywords = [community.name.lower(), community.description.lower()] + community.tags
                for interest in user_interests:
                    if any(interest.lower() in keyword for keyword in community_keywords):
                        score += 1.0
                
                # Facteur d'activité et popularité
                score += community.activity_score * 0.1
                score += min(1.0, community.member_count / 1000) * 0.5
                
                if community.featured:
                    score += 0.3
                
                if score > 0:
                    recommendations.append((community, score))
            
            # Tri par score
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return [comm for comm, score in recommendations[:5]]
            
        except Exception as e:
            self.logger.error(f"Erreur recommandations communautés: {e}")
            return []


__all__ = [
    'AvatarSocialNetwork',
    'CollaborationEngine',
    'AvatarMatching', 
    'CommunityManager',
    'UserProfile',
    'Relationship',
    'RelationshipType',
    'Community',
    'CommunityType',
    'SocialContent',
    'ContentType',
    'Collaboration',
    'CollaborationType',
    'MatchingProfile',
    'MatchingCriteria'
]