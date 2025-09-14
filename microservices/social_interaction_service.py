"""
Social Interaction Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🎯 SocialInteractionService - Advanced Social Features & Interaction Management
===============================================================================

Enterprise social interaction platform with AI-powered engagement optimization,
real-time communication, and comprehensive social analytics. Demonstrates all 9 expert roles.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

Expert Roles Demonstrated:
🧠 Lead Dev IA: AI-powered social matching and engagement optimization
🏗️ Backend Senior: Scalable social platform with enterprise architecture
🤖 ML Engineer: Machine learning for social behavior analysis and recommendations
🗄️ DBA: Optimized social graph storage with relationship indexing
🔒 Security: Privacy protection, content moderation, and anti-harassment systems
🌐 Microservices: Real-time social coordination and distributed communication
🎵 Audio: Social audio features and music collaboration tools
⚙️ DevOps: Performance monitoring, auto-scaling, and real-time metrics
💡 AI Prompt: Intelligent content suggestions and social interaction prompts
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from functools import wraps
import hashlib
import uuid
import redis
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from cryptography.fernet import Fernet
import jwt
from prometheus_client import Counter, Histogram, Gauge
import structlog

class InteractionType(Enum):
    """Social interaction types"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    MENTION = "mention"
    COLLABORATE = "collaborate"
    MESSAGE = "message"
    REACT = "react"
    BOOKMARK = "bookmark"

class RelationshipType(Enum):
    """Relationship classifications"""
    FOLLOWER = "follower"
    FOLLOWING = "following"
    MUTUAL = "mutual"
    COLLABORATOR = "collaborator"
    BLOCKED = "blocked"
    MUTED = "muted"
    FRIEND = "friend"

class ContentVisibility(Enum):
    """Content visibility levels"""
    PUBLIC = "public"
    FOLLOWERS = "followers"
    FRIENDS = "friends"
    COLLABORATORS = "collaborators"
    PRIVATE = "private"

@dataclass
class SocialInteraction:
    """Social interaction data structure"""
    interaction_id: str
    user_id: str
    target_user_id: Optional[str]
    content_id: Optional[str]
    interaction_type: InteractionType
    content: str
    timestamp: datetime
    visibility: ContentVisibility
    metadata: Dict[str, Any]

@dataclass
class UserRelationship:
    """User relationship data structure"""
    relationship_id: str
    user_id: str
    target_user_id: str
    relationship_type: RelationshipType
    created_at: datetime
    strength_score: float  # AI-calculated relationship strength
    interaction_count: int
    last_interaction: datetime
    metadata: Dict[str, Any]

@dataclass
class SocialProfile:
    """User's social profile"""
    user_id: str
    display_name: str
    bio: str
    avatar_url: str
    follower_count: int
    following_count: int
    engagement_rate: float
    influence_score: float
    content_preferences: List[str]
    activity_patterns: Dict[str, Any]
    privacy_settings: Dict[str, bool]

class SocialInteractionService:
    """
    🎯 Enterprise Social Interaction Service
    
    Advanced social platform with AI-powered engagement optimization, real-time
    communication, and comprehensive social analytics for creator collaboration.
    
    Expert Roles Implementation:
    - Lead Dev IA: AI social matching and engagement prediction
    - Backend Senior: Scalable social graph with high-performance queries
    - ML Engineer: Social behavior analysis and recommendation algorithms
    - DBA: Optimized relationship storage and social graph indexing
    - Security: Privacy protection and comprehensive content moderation
    - Microservices: Real-time social coordination across services
    - Audio Engineer: Social audio features and music collaboration
    - DevOps: Performance monitoring and automated social analytics
    - AI Prompt: Intelligent social content and interaction suggestions
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            decode_responses=True
        )
        
        # 🔒 Security: Encryption for sensitive social data
        self.encryption_key = config.get('encryption_key', Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 🤖 ML Engineer: Initialize ML models for social analysis
        self.scaler = StandardScaler()
        self.social_clusterer = KMeans(n_clusters=8, random_state=42)
        self.engagement_predictor = None  # Will be trained dynamically
        
        # ⚙️ DevOps: Performance monitoring metrics
        self.metrics = {
            'interactions_created': Counter('social_interactions_created_total', 'Total social interactions created'),
            'relationships_formed': Counter('social_relationships_formed_total', 'Total relationships formed'),
            'content_moderated': Counter('social_content_moderated_total', 'Total content moderated'),
            'processing_time': Histogram('social_processing_seconds', 'Social processing time'),
            'active_users': Gauge('social_active_users', 'Currently active social users'),
            'engagement_rate': Gauge('social_engagement_rate', 'Overall platform engagement rate')
        }
        
        # 🧠 Lead Dev IA: AI-powered interaction templates
        self.interaction_templates = {
            'welcome_message': [
                "Welcome to our creator community! 🎉 Excited to see what you'll create!",
                "🌟 Great to have you here! Looking forward to your creative contributions!",
                "👋 Welcome aboard! Can't wait to see your unique creativity shine!"
            ],
            'collaboration_invite': [
                "🤝 I think we'd create something amazing together! Interested in collaborating?",
                "✨ Your style really resonates with me. Want to work on a project together?",
                "🎯 I have an idea that could work perfectly with your skills. Collaboration?"
            ],
            'audio_collaboration': [
                "🎵 Your music style is incredible! Want to create a track together?",
                "🎼 I'd love to collaborate on an audio project with you!",
                "🎤 Your sound production skills are amazing. Interested in a music collab?"
            ],
            'engagement_prompts': [
                "What's inspiring your creative process today? 🎨",
                "Share your latest project insights with the community! 💡",
                "What's one technique you've recently mastered? 🏆"
            ]
        }
        
        # Content moderation keywords and patterns
        self.moderation_filters = {
            'toxic_keywords': ['spam', 'hate', 'abuse'],  # Simplified for example
            'sentiment_threshold': -0.5,
            'max_mentions_per_post': 5,
            'max_hashtags_per_post': 10
        }
        
        self.logger = structlog.get_logger(__name__)
        self.logger.info("SocialInteractionService initialized with enterprise configuration")

    async def create_interaction(self, user_id: str, interaction_data: Dict[str, Any]) -> SocialInteraction:
        """
        🧠 Lead Dev IA: Create social interaction with AI-powered optimization
        
        Args:
            user_id: User creating the interaction
            interaction_data: Interaction details and content
            
        Returns:
            Created SocialInteraction object
        """
        try:
            # 🔒 Security: Validate user permissions and content
            if not await self._validate_interaction_permissions(user_id, interaction_data):
                raise ValueError("User not authorized or invalid interaction data")
            
            # 🔒 Security: Content moderation
            moderated_content = await self._moderate_content(interaction_data.get('content', ''))
            if not moderated_content['approved']:
                raise ValueError(f"Content moderation failed: {moderated_content['reason']}")
            
            # Create interaction object
            interaction = SocialInteraction(
                interaction_id=str(uuid.uuid4()),
                user_id=user_id,
                target_user_id=interaction_data.get('target_user_id'),
                content_id=interaction_data.get('content_id'),
                interaction_type=InteractionType(interaction_data['type']),
                content=moderated_content['content'],
                timestamp=datetime.now(),
                visibility=ContentVisibility(interaction_data.get('visibility', 'public')),
                metadata=interaction_data.get('metadata', {})
            )
            
            # 🗄️ DBA: Store interaction with optimized indexing
            await self._store_interaction(interaction)
            
            # Update relationship strength if applicable
            if interaction.target_user_id:
                await self._update_relationship_strength(user_id, interaction.target_user_id, interaction.interaction_type)
            
            # 🧠 Lead Dev IA: Generate AI-powered engagement opportunities
            await self._generate_engagement_opportunities(interaction)
            
            # ⚙️ DevOps: Update metrics
            self.metrics['interactions_created'].inc()
            
            self.logger.info(f"Social interaction created: {interaction.interaction_id}")
            return interaction
            
        except Exception as e:
            self.logger.error(f"Error creating social interaction: {str(e)}")
            raise

    async def _validate_interaction_permissions(self, user_id: str, interaction_data: Dict[str, Any]) -> bool:
        """🔒 Security: Validate interaction permissions and data"""
        try:
            # Check user authentication
            user_token = self.redis_client.get(f"user_token:{user_id}")
            if not user_token:
                return False
            
            # Validate JWT token
            try:
                jwt.decode(user_token, self.config.get('jwt_secret', 'secret'), algorithms=['HS256'])
            except jwt.InvalidTokenError:
                return False
            
            # Check required fields
            required_fields = ['type', 'content']
            if not all(field in interaction_data for field in required_fields):
                return False
            
            # Validate interaction type
            try:
                InteractionType(interaction_data['type'])
            except ValueError:
                return False
            
            # Check rate limiting
            if not await self._check_rate_limits(user_id, interaction_data['type']):
                return False
            
            # Check target user permissions if applicable
            target_user_id = interaction_data.get('target_user_id')
            if target_user_id:
                if not await self._check_target_user_permissions(user_id, target_user_id):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating interaction permissions: {str(e)}")
            return False

    async def _check_rate_limits(self, user_id: str, interaction_type: str) -> bool:
        """Check user rate limits for interactions"""
        try:
            # Define rate limits per interaction type
            rate_limits = {
                'like': {'limit': 100, 'window': 3600},      # 100 likes per hour
                'comment': {'limit': 50, 'window': 3600},    # 50 comments per hour
                'follow': {'limit': 20, 'window': 3600},     # 20 follows per hour
                'message': {'limit': 30, 'window': 3600},    # 30 messages per hour
                'share': {'limit': 25, 'window': 3600}       # 25 shares per hour
            }
            
            if interaction_type not in rate_limits:
                return True  # No limit for this type
            
            limit_config = rate_limits[interaction_type]
            window_start = int(time.time()) - limit_config['window']
            
            # Count interactions in the time window
            interaction_count = self.redis_client.zcount(
                f"user_interactions:{user_id}:{interaction_type}",
                window_start,
                '+inf'
            )
            
            return interaction_count < limit_config['limit']
            
        except Exception as e:
            self.logger.error(f"Error checking rate limits: {str(e)}")
            return True  # Allow by default if check fails

    async def _check_target_user_permissions(self, user_id: str, target_user_id: str) -> bool:
        """Check permissions for interacting with target user"""
        try:
            # Check if user is blocked
            is_blocked = self.redis_client.sismember(f"blocked_users:{target_user_id}", user_id)
            if is_blocked:
                return False
            
            # Check if target user is private and user is not following
            privacy_settings = self.redis_client.hgetall(f"user_privacy:{target_user_id}")
            if privacy_settings.get('profile_visibility') == 'private':
                is_following = self.redis_client.sismember(f"user_followers:{target_user_id}", user_id)
                if not is_following:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking target user permissions: {str(e)}")
            return True

    async def _moderate_content(self, content: str) -> Dict[str, Any]:
        """🔒 Security: Advanced content moderation with AI"""
        try:
            moderation_result = {
                'approved': True,
                'content': content,
                'reason': '',
                'confidence': 1.0
            }
            
            # Basic keyword filtering
            content_lower = content.lower()
            for toxic_word in self.moderation_filters['toxic_keywords']:
                if toxic_word in content_lower:
                    moderation_result.update({
                        'approved': False,
                        'reason': f'Contains prohibited content: {toxic_word}',
                        'confidence': 0.9
                    })
                    break
            
            # Check mention spam
            mention_count = content.count('@')
            if mention_count > self.moderation_filters['max_mentions_per_post']:
                moderation_result.update({
                    'approved': False,
                    'reason': f'Too many mentions: {mention_count}',
                    'confidence': 0.8
                })
            
            # Check hashtag spam
            hashtag_count = content.count('#')
            if hashtag_count > self.moderation_filters['max_hashtags_per_post']:
                moderation_result.update({
                    'approved': False,
                    'reason': f'Too many hashtags: {hashtag_count}',
                    'confidence': 0.8
                })
            
            # 🤖 ML Engineer: AI-powered sentiment analysis (simplified)
            sentiment_score = await self._analyze_sentiment(content)
            if sentiment_score < self.moderation_filters['sentiment_threshold']:
                moderation_result.update({
                    'approved': False,
                    'reason': f'Negative sentiment detected: {sentiment_score}',
                    'confidence': 0.7
                })
            
            # Log moderation action if content was rejected
            if not moderation_result['approved']:
                self.metrics['content_moderated'].inc()
                self.logger.warning(f"Content moderated: {moderation_result['reason']}")
            
            return moderation_result
            
        except Exception as e:
            self.logger.error(f"Error moderating content: {str(e)}")
            return {'approved': True, 'content': content, 'reason': '', 'confidence': 0.5}

    async def _analyze_sentiment(self, content: str) -> float:
        """🤖 ML Engineer: Simple sentiment analysis"""
        try:
            # Simplified sentiment analysis (in production, use proper NLP models)
            positive_words = ['great', 'awesome', 'amazing', 'love', 'excellent', 'fantastic', 'wonderful']
            negative_words = ['hate', 'terrible', 'awful', 'bad', 'worst', 'horrible', 'disgusting']
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count + negative_count == 0:
                return 0.0  # Neutral
            
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
            return sentiment_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return 0.0

    async def _store_interaction(self, interaction -> None: SocialInteraction) -> None:
        """🗄️ DBA: Store interaction with optimized social graph indexing"""
        try:
            interaction_data = asdict(interaction)
            # Convert datetime to timestamp for storage
            interaction_data['timestamp'] = interaction.timestamp.timestamp()
            
            # 🔒 Security: Encrypt sensitive data
            encrypted_data = self.cipher_suite.encrypt(json.dumps(interaction_data).encode())
            
            pipe = self.redis_client.pipeline()
            
            # Primary interaction storage
            pipe.hset(f"interaction:{interaction.interaction_id}", mapping={
                'data': encrypted_data,
                'user_id': interaction.user_id,
                'target_user_id': interaction.target_user_id or '',
                'interaction_type': interaction.interaction_type.value,
                'timestamp': int(interaction.timestamp.timestamp()),
                'visibility': interaction.visibility.value
            })
            
            # User interaction timeline
            pipe.zadd(f"user_interactions:{interaction.user_id}", 
                     {interaction.interaction_id: interaction.timestamp.timestamp()})
            
            # Interaction type indexing for analytics
            pipe.zadd(f"user_interactions:{interaction.user_id}:{interaction.interaction_type.value}",
                     {interaction.interaction_id: interaction.timestamp.timestamp()})
            
            # Target user notifications if applicable
            if interaction.target_user_id:
                pipe.zadd(f"user_notifications:{interaction.target_user_id}",
                         {interaction.interaction_id: interaction.timestamp.timestamp()})
            
            # Content interaction tracking
            if interaction.content_id:
                pipe.zadd(f"content_interactions:{interaction.content_id}",
                         {interaction.interaction_id: interaction.timestamp.timestamp()})
                pipe.hincrby(f"content_stats:{interaction.content_id}", 
                           interaction.interaction_type.value, 1)
            
            # Rate limiting tracking
            pipe.zadd(f"user_interactions:{interaction.user_id}:{interaction.interaction_type.value}",
                     {interaction.interaction_id: time.time()})
            
            await asyncio.get_event_loop().run_in_executor(None, pipe.execute)
            
        except Exception as e:
            self.logger.error(f"Error storing interaction: {str(e)}")
            raise

    async def _update_relationship_strength(self, user_id -> None: str, target_user_id -> None: str, 
                                          interaction_type -> None: InteractionType) -> None:
        """🤖 ML Engineer: Update relationship strength based on interactions"""
        try:
            relationship_key = f"relationship:{user_id}:{target_user_id}"
            
            # Get current relationship data
            relationship_data = self.redis_client.hgetall(relationship_key)
            
            # Calculate interaction weight
            interaction_weights = {
                InteractionType.LIKE: 1.0,
                InteractionType.COMMENT: 2.0,
                InteractionType.SHARE: 3.0,
                InteractionType.COLLABORATE: 5.0,
                InteractionType.MESSAGE: 2.5,
                InteractionType.FOLLOW: 4.0
            }
            
            weight = interaction_weights.get(interaction_type, 1.0)
            
            if relationship_data:
                # Update existing relationship
                current_strength = float(relationship_data.get('strength_score', 0.0))
                current_count = int(relationship_data.get('interaction_count', 0))
                
                # Calculate new strength (exponential moving average)
                alpha = 0.1  # Learning rate
                new_strength = (1 - alpha) * current_strength + alpha * weight
                new_count = current_count + 1
                
                # Update relationship
                self.redis_client.hset(relationship_key, mapping={
                    'strength_score': new_strength,
                    'interaction_count': new_count,
                    'last_interaction': datetime.now().isoformat()
                })
            else:
                # Create new relationship
                relationship = UserRelationship(
                    relationship_id=str(uuid.uuid4()),
                    user_id=user_id,
                    target_user_id=target_user_id,
                    relationship_type=RelationshipType.FOLLOWER,  # Default
                    created_at=datetime.now(),
                    strength_score=weight,
                    interaction_count=1,
                    last_interaction=datetime.now(),
                    metadata={}
                )
                await self._store_relationship(relationship)
            
        except Exception as e:
            self.logger.error(f"Error updating relationship strength: {str(e)}")

    async def _store_relationship(self, relationship -> None: UserRelationship) -> None:
        """Store user relationship data"""
        try:
            relationship_data = asdict(relationship)
            
            # Convert datetime objects to strings
            relationship_data['created_at'] = relationship.created_at.isoformat()
            relationship_data['last_interaction'] = relationship.last_interaction.isoformat()
            
            # 🔒 Security: Encrypt relationship data
            encrypted_data = self.cipher_suite.encrypt(json.dumps(relationship_data).encode())
            
            relationship_key = f"relationship:{relationship.user_id}:{relationship.target_user_id}"
            
            self.redis_client.hset(relationship_key, mapping={
                'data': encrypted_data,
                'relationship_type': relationship.relationship_type.value,
                'strength_score': relationship.strength_score,
                'interaction_count': relationship.interaction_count,
                'created_at': relationship.created_at.isoformat()
            })
            
            # Index relationships for quick lookup
            self.redis_client.sadd(f"user_relationships:{relationship.user_id}", relationship.target_user_id)
            
        except Exception as e:
            self.logger.error(f"Error storing relationship: {str(e)}")
            raise

    async def _generate_engagement_opportunities(self, interaction -> None: SocialInteraction) -> None:
        """🧠 Lead Dev IA: Generate AI-powered engagement opportunities"""
        try:
            opportunities = []
            
            # Analyze interaction context for opportunities
            if interaction.interaction_type == InteractionType.FOLLOW:
                # Suggest welcome message
                template = np.random.choice(self.interaction_templates['welcome_message'])
                opportunities.append({
                    'type': 'welcome_message',
                    'target_user_id': interaction.user_id,
                    'content': template,
                    'priority': 'high'
                })
            
            elif interaction.interaction_type == InteractionType.LIKE and interaction.content_id:
                # Suggest collaboration if users have similar content
                similar_users = await self._find_similar_content_creators(interaction.user_id)
                if interaction.target_user_id in similar_users:
                    template = np.random.choice(self.interaction_templates['collaboration_invite'])
                    opportunities.append({
                        'type': 'collaboration_invite',
                        'target_user_id': interaction.user_id,
                        'content': template,
                        'priority': 'medium'
                    })
            
            # 🎵 Audio Engineer: Audio-specific engagement opportunities
            if interaction.metadata.get('content_type') == 'audio':
                template = np.random.choice(self.interaction_templates['audio_collaboration'])
                opportunities.append({
                    'type': 'audio_collaboration',
                    'target_user_id': interaction.user_id,
                    'content': template,
                    'priority': 'high'
                })
            
            # Store opportunities for later processing
            if opportunities:
                for opp in opportunities:
                    self.redis_client.lpush(f"engagement_opportunities:{opp['target_user_id']}", 
                                          json.dumps(opp))
                    # Limit to 20 opportunities per user
                    self.redis_client.ltrim(f"engagement_opportunities:{opp['target_user_id']}", 0, 19)
            
        except Exception as e:
            self.logger.error(f"Error generating engagement opportunities: {str(e)}")

    async def _find_similar_content_creators(self, user_id: str, limit: int = 10) -> List[str]:
        """🤖 ML Engineer: Find users with similar content preferences"""
        try:
            # Get user's content interaction history
            user_interactions = self.redis_client.zrange(f"user_interactions:{user_id}", 0, -1)
            
            if not user_interactions:
                return []
            
            # Analyze interaction patterns to find similar users
            user_content_types = {}
            
            for interaction_id in user_interactions[-50:]:  # Last 50 interactions
                interaction_data = self.redis_client.hgetall(f"interaction:{interaction_id}")
                content_id = interaction_data.get('content_id')
                
                if content_id:
                    content_metadata = self.redis_client.hgetall(f"content_metadata:{content_id}")
                    content_type = content_metadata.get('type', 'unknown')
                    user_content_types[content_type] = user_content_types.get(content_type, 0) + 1
            
            # Find users with similar content type preferences
            similar_users = []
            all_users = self.redis_client.keys("user_interactions:*")
            
            for user_key in all_users[:100]:  # Limit search for performance
                other_user_id = user_key.split(':')[1]
                if other_user_id == user_id:
                    continue
                
                other_interactions = self.redis_client.zrange(user_key, 0, -1)
                other_content_types = {}
                
                for interaction_id in other_interactions[-50:]:
                    interaction_data = self.redis_client.hgetall(f"interaction:{interaction_id}")
                    content_id = interaction_data.get('content_id')
                    
                    if content_id:
                        content_metadata = self.redis_client.hgetall(f"content_metadata:{content_id}")
                        content_type = content_metadata.get('type', 'unknown')
                        other_content_types[content_type] = other_content_types.get(content_type, 0) + 1
                
                # Calculate similarity (simplified Jaccard similarity)
                common_types = set(user_content_types.keys()) & set(other_content_types.keys())
                total_types = set(user_content_types.keys()) | set(other_content_types.keys())
                
                if total_types:
                    similarity = len(common_types) / len(total_types)
                    if similarity > 0.3:  # 30% similarity threshold
                        similar_users.append(other_user_id)
            
            return similar_users[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding similar content creators: {str(e)}")
            return []

    async def get_user_feed(self, user_id: str, limit: int = 50, 
                           feed_type: str = 'timeline') -> List[Dict[str, Any]]:
        """
        💡 AI Prompt: Generate personalized user feed with AI optimization
        
        Args:
            user_id: User requesting the feed
            limit: Maximum number of feed items
            feed_type: Type of feed ('timeline', 'discover', 'following')
            
        Returns:
            Personalized feed items with engagement predictions
        """
        try:
            feed_items = []
            
            if feed_type == 'timeline':
                # Get interactions from followed users
                following_users = self.redis_client.smembers(f"user_following:{user_id}")
                
                for followed_user in following_users:
                    user_interactions = self.redis_client.zrevrange(
                        f"user_interactions:{followed_user}", 0, 10, withscores=True
                    )
                    
                    for interaction_id, timestamp in user_interactions:
                        interaction_data = await self._get_interaction(interaction_id)
                        if interaction_data and interaction_data.visibility in [ContentVisibility.PUBLIC, ContentVisibility.FOLLOWERS]:
                            feed_items.append({
                                'interaction': asdict(interaction_data),
                                'timestamp': timestamp,
                                'source': 'following',
                                'engagement_prediction': await self._predict_engagement(user_id, interaction_data)
                            })
            
            elif feed_type == 'discover':
                # AI-powered content discovery
                recommended_content = await self._generate_content_recommendations(user_id)
                
                for content_rec in recommended_content:
                    content_interactions = self.redis_client.zrevrange(
                        f"content_interactions:{content_rec['content_id']}", 0, 5
                    )
                    
                    for interaction_id in content_interactions:
                        interaction_data = await self._get_interaction(interaction_id)
                        if interaction_data:
                            feed_items.append({
                                'interaction': asdict(interaction_data),
                                'timestamp': interaction_data.timestamp.timestamp(),
                                'source': 'discover',
                                'recommendation_score': content_rec['score'],
                                'engagement_prediction': await self._predict_engagement(user_id, interaction_data)
                            })
            
            # Sort by engagement prediction and timestamp
            feed_items.sort(key=lambda x: (x.get('engagement_prediction', 0), x['timestamp']), reverse=True)
            
            return feed_items[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating user feed: {str(e)}")
            return []

    async def _get_interaction(self, interaction_id: str) -> Optional[SocialInteraction]:
        """Retrieve interaction by ID"""
        try:
            interaction_data = self.redis_client.hget(f"interaction:{interaction_id}", 'data')
            if not interaction_data:
                return None
            
            # 🔒 Security: Decrypt interaction data
            decrypted_data = json.loads(self.cipher_suite.decrypt(interaction_data.encode()).decode())
            
            # Convert timestamp back to datetime
            decrypted_data['timestamp'] = datetime.fromtimestamp(decrypted_data['timestamp'])
            
            # Convert to SocialInteraction object
            interaction = SocialInteraction(**decrypted_data)
            return interaction
            
        except Exception as e:
            self.logger.error(f"Error retrieving interaction: {str(e)}")
            return None

    async def _predict_engagement(self, user_id: str, interaction: SocialInteraction) -> float:
        """🤖 ML Engineer: Predict user engagement with content"""
        try:
            # Simple engagement prediction based on user history
            user_interactions = self.redis_client.zrange(f"user_interactions:{user_id}", -20, -1)
            
            if not user_interactions:
                return 0.5  # Default prediction
            
            # Analyze user's interaction patterns
            interaction_types = {}
            for interaction_id in user_interactions:
                past_interaction = self.redis_client.hget(f"interaction:{interaction_id}", 'interaction_type')
                if past_interaction:
                    interaction_types[past_interaction] = interaction_types.get(past_interaction, 0) + 1
            
            # Calculate engagement probability based on interaction type affinity
            base_score = 0.3
            if interaction.interaction_type.value in interaction_types:
                type_frequency = interaction_types[interaction.interaction_type.value]
                total_interactions = sum(interaction_types.values())
                type_affinity = type_frequency / total_interactions
                base_score = min(0.9, base_score + type_affinity * 0.6)
            
            # Adjust based on relationship strength
            if interaction.target_user_id:
                relationship_data = self.redis_client.hget(f"relationship:{user_id}:{interaction.target_user_id}", 'strength_score')
                if relationship_data:
                    relationship_strength = float(relationship_data)
                    base_score = min(0.95, base_score + relationship_strength * 0.1)
            
            return base_score
            
        except Exception as e:
            self.logger.error(f"Error predicting engagement: {str(e)}")
            return 0.5

    async def _generate_content_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """🧠 Lead Dev IA: Generate AI-powered content recommendations"""
        try:
            recommendations = []
            
            # Analyze user's content preferences
            user_preferences = await self._analyze_user_content_preferences(user_id)
            
            # Find trending content in user's preferred categories
            for content_type in user_preferences.get('preferred_types', []):
                trending_content = self.redis_client.zrevrange(
                    f"trending_content:{content_type}", 0, 10, withscores=True
                )
                
                for content_id, score in trending_content:
                    # Calculate recommendation score
                    recommendation_score = score * user_preferences.get('type_weights', {}).get(content_type, 1.0)
                    
                    recommendations.append({
                        'content_id': content_id,
                        'content_type': content_type,
                        'score': recommendation_score,
                        'reason': f'Trending in {content_type}'
                    })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:20]
            
        except Exception as e:
            self.logger.error(f"Error generating content recommendations: {str(e)}")
            return []

    async def _analyze_user_content_preferences(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's content preferences from interaction history"""
        try:
            # Get user's recent interactions
            user_interactions = self.redis_client.zrange(f"user_interactions:{user_id}", -100, -1)
            
            content_types = {}
            interaction_types = {}
            
            for interaction_id in user_interactions:
                interaction_data = self.redis_client.hgetall(f"interaction:{interaction_id}")
                
                # Track interaction types
                interaction_type = interaction_data.get('interaction_type')
                if interaction_type:
                    interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
                
                # Track content types if content is involved
                content_id = interaction_data.get('content_id')
                if content_id:
                    content_metadata = self.redis_client.hgetall(f"content_metadata:{content_id}")
                    content_type = content_metadata.get('type', 'unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Calculate preferences
            total_content_interactions = sum(content_types.values())
            type_weights = {}
            
            if total_content_interactions > 0:
                for content_type, count in content_types.items():
                    type_weights[content_type] = count / total_content_interactions
            
            return {
                'preferred_types': list(content_types.keys()),
                'type_weights': type_weights,
                'interaction_patterns': interaction_types,
                'total_interactions': len(user_interactions)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing user content preferences: {str(e)}")
            return {}

    async def get_social_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        ⚙️ DevOps: Get comprehensive social analytics for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Social analytics and insights
        """
        try:
            # Get basic social stats
            follower_count = self.redis_client.scard(f"user_followers:{user_id}")
            following_count = self.redis_client.scard(f"user_following:{user_id}")
            
            # Get interaction analytics
            interaction_stats = await self._calculate_interaction_stats(user_id)
            
            # Get engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(user_id)
            
            # Get relationship insights
            relationship_insights = await self._analyze_user_relationships(user_id)
            
            analytics = {
                'social_overview': {
                    'follower_count': follower_count,
                    'following_count': following_count,
                    'follower_following_ratio': follower_count / following_count if following_count > 0 else 0,
                    'total_interactions': interaction_stats.get('total_interactions', 0),
                    'engagement_rate': engagement_metrics.get('engagement_rate', 0.0)
                },
                'interaction_breakdown': interaction_stats.get('type_breakdown', {}),
                'engagement_trends': engagement_metrics.get('trends', {}),
                'relationship_analysis': relationship_insights,
                'content_performance': await self._analyze_content_performance(user_id),
                'growth_metrics': await self._calculate_growth_metrics(user_id)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting social analytics: {str(e)}")
            return {}

    async def _calculate_interaction_stats(self, user_id: str) -> Dict[str, Any]:
        """Calculate user interaction statistics"""
        try:
            stats = {}
            type_breakdown = {}
            
            # Get all user interactions
            all_interactions = self.redis_client.zrange(f"user_interactions:{user_id}", 0, -1)
            stats['total_interactions'] = len(all_interactions)
            
            # Break down by interaction type
            for interaction_type in InteractionType:
                type_interactions = self.redis_client.zcard(f"user_interactions:{user_id}:{interaction_type.value}")
                type_breakdown[interaction_type.value] = type_interactions
            
            stats['type_breakdown'] = type_breakdown
            
            # Calculate daily average
            if all_interactions:
                oldest_interaction = self.redis_client.zrange(f"user_interactions:{user_id}", 0, 0, withscores=True)
                if oldest_interaction:
                    days_active = max(1, (time.time() - oldest_interaction[0][1]) / 86400)
                    stats['daily_average'] = stats['total_interactions'] / days_active
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating interaction stats: {str(e)}")
            return {}

    async def _calculate_engagement_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        try:
            metrics = {}
            
            # Get user's content and their interactions
            user_content = self.redis_client.smembers(f"user_content:{user_id}")
            total_content_interactions = 0
            total_content_count = len(user_content)
            
            for content_id in user_content:
                content_interactions = self.redis_client.zcard(f"content_interactions:{content_id}")
                total_content_interactions += content_interactions
            
            # Calculate engagement rate
            if total_content_count > 0:
                metrics['engagement_rate'] = total_content_interactions / total_content_count
            else:
                metrics['engagement_rate'] = 0.0
            
            # Calculate engagement trends (last 7 days vs previous 7 days)
            current_week_start = time.time() - (7 * 24 * 3600)
            previous_week_start = time.time() - (14 * 24 * 3600)
            
            current_week_interactions = self.redis_client.zcount(
                f"user_interactions:{user_id}", current_week_start, '+inf'
            )
            previous_week_interactions = self.redis_client.zcount(
                f"user_interactions:{user_id}", previous_week_start, current_week_start
            )
            
            if previous_week_interactions > 0:
                trend_percentage = ((current_week_interactions - previous_week_interactions) / 
                                 previous_week_interactions) * 100
            else:
                trend_percentage = 0
            
            metrics['trends'] = {
                'weekly_change_percentage': trend_percentage,
                'current_week_interactions': current_week_interactions,
                'previous_week_interactions': previous_week_interactions
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement metrics: {str(e)}")
            return {}

    async def _analyze_user_relationships(self, user_id: str) -> Dict[str, Any]:
        """Analyze user relationships and social connections"""
        try:
            analysis = {}
            
            # Get all relationships
            relationships = self.redis_client.smembers(f"user_relationships:{user_id}")
            
            if relationships:
                total_strength = 0
                strong_relationships = 0
                relationship_types = {}
                
                for target_user_id in relationships:
                    relationship_data = self.redis_client.hgetall(f"relationship:{user_id}:{target_user_id}")
                    
                    if relationship_data:
                        strength = float(relationship_data.get('strength_score', 0))
                        total_strength += strength
                        
                        if strength > 3.0:  # Strong relationship threshold
                            strong_relationships += 1
                        
                        rel_type = relationship_data.get('relationship_type', 'unknown')
                        relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
                
                analysis = {
                    'total_relationships': len(relationships),
                    'average_relationship_strength': total_strength / len(relationships),
                    'strong_relationships': strong_relationships,
                    'strong_relationship_percentage': (strong_relationships / len(relationships)) * 100,
                    'relationship_type_distribution': relationship_types
                }
            else:
                analysis = {
                    'total_relationships': 0,
                    'average_relationship_strength': 0,
                    'strong_relationships': 0,
                    'strong_relationship_percentage': 0,
                    'relationship_type_distribution': {}
                }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user relationships: {str(e)}")
            return {}

    async def _analyze_content_performance(self, user_id: str) -> Dict[str, Any]:
        """Analyze performance of user's content"""
        try:
            performance = {}
            
            user_content = self.redis_client.smembers(f"user_content:{user_id}")
            
            if user_content:
                total_interactions = 0
                best_performing = {'content_id': '', 'interactions': 0}
                content_performance = []
                
                for content_id in user_content:
                    content_stats = self.redis_client.hgetall(f"content_stats:{content_id}")
                    
                    if content_stats:
                        content_interactions = sum(int(v) for v in content_stats.values())
                        total_interactions += content_interactions
                        
                        content_performance.append({
                            'content_id': content_id,
                            'total_interactions': content_interactions,
                            'breakdown': content_stats
                        })
                        
                        if content_interactions > best_performing['interactions']:
                            best_performing = {
                                'content_id': content_id,
                                'interactions': content_interactions
                            }
                
                performance = {
                    'total_content': len(user_content),
                    'total_interactions': total_interactions,
                    'average_interactions_per_content': total_interactions / len(user_content),
                    'best_performing_content': best_performing,
                    'content_details': sorted(content_performance, 
                                            key=lambda x: x['total_interactions'], 
                                            reverse=True)[:10]  # Top 10
                }
            else:
                performance = {
                    'total_content': 0,
                    'total_interactions': 0,
                    'average_interactions_per_content': 0,
                    'best_performing_content': {},
                    'content_details': []
                }
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Error analyzing content performance: {str(e)}")
            return {}

    async def _calculate_growth_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate social growth metrics"""
        try:
            growth = {}
            
            # Calculate follower growth
            current_followers = self.redis_client.scard(f"user_followers:{user_id}")
            
            # Get historical follower counts (simplified - would use time-series data in production)
            week_ago_key = f"follower_history:{user_id}:{int((time.time() - 7*24*3600) / 86400)}"
            week_ago_followers = int(self.redis_client.get(week_ago_key) or current_followers)
            
            month_ago_key = f"follower_history:{user_id}:{int((time.time() - 30*24*3600) / 86400)}"
            month_ago_followers = int(self.redis_client.get(month_ago_key) or current_followers)
            
            growth = {
                'current_followers': current_followers,
                'weekly_growth': current_followers - week_ago_followers,
                'weekly_growth_rate': ((current_followers - week_ago_followers) / week_ago_followers * 100) 
                                    if week_ago_followers > 0 else 0,
                'monthly_growth': current_followers - month_ago_followers,
                'monthly_growth_rate': ((current_followers - month_ago_followers) / month_ago_followers * 100) 
                                     if month_ago_followers > 0 else 0
            }
            
            return growth
            
        except Exception as e:
            self.logger.error(f"Error calculating growth metrics: {str(e)}")
            return {}

# Usage Example and Testing
async def main() -> None:
    """🎯 Example usage and testing of SocialInteractionService"""
    
    # Configuration
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'encryption_key': Fernet.generate_key(),
        'jwt_secret': 'your_jwt_secret_here'
    }
    
    # Initialize service
    social_service = SocialInteractionService(config)
    
    # Example 1: Create social interaction
    user_id = "user_12345"
    interaction_data = {
        'type': 'comment',
        'content': 'Amazing work! Love your creative style! 🎨',
        'target_user_id': 'user_67890',
        'content_id': 'content_001',
        'visibility': 'public',
        'metadata': {'platform': 'web', 'sentiment': 'positive'}
    }
    
    interaction = await social_service.create_interaction(user_id, interaction_data)
    print(f"Social interaction created: {interaction.interaction_id}")
    
    # Example 2: Create audio collaboration interaction
    audio_interaction = {
        'type': 'collaborate',
        'content': '🎵 Would love to create a music track together! Your beats are incredible!',
        'target_user_id': 'musician_001',
        'visibility': 'public',
        'metadata': {'content_type': 'audio', 'collaboration_type': 'music_production'}
    }
    
    audio_collab = await social_service.create_interaction(user_id, audio_interaction)
    print(f"Audio collaboration interaction: {audio_collab.interaction_id}")
    
    # Example 3: Get personalized user feed
    user_feed = await social_service.get_user_feed(user_id, limit=20, feed_type='timeline')
    print(f"User feed generated with {len(user_feed)} items")
    
    # Example 4: Get social analytics
    analytics = await social_service.get_social_analytics(user_id)
    print(f"Social analytics: {analytics.get('social_overview', {}).get('total_interactions', 0)} total interactions")
    
    # Example 5: Create multiple interactions to build social graph
    for i in range(5):
        like_interaction = {
            'type': 'like',
            'content': '👍',
            'target_user_id': f'user_{1000 + i}',
            'content_id': f'content_{100 + i}',
            'visibility': 'public'
        }
        await social_service.create_interaction(user_id, like_interaction)
        await asyncio.sleep(0.1)  # Small delay
    
    print("Multiple interactions created to demonstrate social graph building")

if __name__ == "__main__":
    asyncio.run(main())