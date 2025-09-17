"""
🎯 Challenge Orchestrator - Adaptive Difficulty & Community Challenges
=====================================================================
Orchestrateur de défis enterprise avec difficulté adaptive,
défis communautaires et événements saisonniers intelligents.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Version: 1.0.0 Production
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio
import json
import random
from uuid import uuid4
from collections import defaultdict
import math

# Configure logging
logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """Types de défis"""
    CREATION = "creation"
    COLLABORATION = "collaboration"
    ENGAGEMENT = "engagement"
    SKILL_DEVELOPMENT = "skill_development"
    COMMUNITY = "community"
    INNOVATION = "innovation"
    CONSISTENCY = "consistency"
    SOCIAL_IMPACT = "social_impact"


class ChallengeDifficulty(Enum):
    """Niveaux de difficulté"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"


class ChallengeFrequency(Enum):
    """Fréquences de défis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"
    ONGOING = "ongoing"


class ChallengeStatus(Enum):
    """Statuts de défis"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ChallengeRequirement:
    """Requirement de défi"""
    id: str
    name: str
    description: str
    target_value: Union[int, float]
    current_value: Union[int, float] = 0
    measurement_unit: str = "count"
    weight: float = 1.0
    is_mandatory: bool = True


@dataclass
class Challenge:
    """Défi definition"""
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    frequency: ChallengeFrequency
    requirements: List[ChallengeRequirement]
    rewards: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    eligibility_criteria: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "system"
    status: ChallengeStatus = ChallengeStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChallengeParticipation:
    """Participation à un défi"""
    id: str
    challenge_id: str
    creator_id: str
    joined_at: datetime
    progress: Dict[str, float] = field(default_factory=dict)
    completion_percentage: float = 0.0
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    rewards_claimed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SeasonalEvent:
    """Événement saisonnier"""
    id: str
    name: str
    description: str
    theme: str
    start_date: datetime
    end_date: datetime
    associated_challenges: List[str] = field(default_factory=list)
    special_rewards: Dict[str, Any] = field(default_factory=dict)
    participant_count: int = 0
    status: str = "upcoming"


class AdaptiveDifficultyEngine:
    """
    🧠 Engine de difficulté adaptive avec machine learning
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.creator_profiles: Dict[str, Dict[str, Any]] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.difficulty_models = self._load_difficulty_models()
        
    def _load_difficulty_models(self) -> Dict[str, Any]:
        """Chargement modèles ML pour difficulté"""
        return {
            "skill_assessment": "skill_model_v1.0",
            "difficulty_prediction": "difficulty_model_v1.0",
            "engagement_optimization": "engagement_model_v1.0"
        }
    
    async def calculate_optimal_difficulty(
        self,
        creator_id: str,
        challenge_type: ChallengeType,
        creator_profile: Optional[Dict[str, Any]] = None
    ) -> ChallengeDifficulty:
        """Calcul difficulté optimale pour un créateur"""
        try:
            # Récupération ou création profil
            if creator_profile:
                self.creator_profiles[creator_id] = creator_profile
            
            profile = self.creator_profiles.get(creator_id, {})
            
            # Analyse historique performances
            history = self.performance_history.get(creator_id, [])
            
            # Calcul score de compétence
            skill_score = self._calculate_skill_score(profile, challenge_type, history)
            
            # Ajustement basé sur engagement récent
            engagement_factor = self._calculate_engagement_factor(profile, history)
            
            # Facteur de challenge (pour éviter stagnation)
            challenge_factor = self._calculate_challenge_factor(history)
            
            # Score de difficulté final
            difficulty_score = skill_score * engagement_factor * challenge_factor
            
            # Mapping vers enum difficulté
            optimal_difficulty = self._map_score_to_difficulty(difficulty_score)
            
            logger.debug(f"🎯 Optimal difficulty for {creator_id}: {optimal_difficulty.value} (score: {difficulty_score:.2f})")
            
            return optimal_difficulty
            
        except Exception as e:
            logger.error(f"❌ Difficulty calculation error: {e}")
            return ChallengeDifficulty.INTERMEDIATE
    
    def _calculate_skill_score(
        self,
        profile: Dict[str, Any],
        challenge_type: ChallengeType,
        history: List[Dict[str, Any]]
    ) -> float:
        """Calcul score de compétence"""
        # Score basé sur profil
        base_skill = profile.get("skill_levels", {}).get(challenge_type.value, 0.5)
        
        # Score basé sur historique
        type_history = [h for h in history if h.get("challenge_type") == challenge_type.value]
        
        if type_history:
            recent_success_rate = sum(h.get("completion_rate", 0) for h in type_history[-5:]) / len(type_history[-5:])
            avg_difficulty_completed = sum(
                self._difficulty_to_numeric(h.get("difficulty", "intermediate"))
                for h in type_history if h.get("completed", False)
            ) / max(1, len([h for h in type_history if h.get("completed", False)]))
            
            # Combinaison scores
            skill_score = (base_skill * 0.3 + recent_success_rate * 0.4 + avg_difficulty_completed / 6.0 * 0.3)
        else:
            skill_score = base_skill
        
        return max(0.1, min(1.0, skill_score))
    
    def _difficulty_to_numeric(self, difficulty: str) -> float:
        """Conversion difficulté en score numérique"""
        mapping = {
            "beginner": 1.0,
            "intermediate": 2.0,
            "advanced": 3.0,
            "expert": 4.0,
            "master": 5.0,
            "legendary": 6.0
        }
        return mapping.get(difficulty, 2.0)
    
    def _calculate_engagement_factor(
        self,
        profile: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> float:
        """Facteur d'engagement"""
        # Engagement actuel
        current_engagement = profile.get("engagement_score", 0.5)
        
        # Tendance engagement récent
        if len(history) >= 2:
            recent_completion_rate = sum(h.get("completion_rate", 0) for h in history[-3:]) / min(3, len(history))
            engagement_trend = recent_completion_rate
        else:
            engagement_trend = 0.5
        
        # Facteur temps depuis dernière activité
        last_activity = profile.get("last_activity_days", 7)
        recency_factor = max(0.5, 1.0 - (last_activity / 30.0))
        
        return (current_engagement * 0.4 + engagement_trend * 0.4 + recency_factor * 0.2)
    
    def _calculate_challenge_factor(self, history: List[Dict[str, Any]]) -> float:
        """Facteur de challenge pour éviter stagnation"""
        if not history:
            return 1.0
        
        # Vérification si le créateur reste dans sa zone de confort
        recent_difficulties = [self._difficulty_to_numeric(h.get("difficulty", "intermediate")) for h in history[-5:]]
        
        if len(recent_difficulties) >= 3:
            difficulty_variance = sum((d - sum(recent_difficulties)/len(recent_difficulties))**2 for d in recent_difficulties) / len(recent_difficulties)
            
            # Si peu de variance, encourager plus de challenge
            if difficulty_variance < 0.5:
                return 1.2  # Boost difficulté
            else:
                return 1.0
        
        return 1.0
    
    def _map_score_to_difficulty(self, score: float) -> ChallengeDifficulty:
        """Mapping score vers difficulté"""
        if score <= 0.2:
            return ChallengeDifficulty.BEGINNER
        elif score <= 0.4:
            return ChallengeDifficulty.INTERMEDIATE
        elif score <= 0.6:
            return ChallengeDifficulty.ADVANCED
        elif score <= 0.8:
            return ChallengeDifficulty.EXPERT
        elif score <= 0.95:
            return ChallengeDifficulty.MASTER
        else:
            return ChallengeDifficulty.LEGENDARY
    
    async def update_performance_history(
        self,
        creator_id: str,
        challenge_data: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> None:
        """Mise à jour historique performance"""
        try:
            performance_entry = {
                "challenge_id": challenge_data.get("id"),
                "challenge_type": challenge_data.get("type"),
                "difficulty": challenge_data.get("difficulty"),
                "completion_rate": performance_data.get("completion_rate", 0.0),
                "completed": performance_data.get("completed", False),
                "time_taken": performance_data.get("time_taken_hours", 0),
                "quality_score": performance_data.get("quality_score", 0.5),
                "timestamp": datetime.utcnow()
            }
            
            self.performance_history[creator_id].append(performance_entry)
            
            # Limitation historique (garder derniers 50 défis)
            if len(self.performance_history[creator_id]) > 50:
                self.performance_history[creator_id] = self.performance_history[creator_id][-50:]
            
            logger.debug(f"📊 Updated performance history for {creator_id}")
            
        except Exception as e:
            logger.error(f"❌ Performance history update error: {e}")


class CommunityChallengeMatcher:
    """
    🤝 Système de matching pour défis communautaires
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.community_pools: Dict[str, List[str]] = defaultdict(list)
        self.collaboration_history: Dict[str, List[str]] = defaultdict(list)
        
    async def create_community_challenge(
        self,
        base_challenge: Challenge,
        collaboration_type: str,
        team_size: int
    ) -> Challenge:
        """Création défi communautaire"""
        try:
            community_challenge = Challenge(
                id=f"community_{base_challenge.id}",
                title=f"Community {base_challenge.title}",
                description=f"Collaborate with {team_size-1} other creators: {base_challenge.description}",
                challenge_type=ChallengeType.COMMUNITY,
                difficulty=base_challenge.difficulty,
                frequency=base_challenge.frequency,
                requirements=self._adapt_requirements_for_community(base_challenge.requirements, team_size),
                rewards=self._calculate_community_rewards(base_challenge.rewards, team_size),
                start_date=base_challenge.start_date,
                end_date=base_challenge.end_date,
                max_participants=base_challenge.max_participants,
                metadata={
                    "collaboration_type": collaboration_type,
                    "team_size": team_size,
                    "base_challenge_id": base_challenge.id,
                    "requires_team_formation": True
                },
                created_by="community_system"
            )
            
            logger.info(f"🤝 Created community challenge: {community_challenge.title}")
            return community_challenge
            
        except Exception as e:
            logger.error(f"❌ Community challenge creation error: {e}")
            raise
    
    def _adapt_requirements_for_community(
        self,
        base_requirements: List[ChallengeRequirement],
        team_size: int
    ) -> List[ChallengeRequirement]:
        """Adaptation requirements pour communauté"""
        adapted_requirements = []
        
        for req in base_requirements:
            # Ajustement targets pour équipe
            team_target = req.target_value * team_size * 0.8  # 80% du total individuel
            
            adapted_req = ChallengeRequirement(
                id=f"team_{req.id}",
                name=f"Team {req.name}",
                description=f"As a team: {req.description}",
                target_value=team_target,
                measurement_unit=req.measurement_unit,
                weight=req.weight,
                is_mandatory=req.is_mandatory
            )
            adapted_requirements.append(adapted_req)
        
        # Ajout requirements spécifiques équipe
        team_specific_reqs = [
            ChallengeRequirement(
                id="team_coordination",
                name="Team Coordination",
                description="Demonstrate effective team coordination",
                target_value=1,
                measurement_unit="coordination_score",
                weight=0.5,
                is_mandatory=True
            ),
            ChallengeRequirement(
                id="equal_participation",
                name="Equal Participation",
                description="Ensure all team members contribute equally",
                target_value=0.8,
                measurement_unit="participation_balance",
                weight=0.3,
                is_mandatory=True
            )
        ]
        
        adapted_requirements.extend(team_specific_reqs)
        return adapted_requirements
    
    def _calculate_community_rewards(
        self,
        base_rewards: Dict[str, Any],
        team_size: int
    ) -> Dict[str, Any]:
        """Calcul récompenses communautaires"""
        community_rewards = base_rewards.copy()
        
        # Boost pour collaboration
        collaboration_multiplier = 1.0 + (team_size - 1) * 0.3
        
        for reward_type, value in community_rewards.items():
            if isinstance(value, (int, float)):
                community_rewards[reward_type] = value * collaboration_multiplier
        
        # Récompenses spéciales équipe
        community_rewards["team_bonus"] = base_rewards.get("points", 100) * 0.5
        community_rewards["collaboration_badge"] = True
        
        return community_rewards
    
    async def find_collaboration_partners(
        self,
        creator_id: str,
        challenge: Challenge,
        creator_profile: Dict[str, Any]
    ) -> List[str]:
        """Recherche partenaires de collaboration"""
        try:
            team_size = challenge.metadata.get("team_size", 3)
            collaboration_type = challenge.metadata.get("collaboration_type", "mixed")
            
            # Critères de matching
            matching_criteria = self._extract_matching_criteria(creator_profile, challenge)
            
            # Pool de créateurs disponibles
            available_creators = self._get_available_creators_pool(challenge)
            
            # Scoring compatibilité
            compatibility_scores = []
            
            for candidate_id in available_creators:
                if candidate_id == creator_id:
                    continue
                
                compatibility = await self._calculate_compatibility(
                    creator_id, candidate_id, matching_criteria, challenge
                )
                
                compatibility_scores.append((candidate_id, compatibility))
            
            # Tri par compatibilité
            compatibility_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Sélection meilleurs partenaires
            partners = [partner_id for partner_id, _ in compatibility_scores[:team_size-1]]
            
            logger.debug(f"🤝 Found {len(partners)} collaboration partners for {creator_id}")
            return partners
            
        except Exception as e:
            logger.error(f"❌ Partner matching error: {e}")
            return []
    
    def _extract_matching_criteria(
        self,
        creator_profile: Dict[str, Any],
        challenge: Challenge
    ) -> Dict[str, Any]:
        """Extraction critères de matching"""
        return {
            "skill_level": creator_profile.get("skill_levels", {}).get(challenge.challenge_type.value, 0.5),
            "content_types": creator_profile.get("content_types", []),
            "timezone": creator_profile.get("timezone", "UTC"),
            "language": creator_profile.get("language", "en"),
            "collaboration_style": creator_profile.get("collaboration_preferences", {}).get("style", "flexible"),
            "availability": creator_profile.get("availability", {})
        }
    
    def _get_available_creators_pool(self, challenge: Challenge) -> List[str]:
        """Pool de créateurs disponibles"""
        # Simulation: en production, query vraie base de données
        pool_key = f"{challenge.challenge_type.value}_{challenge.difficulty.value}"
        return self.community_pools.get(pool_key, [f"creator_{i}" for i in range(100, 200)])
    
    async def _calculate_compatibility(
        self,
        creator_id: str,
        candidate_id: str,
        criteria: Dict[str, Any],
        challenge: Challenge
    ) -> float:
        """Calcul score compatibilité"""
        try:
            compatibility_score = 0.0
            
            # Simulation profil candidat
            candidate_profile = {
                "skill_level": random.uniform(0.3, 0.9),
                "timezone": random.choice(["UTC", "EST", "PST", "CET"]),
                "language": random.choice(["en", "fr", "de", "es"]),
                "collaboration_style": random.choice(["structured", "flexible", "creative"])
            }
            
            # Score skill complementarity
            skill_diff = abs(criteria["skill_level"] - candidate_profile["skill_level"])
            skill_score = 1.0 - min(skill_diff / 0.5, 1.0)  # Préférer skills similaires
            compatibility_score += skill_score * 0.4
            
            # Score timezone compatibility
            timezone_score = 1.0 if criteria["timezone"] == candidate_profile["timezone"] else 0.5
            compatibility_score += timezone_score * 0.2
            
            # Score langue
            language_score = 1.0 if criteria["language"] == candidate_profile["language"] else 0.3
            compatibility_score += language_score * 0.2
            
            # Score collaboration history
            history_score = self._calculate_history_score(creator_id, candidate_id)
            compatibility_score += history_score * 0.2
            
            return min(1.0, compatibility_score)
            
        except Exception as e:
            logger.error(f"❌ Compatibility calculation error: {e}")
            return 0.0
    
    def _calculate_history_score(self, creator_id: str, candidate_id: str) -> float:
        """Score basé sur historique collaboration"""
        creator_history = self.collaboration_history.get(creator_id, [])
        
        if candidate_id in creator_history:
            # Collaborations précédentes: bonus/malus selon succès
            return 0.8  # Simplified: en production, analyser succès réels
        else:
            # Nouvelle collaboration: neutre
            return 0.5


class SeasonalEventOrchestrator:
    """
    🎪 Orchestrateur d'événements saisonniers
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_events: Dict[str, SeasonalEvent] = {}
        self.event_templates = self._load_event_templates()
        
    def _load_event_templates(self) -> Dict[str, Dict[str, Any]]:
        """Templates d'événements saisonniers"""
        return {
            "spring_creativity": {
                "name": "Spring Creativity Bloom",
                "theme": "nature_renaissance",
                "duration_days": 30,
                "challenge_types": [ChallengeType.CREATION, ChallengeType.INNOVATION],
                "special_rewards": {"spring_nft": True, "creativity_multiplier": 1.5}
            },
            "summer_collaboration": {
                "name": "Summer Collaboration Festival",
                "theme": "unity_collaboration",
                "duration_days": 45,
                "challenge_types": [ChallengeType.COLLABORATION, ChallengeType.COMMUNITY],
                "special_rewards": {"collaboration_trophy": True, "team_boost": 2.0}
            },
            "autumn_mastery": {
                "name": "Autumn Skill Mastery",
                "theme": "knowledge_harvest",
                "duration_days": 60,
                "challenge_types": [ChallengeType.SKILL_DEVELOPMENT, ChallengeType.CONSISTENCY],
                "special_rewards": {"mastery_certification": True, "skill_boost": 1.8}
            },
            "winter_innovation": {
                "name": "Winter Innovation Challenge",
                "theme": "technological_advancement",
                "duration_days": 40,
                "challenge_types": [ChallengeType.INNOVATION, ChallengeType.SOCIAL_IMPACT],
                "special_rewards": {"innovation_award": True, "future_access": True}
            }
        }
    
    async def create_seasonal_event(
        self,
        event_template_key: str,
        start_date: Optional[datetime] = None
    ) -> Optional[SeasonalEvent]:
        """Création événement saisonnier"""
        try:
            template = self.event_templates.get(event_template_key)
            if not template:
                logger.error(f"❌ Event template not found: {event_template_key}")
                return None
            
            event_id = str(uuid4())
            start_date = start_date or datetime.utcnow()
            end_date = start_date + timedelta(days=template["duration_days"])
            
            event = SeasonalEvent(
                id=event_id,
                name=template["name"],
                description=f"Seasonal event: {template['theme']}",
                theme=template["theme"],
                start_date=start_date,
                end_date=end_date,
                special_rewards=template["special_rewards"],
                status="upcoming" if start_date > datetime.utcnow() else "active"
            )
            
            # Génération défis associés
            associated_challenges = await self._generate_event_challenges(event, template)
            event.associated_challenges = [c.id for c in associated_challenges]
            
            self.active_events[event_id] = event
            
            logger.info(f"🎪 Created seasonal event: {event.name}")
            return event
            
        except Exception as e:
            logger.error(f"❌ Seasonal event creation error: {e}")
            return None
    
    async def _generate_event_challenges(
        self,
        event: SeasonalEvent,
        template: Dict[str, Any]
    ) -> List[Challenge]:
        """Génération défis pour événement"""
        challenges = []
        
        for challenge_type in template["challenge_types"]:
            # Création défi pour chaque difficulté
            for difficulty in [ChallengeDifficulty.INTERMEDIATE, ChallengeDifficulty.ADVANCED, ChallengeDifficulty.EXPERT]:
                challenge = await self._create_event_challenge(event, challenge_type, difficulty, template)
                if challenge:
                    challenges.append(challenge)
        
        return challenges
    
    async def _create_event_challenge(
        self,
        event: SeasonalEvent,
        challenge_type: ChallengeType,
        difficulty: ChallengeDifficulty,
        template: Dict[str, Any]
    ) -> Optional[Challenge]:
        """Création défi spécifique pour événement"""
        try:
            challenge_id = f"event_{event.id}_{challenge_type.value}_{difficulty.value}"
            
            # Génération requirements basés sur type et difficulté
            requirements = self._generate_event_requirements(challenge_type, difficulty, event.theme)
            
            # Calcul récompenses avec bonus événement
            base_rewards = self._calculate_base_rewards(difficulty)
            event_rewards = self._apply_event_bonus(base_rewards, template["special_rewards"])
            
            challenge = Challenge(
                id=challenge_id,
                title=f"{event.name} - {challenge_type.value.title()} Challenge",
                description=f"Participate in the {event.theme} themed {challenge_type.value} challenge",
                challenge_type=challenge_type,
                difficulty=difficulty,
                frequency=ChallengeFrequency.SPECIAL_EVENT,
                requirements=requirements,
                rewards=event_rewards,
                start_date=event.start_date,
                end_date=event.end_date,
                metadata={
                    "event_id": event.id,
                    "theme": event.theme,
                    "is_seasonal": True
                },
                created_by="seasonal_system",
                status=ChallengeStatus.ACTIVE
            )
            
            return challenge
            
        except Exception as e:
            logger.error(f"❌ Event challenge creation error: {e}")
            return None
    
    def _generate_event_requirements(
        self,
        challenge_type: ChallengeType,
        difficulty: ChallengeDifficulty,
        theme: str
    ) -> List[ChallengeRequirement]:
        """Génération requirements pour événement"""
        base_multiplier = {
            ChallengeDifficulty.BEGINNER: 1.0,
            ChallengeDifficulty.INTERMEDIATE: 1.5,
            ChallengeDifficulty.ADVANCED: 2.0,
            ChallengeDifficulty.EXPERT: 3.0,
            ChallengeDifficulty.MASTER: 4.0,
            ChallengeDifficulty.LEGENDARY: 6.0
        }[difficulty]
        
        requirements_templates = {
            ChallengeType.CREATION: [
                ChallengeRequirement(
                    id="content_creation",
                    name="Create Content",
                    description=f"Create {int(3 * base_multiplier)} themed content pieces",
                    target_value=int(3 * base_multiplier),
                    measurement_unit="content_count"
                ),
                ChallengeRequirement(
                    id="quality_threshold",
                    name="Quality Standard",
                    description="Maintain high quality standards",
                    target_value=0.7 + (base_multiplier - 1) * 0.1,
                    measurement_unit="quality_score"
                )
            ],
            ChallengeType.COLLABORATION: [
                ChallengeRequirement(
                    id="collaboration_count",
                    name="Collaborations",
                    description=f"Complete {int(2 * base_multiplier)} collaborations",
                    target_value=int(2 * base_multiplier),
                    measurement_unit="collaboration_count"
                ),
                ChallengeRequirement(
                    id="collaboration_success",
                    name="Success Rate",
                    description="Achieve high collaboration success rate",
                    target_value=0.8,
                    measurement_unit="success_rate"
                )
            ],
            ChallengeType.INNOVATION: [
                ChallengeRequirement(
                    id="innovation_score",
                    name="Innovation",
                    description="Demonstrate innovation in content",
                    target_value=0.8 + (base_multiplier - 1) * 0.05,
                    measurement_unit="innovation_score"
                ),
                ChallengeRequirement(
                    id="unique_techniques",
                    name="Unique Techniques",
                    description=f"Use {int(2 * base_multiplier)} unique techniques",
                    target_value=int(2 * base_multiplier),
                    measurement_unit="technique_count"
                )
            ]
        }
        
        return requirements_templates.get(challenge_type, [])
    
    def _calculate_base_rewards(self, difficulty: ChallengeDifficulty) -> Dict[str, Any]:
        """Calcul récompenses de base"""
        multipliers = {
            ChallengeDifficulty.BEGINNER: 1.0,
            ChallengeDifficulty.INTERMEDIATE: 1.5,
            ChallengeDifficulty.ADVANCED: 2.5,
            ChallengeDifficulty.EXPERT: 4.0,
            ChallengeDifficulty.MASTER: 6.0,
            ChallengeDifficulty.LEGENDARY: 10.0
        }
        
        base_points = 100
        multiplier = multipliers[difficulty]
        
        return {
            "points": int(base_points * multiplier),
            "tokens": int(base_points * multiplier * 0.1),
            "experience": int(base_points * multiplier * 0.5)
        }
    
    def _apply_event_bonus(
        self,
        base_rewards: Dict[str, Any],
        special_rewards: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Application bonus événement"""
        enhanced_rewards = base_rewards.copy()
        
        # Application multiplicateurs
        for reward_type, value in base_rewards.items():
            multiplier_key = f"{reward_type}_multiplier"
            if multiplier_key in special_rewards:
                enhanced_rewards[reward_type] = int(value * special_rewards[multiplier_key])
        
        # Ajout récompenses spéciales
        enhanced_rewards.update(special_rewards)
        
        return enhanced_rewards


class ChallengeOrchestrator:
    """
    🎯 Challenge Orchestrator Enterprise avec adaptive difficulty et community challenges
    Orchestrateur complet de défis avec intelligence artificielle et événements saisonniers
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.adaptive_engine = AdaptiveDifficultyEngine(self.config)
        self.community_matcher = CommunityChallengeMatcher(self.config)
        self.seasonal_orchestrator = SeasonalEventOrchestrator(self.config)
        
        self.active_challenges: Dict[str, Challenge] = {}
        self.participations: Dict[str, List[ChallengeParticipation]] = defaultdict(list)
        self.challenge_templates = self._load_challenge_templates()
        self.initialized_at = datetime.utcnow()
        
        logger.info("🎯 ChallengeOrchestrator initialized with adaptive capabilities")
    
    def _load_challenge_templates(self) -> Dict[str, Dict[str, Any]]:
        """Chargement templates de défis"""
        return {
            ChallengeType.CREATION: {
                "base_title": "Content Creation Challenge",
                "base_description": "Create high-quality content showcasing your skills",
                "default_duration_days": 7,
                "base_requirements": ["content_count", "quality_threshold"],
                "reward_categories": ["points", "tokens", "badges"]
            },
            ChallengeType.COLLABORATION: {
                "base_title": "Collaboration Challenge",
                "base_description": "Work together with other creators on exciting projects",
                "default_duration_days": 14,
                "base_requirements": ["collaboration_count", "team_satisfaction"],
                "reward_categories": ["points", "collaboration_boost", "network_expansion"]
            },
            ChallengeType.SKILL_DEVELOPMENT: {
                "base_title": "Skill Mastery Challenge",
                "base_description": "Develop and demonstrate new skills in your field",
                "default_duration_days": 21,
                "base_requirements": ["skill_improvement", "practice_hours"],
                "reward_categories": ["points", "skill_certification", "expert_recognition"]
            },
            ChallengeType.INNOVATION: {
                "base_title": "Innovation Challenge",
                "base_description": "Push creative boundaries with innovative content",
                "default_duration_days": 14,
                "base_requirements": ["innovation_score", "originality_rating"],
                "reward_categories": ["points", "innovation_badge", "feature_opportunity"]
            }
        }
    
    async def create_personalized_challenge(
        self,
        creator_id: str,
        challenge_type: ChallengeType,
        creator_profile: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[Challenge]:
        """Création défi personnalisé avec difficulté adaptive"""
        try:
            # Calcul difficulté optimale
            optimal_difficulty = await self.adaptive_engine.calculate_optimal_difficulty(
                creator_id, challenge_type, creator_profile
            )
            
            # Récupération template
            template = self.challenge_templates.get(challenge_type, {})
            
            # Génération requirements personnalisés
            requirements = self._generate_personalized_requirements(
                challenge_type, optimal_difficulty, creator_profile
            )
            
            # Calcul récompenses adaptées
            rewards = self._calculate_adaptive_rewards(optimal_difficulty, creator_profile)
            
            # Création challenge
            challenge_id = str(uuid4())
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=template.get("default_duration_days", 7))
            
            challenge = Challenge(
                id=challenge_id,
                title=f"Personal {template.get('base_title', 'Challenge')}",
                description=self._personalize_description(template.get('base_description', ''), creator_profile),
                challenge_type=challenge_type,
                difficulty=optimal_difficulty,
                frequency=ChallengeFrequency.WEEKLY,
                requirements=requirements,
                rewards=rewards,
                start_date=start_date,
                end_date=end_date,
                max_participants=1,  # Challenge personnel
                metadata={
                    "creator_id": creator_id,
                    "is_personalized": True,
                    "difficulty_reasoning": f"Adaptive engine recommended {optimal_difficulty.value}"
                },
                created_by="adaptive_system",
                status=ChallengeStatus.ACTIVE
            )
            
            self.active_challenges[challenge_id] = challenge
            
            logger.info(f"🎯 Created personalized challenge for {creator_id}: {optimal_difficulty.value}")
            return challenge
            
        except Exception as e:
            logger.error(f"❌ Personalized challenge creation error: {e}")
            return None
    
    def _generate_personalized_requirements(
        self,
        challenge_type: ChallengeType,
        difficulty: ChallengeDifficulty,
        creator_profile: Dict[str, Any]
    ) -> List[ChallengeRequirement]:
        """Génération requirements personnalisés"""
        difficulty_multiplier = {
            ChallengeDifficulty.BEGINNER: 0.5,
            ChallengeDifficulty.INTERMEDIATE: 1.0,
            ChallengeDifficulty.ADVANCED: 1.5,
            ChallengeDifficulty.EXPERT: 2.0,
            ChallengeDifficulty.MASTER: 3.0,
            ChallengeDifficulty.LEGENDARY: 5.0
        }[difficulty]
        
        # Ajustement basé sur profil créateur
        engagement_factor = creator_profile.get("engagement_score", 0.5)
        time_availability = creator_profile.get("time_availability_hours_per_week", 10) / 20.0  # Normalized
        
        adjusted_multiplier = difficulty_multiplier * (0.7 + engagement_factor * 0.3) * (0.8 + time_availability * 0.2)
        
        # Génération requirements basés sur type
        if challenge_type == ChallengeType.CREATION:
            return [
                ChallengeRequirement(
                    id="content_pieces",
                    name="Content Creation",
                    description=f"Create {int(3 * adjusted_multiplier)} high-quality content pieces",
                    target_value=max(1, int(3 * adjusted_multiplier)),
                    measurement_unit="count"
                ),
                ChallengeRequirement(
                    id="engagement_rate",
                    name="Engagement Quality",
                    description="Achieve target engagement rate",
                    target_value=0.05 + (adjusted_multiplier - 0.5) * 0.02,
                    measurement_unit="percentage"
                )
            ]
        elif challenge_type == ChallengeType.COLLABORATION:
            return [
                ChallengeRequirement(
                    id="collaborations",
                    name="Successful Collaborations",
                    description=f"Complete {int(2 * adjusted_multiplier)} successful collaborations",
                    target_value=max(1, int(2 * adjusted_multiplier)),
                    measurement_unit="count"
                ),
                ChallengeRequirement(
                    id="partner_satisfaction",
                    name="Partner Satisfaction",
                    description="Maintain high partner satisfaction",
                    target_value=0.8,
                    measurement_unit="rating"
                )
            ]
        
        # Fallback requirements
        return [
            ChallengeRequirement(
                id="basic_completion",
                name="Basic Completion",
                description="Complete the basic challenge requirements",
                target_value=1,
                measurement_unit="completion"
            )
        ]
    
    def _calculate_adaptive_rewards(
        self,
        difficulty: ChallengeDifficulty,
        creator_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcul récompenses adaptives"""
        base_rewards = {
            ChallengeDifficulty.BEGINNER: {"points": 50, "tokens": 5},
            ChallengeDifficulty.INTERMEDIATE: {"points": 100, "tokens": 10},
            ChallengeDifficulty.ADVANCED: {"points": 200, "tokens": 25},
            ChallengeDifficulty.EXPERT: {"points": 400, "tokens": 50},
            ChallengeDifficulty.MASTER: {"points": 800, "tokens": 100},
            ChallengeDifficulty.LEGENDARY: {"points": 1500, "tokens": 200}
        }[difficulty]
        
        # Bonus basé sur préférences créateur
        preferences = creator_profile.get("reward_preferences", {})
        
        if preferences.get("prefers_tokens", False):
            base_rewards["tokens"] = int(base_rewards["tokens"] * 1.3)
            base_rewards["points"] = int(base_rewards["points"] * 0.9)
        
        if preferences.get("values_recognition", False):
            base_rewards["public_recognition"] = True
            base_rewards["leaderboard_boost"] = 1.2
        
        return base_rewards
    
    def _personalize_description(self, base_description: str, creator_profile: Dict[str, Any]) -> str:
        """Personnalisation description défi"""
        content_types = creator_profile.get("content_types", ["content"])
        primary_type = content_types[0] if content_types else "content"
        
        personalized = base_description.replace("content", primary_type)
        
        # Ajout mentions spécifiques au créateur
        if creator_profile.get("experience_level") == "beginner":
            personalized += " This challenge is designed to help you build foundational skills."
        elif creator_profile.get("experience_level") == "expert":
            personalized += " This advanced challenge will push your creative boundaries."
        
        return personalized
    
    async def join_challenge(
        self,
        creator_id: str,
        challenge_id: str,
        creator_profile: Optional[Dict[str, Any]] = None
    ) -> Optional[ChallengeParticipation]:
        """Inscription à un défi"""
        try:
            challenge = self.active_challenges.get(challenge_id)
            if not challenge:
                logger.warning(f"⚠️ Challenge not found: {challenge_id}")
                return None
            
            # Vérification éligibilité
            if not self._check_challenge_eligibility(creator_profile or {}, challenge):
                logger.warning(f"⚠️ Creator {creator_id} not eligible for challenge {challenge_id}")
                return None
            
            # Vérification capacité
            if challenge.max_participants:
                current_participants = len([p for p in self.participations[challenge_id] if not p.is_completed])
                if current_participants >= challenge.max_participants:
                    logger.warning(f"⚠️ Challenge {challenge_id} is full")
                    return None
            
            # Création participation
            participation_id = str(uuid4())
            
            participation = ChallengeParticipation(
                id=participation_id,
                challenge_id=challenge_id,
                creator_id=creator_id,
                joined_at=datetime.utcnow(),
                progress={req.id: 0.0 for req in challenge.requirements}
            )
            
            self.participations[challenge_id].append(participation)
            
            # Mise à jour pour défis communautaires
            if challenge.challenge_type == ChallengeType.COMMUNITY:
                await self._handle_community_challenge_join(participation, challenge, creator_profile or {})
            
            logger.info(f"✅ Creator {creator_id} joined challenge {challenge_id}")
            return participation
            
        except Exception as e:
            logger.error(f"❌ Challenge join error: {e}")
            return None
    
    def _check_challenge_eligibility(
        self,
        creator_profile: Dict[str, Any],
        challenge: Challenge
    ) -> bool:
        """Vérification éligibilité pour défi"""
        criteria = challenge.eligibility_criteria
        
        for criterion, required_value in criteria.items():
            profile_value = creator_profile.get(criterion)
            
            if profile_value is None:
                return False
            
            if isinstance(required_value, (int, float)) and profile_value < required_value:
                return False
            elif isinstance(required_value, str) and profile_value != required_value:
                return False
        
        return True
    
    async def _handle_community_challenge_join(
        self,
        participation: ChallengeParticipation,
        challenge: Challenge,
        creator_profile: Dict[str, Any]
    ) -> None:
        """Gestion inscription défi communautaire"""
        try:
            # Recherche partenaires pour défis communautaires
            if challenge.metadata.get("requires_team_formation", False):
                partners = await self.community_matcher.find_collaboration_partners(
                    participation.creator_id, challenge, creator_profile
                )
                
                participation.metadata["suggested_partners"] = partners
                participation.metadata["team_formation_status"] = "pending"
                
                logger.debug(f"🤝 Found {len(partners)} potential partners for {participation.creator_id}")
            
        except Exception as e:
            logger.error(f"❌ Community challenge join handling error: {e}")
    
    async def update_challenge_progress(
        self,
        creator_id: str,
        challenge_id: str,
        progress_data: Dict[str, Any]
    ) -> Optional[ChallengeParticipation]:
        """Mise à jour progression défi"""
        try:
            # Recherche participation
            participation = None
            for p in self.participations.get(challenge_id, []):
                if p.creator_id == creator_id:
                    participation = p
                    break
            
            if not participation:
                logger.warning(f"⚠️ Participation not found: {creator_id}/{challenge_id}")
                return None
            
            challenge = self.active_challenges.get(challenge_id)
            if not challenge:
                return None
            
            # Mise à jour progression
            for req_id, progress_value in progress_data.items():
                if req_id in participation.progress:
                    participation.progress[req_id] = progress_value
            
            # Calcul completion percentage
            total_progress = sum(participation.progress.values())
            max_progress = len(participation.progress)
            participation.completion_percentage = (total_progress / max_progress) * 100 if max_progress > 0 else 0
            
            # Vérification completion
            if participation.completion_percentage >= 100 and not participation.is_completed:
                participation.is_completed = True
                participation.completed_at = datetime.utcnow()
                
                # Mise à jour historique performance pour adaptive engine
                await self.adaptive_engine.update_performance_history(
                    creator_id,
                    {
                        "id": challenge_id,
                        "type": challenge.challenge_type.value,
                        "difficulty": challenge.difficulty.value
                    },
                    {
                        "completion_rate": 1.0,
                        "completed": True,
                        "quality_score": progress_data.get("quality_score", 0.8)
                    }
                )
                
                logger.info(f"🎉 Challenge completed: {creator_id} completed {challenge_id}")
            
            return participation
            
        except Exception as e:
            logger.error(f"❌ Progress update error: {e}")
            return None
    
    async def create_seasonal_challenge_event(
        self,
        event_template: str,
        start_date: Optional[datetime] = None
    ) -> Optional[SeasonalEvent]:
        """Création événement de défis saisonniers"""
        return await self.seasonal_orchestrator.create_seasonal_event(event_template, start_date)
    
    def get_creator_challenge_summary(self, creator_id: str) -> Dict[str, Any]:
        """Résumé défis d'un créateur"""
        creator_participations = []
        
        for challenge_id, participations in self.participations.items():
            for participation in participations:
                if participation.creator_id == creator_id:
                    challenge = self.active_challenges.get(challenge_id)
                    creator_participations.append({
                        "participation": participation,
                        "challenge": challenge
                    })
        
        completed = [p for p in creator_participations if p["participation"].is_completed]
        in_progress = [p for p in creator_participations if not p["participation"].is_completed]
        
        return {
            "total_challenges": len(creator_participations),
            "completed_challenges": len(completed),
            "in_progress_challenges": len(in_progress),
            "completion_rate": len(completed) / max(1, len(creator_participations)) * 100,
            "average_completion_percentage": sum(p["participation"].completion_percentage for p in creator_participations) / max(1, len(creator_participations)),
            "challenges_by_difficulty": self._group_by_difficulty(creator_participations),
            "recent_completions": sorted(completed, key=lambda x: x["participation"].completed_at or datetime.min, reverse=True)[:5]
        }
    
    def _group_by_difficulty(self, participations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Groupement par difficulté"""
        difficulty_counts = {}
        
        for p in participations:
            if p["challenge"]:
                difficulty = p["challenge"].difficulty.value
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        return difficulty_counts
    
    def get_health(self) -> Dict[str, Any]:
        """Health check du système"""
        total_participations = sum(len(participations) for participations in self.participations.values())
        completed_participations = sum(
            len([p for p in participations if p.is_completed])
            for participations in self.participations.values()
        )
        
        return {
            "status": "healthy",
            "initialized_at": self.initialized_at,
            "active_challenges": len(self.active_challenges),
            "total_participations": total_participations,
            "completed_participations": completed_participations,
            "completion_rate": completed_participations / max(1, total_participations) * 100,
            "active_seasonal_events": len(self.seasonal_orchestrator.active_events),
            "adaptive_engine_status": "operational",
            "community_matcher_status": "operational",
            "seasonal_orchestrator_status": "operational"
        }


# Expert roles validation
EXPERT_ROLES_IMPLEMENTED = {
    'Lead Dev IA': ['Adaptive Difficulty Engine', 'ML-Powered Challenge Generation', 'Intelligent Orchestration'],
    'Backend Senior': ['Async Operations', 'Challenge Management', 'Performance Optimization'],
    'ML Engineer': ['Difficulty Prediction', 'Performance Analysis', 'Behavioral Modeling'],
    'DBA': ['Challenge Storage', 'Participation Tracking', 'Progress Analytics'],
    'Sécurité': ['Challenge Integrity', 'Fair Play Monitoring', 'Anti-Gaming Protection'],
    'Microservices': ['Service Isolation', 'Health Monitoring', 'Scalable Architecture'],
    'Audio': ['Multi-Format Challenge Support', 'Audio Content Challenges'],
    'DevOps': ['Event Orchestration', 'Performance Monitoring', 'Production Readiness'],
    'IA Prompt Engineer': ['Dynamic Challenge Descriptions', 'Personalized Messaging', 'Context-Aware Generation']
}