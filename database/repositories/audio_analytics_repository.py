"""Audio Analytics Repository

Enterprise-grade repository for comprehensive audio content analytics,
performance tracking, and AI-powered insights for music and audio creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""from typing import Dict, List, Optional, Union, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
import uuid
import json
import logging
import statistics

from .base_repository import BaseRepository, RepositoryException
from ..models.audio_analytics import AudioAnalytics

logger = logging.getLogger(__name__)

class AudioAnalyticsRepository(BaseRepository[AudioAnalytics]):
    """    Repository for audio analytics management with enterprise-grade
    features including streaming analytics, engagement tracking, and AI insights.
    """    
    def __init__(self, db_session: Session):
        """Initialize Audio Analytics Repository"""        super().__init__(db_session, AudioAnalytics)
        
    def record_audio_analytics(self, 
                             user_id: int,
                             audio_content_id: int,
                             platform: str,
                             streaming_data: Dict[str, Any],
                             engagement_metrics: Dict[str, Any],
                             technical_analysis: Optional[Dict[str, Any]] = None,
                             audience_data: Optional[Dict[str, Any]] = None) -> AudioAnalytics:
        """        Record comprehensive audio analytics data
        
        Args:
            user_id: User ID
            audio_content_id: Audio content ID
            platform: Platform (spotify, apple_music, youtube_music, etc.)
            streaming_data: Streaming metrics (plays, streams, skips, etc.)
            engagement_metrics: Engagement data (likes, shares, saves, etc.)
            technical_analysis: Audio technical analysis (tempo, key, energy, etc.)
            audience_data: Audience demographics and behavior
            
        Returns:
            Created audio analytics record
        """        try:
            analytics_data = {
                'user_id': user_id,
                'audio_content_id': audio_content_id,
                'platform': platform,
                'streaming_data': json.dumps(streaming_data),
                'engagement_metrics': json.dumps(engagement_metrics),
                'technical_analysis': json.dumps(technical_analysis) if technical_analysis else None,
                'audience_data': json.dumps(audience_data) if audience_data else None,
                'recorded_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            
            analytics = self.create(**analytics_data)
            
            self.logger.info(f"Recorded audio analytics for content {audio_content_id} on {platform}")
            return analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to record audio analytics: {str(e)}")
            
    def update_streaming_metrics(self, 
                               analytics_id: int,
                               updated_streaming_data: Dict[str, Any],
                               updated_engagement: Optional[Dict[str, Any]] = None) -> Optional[AudioAnalytics]:
        """        Update streaming metrics for existing analytics record
        
        Args:
            analytics_id: Analytics record ID
            updated_streaming_data: Updated streaming metrics
            updated_engagement: Updated engagement metrics
            
        Returns:
            Updated analytics record
        """        try:
            analytics = self.get_by_id(analytics_id)
            if not analytics:
                return None
                
            # Merge with existing data
            existing_streaming = json.loads(analytics.streaming_data or '{}')
            existing_streaming.update(updated_streaming_data)
            
            update_data = {
                'streaming_data': json.dumps(existing_streaming),
                'updated_at': datetime.utcnow()
            }
            
            if updated_engagement:
                existing_engagement = json.loads(analytics.engagement_metrics or '{}')
                existing_engagement.update(updated_engagement)
                update_data['engagement_metrics'] = json.dumps(existing_engagement)
                
            updated_analytics = self.update(analytics_id, **update_data)
            
            if updated_analytics:
                self.logger.info(f"Updated streaming metrics for analytics: {analytics_id}")
                
            return updated_analytics
            
        except Exception as e:
            raise RepositoryException(f"Failed to update streaming metrics: {str(e)}")
            
    def get_audio_performance_summary(self, 
                                    user_id: int,
                                    audio_content_id: Optional[int] = None,
                                    platform: Optional[str] = None,
                                    days: int = 30) -> Dict[str, Any]:
        """        Get comprehensive audio performance summary
        
        Args:
            user_id: User ID
            audio_content_id: Optional specific audio content
            platform: Optional platform filter
            days: Number of days for analysis
            
        Returns:
            Audio performance summary
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db_session.query(AudioAnalytics).filter(
                and_(
                    AudioAnalytics.user_id == user_id,
                    AudioAnalytics.recorded_at >= start_date
                )
            )
            
            if audio_content_id:
                query = query.filter(AudioAnalytics.audio_content_id == audio_content_id)
                
            if platform:
                query = query.filter(AudioAnalytics.platform == platform)
                
            analytics_records = query.all()
            
            if not analytics_records:
                return {
                    'total_streams': 0,
                    'total_engagement': 0,
                    'platform_breakdown': {},
                    'top_performing_tracks': [],
                    'analysis_period_days': days,
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Aggregate metrics
            total_streams = 0
            total_plays = 0
            total_likes = 0
            total_shares = 0
            total_saves = 0
            platform_breakdown = {}
            track_performance = {}
            
            for record in analytics_records:
                try:
                    streaming_data = json.loads(record.streaming_data or '{}')
                    engagement_data = json.loads(record.engagement_metrics or '{}')
                    
                    # Aggregate streaming data
                    streams = streaming_data.get('streams', 0)
                    plays = streaming_data.get('plays', 0)
                    total_streams += streams
                    total_plays += plays
                    
                    # Aggregate engagement data
                    total_likes += engagement_data.get('likes', 0)
                    total_shares += engagement_data.get('shares', 0)
                    total_saves += engagement_data.get('saves', 0)
                    
                    # Platform breakdown
                    platform = record.platform
                    if platform not in platform_breakdown:
                        platform_breakdown[platform] = {
                            'streams': 0,
                            'plays': 0,
                            'engagement': 0,
                            'track_count': 0
                        }
                    
                    platform_breakdown[platform]['streams'] += streams
                    platform_breakdown[platform]['plays'] += plays
                    platform_breakdown[platform]['engagement'] += (
                        engagement_data.get('likes', 0) + 
                        engagement_data.get('shares', 0) + 
                        engagement_data.get('saves', 0)
                    )
                    platform_breakdown[platform]['track_count'] += 1
                    
                    # Track performance
                    track_id = record.audio_content_id
                    if track_id not in track_performance:
                        track_performance[track_id] = {
                            'total_streams': 0,
                            'total_engagement': 0,
                            'platforms': set(),
                            'latest_record': record
                        }
                    
                    track_performance[track_id]['total_streams'] += streams
                    track_performance[track_id]['total_engagement'] += (
                        engagement_data.get('likes', 0) + 
                        engagement_data.get('shares', 0) + 
                        engagement_data.get('saves', 0)
                    )
                    track_performance[track_id]['platforms'].add(platform)
                    
                    # Keep latest record for track info
                    if (record.recorded_at > 
                        track_performance[track_id]['latest_record'].recorded_at):
                        track_performance[track_id]['latest_record'] = record
                        
                except (json.JSONDecodeError, KeyError) as e:
                    self.logger.warning(f"Error parsing analytics data: {e}")
                    continue
            
            # Top performing tracks
            top_tracks = sorted(
                track_performance.items(),
                key=lambda x: x[1]['total_streams'],
                reverse=True
            )[:10]
            
            top_performing_tracks = [
                {
                    'audio_content_id': track_id,
                    'total_streams': data['total_streams'],
                    'total_engagement': data['total_engagement'],
                    'platform_count': len(data['platforms']),
                    'platforms': list(data['platforms'])
                }
                for track_id, data in top_tracks
            ]
            
            summary = {
                'total_streams': total_streams,
                'total_plays': total_plays,
                'total_engagement': total_likes + total_shares + total_saves,
                'engagement_breakdown': {
                    'likes': total_likes,
                    'shares': total_shares,
                    'saves': total_saves
                },
                'platform_breakdown': platform_breakdown,
                'top_performing_tracks': top_performing_tracks,
                'average_streams_per_track': round(total_streams / len(track_performance), 2) if track_performance else 0,
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            raise RepositoryException(f"Failed to get audio performance summary: {str(e)}")
            
    def get_audio_trends_analysis(self, 
                                user_id: int,
                                days: int = 90) -> Dict[str, Any]:
        """        Analyze audio performance trends and patterns
        
        Args:
            user_id: User ID
            days: Number of days for trend analysis
            
        Returns:
            Audio trends analysis
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            analytics_records = self.db_session.query(AudioAnalytics).filter(
                and_(
                    AudioAnalytics.user_id == user_id,
                    AudioAnalytics.recorded_at >= start_date
                )
            ).order_by(AudioAnalytics.recorded_at).all()
            
            if not analytics_records:
                return {
                    'trend': 'no_data',
                    'daily_trends': {},
                    'platform_trends': {},
                    'engagement_trends': {},
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Daily trends
            daily_trends = {}
            platform_daily_trends = {}
            
            for record in analytics_records:
                date_key = record.recorded_at.date().isoformat()
                
                try:
                    streaming_data = json.loads(record.streaming_data or '{}')
                    engagement_data = json.loads(record.engagement_metrics or '{}')
                    
                    streams = streaming_data.get('streams', 0)
                    engagement = (engagement_data.get('likes', 0) + 
                                engagement_data.get('shares', 0) + 
                                engagement_data.get('saves', 0))
                    
                    # Daily aggregation
                    if date_key not in daily_trends:
                        daily_trends[date_key] = {
                            'streams': 0,
                            'engagement': 0,
                            'track_count': 0
                        }
                    
                    daily_trends[date_key]['streams'] += streams
                    daily_trends[date_key]['engagement'] += engagement
                    daily_trends[date_key]['track_count'] += 1
                    
                    # Platform daily trends
                    platform = record.platform
                    if platform not in platform_daily_trends:
                        platform_daily_trends[platform] = {}
                    
                    if date_key not in platform_daily_trends[platform]:
                        platform_daily_trends[platform][date_key] = {
                            'streams': 0,
                            'engagement': 0
                        }
                    
                    platform_daily_trends[platform][date_key]['streams'] += streams
                    platform_daily_trends[platform][date_key]['engagement'] += engagement
                    
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Calculate overall trend
            dates = sorted(daily_trends.keys())
            if len(dates) >= 7:
                # Compare first week vs last week
                first_week_avg = statistics.mean([
                    daily_trends[date]['streams'] 
                    for date in dates[:7]
                ])
                last_week_avg = statistics.mean([
                    daily_trends[date]['streams'] 
                    for date in dates[-7:]
                ])
                
                if last_week_avg > first_week_avg * 1.1:
                    overall_trend = 'growing'
                elif last_week_avg < first_week_avg * 0.9:
                    overall_trend = 'declining'
                else:
                    overall_trend = 'stable'
            else:
                overall_trend = 'insufficient_data'
            
            # Platform performance trends
            platform_trends = {}
            for platform, daily_data in platform_daily_trends.items():
                platform_dates = sorted(daily_data.keys())
                if len(platform_dates) >= 2:
                    platform_streams = [daily_data[date]['streams'] for date in platform_dates]
                    if len(platform_streams) > 1:
                        # Simple trend calculation
                        recent_avg = statistics.mean(platform_streams[-3:]) if len(platform_streams) >= 3 else platform_streams[-1]
                        early_avg = statistics.mean(platform_streams[:3]) if len(platform_streams) >= 3 else platform_streams[0]
                        
                        if recent_avg > early_avg * 1.1:
                            platform_trend = 'improving'
                        elif recent_avg < early_avg * 0.9:
                            platform_trend = 'declining'
                        else:
                            platform_trend = 'stable'
                    else:
                        platform_trend = 'stable'
                else:
                    platform_trend = 'insufficient_data'
                
                platform_trends[platform] = {
                    'trend': platform_trend,
                    'data_points': len(platform_dates),
                    'total_streams': sum(daily_data[date]['streams'] for date in platform_dates)
                }
            
            analysis = {
                'overall_trend': overall_trend,
                'daily_trends': daily_trends,
                'platform_trends': platform_trends,
                'best_performing_days': self._identify_best_performing_days(daily_trends),
                'trend_insights': self._generate_trend_insights(overall_trend, platform_trends),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            raise RepositoryException(f"Failed to analyze audio trends: {str(e)}")
            
    def _identify_best_performing_days(self, daily_trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify best performing days based on streams and engagement"""        if not daily_trends:
            return []
            
        # Sort days by total streams
        sorted_days = sorted(
            daily_trends.items(),
            key=lambda x: x[1]['streams'],
            reverse=True
        )[:5]
        
        return [
            {
                'date': date,
                'streams': data['streams'],
                'engagement': data['engagement'],
                'track_count': data['track_count']
            }
            for date, data in sorted_days
        ]
        
    def _generate_trend_insights(self, 
                               overall_trend: str,
                               platform_trends: Dict[str, Any]) -> List[str]:
        """Generate insights based on trend analysis"""        insights = []
        
        if overall_trend == 'growing':
            insights.append("🔥 Your audio content is gaining momentum! Keep up the great work.")
        elif overall_trend == 'declining':
            insights.append("📉 Consider refreshing your content strategy to re-engage your audience.")
        elif overall_trend == 'stable':
            insights.append("📊 Your performance is stable. Consider experimenting with new release strategies.")
        
        # Platform-specific insights
        growing_platforms = [p for p, data in platform_trends.items() if data['trend'] == 'improving']
        declining_platforms = [p for p, data in platform_trends.items() if data['trend'] == 'declining']
        
        if growing_platforms:
            insights.append(f"🚀 Strong growth on: {', '.join(growing_platforms)}")
            
        if declining_platforms:
            insights.append(f"⚠️ Focus needed on: {', '.join(declining_platforms)}")
            
        return insights
        
    def get_audio_technical_insights(self, 
                                   user_id: int,
                                   days: int = 30) -> Dict[str, Any]:
        """        Analyze technical audio characteristics and their performance correlation
        
        Args:
            user_id: User ID
            days: Number of days for analysis
            
        Returns:
            Technical audio insights
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            analytics_with_technical = self.db_session.query(AudioAnalytics).filter(
                and_(
                    AudioAnalytics.user_id == user_id,
                    AudioAnalytics.recorded_at >= start_date,
                    AudioAnalytics.technical_analysis.isnot(None)
                )
            ).all()
            
            if not analytics_with_technical:
                return {
                    'technical_analysis_available': False,
                    'message': 'No technical analysis data available',
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Analyze technical characteristics vs performance
            tempo_performance = {}
            key_performance = {}
            energy_performance = {}
            genre_performance = {}
            
            for record in analytics_with_technical:
                try:
                    technical_data = json.loads(record.technical_analysis or '{}')
                    streaming_data = json.loads(record.streaming_data or '{}')
                    
                    streams = streaming_data.get('streams', 0)
                    
                    # Tempo analysis
                    tempo = technical_data.get('tempo')
                    if tempo:
                        tempo_range = self._get_tempo_range(tempo)
                        if tempo_range not in tempo_performance:
                            tempo_performance[tempo_range] = {'total_streams': 0, 'track_count': 0}
                        tempo_performance[tempo_range]['total_streams'] += streams
                        tempo_performance[tempo_range]['track_count'] += 1
                    
                    # Key analysis
                    key = technical_data.get('key')
                    if key:
                        if key not in key_performance:
                            key_performance[key] = {'total_streams': 0, 'track_count': 0}
                        key_performance[key]['total_streams'] += streams
                        key_performance[key]['track_count'] += 1
                    
                    # Energy analysis
                    energy = technical_data.get('energy')
                    if energy is not None:
                        energy_range = self._get_energy_range(energy)
                        if energy_range not in energy_performance:
                            energy_performance[energy_range] = {'total_streams': 0, 'track_count': 0}
                        energy_performance[energy_range]['total_streams'] += streams
                        energy_performance[energy_range]['track_count'] += 1
                    
                    # Genre analysis
                    genre = technical_data.get('genre')
                    if genre:
                        if genre not in genre_performance:
                            genre_performance[genre] = {'total_streams': 0, 'track_count': 0}
                        genre_performance[genre]['total_streams'] += streams
                        genre_performance[genre]['track_count'] += 1
                        
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Calculate averages and identify best performing characteristics
            tempo_insights = self._calculate_performance_insights(tempo_performance)
            key_insights = self._calculate_performance_insights(key_performance)
            energy_insights = self._calculate_performance_insights(energy_performance)
            genre_insights = self._calculate_performance_insights(genre_performance)
            
            insights = {
                'technical_analysis_available': True,
                'tempo_insights': tempo_insights,
                'key_insights': key_insights,
                'energy_insights': energy_insights,
                'genre_insights': genre_insights,
                'recommendations': self._generate_technical_recommendations(
                    tempo_insights, key_insights, energy_insights, genre_insights
                ),
                'total_tracks_analyzed': len(analytics_with_technical),
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            raise RepositoryException(f"Failed to get audio technical insights: {str(e)}")
            
    def _get_tempo_range(self, tempo: float) -> str:
        """Categorize tempo into ranges"""        if tempo < 70:
            return 'Very Slow (< 70 BPM)'
        elif tempo < 100:
            return 'Slow (70-100 BPM)'
        elif tempo < 120:
            return 'Moderate (100-120 BPM)'
        elif tempo < 140:
            return 'Fast (120-140 BPM)'
        else:
            return 'Very Fast (> 140 BPM)'
            
    def _get_energy_range(self, energy: float) -> str:
        """Categorize energy level"""        if energy < 0.3:
            return 'Low Energy'
        elif energy < 0.7:
            return 'Medium Energy'
        else:
            return 'High Energy'
            
    def _calculate_performance_insights(self, performance_data: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Calculate performance insights for technical characteristics"""        if not performance_data:
            return {'best_performing': None, 'data': {}}
            
        # Calculate average streams per track for each characteristic
        insights_data = {}
        best_performer = None
        best_avg = 0
        
        for characteristic, data in performance_data.items():
            avg_streams = data['total_streams'] / data['track_count'] if data['track_count'] > 0 else 0
            insights_data[characteristic] = {
                'total_streams': data['total_streams'],
                'track_count': data['track_count'],
                'average_streams_per_track': round(avg_streams, 2)
            }
            
            if avg_streams > best_avg:
                best_avg = avg_streams
                best_performer = characteristic
        
        return {
            'best_performing': best_performer,
            'data': insights_data
        }
        
    def _generate_technical_recommendations(self, 
                                          tempo_insights: Dict[str, Any],
                                          key_insights: Dict[str, Any],
                                          energy_insights: Dict[str, Any],
                                          genre_insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on technical analysis"""        recommendations = []
        
        if tempo_insights.get('best_performing'):
            recommendations.append(
                f"🎵 Your best-performing tempo range is {tempo_insights['best_performing']}. "
                f"Consider creating more tracks in this range."
            )
        
        if key_insights.get('best_performing'):
            recommendations.append(
                f"🎼 Tracks in {key_insights['best_performing']} perform best for your audience."
            )
        
        if energy_insights.get('best_performing'):
            recommendations.append(
                f"⚡ {energy_insights['best_performing']} tracks resonate most with your listeners."
            )
        
        if genre_insights.get('best_performing'):
            recommendations.append(
                f"🎭 Your {genre_insights['best_performing']} content performs exceptionally well."
            )
        
        if not recommendations:
            recommendations.append("Continue experimenting with different technical approaches to find your optimal sound.")
        
        return recommendations
        
    def get_audience_listening_patterns(self, 
                                      user_id: int,
                                      days: int = 30) -> Dict[str, Any]:
        """        Analyze audience listening patterns and behavior
        
        Args:
            user_id: User ID
            days: Number of days for analysis
            
        Returns:
            Audience listening patterns analysis
        """        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            analytics_with_audience = self.db_session.query(AudioAnalytics).filter(
                and_(
                    AudioAnalytics.user_id == user_id,
                    AudioAnalytics.recorded_at >= start_date,
                    AudioAnalytics.audience_data.isnot(None)
                )
            ).all()
            
            if not analytics_with_audience:
                return {
                    'audience_data_available': False,
                    'message': 'No audience data available',
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            # Aggregate audience patterns
            listening_times = {}
            device_types = {}
            geographic_distribution = {}
            age_demographics = {}
            skip_patterns = {}
            
            for record in analytics_with_audience:
                try:
                    audience_data = json.loads(record.audience_data or '{}')
                    
                    # Listening times
                    if 'listening_times' in audience_data:
                        for hour, count in audience_data['listening_times'].items():
                            listening_times[hour] = listening_times.get(hour, 0) + count
                    
                    # Device types
                    if 'device_types' in audience_data:
                        for device, count in audience_data['device_types'].items():
                            device_types[device] = device_types.get(device, 0) + count
                    
                    # Geographic distribution
                    if 'locations' in audience_data:
                        for location, count in audience_data['locations'].items():
                            geographic_distribution[location] = geographic_distribution.get(location, 0) + count
                    
                    # Age demographics
                    if 'age_groups' in audience_data:
                        for age_group, count in audience_data['age_groups'].items():
                            age_demographics[age_group] = age_demographics.get(age_group, 0) + count
                    
                    # Skip patterns
                    if 'skip_rate' in audience_data:
                        track_id = record.audio_content_id
                        if track_id not in skip_patterns:
                            skip_patterns[track_id] = []
                        skip_patterns[track_id].append(audience_data['skip_rate'])
                        
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Identify peak listening hours
            peak_hours = sorted(listening_times.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Calculate average skip rates
            avg_skip_rates = {}
            for track_id, skip_rates in skip_patterns.items():
                avg_skip_rates[track_id] = statistics.mean(skip_rates) if skip_rates else 0
            
            # Find tracks with lowest skip rates (highest completion)
            best_completion_tracks = sorted(
                avg_skip_rates.items(),
                key=lambda x: x[1]
            )[:5]
            
            patterns = {
                'audience_data_available': True,
                'peak_listening_hours': [
                    {'hour': hour, 'listener_count': count}
                    for hour, count in peak_hours
                ],
                'device_preferences': device_types,
                'geographic_distribution': geographic_distribution,
                'age_demographics': age_demographics,
                'listening_insights': self._generate_listening_insights(
                    listening_times, device_types, geographic_distribution
                ),
                'completion_rates': {
                    'best_completing_tracks': [
                        {'track_id': track_id, 'skip_rate': round(skip_rate, 2)}
                        for track_id, skip_rate in best_completion_tracks
                    ],
                    'average_skip_rate': round(statistics.mean(avg_skip_rates.values()), 2) if avg_skip_rates else 0
                },
                'analysis_period_days': days,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return patterns
            
        except Exception as e:
            raise RepositoryException(f"Failed to analyze audience listening patterns: {str(e)}")
            
    def _generate_listening_insights(self, 
                                   listening_times: Dict[str, int],
                                   device_types: Dict[str, int],
                                   geographic_distribution: Dict[str, int]) -> List[str]:
        """Generate insights from listening patterns"""        insights = []
        
        # Peak listening time insights
        if listening_times:
            peak_hour = max(listening_times.items(), key=lambda x: x[1])[0]
            insights.append(f"🕐 Peak listening time is {peak_hour}:00. Schedule releases and promotions accordingly.")
        
        # Device preference insights
        if device_types:
            primary_device = max(device_types.items(), key=lambda x: x[1])[0]
            if primary_device == 'mobile':
                insights.append("📱 Most listeners use mobile devices. Optimize for mobile experience.")
            elif primary_device == 'desktop':
                insights.append("💻 Desktop listening is prominent. Consider longer-form content.")
        
        # Geographic insights
        if geographic_distribution:
            top_location = max(geographic_distribution.items(), key=lambda x: x[1])[0]
            insights.append(f"🌍 Strong audience in {top_location}. Consider local promotion strategies.")
        
        return insights

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
