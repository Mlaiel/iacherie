"""Business Logic Utilities for IA Influencer Agent Platform
Core business processing, monetization, and influencer management

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import numpy as np
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class PlatformType(Enum):
    """Platform type enumeration"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"


class RevenueSource(Enum):
    """Revenue source enumeration"""
    STREAMING = "streaming"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    COPYRIGHT_CLAIM = "copyright_claim"


@dataclass
class ContentMetrics:
    """Content performance metrics"""
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue_generated: Decimal = field(default_factory=lambda: Decimal('0.00'))


@dataclass
class InfluencerProfile:
    """Comprehensive influencer profile"""
    user_id: str
    username: str
    display_name: str
    content_types: List[ContentType]
    primary_platforms: List[PlatformType]
    follower_count: Dict[str, int] = field(default_factory=dict)
    engagement_rates: Dict[str, float] = field(default_factory=dict)
    content_metrics: Dict[str, ContentMetrics] = field(default_factory=dict)
    collaboration_score: float = 0.0
    monetization_tier: str = "basic"
    verified_status: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueData:
    """Revenue tracking data"""
    source: RevenueSource
    platform: PlatformType
    amount: Decimal
    currency: str = "EUR"
    content_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentProcessor:
    """Advanced content processing and optimization engine"""
    
    def __init__(self):
        self.supported_formats = {
            ContentType.AUDIO: ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
            ContentType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            ContentType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            ContentType.TEXT: ['.txt', '.md', '.doc', '.docx', '.pdf']
        }
        
    async def process_content_upload(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process uploaded content with optimization and analysis"""
        try:
            content_type = self._detect_content_type(content_data.get('filename', ''))
            
            processing_result = {
                'content_id': content_data.get('content_id'),
                'content_type': content_type,
                'processing_status': 'in_progress',
                'optimization_applied': [],
                'metadata_extracted': {},
                'protection_enabled': False
            }
            
            # Content-specific processing
            if content_type == ContentType.AUDIO:
                processing_result.update(await self._process_audio_content(content_data))
            elif content_type == ContentType.VIDEO:
                processing_result.update(await self._process_video_content(content_data))
            elif content_type == ContentType.IMAGE:
                processing_result.update(await self._process_image_content(content_data))
            elif content_type == ContentType.TEXT:
                processing_result.update(await self._process_text_content(content_data))
            
            # Apply universal optimizations
            processing_result.update(await self._apply_universal_optimizations(content_data))
            
            processing_result['processing_status'] = 'completed'
            return processing_result
            
        except Exception as e:
            logger.error(f"Content processing failed: {str(e)}")
            return {
                'processing_status': 'failed',
                'error': str(e)
            }
    
    def _detect_content_type(self, filename: str) -> ContentType:
        """Detect content type from filename"""
        file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        
        for content_type, extensions in self.supported_formats.items():
            if file_ext in extensions:
                return content_type
        
        return ContentType.MIXED
    
    async def _process_audio_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio content specifically"""
        return {
            'optimization_applied': ['audio_normalization', 'format_conversion'],
            'metadata_extracted': {
                'duration': content_data.get('duration', 0),
                'sample_rate': content_data.get('sample_rate', 44100),
                'bitrate': content_data.get('bitrate', 320),
                'channels': content_data.get('channels', 2)
            }
        }
    
    async def _process_video_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process video content specifically"""
        return {
            'optimization_applied': ['video_compression', 'thumbnail_generation'],
            'metadata_extracted': {
                'duration': content_data.get('duration', 0),
                'resolution': content_data.get('resolution', '1920x1080'),
                'fps': content_data.get('fps', 30),
                'codec': content_data.get('codec', 'h264')
            }
        }
    
    async def _process_image_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process image content specifically"""
        return {
            'optimization_applied': ['image_compression', 'format_optimization'],
            'metadata_extracted': {
                'dimensions': content_data.get('dimensions', '1920x1080'),
                'color_space': content_data.get('color_space', 'sRGB'),
                'file_size': content_data.get('file_size', 0)
            }
        }
    
    async def _process_text_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process text content specifically"""
        return {
            'optimization_applied': ['text_analysis', 'keyword_extraction'],
            'metadata_extracted': {
                'word_count': content_data.get('word_count', 0),
                'language': content_data.get('language', 'en'),
                'readability_score': content_data.get('readability_score', 0)
            }
        }
    
    async def _apply_universal_optimizations(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations common to all content types"""
        return {
            'seo_optimized': True,
            'protection_enabled': True,
            'tags_generated': content_data.get('auto_tags', []),
            'description_optimized': True
        }


class RevenueCalculator:
    """Advanced revenue calculation and forecasting engine"""
    
    def __init__(self):
        self.platform_rates = {
            PlatformType.SPOTIFY: Decimal('0.004'),  # Per stream
            PlatformType.YOUTUBE: Decimal('0.002'),  # Per view
            PlatformType.INSTAGRAM: Decimal('0.001'), # Per engagement
            PlatformType.TIKTOK: Decimal('0.0005'),  # Per view
        }
        self.commission_rate = Decimal('0.15')  # 15% platform commission
    
    def calculate_content_revenue(self, metrics: ContentMetrics, platform: PlatformType) -> Decimal:
        """Calculate revenue for specific content"""
        base_rate = self.platform_rates.get(platform, Decimal('0.001'))
        
        # Calculate base revenue
        if platform == PlatformType.SPOTIFY:
            base_revenue = Decimal(str(metrics.views)) * base_rate
        elif platform == PlatformType.YOUTUBE:
            base_revenue = Decimal(str(metrics.views)) * base_rate
        else:
            # Use engagement-based calculation
            total_engagements = metrics.likes + metrics.shares + metrics.comments
            base_revenue = Decimal(str(total_engagements)) * base_rate
        
        # Apply engagement multiplier
        engagement_multiplier = min(Decimal(str(metrics.engagement_rate)) * 10, Decimal('2.0'))
        adjusted_revenue = base_revenue * (Decimal('1.0') + engagement_multiplier)
        
        # Deduct platform commission
        net_revenue = adjusted_revenue * (Decimal('1.0') - self.commission_rate)
        
        return net_revenue.quantize(Decimal('0.01'))
    
    def forecast_revenue(self, historical_data: List[RevenueData], days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast revenue based on historical data"""
        if not historical_data:
            return {'forecast': Decimal('0.00'), 'confidence': 0.0}
        
        # Sort data by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x.timestamp)
        
        # Calculate daily averages
        daily_revenues = defaultdict(Decimal)
        for record in sorted_data:
            date_key = record.timestamp.date()
            daily_revenues[date_key] += record.amount
        
        if not daily_revenues:
            return {'forecast': Decimal('0.00'), 'confidence': 0.0}
        
        # Calculate trend
        revenues = list(daily_revenues.values())
        if len(revenues) < 7:  # Need at least a week of data
            avg_daily = sum(revenues) / len(revenues)
            forecast = avg_daily * days_ahead
            confidence = 0.5
        else:
            # Simple linear trend calculation
            x_values = np.arange(len(revenues))
            y_values = [float(r) for r in revenues]
            
            # Linear regression
            slope = np.polyfit(x_values, y_values, 1)[0]
            recent_avg = sum(revenues[-7:]) / 7  # Last week average
            
            # Project forward
            daily_forecast = recent_avg + Decimal(str(slope * len(revenues)))
            forecast = daily_forecast * days_ahead
            
            # Calculate confidence based on data consistency
            variance = np.var(y_values)
            confidence = max(0.1, min(0.95, 1.0 - (variance / (float(recent_avg) + 1))))
        
        return {
            'forecast': forecast.quantize(Decimal('0.01')),
            'confidence': confidence,
            'daily_average': sum(revenues[-7:]) / min(7, len(revenues)),
            'trend': 'increasing' if len(revenues) > 1 and revenues[-1] > revenues[0] else 'stable'
        }
    
    def calculate_platform_performance(self, revenue_data: List[RevenueData]) -> Dict[str, Dict[str, Any]]:
        """Calculate performance metrics by platform"""
        platform_stats = defaultdict(lambda: {
            'total_revenue': Decimal('0.00'),
            'transaction_count': 0,
            'average_per_transaction': Decimal('0.00'),
            'growth_rate': 0.0
        })
        
        # Group by platform
        platform_revenues = defaultdict(list)
        for record in revenue_data:
            platform_revenues[record.platform].append(record)
        
        # Calculate statistics for each platform
        for platform, records in platform_revenues.items():
            if not records:
                continue
                
            total_revenue = sum(r.amount for r in records)
            transaction_count = len(records)
            
            platform_stats[platform.value] = {
                'total_revenue': total_revenue,
                'transaction_count': transaction_count,
                'average_per_transaction': total_revenue / transaction_count if transaction_count > 0 else Decimal('0.00'),
                'growth_rate': self._calculate_growth_rate(records)
            }
        
        return dict(platform_stats)
    
    def _calculate_growth_rate(self, records: List[RevenueData]) -> float:
        """Calculate growth rate for revenue records"""
        if len(records) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_records = sorted(records, key=lambda x: x.timestamp)
        
        # Calculate monthly growth
        first_month = sorted_records[0].amount
        last_month = sorted_records[-1].amount
        
        if first_month == 0:
            return 100.0 if last_month > 0 else 0.0
        
        growth = ((last_month - first_month) / first_month) * 100
        return float(growth)


class InfluencerMetrics:
    """Comprehensive influencer metrics calculation and analysis"""
    
    def __init__(self):
        self.weight_factors = {
            'engagement_rate': 0.3,
            'follower_growth': 0.2,
            'content_quality': 0.25,
            'platform_diversity': 0.15,
            'monetization_success': 0.1
        }
    
    def calculate_influencer_score(self, profile: InfluencerProfile) -> float:
        """Calculate comprehensive influencer score"""
        scores = {}
        
        # Engagement rate score
        avg_engagement = np.mean(list(profile.engagement_rates.values())) if profile.engagement_rates else 0
        scores['engagement_rate'] = min(avg_engagement * 10, 1.0)
        
        # Follower growth score (simplified)
        total_followers = sum(profile.follower_count.values())
        scores['follower_growth'] = min(total_followers / 100000, 1.0)  # Normalize to 100k followers
        
        # Content quality score (based on metrics)
        avg_metrics = self._calculate_average_metrics(profile.content_metrics)
        scores['content_quality'] = min(avg_metrics / 1000, 1.0)  # Normalize
        
        # Platform diversity score
        scores['platform_diversity'] = min(len(profile.primary_platforms) / 5, 1.0)
        
        # Monetization success score
        revenue_score = self._calculate_revenue_score(profile)
        scores['monetization_success'] = revenue_score
        
        # Calculate weighted average
        total_score = sum(
            scores[metric] * weight 
            for metric, weight in self.weight_factors.items()
        )
        
        return min(total_score * 100, 100.0)  # Scale to 100
    
    def _calculate_average_metrics(self, content_metrics: Dict[str, ContentMetrics]) -> float:
        """Calculate average content performance metrics"""
        if not content_metrics:
            return 0.0
        
        total_score = 0
        for metrics in content_metrics.values():
            content_score = (
                metrics.views * 0.4 + 
                metrics.likes * 0.3 + 
                metrics.shares * 0.2 + 
                metrics.comments * 0.1
            )
            total_score += content_score
        
        return total_score / len(content_metrics)
    
    def _calculate_revenue_score(self, profile: InfluencerProfile) -> float:
        """Calculate monetization success score"""
        # This would typically integrate with revenue data
        # For now, use tier-based scoring
        tier_scores = {
            'basic': 0.2,
            'premium': 0.5,
            'enterprise': 0.8,
            'celebrity': 1.0
        }
        
        return tier_scores.get(profile.monetization_tier, 0.2)
    
    def analyze_content_performance(self, metrics: Dict[str, ContentMetrics]) -> Dict[str, Any]:
        """Analyze content performance across all content"""
        if not metrics:
            return {'status': 'no_data'}
        
        analysis = {
            'total_content': len(metrics),
            'total_views': sum(m.views for m in metrics.values()),
            'total_engagement': sum(m.likes + m.shares + m.comments for m in metrics.values()),
            'average_engagement_rate': np.mean([m.engagement_rate for m in metrics.values()]),
            'top_performing': self._find_top_performing_content(metrics),
            'improvement_suggestions': self._generate_improvement_suggestions(metrics)
        }
        
        return analysis
    
    def _find_top_performing_content(self, metrics: Dict[str, ContentMetrics]) -> List[Dict[str, Any]]:
        """Find top performing content"""
        content_scores = []
        
        for content_id, metric in metrics.items():
            score = (
                metric.views * 0.3 + 
                metric.likes * 0.25 + 
                metric.shares * 0.25 + 
                metric.engagement_rate * 1000 * 0.2
            )
            content_scores.append({
                'content_id': content_id,
                'score': score,
                'metrics': metric
            })
        
        # Sort by score and return top 5
        content_scores.sort(key=lambda x: x['score'], reverse=True)
        return content_scores[:5]
    
    def _generate_improvement_suggestions(self, metrics: Dict[str, ContentMetrics]) -> List[str]:
        """Generate improvement suggestions based on metrics"""
        suggestions = []
        
        avg_engagement = np.mean([m.engagement_rate for m in metrics.values()])
        if avg_engagement < 0.03:  # Less than 3%
            suggestions.append("Focus on increasing audience engagement through interactive content")
        
        avg_shares = np.mean([m.shares for m in metrics.values()])
        if avg_shares < 10:
            suggestions.append("Create more shareable content with strong emotional hooks")
        
        avg_ctr = np.mean([m.click_through_rate for m in metrics.values()])
        if avg_ctr < 0.02:  # Less than 2%
            suggestions.append("Improve call-to-action placement and messaging")
        
        return suggestions


class CollaborationMatcher:
    """AI-powered collaboration matching engine"""
    
    def __init__(self):
        self.matching_weights = {
            'content_type_similarity': 0.25,
            'audience_overlap': 0.2,
            'engagement_compatibility': 0.2,
            'platform_alignment': 0.15,
            'geographic_proximity': 0.1,
            'collaboration_history': 0.1
        }
    
    def find_collaboration_matches(
        self, 
        influencer: InfluencerProfile, 
        potential_partners: List[InfluencerProfile],
        min_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Find best collaboration matches for an influencer"""
        matches = []
        
        for partner in potential_partners:
            if partner.user_id == influencer.user_id:
                continue
                
            match_score = self._calculate_match_score(influencer, partner)
            
            if match_score >= min_score:
                matches.append({
                    'partner': partner,
                    'match_score': match_score,
                    'collaboration_potential': self._assess_collaboration_potential(influencer, partner),
                    'suggested_content_types': self._suggest_collaboration_content(influencer, partner)
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches
    
    def _calculate_match_score(self, influencer1: InfluencerProfile, influencer2: InfluencerProfile) -> float:
        """Calculate collaboration match score between two influencers"""
        scores = {}
        
        # Content type similarity
        common_types = set(influencer1.content_types) & set(influencer2.content_types)
        total_types = set(influencer1.content_types) | set(influencer2.content_types)
        scores['content_type_similarity'] = len(common_types) / len(total_types) if total_types else 0
        
        # Audience overlap (simplified - would use actual audience data)
        scores['audience_overlap'] = 0.7  # Placeholder
        
        # Engagement compatibility
        eng1 = np.mean(list(influencer1.engagement_rates.values())) if influencer1.engagement_rates else 0
        eng2 = np.mean(list(influencer2.engagement_rates.values())) if influencer2.engagement_rates else 0
        eng_diff = abs(eng1 - eng2)
        scores['engagement_compatibility'] = max(0, 1 - eng_diff * 10)
        
        # Platform alignment
        common_platforms = set(influencer1.primary_platforms) & set(influencer2.primary_platforms)
        scores['platform_alignment'] = len(common_platforms) / max(len(influencer1.primary_platforms), 1)
        
        # Geographic proximity (placeholder)
        scores['geographic_proximity'] = 0.8
        
        # Collaboration history (placeholder)
        scores['collaboration_history'] = 0.5
        
        # Calculate weighted score
        total_score = sum(
            scores[factor] * weight 
            for factor, weight in self.matching_weights.items()
        )
        
        return min(total_score, 1.0)
    
    def _assess_collaboration_potential(self, influencer1: InfluencerProfile, influencer2: InfluencerProfile) -> str:
        """Assess the potential success of collaboration"""
        combined_followers = (
            sum(influencer1.follower_count.values()) + 
            sum(influencer2.follower_count.values())
        )
        
        if combined_followers > 1000000:
            return "high"
        elif combined_followers > 100000:
            return "medium"
        else:
            return "low"
    
    def _suggest_collaboration_content(self, influencer1: InfluencerProfile, influencer2: InfluencerProfile) -> List[str]:
        """Suggest collaboration content types"""
        common_types = set(influencer1.content_types) & set(influencer2.content_types)
        
        suggestions = []
        if ContentType.AUDIO in common_types:
            suggestions.extend(["duet", "remix", "podcast_collaboration"])
        if ContentType.VIDEO in common_types:
            suggestions.extend(["joint_video", "challenge", "interview"])
        if ContentType.IMAGE in common_types:
            suggestions.extend(["photo_series", "joint_campaign"])
        
        return suggestions


class MonetizationEngine:
    """Advanced monetization optimization and management"""
    
    def __init__(self):
        self.revenue_sources = [
            RevenueSource.STREAMING,
            RevenueSource.LICENSING,
            RevenueSource.COLLABORATION,
            RevenueSource.SPONSORSHIP
        ]
    
    async def optimize_monetization(self, profile: InfluencerProfile) -> Dict[str, Any]:
        """Optimize monetization strategy for influencer"""
        try:
            optimization_plan = {
                'current_tier': profile.monetization_tier,
                'recommended_tier': self._recommend_tier(profile),
                'revenue_opportunities': await self._identify_revenue_opportunities(profile),
                'optimization_actions': self._generate_optimization_actions(profile),
                'projected_revenue_increase': self._calculate_revenue_projection(profile)
            }
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Monetization optimization failed: {str(e)}")
            return {'error': str(e)}
    
    def _recommend_tier(self, profile: InfluencerProfile) -> str:
        """Recommend appropriate monetization tier"""
        total_followers = sum(profile.follower_count.values())
        avg_engagement = np.mean(list(profile.engagement_rates.values())) if profile.engagement_rates else 0
        
        if total_followers > 500000 and avg_engagement > 0.05:
            return "enterprise"
        elif total_followers > 100000 and avg_engagement > 0.03:
            return "premium"
        else:
            return "basic"
    
    async def _identify_revenue_opportunities(self, profile: InfluencerProfile) -> List[Dict[str, Any]]:
        """Identify revenue opportunities"""
        opportunities = []
        
        # Streaming optimization
        if ContentType.AUDIO in profile.content_types:
            opportunities.append({
                'type': 'streaming_optimization',
                'platform': 'spotify',
                'potential_increase': '15-25%',
                'action': 'Optimize release schedule and playlist targeting'
            })
        
        # Licensing opportunities
        if profile.verified_status:
            opportunities.append({
                'type': 'content_licensing',
                'platform': 'multi',
                'potential_increase': '30-50%',
                'action': 'Enable automated licensing for commercial use'
            })
        
        # Collaboration revenue
        if profile.collaboration_score > 0.7:
            opportunities.append({
                'type': 'collaboration_revenue',
                'platform': 'multi',
                'potential_increase': '20-40%',
                'action': 'Participate in high-value collaborations'
            })
        
        return opportunities
    
    def _generate_optimization_actions(self, profile: InfluencerProfile) -> List[str]:
        """Generate actionable optimization recommendations"""
        actions = []
        
        # Platform-specific actions
        for platform in profile.primary_platforms:
            if platform == PlatformType.SPOTIFY:
                actions.append("Optimize Spotify for Artists settings and playlists")
            elif platform == PlatformType.YOUTUBE:
                actions.append("Enable YouTube monetization and optimize ad placement")
            elif platform == PlatformType.INSTAGRAM:
                actions.append("Activate Instagram Creator Fund and brand partnerships")
        
        # General actions
        actions.extend([
            "Enable content protection and copyright monitoring",
            "Set up automated licensing agreements",
            "Optimize content publishing schedule",
            "Implement cross-platform promotion strategy"
        ])
        
        return actions
    
    def _calculate_revenue_projection(self, profile: InfluencerProfile) -> Dict[str, Decimal]:
        """Calculate projected revenue increase"""
        current_estimated = self._estimate_current_revenue(profile)
        optimized_estimated = current_estimated * Decimal('1.35')  # 35% increase potential
        
        return {
            'current_monthly': current_estimated,
            'optimized_monthly': optimized_estimated,
            'increase_amount': optimized_estimated - current_estimated,
            'increase_percentage': float(((optimized_estimated - current_estimated) / current_estimated) * 100) if current_estimated > 0 else 0
        }
    
    def _estimate_current_revenue(self, profile: InfluencerProfile) -> Decimal:
        """Estimate current revenue based on profile metrics"""
        total_followers = sum(profile.follower_count.values())
        avg_engagement = np.mean(list(profile.engagement_rates.values())) if profile.engagement_rates else 0
        
        # Simplified revenue estimation
        base_revenue = Decimal(str(total_followers)) * Decimal('0.001')  # €0.001 per follower
        engagement_multiplier = Decimal(str(avg_engagement * 10))
        
        estimated_revenue = base_revenue * (Decimal('1.0') + engagement_multiplier)
        return estimated_revenue.quantize(Decimal('0.01'))


class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    pass
