"""Therapy AI Service - Virtual Psychology Agent

Enterprise-grade virtual psychology agent providing 24/7 emotional support,
wellbeing tracking, and therapeutic intervention for content creators.

Business Logic:
Emotional assessment → Crisis detection → Therapeutic response → 
Wellbeing tracking → Progress monitoring → Recovery support → 
Mental health optimization → Sustainable content creation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited. Contact: mlaiel@live.de

⚠️  MEDICAL DISCLAIMER ⚠️
This service provides supportive AI assistance only and is not a substitute
for professional medical or psychological treatment. Users should seek
professional help for serious mental health concerns.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TherapySessionType(Enum):
    """Types of therapy sessions"""
    EMOTIONAL_SUPPORT = "emotional_support"
    STRESS_MANAGEMENT = "stress_management"
    BURNOUT_PREVENTION = "burnout_prevention"
    ANXIETY_SUPPORT = "anxiety_support"
    DEPRESSION_SUPPORT = "depression_support"
    SELF_ESTEEM = "self_esteem"
    WORK_LIFE_BALANCE = "work_life_balance"
    CREATIVITY_BLOCK = "creativity_block"
    CRISIS_INTERVENTION = "crisis_intervention"
    WELLNESS_CHECK = "wellness_check"


class WellbeingStatus(Enum):
    """Wellbeing status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    CONCERNING = "concerning"
    CRITICAL = "critical"


class TherapeuticTechnique(Enum):
    """Available therapeutic techniques"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MINDFULNESS = "mindfulness"
    BREATHING_EXERCISES = "breathing_exercises"
    PROGRESSIVE_RELAXATION = "progressive_relaxation"
    POSITIVE_AFFIRMATIONS = "positive_affirmations"
    GOAL_SETTING = "goal_setting"
    STRESS_REDUCTION = "stress_reduction"
    EMOTIONAL_REGULATION = "emotional_regulation"


@dataclass
class TherapySessionContext:
    """Context for therapy sessions"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_type: TherapySessionType = TherapySessionType.EMOTIONAL_SUPPORT
    started_at: datetime = field(default_factory=datetime.utcnow)
    duration_minutes: int = 0
    current_mood: str = "neutral"
    stress_level: float = 0.5  # 0.0 to 1.0
    session_goals: List[str] = field(default_factory=list)
    techniques_used: List[TherapeuticTechnique] = field(default_factory=list)
    notes: str = ""
    progress_indicators: Dict[str, Any] = field(default_factory=dict)
    crisis_indicators: bool = False
    follow_up_needed: bool = False


@dataclass
class WellbeingProfile:
    """User wellbeing profile"""
    user_id: str
    current_status: WellbeingStatus = WellbeingStatus.MODERATE
    stress_trends: List[float] = field(default_factory=list)
    mood_patterns: Dict[str, float] = field(default_factory=dict)
    coping_strategies: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    support_network: List[str] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.utcnow)
    therapy_history: List[str] = field(default_factory=list)
    preferred_techniques: List[TherapeuticTechnique] = field(default_factory=list)


@dataclass
class TherapeuticResponse:
    """Response from therapy AI"""
    response_text: str
    techniques_suggested: List[TherapeuticTechnique]
    mood_assessment: str
    stress_level: float
    crisis_detected: bool = False
    follow_up_needed: bool = False
    resources_recommended: List[str] = field(default_factory=list)
    session_summary: Optional[str] = None
    next_session_recommendation: Optional[datetime] = None


class TherapyAIService:
    """
    Virtual Psychology Agent providing 24/7 emotional support and wellbeing tracking.
    
    Core capabilities:
    - Emotional assessment and crisis detection
    - Therapeutic response generation
    - Wellbeing tracking and monitoring
    - Progress analysis and recommendations
    - Integration with existing emotional context
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_sessions: Dict[str, TherapySessionContext] = {}
        self.wellbeing_profiles: Dict[str, WellbeingProfile] = {}
        self.crisis_threshold = self.config.get("crisis_threshold", 0.8)
        self.session_timeout = self.config.get("session_timeout_minutes", 60)
        
        # Therapeutic resources
        self.crisis_resources = [
            "National Suicide Prevention Lifeline: 988",
            "Crisis Text Line: Text HOME to 741741",
            "Emergency Services: 911",
            "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
        ]
        
        self.wellness_resources = [
            "Mindfulness meditation apps",
            "Progressive muscle relaxation guides",
            "Breathing exercise tutorials",
            "Mental health professional directories",
            "Support group resources"
        ]
        
        logger.info("TherapyAIService initialized with 24/7 support capabilities")

    async def initialize(self) -> bool:
        """Initialize the therapy AI service"""
        try:
            # Initialize AI models and resources
            await self._load_therapeutic_models()
            await self._initialize_crisis_detection()
            await self._load_wellbeing_templates()
            
            logger.info("Therapy AI Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Therapy AI Service: {e}")
            return False

    async def start_therapy_session(
        self, 
        user_id: str, 
        session_type: TherapySessionType = TherapySessionType.EMOTIONAL_SUPPORT,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new therapy session"""
        try:
            session_context = TherapySessionContext(
                user_id=user_id,
                session_type=session_type,
                session_goals=initial_context.get("goals", []) if initial_context else [],
                current_mood=initial_context.get("mood", "neutral") if initial_context else "neutral"
            )
            
            # Store session
            self.active_sessions[session_context.session_id] = session_context
            
            # Get or create wellbeing profile
            if user_id not in self.wellbeing_profiles:
                self.wellbeing_profiles[user_id] = WellbeingProfile(user_id=user_id)
            
            # Generate welcome message
            welcome_response = await self._generate_session_welcome(session_context)
            
            logger.info(f"Therapy session started: {session_context.session_id} for user {user_id}")
            return session_context.session_id
            
        except Exception as e:
            logger.error(f"Failed to start therapy session for user {user_id}: {e}")
            raise

    async def process_therapy_input(
        self, 
        session_id: str, 
        user_input: str,
        emotional_context: Optional[Dict[str, Any]] = None
    ) -> TherapeuticResponse:
        """Process user input and provide therapeutic response"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Invalid session ID: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # Analyze emotional state
            emotional_analysis = await self._analyze_emotional_state(user_input, emotional_context)
            
            # Check for crisis indicators
            crisis_detected = await self._detect_crisis_indicators(user_input, emotional_analysis)
            
            # Update session context
            session.stress_level = emotional_analysis.get("stress_level", session.stress_level)
            session.current_mood = emotional_analysis.get("mood", session.current_mood)
            session.crisis_indicators = crisis_detected
            
            # Generate therapeutic response
            if crisis_detected:
                response = await self._generate_crisis_response(session, user_input)
            else:
                response = await self._generate_therapeutic_response(session, user_input, emotional_analysis)
            
            # Update wellbeing profile
            await self._update_wellbeing_profile(session.user_id, emotional_analysis)
            
            # Update session duration
            session.duration_minutes = int((datetime.utcnow() - session.started_at).total_seconds() / 60)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing therapy input for session {session_id}: {e}")
            raise

    async def end_therapy_session(self, session_id: str) -> Dict[str, Any]:
        """End therapy session and generate summary"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Invalid session ID: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # Generate session summary
            summary = await self._generate_session_summary(session)
            
            # Update wellbeing profile with session data
            profile = self.wellbeing_profiles[session.user_id]
            profile.therapy_history.append(session_id)
            profile.last_assessment = datetime.utcnow()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Therapy session ended: {session_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error ending therapy session {session_id}: {e}")
            raise

    async def get_wellbeing_assessment(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive wellbeing assessment for user"""
        try:
            if user_id not in self.wellbeing_profiles:
                # Create new profile with basic assessment
                self.wellbeing_profiles[user_id] = WellbeingProfile(user_id=user_id)
            
            profile = self.wellbeing_profiles[user_id]
            
            # Calculate current wellbeing metrics
            assessment = {
                "user_id": user_id,
                "current_status": profile.current_status.value,
                "stress_level": self._calculate_average_stress(profile),
                "mood_stability": self._analyze_mood_patterns(profile),
                "coping_effectiveness": len(profile.coping_strategies),
                "support_strength": len(profile.support_network),
                "risk_level": self._assess_risk_level(profile),
                "recommendations": await self._generate_wellbeing_recommendations(profile),
                "last_assessment": profile.last_assessment.isoformat(),
                "session_count": len(profile.therapy_history)
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating wellbeing assessment for user {user_id}: {e}")
            raise

    async def track_daily_wellbeing(self, user_id: str, daily_data: Dict[str, Any]) -> bool:
        """Track daily wellbeing metrics"""
        try:
            if user_id not in self.wellbeing_profiles:
                self.wellbeing_profiles[user_id] = WellbeingProfile(user_id=user_id)
            
            profile = self.wellbeing_profiles[user_id]
            
            # Update stress trends
            stress_level = daily_data.get("stress_level", 0.5)
            profile.stress_trends.append(stress_level)
            
            # Limit trend history
            if len(profile.stress_trends) > 30:  # Keep 30 days
                profile.stress_trends.pop(0)
            
            # Update mood patterns
            mood = daily_data.get("mood", "neutral")
            if mood not in profile.mood_patterns:
                profile.mood_patterns[mood] = 0
            profile.mood_patterns[mood] += 1
            
            # Update wellbeing status based on trends
            profile.current_status = await self._assess_wellbeing_status(profile)
            
            logger.info(f"Daily wellbeing tracked for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking daily wellbeing for user {user_id}: {e}")
            return False

    # Private helper methods
    
    async def _load_therapeutic_models(self):
        """Load AI models for therapeutic responses"""
        # Mock implementation - in production would load actual AI models
        logger.info("Therapeutic models loaded")

    async def _initialize_crisis_detection(self):
        """Initialize crisis detection algorithms"""
        # Mock implementation - in production would set up crisis detection
        logger.info("Crisis detection initialized")

    async def _load_wellbeing_templates(self):
        """Load wellbeing assessment templates"""
        # Mock implementation - in production would load templates
        logger.info("Wellbeing templates loaded")

    async def _generate_session_welcome(self, session: TherapySessionContext) -> str:
        """Generate personalized welcome message"""
        session_type_messages = {
            TherapySessionType.EMOTIONAL_SUPPORT: "I'm here to provide emotional support. How are you feeling today?",
            TherapySessionType.STRESS_MANAGEMENT: "Let's work together on managing stress. What's been on your mind?",
            TherapySessionType.ANXIETY_SUPPORT: "I understand anxiety can be overwhelming. Take a deep breath, and let's talk.",
            TherapySessionType.CRISIS_INTERVENTION: "I'm here to help you through this difficult time. You're not alone."
        }
        
        return session_type_messages.get(
            session.session_type, 
            "Welcome to your therapy session. I'm here to listen and support you."
        )

    async def _analyze_emotional_state(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze emotional state from user input"""
        # Mock emotional analysis - in production would use actual sentiment analysis
        return {
            "mood": "neutral",
            "stress_level": 0.4,
            "emotional_intensity": 0.5,
            "dominant_emotions": ["neutral"],
            "sentiment_score": 0.0
        }

    async def _detect_crisis_indicators(self, user_input: str, emotional_analysis: Dict[str, Any]) -> bool:
        """Detect crisis indicators requiring immediate intervention"""
        crisis_keywords = [
            "suicide", "kill myself", "end it all", "don't want to live",
            "hopeless", "worthless", "can't go on", "no point"
        ]
        
        # Check for explicit crisis language
        text_lower = user_input.lower()
        for keyword in crisis_keywords:
            if keyword in text_lower:
                return True
        
        # Check emotional analysis scores
        stress_level = emotional_analysis.get("stress_level", 0.0)
        emotional_intensity = emotional_analysis.get("emotional_intensity", 0.0)
        
        if stress_level > self.crisis_threshold or emotional_intensity > self.crisis_threshold:
            return True
        
        return False

    async def _generate_crisis_response(self, session: TherapySessionContext, user_input: str) -> TherapeuticResponse:
        """Generate crisis intervention response"""
        response_text = (
            "I'm deeply concerned about what you're sharing with me. Your safety and wellbeing are my priority. "
            "Please know that you're not alone, and there are people who want to help. "
            "I strongly encourage you to reach out to a crisis helpline or emergency services immediately."
        )
        
        return TherapeuticResponse(
            response_text=response_text,
            techniques_suggested=[TherapeuticTechnique.BREATHING_EXERCISES],
            mood_assessment="crisis",
            stress_level=1.0,
            crisis_detected=True,
            follow_up_needed=True,
            resources_recommended=self.crisis_resources
        )

    async def _generate_therapeutic_response(
        self, 
        session: TherapySessionContext, 
        user_input: str, 
        emotional_analysis: Dict[str, Any]
    ) -> TherapeuticResponse:
        """Generate appropriate therapeutic response"""
        mood = emotional_analysis.get("mood", "neutral")
        stress_level = emotional_analysis.get("stress_level", 0.5)
        
        # Generate contextual response based on session type and emotional state
        response_templates = {
            "high_stress": "I can sense you're feeling quite stressed right now. That's completely understandable. Let's try some breathing exercises to help you feel more grounded.",
            "low_mood": "It sounds like you're going through a difficult time. Your feelings are valid, and it's okay to not be okay sometimes.",
            "neutral": "Thank you for sharing that with me. How does it feel to express these thoughts?"
        }
        
        if stress_level > 0.7:
            response_key = "high_stress"
            techniques = [TherapeuticTechnique.BREATHING_EXERCISES, TherapeuticTechnique.PROGRESSIVE_RELAXATION]
        elif mood in ["sad", "depressed", "anxious"]:
            response_key = "low_mood"
            techniques = [TherapeuticTechnique.MINDFULNESS, TherapeuticTechnique.POSITIVE_AFFIRMATIONS]
        else:
            response_key = "neutral"
            techniques = [TherapeuticTechnique.COGNITIVE_BEHAVIORAL]
        
        return TherapeuticResponse(
            response_text=response_templates[response_key],
            techniques_suggested=techniques,
            mood_assessment=mood,
            stress_level=stress_level,
            resources_recommended=self.wellness_resources[:2]
        )

    async def _update_wellbeing_profile(self, user_id: str, emotional_analysis: Dict[str, Any]):
        """Update user's wellbeing profile with session data"""
        profile = self.wellbeing_profiles[user_id]
        
        # Update stress trends
        stress_level = emotional_analysis.get("stress_level", 0.5)
        profile.stress_trends.append(stress_level)
        
        # Update mood patterns
        mood = emotional_analysis.get("mood", "neutral")
        if mood not in profile.mood_patterns:
            profile.mood_patterns[mood] = 0
        profile.mood_patterns[mood] += 1
        
        # Update assessment timestamp
        profile.last_assessment = datetime.utcnow()

    async def _generate_session_summary(self, session: TherapySessionContext) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        return {
            "session_id": session.session_id,
            "duration_minutes": session.duration_minutes,
            "session_type": session.session_type.value,
            "techniques_used": [t.value for t in session.techniques_used],
            "mood_progression": session.current_mood,
            "stress_level": session.stress_level,
            "goals_addressed": session.session_goals,
            "crisis_indicators": session.crisis_indicators,
            "follow_up_needed": session.follow_up_needed,
            "recommendations": "Continue with regular check-ins and practice suggested techniques"
        }

    def _calculate_average_stress(self, profile: WellbeingProfile) -> float:
        """Calculate average stress level from trends"""
        if not profile.stress_trends:
            return 0.5
        return sum(profile.stress_trends) / len(profile.stress_trends)

    def _analyze_mood_patterns(self, profile: WellbeingProfile) -> float:
        """Analyze mood stability patterns"""
        if not profile.mood_patterns:
            return 0.5
        
        # Calculate mood diversity (more diverse = less stable)
        total_entries = sum(profile.mood_patterns.values())
        if total_entries == 0:
            return 0.5
        
        # Simple stability metric based on dominant mood frequency
        max_frequency = max(profile.mood_patterns.values())
        stability = max_frequency / total_entries
        return stability

    def _assess_risk_level(self, profile: WellbeingProfile) -> str:
        """Assess overall risk level"""
        avg_stress = self._calculate_average_stress(profile)
        risk_factors_count = len(profile.risk_factors)
        
        if avg_stress > 0.8 or risk_factors_count > 3:
            return "high"
        elif avg_stress > 0.6 or risk_factors_count > 1:
            return "moderate"
        else:
            return "low"

    async def _generate_wellbeing_recommendations(self, profile: WellbeingProfile) -> List[str]:
        """Generate personalized wellbeing recommendations"""
        recommendations = []
        
        avg_stress = self._calculate_average_stress(profile)
        
        if avg_stress > 0.7:
            recommendations.extend([
                "Practice daily stress reduction techniques",
                "Consider regular therapy sessions",
                "Establish healthy work-life boundaries"
            ])
        
        if len(profile.support_network) < 3:
            recommendations.append("Build stronger social support connections")
        
        if not profile.coping_strategies:
            recommendations.append("Develop healthy coping strategies")
        
        return recommendations

    async def _assess_wellbeing_status(self, profile: WellbeingProfile) -> WellbeingStatus:
        """Assess current wellbeing status based on profile data"""
        avg_stress = self._calculate_average_stress(profile)
        risk_level = self._assess_risk_level(profile)
        
        if avg_stress > 0.8 or risk_level == "high":
            return WellbeingStatus.CRITICAL
        elif avg_stress > 0.6 or risk_level == "moderate":
            return WellbeingStatus.CONCERNING
        elif avg_stress > 0.4:
            return WellbeingStatus.MODERATE
        elif avg_stress > 0.2:
            return WellbeingStatus.GOOD
        else:
            return WellbeingStatus.EXCELLENT


# Factory function for creating therapy service
async def create_therapy_service(config: Optional[Dict[str, Any]] = None) -> TherapyAIService:
    """Create and initialize therapy AI service"""
    service = TherapyAIService(config)
    await service.initialize()
    return service