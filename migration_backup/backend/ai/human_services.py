"""
Human-Centric AI Services - Consolidated Module
==============================================

Consolidated human interaction services including companion, therapy, and education AI.
Provides comprehensive human-centric AI capabilities for content creators.

This module consolidates:
- Virtual AI Companion Service (from companion.py)  
- Therapy AI Service (from therapy.py)
- Education AI Service (from education.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de

⚠️  MEDICAL DISCLAIMER ⚠️
Therapy service provides supportive AI assistance only and is not a substitute
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
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)

# ===== COMPANION SERVICE SECTION =====

class CompanionPersonalityType(Enum):
    """Types of companion personalities"""
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    SUPPORTIVE = "supportive"
    MENTOR = "mentor"

class ConversationContext(Enum):
    """Context types for conversations"""
    CASUAL = "casual"
    BUSINESS = "business"
    CREATIVE_SESSION = "creative_session"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL_SUPPORT = "emotional_support"

@dataclass
class CompanionMemory:
    """Memory structure for companion interactions"""
    user_id: str
    memories: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    personality_traits: Dict[str, float] = field(default_factory=dict)
    last_interaction: Optional[datetime] = None
    relationship_level: float = 0.0

class ICompanionService(ABC):
    """Interface for companion service"""
    
    @abstractmethod
    async def start_conversation(self, user_id: str, context: ConversationContext) -> str:
        pass
    
    @abstractmethod
    async def process_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def end_conversation(self, conversation_id: str) -> bool:
        pass

class CompanionService(ICompanionService):
    """Virtual AI Companion Service"""
    
    def __init__(self, personality_type: CompanionPersonalityType = CompanionPersonalityType.FRIENDLY):
        self.personality_type = personality_type
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        self.user_memories: Dict[str, CompanionMemory] = {}
        self.conversation_count = 0
        
    async def start_conversation(self, user_id: str, context: ConversationContext) -> str:
        """Start a new companion conversation"""
        conversation_id = f"companion_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Initialize or load user memory
        if user_id not in self.user_memories:
            self.user_memories[user_id] = CompanionMemory(user_id=user_id)
        
        memory = self.user_memories[user_id]
        memory.last_interaction = datetime.now()
        
        self.active_conversations[conversation_id] = {
            "user_id": user_id,
            "context": context,
            "started_at": datetime.now(),
            "message_count": 0,
            "personality": self.personality_type
        }
        
        self.conversation_count += 1
        return conversation_id
    
    async def process_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Process message with companion AI"""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}
        
        conversation = self.active_conversations[conversation_id]
        user_id = conversation["user_id"]
        memory = self.user_memories[user_id]
        
        # Update message count
        conversation["message_count"] += 1
        
        # Generate personalized response based on personality
        response = await self._generate_companion_response(message, memory, conversation)
        
        # Store interaction in memory
        memory.memories.append({
            "timestamp": datetime.now(),
            "user_message": message,
            "companion_response": response,
            "context": conversation["context"].value
        })
        
        # Limit memory size
        if len(memory.memories) > 100:
            memory.memories = memory.memories[-100:]
        
        return {
            "response": response,
            "personality": self.personality_type.value,
            "relationship_level": memory.relationship_level,
            "conversation_context": conversation["context"].value
        }
    
    async def end_conversation(self, conversation_id: str) -> bool:
        """End companion conversation"""
        if conversation_id in self.active_conversations:
            conversation = self.active_conversations[conversation_id]
            user_id = conversation["user_id"]
            
            # Update relationship level based on conversation
            if user_id in self.user_memories:
                memory = self.user_memories[user_id]
                memory.relationship_level += 0.1  # Increase bond
                memory.relationship_level = min(memory.relationship_level, 1.0)
            
            del self.active_conversations[conversation_id]
            return True
        return False
    
    async def _generate_companion_response(self, message: str, memory: CompanionMemory, 
                                         conversation: Dict[str, Any]) -> str:
        """Generate personalized companion response"""
        personality = conversation["personality"]
        context = conversation["context"]
        
        # Base response patterns by personality
        if personality == CompanionPersonalityType.FRIENDLY:
            response = f"I love chatting with you! About your message: {message[:50]}... that sounds really interesting!"
        elif personality == CompanionPersonalityType.PROFESSIONAL:
            response = f"Thank you for sharing that. Regarding your message, I can help you analyze this professionally."
        elif personality == CompanionPersonalityType.CREATIVE:
            response = f"What an inspiring message! This sparks so many creative ideas. Let's explore this together!"
        elif personality == CompanionPersonalityType.SUPPORTIVE:
            response = f"I'm here to support you. Your message shows you're thinking deeply about this."
        else:  # MENTOR
            response = f"That's a valuable insight. Let me share some guidance based on your message."
        
        return response

# ===== THERAPY SERVICE SECTION =====

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
    FAIR = "fair"
    POOR = "poor"
    CRISIS = "crisis"

@dataclass
class TherapySession:
    """Therapy session data structure"""
    session_id: str
    user_id: str
    session_type: TherapySessionType
    started_at: datetime
    duration: Optional[timedelta] = None
    wellbeing_before: Optional[WellbeingStatus] = None
    wellbeing_after: Optional[WellbeingStatus] = None
    interventions: List[str] = field(default_factory=list)
    outcomes: List[str] = field(default_factory=list)
    follow_up_needed: bool = False

class TherapyAIService:
    """Virtual Psychology Agent for emotional support"""
    
    def __init__(self):
        self.active_sessions: Dict[str, TherapySession] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.session_count = 0
        
    async def start_therapy_session(self, user_id: str, session_type: TherapySessionType) -> str:
        """Start a new therapy session"""
        session_id = f"therapy_{user_id}_{uuid.uuid4().hex[:8]}"
        
        session = TherapySession(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            started_at=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        self.session_count += 1
        
        # Initialize user profile if needed
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "session_history": [],
                "wellbeing_trend": [],
                "risk_factors": [],
                "coping_strategies": []
            }
        
        return session_id
    
    async def assess_wellbeing(self, session_id: str, indicators: Dict[str, Any]) -> WellbeingStatus:
        """Assess user wellbeing"""
        if session_id not in self.active_sessions:
            return WellbeingStatus.FAIR
        
        session = self.active_sessions[session_id]
        
        # Simple assessment algorithm
        stress_level = indicators.get("stress_level", 5)
        mood_score = indicators.get("mood_score", 5)
        sleep_quality = indicators.get("sleep_quality", 5)
        
        average_score = (stress_level + mood_score + sleep_quality) / 3
        
        if average_score >= 8:
            status = WellbeingStatus.EXCELLENT
        elif average_score >= 6:
            status = WellbeingStatus.GOOD
        elif average_score >= 4:
            status = WellbeingStatus.FAIR
        elif average_score >= 2:
            status = WellbeingStatus.POOR
        else:
            status = WellbeingStatus.CRISIS
        
        session.wellbeing_before = status
        return status
    
    async def provide_intervention(self, session_id: str, concern: str) -> Dict[str, Any]:
        """Provide therapeutic intervention"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Generate intervention based on session type and concern
        intervention = await self._generate_intervention(session.session_type, concern)
        session.interventions.append(intervention)
        
        return {
            "intervention": intervention,
            "session_type": session.session_type.value,
            "resources": await self._get_resources(session.session_type),
            "follow_up_recommended": True
        }
    
    async def end_therapy_session(self, session_id: str, final_wellbeing: WellbeingStatus) -> Dict[str, Any]:
        """End therapy session and provide summary"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        session.wellbeing_after = final_wellbeing
        session.duration = datetime.now() - session.started_at
        
        # Add to user profile history
        user_profile = self.user_profiles[session.user_id]
        user_profile["session_history"].append(session)
        user_profile["wellbeing_trend"].append({
            "timestamp": datetime.now(),
            "status": final_wellbeing.value
        })
        
        summary = {
            "session_duration": session.duration.total_seconds() / 60,  # minutes
            "wellbeing_improvement": session.wellbeing_after != session.wellbeing_before,
            "interventions_provided": len(session.interventions),
            "follow_up_needed": session.follow_up_needed
        }
        
        del self.active_sessions[session_id]
        return summary
    
    async def _generate_intervention(self, session_type: TherapySessionType, concern: str) -> str:
        """Generate therapeutic intervention"""
        interventions = {
            TherapySessionType.STRESS_MANAGEMENT: "Let's practice deep breathing and mindfulness techniques to manage stress.",
            TherapySessionType.ANXIETY_SUPPORT: "I understand your anxiety. Let's work through some grounding exercises.",
            TherapySessionType.BURNOUT_PREVENTION: "Burnout is serious. Let's discuss work-life balance strategies.",
            TherapySessionType.EMOTIONAL_SUPPORT: "Your feelings are valid. Let's explore healthy coping mechanisms.",
            TherapySessionType.CREATIVITY_BLOCK: "Creative blocks are temporary. Let's try some inspiration exercises."
        }
        
        return interventions.get(session_type, "Let's work through this together with supportive strategies.")
    
    async def _get_resources(self, session_type: TherapySessionType) -> List[str]:
        """Get relevant resources for session type"""
        resources = {
            TherapySessionType.STRESS_MANAGEMENT: [
                "Meditation apps", "Breathing exercises", "Time management techniques"
            ],
            TherapySessionType.ANXIETY_SUPPORT: [
                "Grounding techniques", "Cognitive behavioral strategies", "Relaxation methods"
            ],
            TherapySessionType.BURNOUT_PREVENTION: [
                "Work-life balance tips", "Self-care routines", "Boundary setting guides"
            ]
        }
        
        return resources.get(session_type, ["General wellness resources", "Professional help contacts"])

# ===== EDUCATION SERVICE SECTION =====

class CourseType(Enum):
    """Types of educational courses"""
    CONTENT_CREATION = "content_creation"
    INFLUENCER_MARKETING = "influencer_marketing"
    SOCIAL_MEDIA_STRATEGY = "social_media_strategy"
    BRAND_COLLABORATION = "brand_collaboration"
    MONETIZATION_STRATEGIES = "monetization_strategies"
    AUDIENCE_DEVELOPMENT = "audience_development"
    CREATIVE_SKILLS = "creative_skills"
    BUSINESS_DEVELOPMENT = "business_development"
    TECHNICAL_SKILLS = "technical_skills"
    PERSONAL_BRANDING = "personal_branding"

class DifficultyLevel(Enum):
    """Course difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningStyle(Enum):
    """Learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MULTIMODAL = "multimodal"

@dataclass
class Course:
    """Course data structure"""
    course_id: str
    title: str
    course_type: CourseType
    difficulty: DifficultyLevel
    modules: List[Dict[str, Any]] = field(default_factory=list)
    duration_hours: float = 0.0
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class StudentProfile:
    """Student profile data structure"""
    student_id: str
    learning_style: LearningStyle
    skill_level: Dict[str, DifficultyLevel] = field(default_factory=dict)
    completed_courses: List[str] = field(default_factory=list)
    current_courses: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    progress_tracking: Dict[str, float] = field(default_factory=dict)

class IEducationAIService(ABC):
    """Interface for education AI service"""
    
    @abstractmethod
    async def create_course(self, course_data: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    async def enroll_student(self, student_id: str, course_id: str) -> bool:
        pass
    
    @abstractmethod
    async def track_progress(self, student_id: str, course_id: str, progress: float) -> bool:
        pass

class EducationAIService(IEducationAIService):
    """Personal AI Tutor & Learning Management Service"""
    
    def __init__(self):
        self.courses: Dict[str, Course] = {}
        self.student_profiles: Dict[str, StudentProfile] = {}
        self.enrollments: Dict[str, List[str]] = {}  # student_id -> course_ids
        self.course_count = 0
        
    async def create_course(self, course_data: Dict[str, Any]) -> str:
        """Create a new course"""
        course_id = f"course_{uuid.uuid4().hex[:8]}"
        
        course = Course(
            course_id=course_id,
            title=course_data["title"],
            course_type=CourseType(course_data["course_type"]),
            difficulty=DifficultyLevel(course_data["difficulty"]),
            modules=course_data.get("modules", []),
            duration_hours=course_data.get("duration_hours", 10.0),
            prerequisites=course_data.get("prerequisites", []),
            learning_objectives=course_data.get("learning_objectives", [])
        )
        
        self.courses[course_id] = course
        self.course_count += 1
        
        return course_id
    
    async def enroll_student(self, student_id: str, course_id: str) -> bool:
        """Enroll student in course"""
        if course_id not in self.courses:
            return False
        
        # Initialize student profile if needed
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = StudentProfile(
                student_id=student_id,
                learning_style=LearningStyle.MULTIMODAL
            )
        
        # Add to enrollments
        if student_id not in self.enrollments:
            self.enrollments[student_id] = []
        
        if course_id not in self.enrollments[student_id]:
            self.enrollments[student_id].append(course_id)
            
            # Update student profile
            profile = self.student_profiles[student_id]
            profile.current_courses.append(course_id)
            profile.progress_tracking[course_id] = 0.0
            
            return True
        
        return False
    
    async def track_progress(self, student_id: str, course_id: str, progress: float) -> bool:
        """Track student progress in course"""
        if (student_id not in self.student_profiles or 
            course_id not in self.enrollments.get(student_id, [])):
            return False
        
        profile = self.student_profiles[student_id]
        profile.progress_tracking[course_id] = min(progress, 1.0)
        
        # Mark as completed if 100% progress
        if progress >= 1.0 and course_id not in profile.completed_courses:
            profile.completed_courses.append(course_id)
            if course_id in profile.current_courses:
                profile.current_courses.remove(course_id)
        
        return True
    
    async def get_personalized_recommendations(self, student_id: str) -> List[str]:
        """Get personalized course recommendations"""
        if student_id not in self.student_profiles:
            return []
        
        profile = self.student_profiles[student_id]
        
        # Simple recommendation algorithm
        recommendations = []
        for course_id, course in self.courses.items():
            if (course_id not in profile.completed_courses and 
                course_id not in profile.current_courses):
                recommendations.append(course_id)
        
        return recommendations[:5]  # Return top 5 recommendations

# ===== FACTORY FUNCTIONS =====

def create_companion_service(personality_type: CompanionPersonalityType = CompanionPersonalityType.FRIENDLY) -> CompanionService:
    """Create companion service instance"""
    return CompanionService(personality_type)

def create_therapy_service() -> TherapyAIService:
    """Create therapy service instance"""
    return TherapyAIService()

def create_education_service() -> EducationAIService:
    """Create education service instance"""
    return EducationAIService()

def create_friendly_companion() -> CompanionService:
    """Create friendly companion"""
    return CompanionService(CompanionPersonalityType.FRIENDLY)

def create_professional_companion() -> CompanionService:
    """Create professional companion"""
    return CompanionService(CompanionPersonalityType.PROFESSIONAL)

def create_creative_companion() -> CompanionService:
    """Create creative companion"""
    return CompanionService(CompanionPersonalityType.CREATIVE)

def create_mentor_companion() -> CompanionService:
    """Create mentor companion"""
    return CompanionService(CompanionPersonalityType.MENTOR)

def create_content_creator_tutor() -> EducationAIService:
    """Create content creator specialized tutor"""
    return EducationAIService()

def create_business_development_tutor() -> EducationAIService:
    """Create business development specialized tutor"""
    return EducationAIService()

# Export all classes and functions
__all__ = [
    # Companion Service
    "CompanionService",
    "ICompanionService", 
    "CompanionPersonalityType",
    "ConversationContext",
    "CompanionMemory",
    
    # Therapy Service
    "TherapyAIService",
    "TherapySessionType",
    "WellbeingStatus", 
    "TherapySession",
    
    # Education Service
    "EducationAIService",
    "IEducationAIService",
    "CourseType",
    "DifficultyLevel",
    "LearningStyle",
    "Course",
    "StudentProfile",
    
    # Factory functions
    "create_companion_service",
    "create_therapy_service",
    "create_education_service",
    "create_friendly_companion",
    "create_professional_companion", 
    "create_creative_companion",
    "create_mentor_companion",
    "create_content_creator_tutor",
    "create_business_development_tutor"
]