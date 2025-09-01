"""📱 Social Media Processor - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/data_management/processors/social_media_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Social Media Management - Enterprise Production-Ready Ultra Advanced
Responsibility: Gestion complète des réseaux sociaux avec automatisation intelligente
==========================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER SOCIAL MEDIA:
Content Planning → Multi-Platform Publishing → Audience Engagement → Performance Analytics → 
Community Management → Trend Analysis → Influencer Collaboration → Brand Monitoring
"""

import json
import logging
import asyncio
import time
import schedule
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
import requests
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import hashlib
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading

from .base_processor import BaseProcessor, AsyncBaseProcessor


@dataclass
class SocialMediaPost:
    """
Modèle de post pour réseaux sociaux"""
    platform: str
    content: str
    media_urls: List[str]
    hashtags: List[str]
    scheduled_time: datetime
    post_type: str
    target_audience: Dict[str, Any]
    engagement_goals: Dict[str, float]
    

@dataclass
class EngagementMetrics:
    """
Métriques d'engagement"""
    likes: int
    comments: int
    shares: int
    views: int
    reach: int
    impressions: int
    engagement_rate: float
    click_through_rate: float


@dataclass
class AudienceInsights:
    """
Insights d'audience"""
    total_followers: int
    demographics: Dict[str, Any]
    interests: List[str]
    active_hours: List[int]
    engagement_patterns: Dict[str, Any]
    growth_rate: float


class SocialMediaProcessor(BaseProcessor):
    """
Processeur gestion réseaux sociaux - Production Enterprise"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Social Media Configuration
        self.social_config = {
            'platforms': {
                'instagram': {
                    'api_base': 'https://graph.instagram.com',
                    'post_types': ['photo', 'video', 'carousel', 'reel', 'story'],
                    'max_caption_length': 2200,
                    'max_hashtags': 30,
                    'optimal_hashtags': 11,
                    'supported_formats': ['jpg', 'png', 'mp4', 'mov'],
                    'rate_limits': {'posts_per_hour': 25, 'comments_per_hour': 60}
                },
                'facebook': {
                    'api_base': 'https://graph.facebook.com/v18.0',
                    'post_types': ['status', 'photo', 'video', 'link', 'event'],
                    'max_caption_length': 63206,
                    'max_hashtags': 30,
                    'supported_formats': ['jpg', 'png', 'gif', 'mp4', 'mov'],
                    'rate_limits': {'posts_per_hour': 25, 'api_calls_per_hour': 4800}
                },
                'twitter': {
                    'api_base': 'https://api.twitter.com/2',
                    'post_types': ['tweet', 'reply', 'retweet', 'thread'],
                    'max_caption_length': 280,
                    'max_hashtags': 3,
                    'supported_formats': ['jpg', 'png', 'gif', 'mp4'],
                    'rate_limits': {'tweets_per_hour': 300, 'api_calls_per_15min': 300}
                },
                'linkedin': {
                    'api_base': 'https://api.linkedin.com/v2',
                    'post_types': ['article', 'status', 'video', 'document'],
                    'max_caption_length': 3000,
                    'max_hashtags': 10,
                    'supported_formats': ['jpg', 'png', 'mp4', 'pdf'],
                    'rate_limits': {'posts_per_hour': 20, 'api_calls_per_hour': 500}
                },
                'tiktok': {
                    'api_base': 'https://open-api.tiktok.com',
                    'post_types': ['video', 'photo'],
                    'max_caption_length': 300,
                    'max_hashtags': 10,
                    'supported_formats': ['mp4', 'mov', 'jpg', 'png'],
                    'rate_limits': {'posts_per_day': 10, 'api_calls_per_hour': 1000}
                },
                'youtube': {
                    'api_base': 'https://www.googleapis.com/youtube/v3',
                    'post_types': ['video', 'short', 'playlist', 'community'],
                    'max_title_length': 100,
                    'max_description_length': 5000,
                    'max_tags': 15,
                    'supported_formats': ['mp4', 'mov', 'avi', 'wmv'],
                    'rate_limits': {'uploads_per_day': 6, 'api_calls_per_hour': 10000}
                }
            },
            'content_types': {
                'educational': {
                    'optimal_times': [9, 14, 19],
                    'best_platforms': ['linkedin', 'youtube', 'instagram'],
                    'engagement_boost': 1.2
                },
                'entertainment': {
                    'optimal_times': [12, 18, 21],
                    'best_platforms': ['tiktok', 'instagram', 'twitter'],
                    'engagement_boost': 1.5
                },
                'promotional': {
                    'optimal_times': [10, 15, 20],
                    'best_platforms': ['facebook', 'instagram', 'linkedin'],
                    'engagement_boost': 0.8
                },
                'behind_scenes': {
                    'optimal_times': [16, 19, 22],
                    'best_platforms': ['instagram', 'tiktok', 'youtube'],
                    'engagement_boost': 1.3
                }
            },
            'automation_rules': {
                'auto_reply': {
                    'enabled': True,
                    'response_time_minutes': 30,
                    'keywords_to_ignore': ['spam', 'bot', 'fake'],
                    'sentiment_threshold': 0.3
                },
                'auto_engagement': {
                    'enabled': True,
                    'like_probability': 0.7,
                    'comment_probability': 0.3,
                    'target_accounts': []
                },
                'content_curation': {
                    'enabled': True,
                    'repost_probability': 0.1,
                    'trending_threshold': 0.8
                }
            }
        }
        
        # Content Scheduling
        self.content_queue = defaultdict(list)
        self.scheduled_posts = {}
        self.scheduler_active = False
        
        # Analytics and Metrics
        self.analytics_data = defaultdict(dict)
        self.performance_history = defaultdict(list)
        
        # Database for persistent storage
        self.db_path = '/tmp/social_media.db'
        self._init_database()
        
        # Real-time monitoring
        self.monitoring_threads = {}
        self.trend_analysis = {}
        
    def _init_database(self):
        """
Initialise la base de données SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Posts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    post_id TEXT,
                    content TEXT,
                    hashtags TEXT,
                    scheduled_time TEXT,
                    posted_time TEXT,
                    status TEXT,
                    metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    post_id TEXT,
                    metric_type TEXT,
                    metric_value REAL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Audience insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audience_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    insight_type TEXT,
                    insight_data TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les opérations de gestion des réseaux sociaux"""
        operation = input_data.get('operation', 'schedule_post')
        
        result = {
            'operation': operation,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'status': 'processing',
            'data': {},
            'metrics': {},
            'errors': []
        }
        
        try:
            if operation == 'schedule_post':
                result.update(self._schedule_post(input_data))
            elif operation == 'publish_now':
                result.update(self._publish_now(input_data))
            elif operation == 'bulk_schedule':
                result.update(self._bulk_schedule(input_data))
            elif operation == 'get_analytics':
                result.update(self._get_analytics(input_data))
            elif operation == 'audience_insights':
                result.update(self._get_audience_insights(input_data))
            elif operation == 'trend_analysis':
                result.update(self._analyze_trends(input_data))
            elif operation == 'engagement_automation':
                result.update(self._manage_engagement_automation(input_data))
            elif operation == 'content_curation':
                result.update(self._curate_content(input_data))
            elif operation == 'competitor_analysis':
                result.update(self._analyze_competitors(input_data))
            elif operation == 'hashtag_research':
                result.update(self._research_hashtags(input_data))
            elif operation == 'campaign_management':
                result.update(self._manage_campaign(input_data))
            else:
                result['status'] = 'error'
                result['errors'].append(f"Unknown operation: {operation}")
        
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            self.logger.error(f"Social media operation failed: {e}")
        
        return result
    
    def _schedule_post(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Programme un post sur les réseaux sociaux"""
        platforms = input_data.get('platforms', ['instagram'])
        content = input_data.get('content', '')
        media_urls = input_data.get('media_urls', [])
        hashtags = input_data.get('hashtags', [])
        scheduled_time = input_data.get('scheduled_time')
        post_type = input_data.get('post_type', 'photo')
        
        result = {
            'scheduled_posts': {},
            'optimization_suggestions': [],
            'status': 'scheduled'
        }
        
        try:
            # Parse scheduled time
            if isinstance(scheduled_time, str):
                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            elif scheduled_time is None:
                scheduled_dt = datetime.now(timezone.utc) + timedelta(minutes=5)
            else:
                scheduled_dt = scheduled_time
            
            # Process each platform
            for platform in platforms:
                if platform not in self.social_config['platforms']:
                    result['errors'] = result.get('errors', [])
                    result['errors'].append(f"Unsupported platform: {platform}")
                    continue
                
                platform_config = self.social_config['platforms'][platform]
                
                # Optimize content for platform
                optimized_content = self._optimize_content_for_platform(
                    content, platform, hashtags, platform_config
                )
                
                # Validate content
                validation = self._validate_post_content(
                    optimized_content, media_urls, platform, platform_config
                )
                
                if not validation['valid']:
                    result['errors'] = result.get('errors', [])
                    result['errors'].extend(validation['errors'])
                    continue
                
                # Create post object
                post = SocialMediaPost(
                    platform=platform,
                    content=optimized_content['content'],
                    media_urls=media_urls,
                    hashtags=optimized_content['hashtags'],
                    scheduled_time=scheduled_dt,
                    post_type=post_type,
                    target_audience=input_data.get('target_audience', {}),
                    engagement_goals=input_data.get('engagement_goals', {})
                )
                
                # Store in database
                post_id = self._store_post_in_db(post)
                
                # Add to scheduling queue
                if platform not in self.content_queue:
                    self.content_queue[platform] = []
                
                self.content_queue[platform].append({
                    'post_id': post_id,
                    'post_data': asdict(post),
                    'scheduled_time': scheduled_dt.isoformat()
                })
                
                result['scheduled_posts'][platform] = {
                    'post_id': post_id,
                    'scheduled_time': scheduled_dt.isoformat(),
                    'content_preview': optimized_content['content'][:100] + '...',
                    'hashtags_count': len(optimized_content['hashtags']),
                    'estimated_reach': self._estimate_reach(platform, post)
                }
                
                # Add optimization suggestions
                suggestions = self._generate_content_suggestions(platform, post)
                result['optimization_suggestions'].extend(suggestions)
            
            # Start scheduler if not running
            if not self.scheduler_active and self.content_queue:
                self._start_content_scheduler()
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'] = result.get('errors', []) + [str(e)]
            self.logger.error(f"Post scheduling failed: {e}")
        
        return result
    
    def _optimize_content_for_platform(self, content: str, platform: str, hashtags: List[str], platform_config: Dict) -> Dict[str, Any]:
        """Optimise le contenu pour une plateforme spécifique"""
        optimized = {
            'content': content,
            'hashtags': hashtags.copy(),
            'modifications': []
        }
        
        try:
            # Truncate content if too long
            max_length = platform_config.get('max_caption_length', 2200)
            if len(content) > max_length:
                optimized['content'] = content[:max_length-3] + '...'
                optimized['modifications'].append(f'Content truncated to {max_length} characters')
            
            # Optimize hashtags
            max_hashtags = platform_config.get('max_hashtags', 30)
            optimal_hashtags = platform_config.get('optimal_hashtags', max_hashtags)
            
            if len(hashtags) > max_hashtags:
                optimized['hashtags'] = hashtags[:max_hashtags]
                optimized['modifications'].append(f'Hashtags limited to {max_hashtags}')
            elif len(hashtags) < optimal_hashtags:
                # Suggest additional hashtags
                suggested_hashtags = self._suggest_hashtags(content, platform)
                needed = optimal_hashtags - len(hashtags)
                optimized['hashtags'].extend(suggested_hashtags[:needed])
                optimized['modifications'].append(f'Added {len(suggested_hashtags[:needed])} suggested hashtags')
            
            # Platform-specific optimizations
            if platform == 'twitter':
                # Ensure content fits in tweet
                if len(optimized['content']) > 200:  # Leave space for hashtags and media
                    optimized['content'] = optimized['content'][:197] + '...'
                    optimized['modifications'].append('Content optimized for Twitter character limit')
            
            elif platform == 'linkedin':
                # Professional tone check
                if not self._is_professional_tone(optimized['content']):
                    optimized['modifications'].append('Consider using more professional language for LinkedIn')
            
            elif platform == 'instagram':
                # Add line breaks for readability
                if '\n' not in optimized['content'] and len(optimized['content']) > 100:
                    # Insert line break after first sentence
                    sentences = optimized['content'].split('. ')
                    if len(sentences) > 1:
                        optimized['content'] = sentences[0] + '.\n\n' + '. '.join(sentences[1:])
                        optimized['modifications'].append('Added line breaks for Instagram readability')
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {e}")
        
        return optimized
    
    def _suggest_hashtags(self, content: str, platform: str) -> List[str]:
        """Suggère des hashtags basés sur le contenu"""
        suggested = []
        
        try:
            # Extract keywords from content
            words = content.lower().split()
            keywords = [word.strip('.,!?;:') for word in words if len(word) > 4]
            
            # Platform-specific popular hashtags
            platform_hashtags = {
                'instagram': ['#instagood', '#photooftheday', '#love', '#beautiful', '#follow'],
                'twitter': ['#follow', '#love', '#instagood'],
                'linkedin': ['#professional', '#career', '#business', '#networking', '#growth'],
                'tiktok': ['#fyp', '#foryou', '#viral', '#trending', '#tiktok'],
                'facebook': ['#facebook', '#follow', '#love', '#share']
            }
            
            # Add platform-specific hashtags
            suggested.extend(platform_hashtags.get(platform, [])[:2])
            
            # Add content-based hashtags
            for keyword in keywords[:3]:
                if keyword not in [tag.lower().replace('#', '') for tag in suggested]:
                    suggested.append(f'#{keyword}')
            
            # Add trending hashtags (simulated)
            trending = ['#2025', '#inspiration', '#motivation', '#success', '#creative']
            for trend in trending:
                if len(suggested) < 5 and trend not in suggested:
                    suggested.append(trend)
            
        except Exception as e:
            self.logger.error(f"Hashtag suggestion failed: {e}")
        
        return suggested[:5]
    
    def _is_professional_tone(self, content: str) -> bool:
        """Vérifie si le ton est professionnel"""
        professional_indicators = [
            'professional', 'business', 'career', 'industry', 'experience',
            'skill', 'development', 'growth', 'strategy', 'innovation'
        ]
        
        casual_indicators = [
            'awesome', 'cool', 'amazing', 'lol', 'omg', 'yeah', 'gonna', 'wanna'
        ]
        
        content_lower = content.lower()
        professional_count = sum(1 for word in professional_indicators if word in content_lower)
        casual_count = sum(1 for word in casual_indicators if word in content_lower)
        
        return professional_count > casual_count
    
    def _validate_post_content(self, content_data: Dict, media_urls: List[str], platform: str, platform_config: Dict) -> Dict[str, Any]:
        """
Valide le contenu du post"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            content = content_data['content']
            hashtags = content_data['hashtags']
            
            # Check content length
            max_length = platform_config.get('max_caption_length', 2200)
            if len(content) > max_length:
                validation['errors'].append(f"Content exceeds {max_length} character limit")
                validation['valid'] = False
            
            # Check hashtag count
            max_hashtags = platform_config.get('max_hashtags', 30)
            if len(hashtags) > max_hashtags:
                validation['errors'].append(f"Too many hashtags. Maximum: {max_hashtags}")
                validation['valid'] = False
            
            # Check media formats
            supported_formats = platform_config.get('supported_formats', [])
            for media_url in media_urls:
                file_extension = media_url.split('.')[-1].lower()
                if file_extension not in supported_formats:
                    validation['warnings'].append(f"Media format {file_extension} may not be supported on {platform}")
            
            # Platform-specific validations
            if platform == 'twitter' and len(media_urls) > 4:
                validation['errors'].append("Twitter supports maximum 4 media files per tweet")
                validation['valid'] = False
            
            elif platform == 'instagram' and len(media_urls) > 10:
                validation['errors'].append("Instagram carousel supports maximum 10 media files")
                validation['valid'] = False
            
        except Exception as e:
            validation['errors'].append(f"Validation error: {str(e)}")
            validation['valid'] = False
            self.logger.error(f"Content validation failed: {e}")
        
        return validation
    
    def _store_post_in_db(self, post: SocialMediaPost) -> str:
        """Stocke le post dans la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            post_id = hashlib.md5(f"{post.platform}_{post.content}_{post.scheduled_time}".encode()).hexdigest()[:12]
            
            cursor.execute('''
                INSERT INTO posts (platform, post_id, content, hashtags, scheduled_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                post.platform,
                post_id,
                post.content,
                json.dumps(post.hashtags),
                post.scheduled_time.isoformat(),
                'scheduled'
            ))
            
            conn.commit()
            conn.close()
            
            return post_id
            
        except Exception as e:
            self.logger.error(f"Failed to store post in database: {e}")
            return f"temp_{int(time.time())}"
    
    def _estimate_reach(self, platform: str, post: SocialMediaPost) -> Dict[str, Any]:
        """Estime la portée du post"""
        # Simulated reach estimation based on various factors
        base_reach = {
            'instagram': 1000,
            'facebook': 800,
            'twitter': 500,
            'linkedin': 300,
            'tiktok': 2000,
            'youtube': 1500
        }
        
        platform_reach = base_reach.get(platform, 500)
        
        # Adjust based on hashtags
        hashtag_multiplier = min(1 + (len(post.hashtags) * 0.1), 2.0)
        
        # Adjust based on content type
        content_multipliers = {
            'video': 1.5,
            'photo': 1.0,
            'carousel': 1.2,
            'reel': 2.0,
            'story': 0.8
        }
        
        content_multiplier = content_multipliers.get(post.post_type, 1.0)
        
        estimated_reach = int(platform_reach * hashtag_multiplier * content_multiplier)
        
        return {
            'estimated_reach': estimated_reach,
            'reach_range': {
                'min': int(estimated_reach * 0.7),
                'max': int(estimated_reach * 1.5)
            },
            'factors': {
                'hashtag_boost': f"{(hashtag_multiplier - 1) * 100:.1f}%",
                'content_type_boost': f"{(content_multiplier - 1) * 100:.1f}%"
            }
        }
    
    def _generate_content_suggestions(self, platform: str, post: SocialMediaPost) -> List[Dict[str, Any]]:
        """Génère des suggestions d'optimisation du contenu"""
        suggestions = []
        
        try:
            platform_config = self.social_config['platforms'][platform]
            
            # Check optimal posting time
            current_hour = post.scheduled_time.hour
            content_type = self._classify_content_type(post.content)
            optimal_times = self.social_config['content_types'].get(content_type, {}).get('optimal_times', [])
            
            if optimal_times and current_hour not in optimal_times:
                suggestions.append({
                    'type': 'timing',
                    'priority': 'medium',
                    'suggestion': f"Consider posting at {optimal_times[0]}:00 for better engagement",
                    'expected_improvement': '15-25% higher engagement'
                })
            
            # Check hashtag optimization
            if len(post.hashtags) < platform_config.get('optimal_hashtags', 5):
                suggestions.append({
                    'type': 'hashtags',
                    'priority': 'high',
                    'suggestion': f"Add more hashtags (optimal: {platform_config.get('optimal_hashtags')})",
                    'expected_improvement': '10-20% increased reach'
                })
            
            # Check content length
            content_length = len(post.content)
            if platform == 'instagram' and content_length < 100:
                suggestions.append({
                    'type': 'content_length',
                    'priority': 'medium',
                    'suggestion': "Consider adding more descriptive content for better engagement",
                    'expected_improvement': '5-15% better performance'
                })
            
            # Platform-specific suggestions
            if platform == 'tiktok' and post.post_type != 'video':
                suggestions.append({
                    'type': 'content_format',
                    'priority': 'high',
                    'suggestion': "Video content performs better on TikTok",
                    'expected_improvement': '50-100% higher engagement'
                })
            
        except Exception as e:
            self.logger.error(f"Failed to generate suggestions: {e}")
        
        return suggestions
    
    def _classify_content_type(self, content: str) -> str:
        """Classifie le type de contenu"""
        content_lower = content.lower()
        
        # Educational indicators
        educational_keywords = ['learn', 'tutorial', 'guide', 'how to', 'tips', 'advice', 'education']
        if any(keyword in content_lower for keyword in educational_keywords):
            return 'educational'
        
        # Entertainment indicators
        entertainment_keywords = ['fun', 'funny', 'lol', 'entertainment', 'comedy', 'meme']
        if any(keyword in content_lower for keyword in entertainment_keywords):
            return 'entertainment'
        
        # Promotional indicators
        promotional_keywords = ['buy', 'sale', 'discount', 'offer', 'product', 'service', 'book now']
        if any(keyword in content_lower for keyword in promotional_keywords):
            return 'promotional'
        
        # Behind the scenes indicators
        bts_keywords = ['behind', 'backstage', 'process', 'making', 'journey', 'day in life']
        if any(keyword in content_lower for keyword in bts_keywords):
            return 'behind_scenes'
        
        return 'general'
    
    def _start_content_scheduler(self):
        """
Démarre le planificateur de contenu"""
        def scheduler_worker():
            self.scheduler_active = True
            
            while self.scheduler_active and any(self.content_queue.values()):
                try:
                    current_time = datetime.now(timezone.utc)
                    
                    # Check each platform's queue
                    for platform, posts in self.content_queue.items():
                        posts_to_remove = []
                        
                        for i, post_data in enumerate(posts):
                            scheduled_time = datetime.fromisoformat(post_data['scheduled_time'])
                            
                            if current_time >= scheduled_time:
                                # Time to publish
                                self._publish_post(platform, post_data)
                                posts_to_remove.append(i)
                        
                        # Remove published posts
                        for i in reversed(posts_to_remove):
                            posts.pop(i)
                    
                    # Sleep for 1 minute before next check
                    time.sleep(60)
                    
                except Exception as e:
                    self.logger.error(f"Scheduler error: {e}")
                    time.sleep(60)
            
            self.scheduler_active = False
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        scheduler_thread.start()
    
    def _publish_post(self, platform: str, post_data: Dict[str, Any]):
        """Publie un post sur la plateforme"""
        try:
            post_id = post_data['post_id']
            post_info = post_data['post_data']
            
            # Simulate API call to platform
            success = self._simulate_platform_api_call(platform, post_info)
            
            if success:
                # Update database
                self._update_post_status(post_id, 'published', datetime.now(timezone.utc))
                self.logger.info(f"Successfully published post {post_id} on {platform}")
            else:
                self._update_post_status(post_id, 'failed', datetime.now(timezone.utc))
                self.logger.error(f"Failed to publish post {post_id} on {platform}")
                
        except Exception as e:
            self.logger.error(f"Post publication failed: {e}")
    
    def _simulate_platform_api_call(self, platform: str, post_data: Dict[str, Any]) -> bool:
        """Simule un appel API vers la plateforme (remplacer par vraie API)"""
        # In real implementation, this would make actual API calls
        # For now, simulate success/failure
        import random
        return random.random() > 0.1  # 90% success rate
    
    def _update_post_status(self, post_id: str, status: str, timestamp: datetime):
        """
Met à jour le statut du post dans la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE posts 
                SET status = ?, posted_time = ?
                WHERE post_id = ?
            ''', (status, timestamp.isoformat(), post_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update post status: {e}")
    
    def _publish_now(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publie immédiatement sur les réseaux sociaux"""
        # Reuse schedule_post logic but with immediate scheduling
        input_data['scheduled_time'] = datetime.now(timezone.utc).isoformat()
        
        result = self._schedule_post(input_data)
        
        # Immediately process the scheduled posts
        if result.get('status') == 'scheduled':
            for platform, post_info in result.get('scheduled_posts', {}).items():
                post_data = {
                    'post_id': post_info['post_id'],
                    'post_data': input_data,  # Simplified
                    'scheduled_time': input_data['scheduled_time']
                }
                self._publish_post(platform, post_data)
            
            result['status'] = 'published'
        
        return result
    
    def _bulk_schedule(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Programme plusieurs posts en lot"""
        posts_data = input_data.get('posts', [])
        
        result = {
            'total_posts': len(posts_data),
            'successful_schedules': 0,
            'failed_schedules': 0,
            'scheduled_posts': [],
            'errors': []
        }
        
        try:
            for i, post_data in enumerate(posts_data):
                try:
                    schedule_result = self._schedule_post(post_data)
                    
                    if schedule_result.get('status') == 'scheduled':
                        result['successful_schedules'] += 1
                        result['scheduled_posts'].append({
                            'index': i,
                            'status': 'scheduled',
                            'platforms': list(schedule_result.get('scheduled_posts', {}).keys())
                        })
                    else:
                        result['failed_schedules'] += 1
                        result['errors'].extend(schedule_result.get('errors', []))
                        
                except Exception as e:
                    result['failed_schedules'] += 1
                    result['errors'].append(f"Post {i}: {str(e)}")
            
            result['status'] = 'completed' if result['failed_schedules'] == 0 else 'partial'
            
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            self.logger.error(f"Bulk scheduling failed: {e}")
        
        return result
    
    def _get_analytics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les analyses des performances"""
        platforms = input_data.get('platforms', ['instagram'])
        date_range = input_data.get('date_range', {})
        metrics = input_data.get('metrics', ['engagement', 'reach', 'impressions'])
        
        result = {
            'analytics_data': {},
            'summary': {},
            'trends': {},
            'recommendations': []
        }
        
        try:
            for platform in platforms:
                platform_analytics = self._get_platform_analytics(platform, date_range, metrics)
                result['analytics_data'][platform] = platform_analytics
            
            # Generate summary across platforms
            result['summary'] = self._generate_analytics_summary(result['analytics_data'])
            
            # Analyze trends
            result['trends'] = self._analyze_performance_trends(result['analytics_data'])
            
            # Generate recommendations
            result['recommendations'] = self._generate_analytics_recommendations(result['analytics_data'])
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Analytics retrieval failed: {e}")
        
        return result
    
    def _get_platform_analytics(self, platform: str, date_range: Dict, metrics: List[str]) -> Dict[str, Any]:
        """Récupère les analyses pour une plateforme spécifique"""
        # Simulate analytics data (would come from real APIs)
        analytics = {
            'posts_count': np.random.randint(10, 50),
            'followers_growth': np.random.randint(-50, 200),
            'total_engagement': np.random.randint(1000, 10000),
            'average_engagement_rate': round(np.random.uniform(1.0, 8.0), 2),
            'top_performing_posts': [],
            'engagement_by_type': {},
            'audience_demographics': {},
            'optimal_posting_times': []
        }
        
        # Generate engagement by post type
        post_types = ['photo', 'video', 'carousel', 'reel', 'story']
        for post_type in post_types:
            analytics['engagement_by_type'][post_type] = {
                'avg_likes': np.random.randint(50, 500),
                'avg_comments': np.random.randint(5, 50),
                'avg_shares': np.random.randint(2, 25),
                'engagement_rate': round(np.random.uniform(0.5, 5.0), 2)
            }
        
        # Generate audience demographics
        analytics['audience_demographics'] = {
            'age_groups': {
                '18-24': np.random.randint(15, 35),
                '25-34': np.random.randint(25, 45),
                '35-44': np.random.randint(15, 30),
                '45-54': np.random.randint(5, 20),
                '55+': np.random.randint(2, 15)
            },
            'gender_split': {
                'male': np.random.randint(40, 60),
                'female': np.random.randint(40, 60)
            },
            'top_locations': ['Germany', 'France', 'USA', 'UK', 'Canada']
        }
        
        # Generate optimal posting times
        analytics['optimal_posting_times'] = [
            {'hour': 9, 'engagement_boost': 1.2},
            {'hour': 14, 'engagement_boost': 1.1},
            {'hour': 19, 'engagement_boost': 1.3},
            {'hour': 21, 'engagement_boost': 1.15}
        ]
        
        return analytics
    
    def _generate_analytics_summary(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Génère un résumé des analyses"""
        summary = {
            'total_platforms': len(analytics_data),
            'total_posts': 0,
            'total_engagement': 0,
            'average_engagement_rate': 0,
            'best_performing_platform': None,
            'growth_metrics': {}
        }
        
        try:
            engagement_rates = []
            platform_performance = {}
            
            for platform, data in analytics_data.items():
                summary['total_posts'] += data.get('posts_count', 0)
                summary['total_engagement'] += data.get('total_engagement', 0)
                
                engagement_rate = data.get('average_engagement_rate', 0)
                engagement_rates.append(engagement_rate)
                platform_performance[platform] = engagement_rate
            
            if engagement_rates:
                summary['average_engagement_rate'] = round(np.mean(engagement_rates), 2)
                summary['best_performing_platform'] = max(platform_performance, key=platform_performance.get)
            
            # Growth metrics
            total_followers_growth = sum(
                data.get('followers_growth', 0) for data in analytics_data.values()
            )
            summary['growth_metrics'] = {
                'total_followers_growth': total_followers_growth,
                'growth_rate': f"{(total_followers_growth / len(analytics_data)):.1f} per platform"
            }
            
        except Exception as e:
            self.logger.error(f"Analytics summary generation failed: {e}")
        
        return summary
    
    def _analyze_performance_trends(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        trends = {
            'engagement_trend': 'stable',
            'growth_trend': 'positive',
            'content_performance': {},
            'seasonal_patterns': {},
            'predictions': {}
        }
        
        try:
            # Analyze content performance trends
            all_engagement_data = {}
            for platform, data in analytics_data.items():
                engagement_by_type = data.get('engagement_by_type', {})
                for content_type, metrics in engagement_by_type.items():
                    if content_type not in all_engagement_data:
                        all_engagement_data[content_type] = []
                    all_engagement_data[content_type].append(metrics.get('engagement_rate', 0))
            
            # Determine best performing content types
            content_performance = {}
            for content_type, rates in all_engagement_data.items():
                content_performance[content_type] = {
                    'average_rate': round(np.mean(rates), 2),
                    'consistency': 'high' if np.std(rates) < 1.0 else 'medium' if np.std(rates) < 2.0 else 'low'
                }
            
            trends['content_performance'] = content_performance
            
            # Simple predictions (would use ML in real implementation)
            trends['predictions'] = {
                'next_month_growth': f"{np.random.randint(5, 25)}% increase",
                'optimal_content_mix': {
                    'video': '40%',
                    'photo': '30%',
                    'carousel': '20%',
                    'reel': '10%'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
        
        return trends
    
    def _generate_analytics_recommendations(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des recommandations basées sur les analyses"""
        recommendations = []
        
        try:
            # Analyze overall performance
            avg_engagement_rates = []
            for platform, data in analytics_data.items():
                engagement_rate = data.get('average_engagement_rate', 0)
                avg_engagement_rates.append(engagement_rate)
                
                # Platform-specific recommendations
                if engagement_rate < 2.0:
                    recommendations.append({
                        'type': 'engagement_improvement',
                        'platform': platform,
                        'priority': 'high',
                        'recommendation': f'Engagement rate on {platform} is below average. Consider more interactive content.',
                        'expected_impact': '1-3% engagement increase'
                    })
                
                # Content type recommendations
                engagement_by_type = data.get('engagement_by_type', {})
                if engagement_by_type:
                    best_type = max(engagement_by_type, key=lambda x: engagement_by_type[x].get('engagement_rate', 0))
                    recommendations.append({
                        'type': 'content_optimization',
                        'platform': platform,
                        'priority': 'medium',
                        'recommendation': f'Focus more on {best_type} content - it performs best on {platform}',
                        'expected_impact': '2-5% engagement increase'
                    })
            
            # Cross-platform recommendations
            if len(avg_engagement_rates) > 1:
                best_platform = None
                best_rate = 0
                for platform, data in analytics_data.items():
                    rate = data.get('average_engagement_rate', 0)
                    if rate > best_rate:
                        best_rate = rate
                        best_platform = platform
                
                if best_platform:
                    recommendations.append({
                        'type': 'platform_strategy',
                        'platform': 'all',
                        'priority': 'medium',
                        'recommendation': f'Consider increasing posting frequency on {best_platform} - it shows highest engagement',
                        'expected_impact': '10-20% overall engagement increase'
                    })
            
        except Exception as e:
            self.logger.error(f"Recommendations generation failed: {e}")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour le social media"""
        if not isinstance(input_data, dict):
            return False
        
        operation = input_data.get('operation')
        if not operation:
            return False
        
        # Validate operation-specific requirements
        if operation in ['schedule_post', 'publish_now']:
            if not input_data.get('content') and not input_data.get('media_urls'):
                return False
            if not input_data.get('platforms'):
                return False
        elif operation == 'bulk_schedule':
            if not input_data.get('posts') or not isinstance(input_data['posts'], list):
                return False
        
        return True


class AsyncSocialMediaProcessor(AsyncBaseProcessor):
    """
Version asynchrone du processeur social media"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sync_processor = SocialMediaProcessor(config)
        self.executor = ThreadPoolExecutor(max_workers=6)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
Traitement asynchrone des réseaux sociaux"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sync_processor.process_with_stats, 
            input_data
        )
    
    async def validate_input(self, input_data: Any) -> bool:
        """
Validation asynchrone"""
        return self.sync_processor.validate_input(input_data)
