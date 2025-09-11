"""
AINFLUE INTEGRATIONS - FIREBASE BACKEND SERVICES
===============================================

Enterprise Firebase integration for creator economy platform backend services.
Combines multiple expert roles for comprehensive real-time backend management.

Author: Fahed Mlaiel <mlaiel@live.de>
Platform: Ainflue - IA Influencer Agent + Content Protection Platform
Architecture Level: Level 3 (integrations/cloud_providers)

Expert Roles Applied:
- Lead Dev IA: AI-powered analytics, intelligent user segmentation, smart notifications
- Backend Senior: Robust real-time architecture, scalable database design, enterprise patterns
- ML Engineer: Advanced analytics processing, user behavior prediction, content recommendations
- DBA: NoSQL optimization, real-time data management, indexing strategies
- Security: Authentication, authorization, data protection, Firebase security rules
- Microservices: Cloud Functions, distributed processing, event-driven architecture
- Audio Engineer: Real-time audio processing, streaming optimization
- DevOps: Cloud deployment, monitoring, performance optimization, automated scaling
- IA Prompt Engineer: AI-driven user experience, intelligent content delivery

Business Logic Integration:
Creator → Authentication → Real-time Database → Cloud Functions → Analytics → Push Notifications → Revenue Tracking
"""

import asyncio
import base64
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import aiofiles
from pydantic import BaseModel, Field, validator

# Firebase SDK
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, messaging, analytics
from firebase_admin.exceptions import FirebaseError

# Google Cloud Libraries
from google.cloud import firestore as gcs_firestore
from google.cloud import storage as gcs_storage
from google.cloud import functions_v1
from google.api_core import exceptions as gcs_exceptions

# Security and Authentication
import jwt
from cryptography.hazmat.primitives import hashes

# Monitoring and Performance
import psutil
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics for DevOps monitoring
DATABASE_OPERATIONS = Counter('firebase_database_operations_total', 'Total database operations', ['operation', 'collection'])
FUNCTION_INVOCATIONS = Counter('firebase_function_invocations_total', 'Cloud Function invocations', ['function_name'])
AUTH_OPERATIONS = Counter('firebase_auth_operations_total', 'Authentication operations', ['operation'])
STORAGE_OPERATIONS = Counter('firebase_storage_operations_total', 'Storage operations', ['operation'])
RESPONSE_TIME = Histogram('firebase_response_time_seconds', 'Firebase response time', ['service'])
ACTIVE_CONNECTIONS = Gauge('firebase_active_connections', 'Active Firebase connections')
ERROR_COUNTER = Counter('firebase_errors_total', 'Firebase errors', ['error_type', 'service'])

class FirebaseService(Enum):
    """Firebase services"""
    FIRESTORE = "firestore"
    REALTIME_DATABASE = "realtime_database"
    AUTH = "auth"
    STORAGE = "storage"
    FUNCTIONS = "functions"
    MESSAGING = "messaging"
    ANALYTICS = "analytics"
    HOSTING = "hosting"

class UserRole(Enum):
    """User roles in the creator economy"""
    CREATOR = "creator"
    VIEWER = "viewer"
    COLLABORATOR = "collaborator"
    ADMIN = "admin"
    MODERATOR = "moderator"

class ContentType(Enum):
    """Content types for categorization"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    COURSE = "course"
    PODCAST = "podcast"

@dataclass
class FirebaseUser:
    """Firebase user data structure"""
    uid: str
    email: str
    display_name: Optional[str]
    role: UserRole
    creator_profile: Optional[Dict] = None
    subscription_tier: Optional[str] = None
    analytics_data: Optional[Dict] = None
    created_at: datetime = None
    last_login: datetime = None
    is_verified: bool = False

@dataclass
class CreatorContent:
    """Creator content data structure"""
    content_id: str
    creator_uid: str
    title: str
    description: str
    content_type: ContentType
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    visibility: str = "public"
    monetization_enabled: bool = False
    analytics: Optional[Dict] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class RealtimeEvent:
    """Real-time event data structure"""
    event_id: str
    event_type: str
    user_uid: str
    content_id: Optional[str] = None
    data: Dict[str, Any] = None
    timestamp: datetime = None

class FirebaseConfig(BaseModel):
    """Configuration for Firebase integration"""
    # Project Configuration
    project_id: str = Field(..., description="Firebase project ID")
    service_account_path: str = Field(..., description="Path to service account JSON")
    
    # Database Configuration
    firestore_enabled: bool = Field(default=True, description="Enable Firestore")
    realtime_db_enabled: bool = Field(default=True, description="Enable Realtime Database")
    realtime_db_url: Optional[str] = Field(default=None, description="Realtime Database URL")
    
    # Storage Configuration
    storage_bucket: Optional[str] = Field(default=None, description="Firebase Storage bucket")
    storage_rules_enabled: bool = Field(default=True, description="Enable storage security rules")
    
    # Authentication Configuration
    auth_providers: List[str] = Field(
        default=["email", "google", "twitter", "facebook"],
        description="Enabled authentication providers"
    )
    custom_token_enabled: bool = Field(default=True, description="Enable custom tokens")
    
    # Functions Configuration
    functions_region: str = Field(default="us-central1", description="Cloud Functions region")
    functions_runtime: str = Field(default="python39", description="Functions runtime")
    
    # Analytics Configuration
    analytics_enabled: bool = Field(default=True, description="Enable Firebase Analytics")
    custom_events_enabled: bool = Field(default=True, description="Enable custom events")
    
    # Messaging Configuration
    fcm_enabled: bool = Field(default=True, description="Enable Firebase Cloud Messaging")
    topic_messaging: bool = Field(default=True, description="Enable topic messaging")
    
    # Performance Configuration
    connection_pool_size: int = Field(default=10, description="Connection pool size")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # Security Configuration
    security_rules_strict: bool = Field(default=True, description="Use strict security rules")
    admin_sdk_enabled: bool = Field(default=True, description="Enable Admin SDK features")
    
    @validator('project_id')
    def validate_project_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Valid Firebase project ID required")
        return v

class FirebaseSecurityManager:
    """Security manager for Firebase - Security Expert role"""
    
    def __init__(self, config: FirebaseConfig):
        self.config = config
        
    def generate_firestore_rules(self, creator_focused: bool = True) -> str:
        """Generate Firestore security rules for creator economy"""
        if creator_focused:
            return """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // User profile rules
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      allow read: if request.auth != null && 
                     resource.data.visibility == 'public';
    }
    
    // Creator content rules
    match /content/{contentId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                      request.auth.uid == resource.data.creator_uid;
      allow create: if request.auth != null && 
                       request.auth.uid == request.resource.data.creator_uid;
    }
    
    // Analytics rules (admin only)
    match /analytics/{document=**} {
      allow read, write: if request.auth != null && 
                            request.auth.token.admin == true;
    }
    
    // Subscription rules
    match /subscriptions/{subscriptionId} {
      allow read, write: if request.auth != null && 
                            (request.auth.uid == resource.data.subscriber_uid ||
                             request.auth.uid == resource.data.creator_uid);
    }
    
    // Revenue tracking (creator and admin only)
    match /revenue/{revenueId} {
      allow read: if request.auth != null && 
                     (request.auth.uid == resource.data.creator_uid ||
                      request.auth.token.admin == true);
      allow write: if request.auth != null && 
                      request.auth.token.admin == true;
    }
    
    // Real-time events
    match /events/{eventId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null && 
                       request.auth.uid == request.resource.data.user_uid;
    }
  }
}
            """.strip()
        else:
            return """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
            """.strip()
    
    def generate_storage_rules(self) -> str:
        """Generate Firebase Storage security rules"""
        return """
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // User profile images
    match /users/{userId}/profile/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Creator content
    match /content/{creatorId}/{contentId}/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == creatorId;
    }
    
    // Thumbnails and previews
    match /thumbnails/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // Private uploads (creator only)
    match /private/{creatorId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == creatorId;
    }
    
    // Admin uploads
    match /admin/{allPaths=**} {
      allow read, write: if request.auth != null && 
                            request.auth.token.admin == true;
    }
  }
}
        """.strip()
    
    def create_custom_claims(self, user_role: UserRole, additional_claims: Dict = None) -> Dict[str, Any]:
        """Create custom claims for user authentication"""
        claims = {
            "role": user_role.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Role-specific claims
        if user_role == UserRole.ADMIN:
            claims["admin"] = True
            claims["permissions"] = ["read", "write", "delete", "manage_users"]
        elif user_role == UserRole.CREATOR:
            claims["creator"] = True
            claims["permissions"] = ["read", "write", "upload_content", "monetize"]
        elif user_role == UserRole.MODERATOR:
            claims["moderator"] = True
            claims["permissions"] = ["read", "moderate_content", "manage_reports"]
        else:
            claims["permissions"] = ["read"]
        
        # Add additional claims
        if additional_claims:
            claims.update(additional_claims)
        
        return claims
    
    def validate_content_security(self, content_data: Dict) -> Dict[str, Any]:
        """Validate content for security issues"""
        security_check = {
            "safe": True,
            "issues": [],
            "content_rating": "safe",
            "moderation_required": False
        }
        
        # Check for sensitive content indicators
        sensitive_keywords = ["explicit", "adult", "violence", "hate", "spam"]
        content_text = f"{content_data.get('title', '')} {content_data.get('description', '')}".lower()
        
        for keyword in sensitive_keywords:
            if keyword in content_text:
                security_check["issues"].append(f"Sensitive keyword detected: {keyword}")
                security_check["content_rating"] = "moderate"
                security_check["moderation_required"] = True
        
        # Validate file URLs for security
        file_url = content_data.get("file_url", "")
        if file_url and not file_url.startswith(("https://", "gs://")):
            security_check["issues"].append("Insecure file URL detected")
            security_check["safe"] = False
        
        return security_check

class FirebaseMLAnalytics:
    """ML-powered Firebase analytics - ML Engineer + Lead Dev IA roles"""
    
    def __init__(self, config: FirebaseConfig, db_client):
        self.config = config
        self.db = db_client
        
    async def analyze_user_behavior(self, user_uid: str, time_period_days: int = 30) -> Dict[str, Any]:
        """Analyze user behavior patterns using Firebase data"""
        analysis = {
            "user_profile": {},
            "engagement_metrics": {},
            "content_preferences": {},
            "monetization_potential": {},
            "recommendations": []
        }
        
        try:
            # Get user events from the time period
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_period_days)
            
            events_query = self.db.collection('events').where(
                'user_uid', '==', user_uid
            ).where(
                'timestamp', '>=', start_date
            ).where(
                'timestamp', '<=', end_date
            )
            
            events = [doc.to_dict() for doc in events_query.stream()]
            
            # Analyze engagement patterns
            engagement_analysis = self._analyze_engagement_patterns(events)
            analysis["engagement_metrics"] = engagement_analysis
            
            # Analyze content preferences
            content_analysis = self._analyze_content_preferences(events)
            analysis["content_preferences"] = content_analysis
            
            # Predict monetization potential
            monetization_analysis = await self._predict_monetization_potential(user_uid, events)
            analysis["monetization_potential"] = monetization_analysis
            
            # Generate personalized recommendations
            recommendations = await self._generate_user_recommendations(user_uid, analysis)
            analysis["recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"User behavior analysis failed: {e}")
            ERROR_COUNTER.labels(error_type="analytics_error", service="firestore").inc()
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_engagement_patterns(self, events: List[Dict]) -> Dict[str, Any]:
        """Analyze user engagement patterns"""
        if not events:
            return {"total_events": 0, "engagement_score": 0}
        
        # Categorize events
        event_types = {}
        daily_activity = {}
        
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Daily activity tracking
            event_date = event.get("timestamp", datetime.utcnow()).date()
            daily_activity[str(event_date)] = daily_activity.get(str(event_date), 0) + 1
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(event_types, daily_activity)
        
        return {
            "total_events": len(events),
            "event_types": event_types,
            "daily_activity": daily_activity,
            "engagement_score": engagement_score,
            "active_days": len(daily_activity),
            "average_daily_events": len(events) / max(len(daily_activity), 1)
        }
    
    def _calculate_engagement_score(self, event_types: Dict, daily_activity: Dict) -> float:
        """Calculate user engagement score (0-100)"""
        base_score = 0
        
        # Score based on event diversity
        event_diversity = len(event_types)
        base_score += min(event_diversity * 10, 30)  # Max 30 points
        
        # Score based on frequency
        total_events = sum(event_types.values())
        base_score += min(total_events / 10, 40)  # Max 40 points
        
        # Score based on consistency
        active_days = len(daily_activity)
        base_score += min(active_days * 2, 30)  # Max 30 points
        
        return min(base_score, 100)
    
    def _analyze_content_preferences(self, events: List[Dict]) -> Dict[str, Any]:
        """Analyze user content preferences"""
        preferences = {
            "content_types": {},
            "preferred_creators": {},
            "engagement_times": {},
            "content_categories": {}
        }
        
        for event in events:
            if event.get("content_id"):
                # Would normally fetch content details
                content_type = event.get("data", {}).get("content_type", "unknown")
                preferences["content_types"][content_type] = preferences["content_types"].get(content_type, 0) + 1
                
                creator_id = event.get("data", {}).get("creator_id")
                if creator_id:
                    preferences["preferred_creators"][creator_id] = preferences["preferred_creators"].get(creator_id, 0) + 1
            
            # Analyze engagement times
            event_time = event.get("timestamp", datetime.utcnow())
            hour = event_time.hour
            time_bucket = f"{hour:02d}:00"
            preferences["engagement_times"][time_bucket] = preferences["engagement_times"].get(time_bucket, 0) + 1
        
        return preferences
    
    async def _predict_monetization_potential(self, user_uid: str, events: List[Dict]) -> Dict[str, Any]:
        """Predict user's monetization potential"""
        potential = {
            "score": 0.0,
            "factors": {},
            "recommendations": [],
            "revenue_estimate": 0.0
        }
        
        try:
            # Analyze engagement level
            engagement_level = len(events) / 30  # Events per day average
            potential["factors"]["engagement_level"] = engagement_level
            
            # Analyze content interaction
            content_interactions = len([e for e in events if e.get("event_type") in ["view", "like", "share"]])
            potential["factors"]["content_interactions"] = content_interactions
            
            # Calculate base score
            base_score = min((engagement_level * 10) + (content_interactions / 10), 100)
            potential["score"] = base_score
            
            # Estimate potential revenue
            potential["revenue_estimate"] = base_score * 0.1  # $0.10 per point
            
            # Generate recommendations
            if base_score > 70:
                potential["recommendations"].append("High monetization potential - consider premium content")
            elif base_score > 40:
                potential["recommendations"].append("Medium potential - focus on engagement")
            else:
                potential["recommendations"].append("Build engagement before monetizing")
        
        except Exception as e:
            logger.error(f"Monetization prediction failed: {e}")
            potential["error"] = str(e)
        
        return potential
    
    async def _generate_user_recommendations(self, user_uid: str, analysis: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        try:
            engagement_score = analysis.get("engagement_metrics", {}).get("engagement_score", 0)
            content_prefs = analysis.get("content_preferences", {})
            
            # Engagement-based recommendations
            if engagement_score < 30:
                recommendations.append("Discover new creators and content types")
                recommendations.append("Join community discussions and events")
            elif engagement_score < 70:
                recommendations.append("Try creating your own content")
                recommendations.append("Engage more with your favorite creators")
            else:
                recommendations.append("Consider becoming a creator yourself")
                recommendations.append("Explore monetization opportunities")
            
            # Content-based recommendations
            top_content_type = max(
                content_prefs.get("content_types", {}).items(),
                key=lambda x: x[1],
                default=("video", 0)
            )[0]
            
            if top_content_type != "unknown":
                recommendations.append(f"Explore more {top_content_type} content")
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def generate_creator_insights(self, creator_uid: str) -> Dict[str, Any]:
        """Generate insights for content creators"""
        insights = {
            "audience_analysis": {},
            "content_performance": {},
            "revenue_analytics": {},
            "growth_recommendations": []
        }
        
        try:
            # Analyze creator's audience
            audience_analysis = await self._analyze_creator_audience(creator_uid)
            insights["audience_analysis"] = audience_analysis
            
            # Analyze content performance
            content_performance = await self._analyze_content_performance(creator_uid)
            insights["content_performance"] = content_performance
            
            # Revenue analytics
            revenue_analytics = await self._analyze_creator_revenue(creator_uid)
            insights["revenue_analytics"] = revenue_analytics
            
            # Growth recommendations
            growth_recommendations = await self._generate_growth_recommendations(creator_uid, insights)
            insights["growth_recommendations"] = growth_recommendations
        
        except Exception as e:
            logger.error(f"Creator insights generation failed: {e}")
            insights["error"] = str(e)
        
        return insights
    
    async def _analyze_creator_audience(self, creator_uid: str) -> Dict[str, Any]:
        """Analyze creator's audience demographics and behavior"""
        # In real implementation, this would analyze follower data
        return {
            "total_followers": 0,
            "engagement_rate": 0.0,
            "top_demographics": {},
            "audience_growth": 0.0
        }
    
    async def _analyze_content_performance(self, creator_uid: str) -> Dict[str, Any]:
        """Analyze creator's content performance"""
        # In real implementation, this would analyze content metrics
        return {
            "total_views": 0,
            "average_engagement": 0.0,
            "top_performing_content": [],
            "content_trends": {}
        }
    
    async def _analyze_creator_revenue(self, creator_uid: str) -> Dict[str, Any]:
        """Analyze creator's revenue streams"""
        # In real implementation, this would analyze revenue data
        return {
            "total_revenue": 0.0,
            "revenue_streams": {},
            "monthly_growth": 0.0,
            "revenue_per_follower": 0.0
        }
    
    async def _generate_growth_recommendations(self, creator_uid: str, insights: Dict) -> List[str]:
        """Generate growth recommendations for creators"""
        recommendations = [
            "Focus on creating engaging, high-quality content",
            "Maintain consistent posting schedule",
            "Engage actively with your audience",
            "Collaborate with other creators",
            "Analyze and optimize content based on performance metrics"
        ]
        
        return recommendations

class FirebaseRealtimeManager:
    """Real-time data management - Backend Senior + Microservices roles"""
    
    def __init__(self, config: FirebaseConfig, db_client):
        self.config = config
        self.db = db_client
        self.active_listeners = {}
        
    async def setup_realtime_listeners(self) -> bool:
        """Setup real-time listeners for key collections"""
        try:
            # Listen to user events
            self._setup_user_events_listener()
            
            # Listen to content updates
            self._setup_content_updates_listener()
            
            # Listen to revenue events
            self._setup_revenue_events_listener()
            
            logger.info("Real-time listeners setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Real-time listeners setup failed: {e}")
            return False
    
    def _setup_user_events_listener(self):
        """Setup listener for user events"""
        def on_user_event_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':
                    self._handle_new_user_event(change.document.to_dict())
                elif change.type.name == 'MODIFIED':
                    self._handle_user_event_update(change.document.to_dict())
        
        # Setup listener
        events_ref = self.db.collection('events')
        listener = events_ref.on_snapshot(on_user_event_snapshot)
        self.active_listeners['user_events'] = listener
    
    def _setup_content_updates_listener(self):
        """Setup listener for content updates"""
        def on_content_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':
                    self._handle_new_content(change.document.to_dict())
                elif change.type.name == 'MODIFIED':
                    self._handle_content_update(change.document.to_dict())
        
        content_ref = self.db.collection('content')
        listener = content_ref.on_snapshot(on_content_snapshot)
        self.active_listeners['content'] = listener
    
    def _setup_revenue_events_listener(self):
        """Setup listener for revenue events"""
        def on_revenue_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':
                    self._handle_revenue_event(change.document.to_dict())
        
        revenue_ref = self.db.collection('revenue')
        listener = revenue_ref.on_snapshot(on_revenue_snapshot)
        self.active_listeners['revenue'] = listener
    
    def _handle_new_user_event(self, event_data: Dict):
        """Handle new user event"""
        try:
            # Process real-time analytics
            event_type = event_data.get("event_type")
            user_uid = event_data.get("user_uid")
            
            # Update real-time metrics
            if event_type == "content_view":
                self._update_view_metrics(event_data)
            elif event_type == "subscription":
                self._handle_subscription_event(event_data)
            elif event_type == "purchase":
                self._handle_purchase_event(event_data)
            
            logger.info(f"Processed user event: {event_type} for user {user_uid}")
            
        except Exception as e:
            logger.error(f"User event handling failed: {e}")
    
    def _handle_new_content(self, content_data: Dict):
        """Handle new content creation"""
        try:
            content_id = content_data.get("content_id")
            creator_uid = content_data.get("creator_uid")
            
            # Initialize content analytics
            self._initialize_content_analytics(content_id)
            
            # Send notifications to followers
            asyncio.create_task(self._notify_followers_new_content(creator_uid, content_data))
            
            logger.info(f"Processed new content: {content_id} from creator {creator_uid}")
            
        except Exception as e:
            logger.error(f"New content handling failed: {e}")
    
    def _handle_content_update(self, content_data: Dict):
        """Handle content updates"""
        try:
            content_id = content_data.get("content_id")
            
            # Update content metrics
            self._update_content_metrics(content_id, content_data)
            
            logger.info(f"Processed content update: {content_id}")
            
        except Exception as e:
            logger.error(f"Content update handling failed: {e}")
    
    def _handle_revenue_event(self, revenue_data: Dict):
        """Handle revenue events"""
        try:
            creator_uid = revenue_data.get("creator_uid")
            amount = revenue_data.get("amount", 0)
            
            # Update creator revenue metrics
            self._update_creator_revenue_metrics(creator_uid, amount)
            
            # Send revenue notification
            asyncio.create_task(self._send_revenue_notification(creator_uid, amount))
            
            logger.info(f"Processed revenue event: ${amount} for creator {creator_uid}")
            
        except Exception as e:
            logger.error(f"Revenue event handling failed: {e}")
    
    def _update_view_metrics(self, event_data: Dict):
        """Update view metrics in real-time"""
        content_id = event_data.get("content_id")
        if content_id:
            # Increment view count
            content_ref = self.db.collection('content').document(content_id)
            content_ref.update({
                'view_count': firestore.Increment(1),
                'last_viewed': datetime.utcnow()
            })
    
    def _handle_subscription_event(self, event_data: Dict):
        """Handle subscription events"""
        creator_uid = event_data.get("data", {}).get("creator_uid")
        if creator_uid:
            # Update creator subscriber count
            creator_ref = self.db.collection('users').document(creator_uid)
            creator_ref.update({
                'subscriber_count': firestore.Increment(1)
            })
    
    def _handle_purchase_event(self, event_data: Dict):
        """Handle purchase events"""
        creator_uid = event_data.get("data", {}).get("creator_uid")
        amount = event_data.get("data", {}).get("amount", 0)
        
        if creator_uid and amount:
            # Update creator revenue
            creator_ref = self.db.collection('users').document(creator_uid)
            creator_ref.update({
                'total_revenue': firestore.Increment(amount)
            })
    
    def _initialize_content_analytics(self, content_id: str):
        """Initialize analytics for new content"""
        analytics_data = {
            'content_id': content_id,
            'view_count': 0,
            'like_count': 0,
            'share_count': 0,
            'comment_count': 0,
            'revenue_generated': 0.0,
            'created_at': datetime.utcnow()
        }
        
        self.db.collection('analytics').document(content_id).set(analytics_data)
    
    async def _notify_followers_new_content(self, creator_uid: str, content_data: Dict):
        """Notify followers about new content"""
        try:
            # Get creator's followers
            followers_ref = self.db.collection('subscriptions').where('creator_uid', '==', creator_uid)
            followers = [doc.to_dict() for doc in followers_ref.stream()]
            
            # Send notifications (would use FCM in real implementation)
            notification_data = {
                'title': f"New content from {content_data.get('creator_name', 'Creator')}",
                'body': content_data.get('title', 'Check out this new content!'),
                'content_id': content_data.get('content_id'),
                'creator_uid': creator_uid
            }
            
            # Batch send notifications
            for follower in followers[:100]:  # Limit batch size
                follower_uid = follower.get('subscriber_uid')
                if follower_uid:
                    await self._send_push_notification(follower_uid, notification_data)
            
        except Exception as e:
            logger.error(f"Follower notification failed: {e}")
    
    async def _send_push_notification(self, user_uid: str, notification_data: Dict):
        """Send push notification to user"""
        try:
            # In real implementation, would use Firebase Cloud Messaging
            logger.info(f"Sending notification to {user_uid}: {notification_data['title']}")
            
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
    
    def _update_content_metrics(self, content_id: str, content_data: Dict):
        """Update content performance metrics"""
        try:
            analytics_ref = self.db.collection('analytics').document(content_id)
            
            # Update based on content changes
            updates = {
                'updated_at': datetime.utcnow()
            }
            
            # Check if monetization was enabled
            if content_data.get('monetization_enabled'):
                updates['monetization_enabled_at'] = datetime.utcnow()
            
            analytics_ref.update(updates)
            
        except Exception as e:
            logger.error(f"Content metrics update failed: {e}")
    
    def _update_creator_revenue_metrics(self, creator_uid: str, amount: float):
        """Update creator revenue metrics"""
        try:
            # Update monthly revenue
            current_month = datetime.utcnow().strftime("%Y-%m")
            revenue_ref = self.db.collection('revenue_monthly').document(f"{creator_uid}_{current_month}")
            
            revenue_ref.set({
                'creator_uid': creator_uid,
                'month': current_month,
                'total_revenue': firestore.Increment(amount),
                'transaction_count': firestore.Increment(1),
                'updated_at': datetime.utcnow()
            }, merge=True)
            
        except Exception as e:
            logger.error(f"Revenue metrics update failed: {e}")
    
    async def _send_revenue_notification(self, creator_uid: str, amount: float):
        """Send revenue notification to creator"""
        try:
            notification_data = {
                'title': 'Revenue Update',
                'body': f'You earned ${amount:.2f}!',
                'type': 'revenue',
                'amount': amount
            }
            
            await self._send_push_notification(creator_uid, notification_data)
            
        except Exception as e:
            logger.error(f"Revenue notification failed: {e}")
    
    def cleanup_listeners(self):
        """Cleanup active listeners"""
        for listener_name, listener in self.active_listeners.items():
            try:
                listener.unsubscribe()
                logger.info(f"Unsubscribed from {listener_name} listener")
            except Exception as e:
                logger.error(f"Failed to unsubscribe from {listener_name}: {e}")
        
        self.active_listeners.clear()

class FirebaseIntegration:
    """Main Firebase integration orchestrator - Lead Dev IA + Backend Senior roles"""
    
    def __init__(self, config: FirebaseConfig):
        self.config = config
        self.app = None
        self.db = None
        self.auth_client = None
        self.storage_client = None
        self.messaging_client = None
        
        # Service managers
        self.security_manager = FirebaseSecurityManager(config)
        self.ml_analytics = None
        self.realtime_manager = None
        
        # Connection tracking
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize Firebase services"""
        try:
            logger.info("Initializing Firebase integration")
            
            # Initialize Firebase app
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config.service_account_path)
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': self.config.project_id,
                    'storageBucket': self.config.storage_bucket or f"{self.config.project_id}.appspot.com"
                })
            else:
                self.app = firebase_admin.get_app()
            
            # Initialize services
            if self.config.firestore_enabled:
                self.db = firestore.client()
                self.ml_analytics = FirebaseMLAnalytics(self.config, self.db)
                self.realtime_manager = FirebaseRealtimeManager(self.config, self.db)
            
            if self.config.auth_providers:
                self.auth_client = auth
            
            if self.config.storage_bucket:
                self.storage_client = storage.bucket()
            
            if self.config.fcm_enabled:
                self.messaging_client = messaging
            
            # Setup real-time listeners
            if self.realtime_manager:
                await self.realtime_manager.setup_realtime_listeners()
            
            self.is_initialized = True
            ACTIVE_CONNECTIONS.inc()
            
            logger.info("Firebase integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            ERROR_COUNTER.labels(error_type="initialization", service="firebase").inc()
            return False
    
    async def create_user(self, email: str, password: str, display_name: str, role: UserRole) -> FirebaseUser:
        """Create a new user with custom claims"""
        try:
            with RESPONSE_TIME.labels(service="auth").time():
                # Create user in Firebase Auth
                user_record = self.auth_client.create_user(
                    email=email,
                    password=password,
                    display_name=display_name
                )
                
                # Set custom claims
                custom_claims = self.security_manager.create_custom_claims(role)
                self.auth_client.set_custom_user_claims(user_record.uid, custom_claims)
                
                # Create user document in Firestore
                firebase_user = FirebaseUser(
                    uid=user_record.uid,
                    email=email,
                    display_name=display_name,
                    role=role,
                    created_at=datetime.utcnow(),
                    is_verified=user_record.email_verified
                )
                
                await self._save_user_to_firestore(firebase_user)
                
                AUTH_OPERATIONS.labels(operation="create_user").inc()
                logger.info(f"User created successfully: {user_record.uid}")
                
                return firebase_user
                
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            ERROR_COUNTER.labels(error_type="user_creation", service="auth").inc()
            raise
    
    async def authenticate_user(self, id_token: str) -> Optional[FirebaseUser]:
        """Authenticate user with ID token"""
        try:
            with RESPONSE_TIME.labels(service="auth").time():
                # Verify the ID token
                decoded_token = self.auth_client.verify_id_token(id_token)
                uid = decoded_token['uid']
                
                # Get user data from Firestore
                user_doc = self.db.collection('users').document(uid).get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    firebase_user = FirebaseUser(
                        uid=uid,
                        email=user_data.get('email'),
                        display_name=user_data.get('display_name'),
                        role=UserRole(user_data.get('role', 'viewer')),
                        creator_profile=user_data.get('creator_profile'),
                        subscription_tier=user_data.get('subscription_tier'),
                        analytics_data=user_data.get('analytics_data'),
                        created_at=user_data.get('created_at'),
                        last_login=datetime.utcnow(),
                        is_verified=user_data.get('is_verified', False)
                    )
                    
                    # Update last login
                    await self._update_user_last_login(uid)
                    
                    AUTH_OPERATIONS.labels(operation="authenticate").inc()
                    return firebase_user
                
                return None
                
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            ERROR_COUNTER.labels(error_type="authentication", service="auth").inc()
            return None
    
    async def create_content(self, creator_uid: str, content_data: Dict) -> CreatorContent:
        """Create new creator content"""
        try:
            with RESPONSE_TIME.labels(service="firestore").time():
                content_id = str(uuid.uuid4())
                
                # Validate content security
                security_check = self.security_manager.validate_content_security(content_data)
                if not security_check["safe"]:
                    raise ValueError(f"Content security validation failed: {security_check['issues']}")
                
                # Create content object
                content = CreatorContent(
                    content_id=content_id,
                    creator_uid=creator_uid,
                    title=content_data.get('title'),
                    description=content_data.get('description'),
                    content_type=ContentType(content_data.get('content_type', 'video')),
                    file_url=content_data.get('file_url'),
                    thumbnail_url=content_data.get('thumbnail_url'),
                    duration=content_data.get('duration'),
                    visibility=content_data.get('visibility', 'public'),
                    monetization_enabled=content_data.get('monetization_enabled', False),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # Save to Firestore
                await self._save_content_to_firestore(content)
                
                DATABASE_OPERATIONS.labels(operation="create", collection="content").inc()
                logger.info(f"Content created successfully: {content_id}")
                
                return content
                
        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            ERROR_COUNTER.labels(error_type="content_creation", service="firestore").inc()
            raise
    
    async def track_event(self, user_uid: str, event_type: str, event_data: Dict = None) -> RealtimeEvent:
        """Track real-time user events"""
        try:
            with RESPONSE_TIME.labels(service="firestore").time():
                event_id = str(uuid.uuid4())
                
                event = RealtimeEvent(
                    event_id=event_id,
                    event_type=event_type,
                    user_uid=user_uid,
                    content_id=event_data.get('content_id') if event_data else None,
                    data=event_data or {},
                    timestamp=datetime.utcnow()
                )
                
                # Save to Firestore
                await self._save_event_to_firestore(event)
                
                DATABASE_OPERATIONS.labels(operation="create", collection="events").inc()
                logger.info(f"Event tracked: {event_type} for user {user_uid}")
                
                return event
                
        except Exception as e:
            logger.error(f"Event tracking failed: {e}")
            ERROR_COUNTER.labels(error_type="event_tracking", service="firestore").inc()
            raise
    
    async def upload_file(self, file_path: str, destination_path: str, content_type: str = None) -> str:
        """Upload file to Firebase Storage"""
        try:
            with RESPONSE_TIME.labels(service="storage").time():
                blob = self.storage_client.blob(destination_path)
                
                with open(file_path, 'rb') as file_data:
                    blob.upload_from_file(file_data, content_type=content_type)
                
                # Make public if needed
                blob.make_public()
                
                STORAGE_OPERATIONS.labels(operation="upload").inc()
                logger.info(f"File uploaded successfully: {destination_path}")
                
                return blob.public_url
                
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            ERROR_COUNTER.labels(error_type="file_upload", service="storage").inc()
            raise
    
    async def send_notification(self, user_uid: str, title: str, body: str, data: Dict = None) -> bool:
        """Send push notification to user"""
        try:
            if not self.messaging_client:
                logger.warning("Firebase messaging not initialized")
                return False
            
            # Get user's FCM token (would be stored in user document)
            user_doc = self.db.collection('users').document(user_uid).get()
            if not user_doc.exists:
                return False
            
            fcm_token = user_doc.to_dict().get('fcm_token')
            if not fcm_token:
                return False
            
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=fcm_token
            )
            
            # Send message
            response = self.messaging_client.send(message)
            
            logger.info(f"Notification sent successfully: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            ERROR_COUNTER.labels(error_type="notification", service="messaging").inc()
            return False
    
    async def get_user_analytics(self, user_uid: str) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        if not self.ml_analytics:
            return {"error": "Analytics not available"}
        
        return await self.ml_analytics.analyze_user_behavior(user_uid)
    
    async def get_creator_insights(self, creator_uid: str) -> Dict[str, Any]:
        """Get creator-specific insights"""
        if not self.ml_analytics:
            return {"error": "Analytics not available"}
        
        return await self.ml_analytics.generate_creator_insights(creator_uid)
    
    async def _save_user_to_firestore(self, user: FirebaseUser):
        """Save user data to Firestore"""
        user_data = asdict(user)
        user_data['created_at'] = user.created_at
        user_data['last_login'] = user.last_login
        
        self.db.collection('users').document(user.uid).set(user_data)
    
    async def _save_content_to_firestore(self, content: CreatorContent):
        """Save content data to Firestore"""
        content_data = asdict(content)
        content_data['created_at'] = content.created_at
        content_data['updated_at'] = content.updated_at
        
        self.db.collection('content').document(content.content_id).set(content_data)
    
    async def _save_event_to_firestore(self, event: RealtimeEvent):
        """Save event data to Firestore"""
        event_data = asdict(event)
        event_data['timestamp'] = event.timestamp
        
        self.db.collection('events').document(event.event_id).set(event_data)
    
    async def _update_user_last_login(self, uid: str):
        """Update user's last login timestamp"""
        self.db.collection('users').document(uid).update({
            'last_login': datetime.utcnow()
        })
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {},
            "metrics": {
                "active_connections": ACTIVE_CONNECTIONS._value.get(),
                "system_memory_usage": psutil.virtual_memory().percent,
                "system_cpu_usage": psutil.cpu_percent()
            }
        }
        
        # Check individual services
        if self.db:
            health_status["services"]["firestore"] = await self._check_firestore_health()
        
        if self.auth_client:
            health_status["services"]["auth"] = await self._check_auth_health()
        
        if self.storage_client:
            health_status["services"]["storage"] = await self._check_storage_health()
        
        # Determine overall health
        service_statuses = list(health_status["services"].values())
        if "unhealthy" in service_statuses:
            health_status["status"] = "unhealthy"
        elif "degraded" in service_statuses:
            health_status["status"] = "degraded"
        
        return health_status
    
    async def _check_firestore_health(self) -> str:
        """Check Firestore health"""
        try:
            # Simple read operation
            test_doc = self.db.collection('health_check').document('test').get()
            return "healthy"
        except Exception as e:
            logger.error(f"Firestore health check failed: {e}")
            return "unhealthy"
    
    async def _check_auth_health(self) -> str:
        """Check Auth health"""
        try:
            # Simple auth operation
            users = self.auth_client.list_users(max_results=1)
            return "healthy"
        except Exception as e:
            logger.error(f"Auth health check failed: {e}")
            return "unhealthy"
    
    async def _check_storage_health(self) -> str:
        """Check Storage health"""
        try:
            # Simple storage operation
            list(self.storage_client.list_blobs(max_results=1))
            return "healthy"
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return "unhealthy"
    
    async def cleanup(self):
        """Cleanup Firebase resources"""
        try:
            # Cleanup real-time listeners
            if self.realtime_manager:
                self.realtime_manager.cleanup_listeners()
            
            ACTIVE_CONNECTIONS.dec()
            self.is_initialized = False
            
            logger.info("Firebase integration cleanup completed")
            
        except Exception as e:
            logger.error(f"Firebase cleanup failed: {e}")

# Service factory and configuration
class FirebaseService:
    """Main Firebase service facade - DevOps + Integration role"""
    
    def __init__(self, config: Optional[FirebaseConfig] = None):
        self.config = config or FirebaseConfig(
            project_id="your-firebase-project-id",
            service_account_path="path/to/service-account.json",
            firestore_enabled=True,
            auth_providers=["email", "google"],
            fcm_enabled=True,
            analytics_enabled=True
        )
        self.integration = FirebaseIntegration(self.config)
    
    async def initialize(self) -> bool:
        """Initialize the Firebase service"""
        logger.info("Initializing Firebase Service")
        
        # Validate configuration
        await self._validate_configuration()
        
        # Initialize Firebase integration
        success = await self.integration.initialize()
        
        if success:
            logger.info("Firebase Service initialized successfully")
        else:
            logger.error("Firebase Service initialization failed")
        
        return success
    
    async def _validate_configuration(self):
        """Validate service configuration"""
        if not os.path.exists(self.config.service_account_path):
            logger.warning("Firebase service account file not found")
        
        if not self.config.project_id or self.config.project_id == "your-firebase-project-id":
            logger.warning("Firebase project ID not configured")
    
    async def create_user(self, email: str, password: str, display_name: str, role: UserRole = UserRole.VIEWER) -> FirebaseUser:
        """Create user with full enterprise features"""
        return await self.integration.create_user(email, password, display_name, role)
    
    async def authenticate_user(self, id_token: str) -> Optional[FirebaseUser]:
        """Authenticate user"""
        return await self.integration.authenticate_user(id_token)
    
    async def create_content(self, creator_uid: str, content_data: Dict) -> CreatorContent:
        """Create content"""
        return await self.integration.create_content(creator_uid, content_data)
    
    async def track_event(self, user_uid: str, event_type: str, event_data: Dict = None) -> RealtimeEvent:
        """Track event"""
        return await self.integration.track_event(user_uid, event_type, event_data)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return await self.integration.health_check()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            "database_operations": DATABASE_OPERATIONS._value.sum(),
            "auth_operations": AUTH_OPERATIONS._value.sum(),
            "storage_operations": STORAGE_OPERATIONS._value.sum(),
            "function_invocations": FUNCTION_INVOCATIONS._value.sum(),
            "active_connections": ACTIVE_CONNECTIONS._value.get(),
            "error_count": ERROR_COUNTER._value.sum()
        }
    
    async def cleanup(self):
        """Cleanup service resources"""
        await self.integration.cleanup()

# Export main classes and functions
__all__ = [
    'FirebaseService',
    'FirebaseConfig',
    'FirebaseUser',
    'CreatorContent',
    'RealtimeEvent',
    'UserRole',
    'ContentType',
    'FirebaseService',
    'FirebaseIntegration'
]

if __name__ == "__main__":
    # Example usage and testing
    async def main():
        # Initialize service
        service = FirebaseService()
        success = await service.initialize()
        
        if success:
            # Health check
            health = await service.get_health_status()
            print(f"Service Health: {health}")
            
            # Example user creation
            # user = await service.create_user("test@example.com", "password123", "Test User", UserRole.CREATOR)
            # print(f"User created: {user}")
        
        # Cleanup
        await service.cleanup()
    
    # Run example
    # asyncio.run(main())