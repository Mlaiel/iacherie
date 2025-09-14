"""Avatar Intelligence - IA Avatar

Intelligence artificielle pour avatars adaptatifs avec personnalité,
comportements dynamiques et interaction naturelle utilisateur.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid

# Local imports
from .facial_expressions import BaseEmotion, ComplexEmotion


class PersonalityTrait(Enum):
    """Traits de personnalité fondamentaux"""
    EXTROVERT = "extrovert"
    INTROVERT = "introvert"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    ASSERTIVE = "assertive"
    CALM = "calm"
    ENERGETIC = "energetic"
    CAUTIOUS = "cautious"
    ADVENTUROUS = "adventurous"


class BehaviorType(Enum):
    """Types de comportements"""
    GREETING = "greeting"
    CONVERSATION = "conversation"
    PRESENTATION = "presentation"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    SUPPORTIVE = "supportive"
    PROMOTIONAL = "promotional"
    INTERACTIVE = "interactive"
    REACTIVE = "reactive"
    PROACTIVE = "proactive"


class InteractionContext(Enum):
    """Contextes d'interaction"""
    BUSINESS_MEETING = "business_meeting"
    SOCIAL_MEDIA = "social_media"
    EDUCATIONAL_SESSION = "educational_session"
    ENTERTAINMENT_SHOW = "entertainment_show"
    CUSTOMER_SERVICE = "customer_service"
    PERSONAL_CHAT = "personal_chat"
    LIVE_STREAM = "live_stream"
    CONTENT_CREATION = "content_creation"


class LearningMode(Enum):
    """Modes d'apprentissage"""
    PASSIVE = "passive"
    ACTIVE = "active"
    REINFORCEMENT = "reinforcement"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"


@dataclass
class PersonalityProfile:
    """Profil de personnalité complet"""
    primary_traits: List[PersonalityTrait]
    secondary_traits: List[PersonalityTrait] = field(default_factory=list)
    energy_level: float = 0.7  # 0.0 à 1.0
    social_confidence: float = 0.7  # 0.0 à 1.0
    creativity_level: float = 0.5  # 0.0 à 1.0
    emotional_stability: float = 0.8  # 0.0 à 1.0
    adaptability: float = 0.6  # 0.0 à 1.0
    humor_level: float = 0.5  # 0.0 à 1.0
    custom_attributes: Dict[str, float] = field(default_factory=dict)


@dataclass
class EmotionalState:
    """État émotionnel actuel"""
    primary_emotion: BaseEmotion
    secondary_emotions: List[BaseEmotion] = field(default_factory=list)
    complex_emotions: List[ComplexEmotion] = field(default_factory=list)
    intensity: float = 0.5  # 0.0 à 1.0
    duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    triggers: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BehaviorPattern:
    """Modèle de comportement"""
    behavior_id: str
    behavior_type: BehaviorType
    triggers: List[str]
    responses: List[Dict[str, Any]]
    conditions: Dict[str, Any] = field(default_factory=dict)
    probability: float = 1.0
    learning_weight: float = 1.0
    success_rate: float = 0.0
    usage_count: int = 0


@dataclass
class InteractionMemory:
    """Mémoire d'interaction"""
    interaction_id: str
    user_id: Optional[str] = None
    context: InteractionContext = InteractionContext.PERSONAL_CHAT
    timestamp: datetime = field(default_factory=datetime.now)
    user_input: str = ""
    avatar_response: str = ""
    emotional_state: Optional[EmotionalState] = None
    satisfaction_score: Optional[float] = None
    learned_patterns: List[str] = field(default_factory=list)


class EmotionalIntelligence:
    """Intelligence émotionnelle adaptative"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.emotional_history: List[EmotionalState] = []
        self.emotion_patterns: Dict[str, List[EmotionalState]] = {}
    
    async def analyze_emotional_context(self, input_text: str, 
                                      context: InteractionContext) -> EmotionalState:
        """Analyse du contexte émotionnel"""
        try:
            # Analyse basique du sentiment (simulation)
            emotional_keywords = {
                BaseEmotion.HAPPINESS: ['happy', 'joy', 'excited', 'great', 'awesome', 'love'],
                BaseEmotion.SADNESS: ['sad', 'sorry', 'down', 'disappointed', 'upset'],
                BaseEmotion.ANGER: ['angry', 'mad', 'frustrated', 'annoyed', 'furious'],
                BaseEmotion.FEAR: ['worried', 'scared', 'nervous', 'anxious', 'afraid'],
                BaseEmotion.SURPRISE: ['wow', 'amazing', 'unexpected', 'surprised'],
                BaseEmotion.DISGUST: ['disgusting', 'awful', 'terrible', 'horrible']
            }
            
            detected_emotion = BaseEmotion.NEUTRAL
            max_matches = 0
            
            for emotion, keywords in emotional_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in input_text.lower())
                if matches > max_matches:
                    max_matches = matches
                    detected_emotion = matches > 0 and emotion or BaseEmotion.NEUTRAL
            
            # Calcul de l'intensité
            intensity = min(1.0, max_matches * 0.3 + 0.2)
            
            emotional_state = EmotionalState(
                primary_emotion=detected_emotion,
                intensity=intensity,
                triggers=[input_text[:50]]
            )
            
            self.emotional_history.append(emotional_state)
            return emotional_state
            
        except Exception as e:
            self.logger.error(f"Erreur analyse émotionnelle: {e}")
            return EmotionalState(primary_emotion=BaseEmotion.NEUTRAL)
    
    async def adapt_response_emotion(self, response: str, 
                                   target_emotion: EmotionalState) -> str:
        """Adaptation de la réponse selon l'émotion cible"""
        try:
            emotion_modifiers = {
                BaseEmotion.HAPPINESS: {
                    'prefix': ['😊 ', '🌟 ', ''],
                    'style': 'enthusiastic',
                    'tone': 'upbeat'
                },
                BaseEmotion.SADNESS: {
                    'prefix': ['💙 ', '🤗 ', ''],
                    'style': 'supportive',
                    'tone': 'gentle'
                },
                BaseEmotion.ANGER: {
                    'prefix': ['🔥 ', '💪 ', ''],
                    'style': 'understanding',
                    'tone': 'calm'
                },
                BaseEmotion.FEAR: {
                    'prefix': ['🌈 ', '💝 ', ''],
                    'style': 'reassuring',
                    'tone': 'confident'
                }
            }
            
            modifier = emotion_modifiers.get(target_emotion.primary_emotion, {})
            if modifier:
                prefix = random.choice(modifier.get('prefix', ['']))
                adapted_response = f"{prefix}{response}"
                return adapted_response
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur adaptation émotionnelle: {e}")
            return response
    
    def get_emotional_trend(self, hours: int = 24) -> Dict[str, float]:
        """Analyse des tendances émotionnelles"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_emotions = [
            state for state in self.emotional_history 
            if state.timestamp >= cutoff_time
        ]
        
        if not recent_emotions:
            return {}
        
        emotion_counts = {}
        for state in recent_emotions:
            emotion = state.primary_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total = len(recent_emotions)
        return {emotion: count/total for emotion, count in emotion_counts.items()}


class BehaviorEngine:
    """Moteur comportements dynamiques"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.behavior_patterns: Dict[str, BehaviorPattern] = {}
        self.active_behaviors: List[str] = []
        self._initialize_default_behaviors()
    
    def _initialize_default_behaviors(self) -> None:
        """Initialisation des comportements par défaut"""
        default_behaviors = [
            BehaviorPattern(
                behavior_id="greeting_enthusiastic",
                behavior_type=BehaviorType.GREETING,
                triggers=["hello", "hi", "hey", "good morning"],
                responses=[
                    {"text": "Hello! Great to see you! 😊", "animation": "wave", "expression": "happy"},
                    {"text": "Hi there! How are you doing today?", "animation": "smile", "expression": "friendly"}
                ]
            ),
            BehaviorPattern(
                behavior_id="conversation_engaging",
                behavior_type=BehaviorType.CONVERSATION,
                triggers=["tell me", "what do you think", "your opinion"],
                responses=[
                    {"text": "That's a fascinating topic! Let me share my thoughts...", "expression": "thoughtful"},
                    {"text": "I'd love to discuss this with you!", "expression": "engaged"}
                ]
            ),
            BehaviorPattern(
                behavior_id="supportive_encouragement",
                behavior_type=BehaviorType.SUPPORTIVE,
                triggers=["help", "advice", "struggling", "difficult"],
                responses=[
                    {"text": "I'm here to help! Let's work through this together.", "expression": "caring"},
                    {"text": "You've got this! I believe in you.", "expression": "encouraging"}
                ]
            )
        ]
        
        for behavior in default_behaviors:
            self.behavior_patterns[behavior.behavior_id] = behavior
    
    async def select_behavior(self, input_text: str, context: InteractionContext,
                            personality: PersonalityProfile) -> Optional[BehaviorPattern]:
        """Sélection du comportement approprié"""
        try:
            matching_behaviors = []
            
            for behavior in self.behavior_patterns.values():
                match_score = await self._calculate_behavior_match(
                    behavior, input_text, context, personality
                )
                if match_score > 0.3:  # Seuil de correspondance
                    matching_behaviors.append((behavior, match_score))
            
            if not matching_behaviors:
                return None
            
            # Sélection pondérée par le score et la probabilité
            matching_behaviors.sort(key=lambda x: x[1] * x[0].probability, reverse=True)
            selected_behavior = matching_behaviors[0][0]
            
            # Mise à jour des statistiques
            selected_behavior.usage_count += 1
            
            return selected_behavior
            
        except Exception as e:
            self.logger.error(f"Erreur sélection comportement: {e}")
            return None
    
    async def _calculate_behavior_match(self, behavior: BehaviorPattern, 
                                      input_text: str, context: InteractionContext,
                                      personality: PersonalityProfile) -> float:
        """Calcul du score de correspondance d'un comportement"""
        score = 0.0
        
        # Correspondance des déclencheurs
        for trigger in behavior.triggers:
            if trigger.lower() in input_text.lower():
                score += 0.4
        
        # Correspondance du contexte
        if context.value in behavior.conditions.get('contexts', [context.value]):
            score += 0.3
        
        # Correspondance de la personnalité
        personality_match = await self._calculate_personality_match(behavior, personality)
        score += personality_match * 0.3
        
        return min(1.0, score)
    
    async def _calculate_personality_match(self, behavior: BehaviorPattern,
                                         personality: PersonalityProfile) -> float:
        """Calcul de la correspondance avec la personnalité"""
        # Correspondance basée sur les traits de personnalité
        if behavior.behavior_type == BehaviorType.GREETING:
            if PersonalityTrait.EXTROVERT in personality.primary_traits:
                return 0.8
            elif PersonalityTrait.INTROVERT in personality.primary_traits:
                return 0.4
        elif behavior.behavior_type == BehaviorType.ENTERTAINMENT:
            if PersonalityTrait.ENERGETIC in personality.primary_traits:
                return 0.9
        elif behavior.behavior_type == BehaviorType.SUPPORTIVE:
            if PersonalityTrait.EMPATHETIC in personality.primary_traits:
                return 0.9
        
        return 0.5  # Score neutre par défaut
    
    async def learn_from_interaction(self, behavior_id: str, 
                                   satisfaction_score: float) -> None:
        """Apprentissage depuis l'interaction"""
        if behavior_id in self.behavior_patterns:
            behavior = self.behavior_patterns[behavior_id]
            
            # Mise à jour du taux de succès
            total_weight = behavior.usage_count * behavior.success_rate + satisfaction_score
            behavior.success_rate = total_weight / (behavior.usage_count + 1)
            
            # Ajustement de la probabilité basé sur le succès
            if satisfaction_score > 0.7:
                behavior.probability = min(1.0, behavior.probability * 1.1)
            elif satisfaction_score < 0.3:
                behavior.probability = max(0.1, behavior.probability * 0.9)


class InteractionManager:
    """Gestion interactions utilisateur"""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.interaction_history: List[InteractionMemory] = []
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
    
    async def process_interaction(self, user_input: str, user_id: Optional[str] = None,
                                context: InteractionContext = InteractionContext.PERSONAL_CHAT) -> Dict[str, Any]:
        """Traitement complet d'une interaction"""
        try:
            interaction_id = str(uuid.uuid4())
            
            # Création de la mémoire d'interaction
            memory = InteractionMemory(
                interaction_id=interaction_id,
                user_id=user_id,
                context=context,
                user_input=user_input
            )
            
            # Analyse du profil utilisateur
            user_profile = await self._get_or_create_user_profile(user_id)
            
            # Génération de la réponse
            response_data = await self._generate_response(user_input, context, user_profile)
            memory.avatar_response = response_data.get('text', '')
            memory.emotional_state = response_data.get('emotional_state')
            
            # Sauvegarde de l'interaction
            self.interaction_history.append(memory)
            
            # Mise à jour du profil utilisateur
            if user_id:
                await self._update_user_profile(user_id, memory)
            
            return {
                'interaction_id': interaction_id,
                'response': response_data,
                'memory': memory
            }
            
        except Exception as e:
            self.logger.error(f"Erreur traitement interaction: {e}")
            return {
                'interaction_id': str(uuid.uuid4()),
                'response': {'text': 'Je suis désolé, je rencontre une difficulté technique.'},
                'error': str(e)
            }
    
    async def _get_or_create_user_profile(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Récupération ou création du profil utilisateur"""
        if not user_id:
            return {'interaction_count': 0, 'preferences': {}}
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'interaction_count': 0,
                'preferences': {},
                'emotional_history': [],
                'satisfaction_scores': []
            }
        
        return self.user_profiles[user_id]
    
    async def _generate_response(self, user_input: str, context: InteractionContext,
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Génération de réponse personnalisée"""
        # Simulation de génération de réponse intelligente
        response_templates = [
            "C'est une excellente question! Voici ce que je pense...",
            "J'apprécie que vous me demandiez cela. Mon point de vue est...",
            "Intéressant! Laissez-moi vous expliquer...",
            "Je comprends votre perspective. De mon côté...",
            "C'est un sujet fascinant! Permettez-moi de partager..."
        ]
        
        response_text = random.choice(response_templates)
        
        return {
            'text': response_text,
            'animation': 'talking',
            'expression': 'engaged',
            'emotional_state': EmotionalState(primary_emotion=BaseEmotion.HAPPINESS),
            'confidence': 0.8
        }
    
    async def _update_user_profile(self, user_id: str, memory: InteractionMemory) -> None:
        """Mise à jour du profil utilisateur"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            profile['interaction_count'] += 1
            profile['last_interaction'] = memory.timestamp.isoformat()
            
            # Mise à jour de l'historique émotionnel
            if memory.emotional_state:
                profile['emotional_history'].append({
                    'emotion': memory.emotional_state.primary_emotion.value,
                    'intensity': memory.emotional_state.intensity,
                    'timestamp': memory.emotional_state.timestamp.isoformat()
                })
    
    def get_interaction_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyse des interactions"""
        if user_id:
            user_interactions = [m for m in self.interaction_history if m.user_id == user_id]
        else:
            user_interactions = self.interaction_history
        
        if not user_interactions:
            return {'total_interactions': 0}
        
        return {
            'total_interactions': len(user_interactions),
            'avg_satisfaction': sum(m.satisfaction_score or 0.5 for m in user_interactions) / len(user_interactions),
            'most_common_context': max(
                set(m.context.value for m in user_interactions),
                key=lambda x: sum(1 for m in user_interactions if m.context.value == x)
            ) if user_interactions else None,
            'interaction_frequency': len(user_interactions) / max(1, (datetime.now() - user_interactions[0].timestamp).days)
        }


class AvatarPersonality:
    """Personnalité et comportements IA"""
    
    def __init__(self, personality_profile -> None: Optional[PersonalityProfile] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.personality = personality_profile or self._create_default_personality()
        self.emotional_intelligence = EmotionalIntelligence()
        self.behavior_engine = BehaviorEngine()
        self.interaction_manager = InteractionManager()
        self.learning_mode = LearningMode.ACTIVE
    
    def _create_default_personality(self) -> PersonalityProfile:
        """Création d'une personnalité par défaut équilibrée"""
        return PersonalityProfile(
            primary_traits=[PersonalityTrait.OPTIMISTIC, PersonalityTrait.EMPATHETIC],
            secondary_traits=[PersonalityTrait.CREATIVE, PersonalityTrait.ENERGETIC],
            energy_level=0.7,
            social_confidence=0.8,
            creativity_level=0.6,
            emotional_stability=0.8,
            adaptability=0.7,
            humor_level=0.6
        )
    
    async def process_user_interaction(self, user_input: str, 
                                     context: InteractionContext = InteractionContext.PERSONAL_CHAT,
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Traitement complet d'une interaction utilisateur"""
        try:
            # Analyse émotionnelle
            emotional_state = await self.emotional_intelligence.analyze_emotional_context(
                user_input, context
            )
            
            # Sélection du comportement
            behavior = await self.behavior_engine.select_behavior(
                user_input, context, self.personality
            )
            
            # Génération de la réponse
            interaction_result = await self.interaction_manager.process_interaction(
                user_input, user_id, context
            )
            
            # Adaptation émotionnelle de la réponse
            if behavior and behavior.responses:
                selected_response = random.choice(behavior.responses)
                adapted_text = await self.emotional_intelligence.adapt_response_emotion(
                    selected_response.get('text', ''), emotional_state
                )
                selected_response['text'] = adapted_text
                interaction_result['response'].update(selected_response)
            
            # Apprentissage (si activé)
            if self.learning_mode in [LearningMode.ACTIVE, LearningMode.REINFORCEMENT]:
                await self._learn_from_interaction(interaction_result, behavior)
            
            return interaction_result
            
        except Exception as e:
            self.logger.error(f"Erreur traitement interaction: {e}")
            return {
                'response': {
                    'text': 'Je rencontre une difficulté pour répondre à votre message.',
                    'expression': 'confused'
                },
                'error': str(e)
            }
    
    async def _learn_from_interaction(self, interaction_result: Dict[str, Any],
                                    behavior: Optional[BehaviorPattern]) -> None:
        """Apprentissage depuis l'interaction"""
        if behavior and self.learning_mode == LearningMode.REINFORCEMENT:
            # Simulation d'un score de satisfaction
            satisfaction_score = random.uniform(0.6, 0.9)
            await self.behavior_engine.learn_from_interaction(
                behavior.behavior_id, satisfaction_score
            )
    
    def update_personality_trait(self, trait: PersonalityTrait, intensity: float) -> None:
        """Mise à jour d'un trait de personnalité"""
        if trait in self.personality.primary_traits:
            # Ajustement des attributs personnalisés
            trait_name = trait.value
            self.personality.custom_attributes[trait_name] = intensity
        else:
            self.personality.secondary_traits.append(trait)
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Résumé de la personnalité"""
        return {
            'primary_traits': [trait.value for trait in self.personality.primary_traits],
            'secondary_traits': [trait.value for trait in self.personality.secondary_traits],
            'energy_level': self.personality.energy_level,
            'social_confidence': self.personality.social_confidence,
            'creativity_level': self.personality.creativity_level,
            'emotional_stability': self.personality.emotional_stability,
            'adaptability': self.personality.adaptability,
            'humor_level': self.personality.humor_level,
            'behavior_patterns': len(self.behavior_engine.behavior_patterns),
            'learning_mode': self.learning_mode.value
        }


__all__ = [
    'AvatarPersonality',
    'EmotionalIntelligence', 
    'BehaviorEngine',
    'InteractionManager',
    'PersonalityProfile',
    'PersonalityTrait',
    'EmotionalState',
    'BehaviorPattern',
    'BehaviorType',
    'InteractionContext',
    'InteractionMemory',
    'LearningMode'
]