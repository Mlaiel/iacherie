"""Streaming Analytics Engine
Real-time streaming performance monitoring and quality of service analytics.

This module provides comprehensive streaming analytics including bandwidth monitoring,
quality of service metrics, viewer analytics, and streaming optimization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class StreamQuality(Enum):
    """Stream quality levels"""
    ULTRA_LOW = "144p"
    LOW = "240p"
    MEDIUM = "480p"
    HIGH = "720p"
    FULL_HD = "1080p"
    QUAD_HD = "1440p"
    ULTRA_HD = "2160p"

class BufferingEvent(Enum):
    """Types of buffering events"""
    INITIAL_BUFFERING = "initial"
    RE_BUFFERING = "rebuffering"
    BUFFER_UNDERRUN = "underrun"
    BUFFER_OVERFLOW = "overflow"

@dataclass
class StreamingSession:
    """Individual streaming session data"""
    session_id: str
    user_id: str
    content_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Connection details
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    
    # Stream configuration
    requested_quality: Optional[StreamQuality] = None
    actual_quality: Optional[StreamQuality] = None
    bitrate: Optional[int] = None  # kbps
    resolution: Optional[Tuple[int, int]] = None
    framerate: Optional[float] = None
    
    # Performance metrics
    total_watch_time: float = 0.0
    buffer_events: List[Dict[str, Any]] = field(default_factory=list)
    quality_switches: List[Dict[str, Any]] = field(default_factory=list)
    bandwidth_samples: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Quality of experience
    startup_delay: Optional[float] = None
    total_buffer_time: float = 0.0
    buffer_ratio: float = 0.0
    average_bitrate: Optional[float] = None
    dropped_frames: int = 0
    
    # Session outcome
    completion_rate: float = 0.0
    exit_reason: Optional[str] = None
    error_events: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class StreamingMetrics:
    """Aggregated streaming analytics"""
    analysis_period: Tuple[datetime, datetime]
    content_id: Optional[str] = None
    
    # Volume metrics
    total_sessions: int = 0
    unique_viewers: int = 0
    total_watch_time: float = 0.0  # minutes
    average_session_duration: float = 0.0
    
    # Quality metrics
    average_startup_delay: float = 0.0
    buffer_ratio: float = 0.0
    quality_distribution: Dict[str, float] = field(default_factory=dict)
    average_bitrate: float = 0.0
    
    # Performance metrics
    completion_rate: float = 0.0
    error_rate: float = 0.0
    rebuffering_frequency: float = 0.0  # events per hour
    quality_switch_frequency: float = 0.0
    
    # Bandwidth analytics
    bandwidth_stats: Dict[str, float] = field(default_factory=dict)
    peak_concurrent_viewers: int = 0
    
    # Geographic distribution
    viewer_locations: Dict[str, int] = field(default_factory=dict)
    device_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Real-time insights
    current_viewers: int = 0
    trending_score: float = 0.0
    engagement_score: float = 0.0

@dataclass
class QoSMetrics:
    """Quality of Service metrics"""
    timestamp: datetime
    
    # Video quality metrics
    video_bitrate: Optional[float] = None
    video_framerate: Optional[float] = None
    video_resolution: Optional[Tuple[int, int]] = None
    dropped_frames: int = 0
    
    # Audio quality metrics
    audio_bitrate: Optional[float] = None
    audio_sample_rate: Optional[int] = None
    audio_channels: int = 0
    
    # Network metrics
    bandwidth: Optional[float] = None  # Mbps
    latency: Optional[float] = None    # ms
    packet_loss: float = 0.0          # percentage
    jitter: Optional[float] = None     # ms
    
    # Buffer metrics
    buffer_level: Optional[float] = None  # seconds
    buffer_health: float = 0.0           # 0-1 score
    
    # Calculated scores
    video_quality_score: float = 0.0
    audio_quality_score: float = 0.0
    network_quality_score: float = 0.0
    overall_qos_score: float = 0.0


class StreamingMonitor:
    """Real-time streaming monitoring system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Active sessions tracking
        self.active_sessions: Dict[str, StreamingSession] = {}
        self.completed_sessions: deque = deque(maxlen=self.config.get('max_sessions', 10000))
        
        # Real-time metrics
        self.qos_history: deque = deque(maxlen=1000)
        self.bandwidth_history: deque = deque(maxlen=5000)
        
        # Performance tracking
        self.quality_thresholds = self.config.get('quality_thresholds', {
            'startup_delay_ms': 2000,
            'buffer_ratio_threshold': 0.05,
            'completion_rate_threshold': 0.8,
            'bitrate_adaptation_threshold': 0.2
        })
        
    async def start_streaming_session(self, session_data: Dict[str, Any]) -> str:
        """Start tracking a new streaming session"""
        try:
            session = StreamingSession(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                content_id=session_data['content_id'],
                start_time=datetime.now(),
                ip_address=session_data.get('ip_address'),
                user_agent=session_data.get('user_agent'),
                device_type=session_data.get('device_type'),
                location=session_data.get('location'),
                requested_quality=session_data.get('requested_quality'),
                bitrate=session_data.get('bitrate'),
                resolution=session_data.get('resolution'),
                framerate=session_data.get('framerate')
            )
            
            self.active_sessions[session.session_id] = session
            
            self.logger.info(f"Started streaming session {session.session_id}")
            return session.session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming session: {e}")
            raise
    
    async def update_session_metrics(self, session_id: str, metrics: Dict[str, Any]):
        """Update real-time session metrics"""
        try:
            if session_id not in self.active_sessions:
                self.logger.warning(f"Session {session_id} not found")
                return
            
            session = self.active_sessions[session_id]
            timestamp = datetime.now()
            
            # Update bandwidth if provided
            if 'bandwidth' in metrics:
                session.bandwidth_samples.append((timestamp, metrics['bandwidth']))
            
            # Handle buffer events
            if 'buffer_event' in metrics:
                buffer_event = {
                    'timestamp': timestamp,
                    'event_type': metrics['buffer_event'],
                    'buffer_level': metrics.get('buffer_level', 0),
                    'duration': metrics.get('duration', 0)
                }
                session.buffer_events.append(buffer_event)
                
                # Update total buffer time
                if metrics.get('duration'):
                    session.total_buffer_time += metrics['duration']
            
            # Handle quality switches
            if 'quality_switch' in metrics:
                quality_event = {
                    'timestamp': timestamp,
                    'from_quality': metrics.get('from_quality'),
                    'to_quality': metrics['quality_switch'],
                    'reason': metrics.get('switch_reason', 'unknown')
                }
                session.quality_switches.append(quality_event)
                session.actual_quality = metrics['quality_switch']
            
            # Handle errors
            if 'error' in metrics:
                error_event = {
                    'timestamp': timestamp,
                    'error_type': metrics['error'],
                    'error_message': metrics.get('error_message', ''),
                    'severity': metrics.get('severity', 'medium')
                }
                session.error_events.append(error_event)
            
            # Update dropped frames
            if 'dropped_frames' in metrics:
                session.dropped_frames += metrics['dropped_frames']
            
            # Update watch time
            if 'watch_time_increment' in metrics:
                session.total_watch_time += metrics['watch_time_increment']
            
        except Exception as e:
            self.logger.error(f"Failed to update session metrics: {e}")
    
    async def end_streaming_session(self, session_id: str, end_data: Optional[Dict[str, Any]] = None):
        """End a streaming session"""
        try:
            if session_id not in self.active_sessions:
                self.logger.warning(f"Session {session_id} not found")
                return
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            
            if end_data:
                session.exit_reason = end_data.get('exit_reason')
                if 'completion_rate' in end_data:
                    session.completion_rate = end_data['completion_rate']
                if 'total_watch_time' in end_data:
                    session.total_watch_time = end_data['total_watch_time']
            
            # Calculate final metrics
            await self._calculate_session_metrics(session)
            
            # Move to completed sessions
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            
            self.logger.info(f"Ended streaming session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to end streaming session: {e}")
    
    async def _calculate_session_metrics(self, session: StreamingSession):
        """Calculate final session metrics"""
        try:
            session_duration = 0
            if session.end_time and session.start_time:
                session_duration = (session.end_time - session.start_time).total_seconds()
            
            # Calculate buffer ratio
            if session_duration > 0:
                session.buffer_ratio = session.total_buffer_time / session_duration
            
            # Calculate average bitrate
            if session.bandwidth_samples:
                bandwidths = [bw for _, bw in session.bandwidth_samples]
                session.average_bitrate = np.mean(bandwidths)
            
            # Set startup delay if available
            if session.buffer_events:
                initial_buffer = next(
                    (event for event in session.buffer_events 
                     if event.get('event_type') == BufferingEvent.INITIAL_BUFFERING.value), 
                    None
                )
                if initial_buffer:
                    session.startup_delay = initial_buffer.get('duration', 0)
            
        except Exception as e:
            self.logger.error(f"Session metrics calculation failed: {e}")
    
    async def record_qos_metrics(self, session_id: str, qos_data: Dict[str, Any]):
        """Record Quality of Service metrics"""
        try:
            qos_metrics = QoSMetrics(
                timestamp=datetime.now(),
                video_bitrate=qos_data.get('video_bitrate'),
                video_framerate=qos_data.get('video_framerate'),
                video_resolution=qos_data.get('video_resolution'),
                dropped_frames=qos_data.get('dropped_frames', 0),
                audio_bitrate=qos_data.get('audio_bitrate'),
                audio_sample_rate=qos_data.get('audio_sample_rate'),
                audio_channels=qos_data.get('audio_channels', 0),
                bandwidth=qos_data.get('bandwidth'),
                latency=qos_data.get('latency'),
                packet_loss=qos_data.get('packet_loss', 0.0),
                jitter=qos_data.get('jitter'),
                buffer_level=qos_data.get('buffer_level'),
                buffer_health=qos_data.get('buffer_health', 0.0)
            )
            
            # Calculate quality scores
            await self._calculate_qos_scores(qos_metrics)
            
            # Store metrics
            self.qos_history.append(qos_metrics)
            
        except Exception as e:
            self.logger.error(f"QoS metrics recording failed: {e}")
    
    async def _calculate_qos_scores(self, qos_metrics: QoSMetrics):
        """Calculate QoS quality scores"""
        try:
            # Video quality score
            video_factors = []
            
            if qos_metrics.video_bitrate:
                # Normalize bitrate (assuming 1-10 Mbps range)
                bitrate_score = min(qos_metrics.video_bitrate / 10.0, 1.0)
                video_factors.append(bitrate_score)
            
            if qos_metrics.video_framerate:
                # Normalize framerate (24-60 fps range)
                fps_score = min((qos_metrics.video_framerate - 24) / 36.0, 1.0)
                video_factors.append(max(0.0, fps_score))
            
            if qos_metrics.dropped_frames is not None:
                # Penalize dropped frames
                dropped_score = max(0.0, 1.0 - qos_metrics.dropped_frames / 100.0)
                video_factors.append(dropped_score)
            
            qos_metrics.video_quality_score = np.mean(video_factors) if video_factors else 0.0
            
            # Audio quality score
            audio_factors = []
            
            if qos_metrics.audio_bitrate:
                # Normalize audio bitrate (64-320 kbps range)
                audio_bitrate_score = min((qos_metrics.audio_bitrate - 64) / 256.0, 1.0)
                audio_factors.append(max(0.0, audio_bitrate_score))
            
            if qos_metrics.audio_sample_rate:
                # Normalize sample rate (22kHz-48kHz range)
                sample_rate_score = min((qos_metrics.audio_sample_rate - 22050) / 25950.0, 1.0)
                audio_factors.append(max(0.0, sample_rate_score))
            
            qos_metrics.audio_quality_score = np.mean(audio_factors) if audio_factors else 0.0
            
            # Network quality score
            network_factors = []
            
            if qos_metrics.bandwidth:
                # Normalize bandwidth (1-100 Mbps range)
                bandwidth_score = min(qos_metrics.bandwidth / 100.0, 1.0)
                network_factors.append(bandwidth_score)
            
            if qos_metrics.latency:
                # Lower latency is better (0-500ms range)
                latency_score = max(0.0, 1.0 - qos_metrics.latency / 500.0)
                network_factors.append(latency_score)
            
            if qos_metrics.packet_loss is not None:
                # Lower packet loss is better
                packet_loss_score = max(0.0, 1.0 - qos_metrics.packet_loss / 10.0)
                network_factors.append(packet_loss_score)
            
            qos_metrics.network_quality_score = np.mean(network_factors) if network_factors else 0.0
            
            # Overall QoS score
            all_scores = [
                qos_metrics.video_quality_score,
                qos_metrics.audio_quality_score,
                qos_metrics.network_quality_score,
                qos_metrics.buffer_health
            ]
            
            qos_metrics.overall_qos_score = np.mean([s for s in all_scores if s > 0])
            
        except Exception as e:
            self.logger.error(f"QoS scores calculation failed: {e}")
    
    async def get_streaming_analytics(self, period_hours: int = 24,
                                    content_id: Optional[str] = None) -> StreamingMetrics:
        """Get comprehensive streaming analytics"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)
            
            # Filter sessions
            sessions = [
                session for session in self.completed_sessions
                if start_time <= session.start_time <= end_time
            ]
            
            if content_id:
                sessions = [s for s in sessions if s.content_id == content_id]
            
            # Initialize metrics
            metrics = StreamingMetrics(
                analysis_period=(start_time, end_time),
                content_id=content_id
            )
            
            if not sessions:
                return metrics
            
            # Calculate metrics
            await self._calculate_volume_metrics(sessions, metrics)
            await self._calculate_quality_metrics(sessions, metrics)
            await self._calculate_performance_metrics(sessions, metrics)
            await self._calculate_bandwidth_analytics(sessions, metrics)
            await self._calculate_distribution_metrics(sessions, metrics)
            await self._calculate_real_time_insights(sessions, metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Streaming analytics calculation failed: {e}")
            return StreamingMetrics(analysis_period=(start_time, end_time))
    
    async def _calculate_volume_metrics(self, sessions: List[StreamingSession],
                                      metrics: StreamingMetrics):
        """Calculate volume-based metrics"""
        try:
            metrics.total_sessions = len(sessions)
            
            unique_users = set(session.user_id for session in sessions)
            metrics.unique_viewers = len(unique_users)
            
            total_watch_time = sum(session.total_watch_time for session in sessions)
            metrics.total_watch_time = total_watch_time / 60.0  # Convert to minutes
            
            if metrics.total_sessions > 0:
                metrics.average_session_duration = metrics.total_watch_time / metrics.total_sessions
            
        except Exception as e:
            self.logger.error(f"Volume metrics calculation failed: {e}")
    
    async def _calculate_quality_metrics(self, sessions: List[StreamingSession],
                                       metrics: StreamingMetrics):
        """Calculate quality-related metrics"""
        try:
            startup_delays = [s.startup_delay for s in sessions if s.startup_delay is not None]
            if startup_delays:
                metrics.average_startup_delay = np.mean(startup_delays)
            
            buffer_ratios = [s.buffer_ratio for s in sessions if s.buffer_ratio is not None]
            if buffer_ratios:
                metrics.buffer_ratio = np.mean(buffer_ratios)
            
            # Quality distribution
            quality_counts = defaultdict(int)
            for session in sessions:
                if session.actual_quality:
                    quality_counts[session.actual_quality.value] += 1
            
            total_sessions = len(sessions)
            if total_sessions > 0:
                metrics.quality_distribution = {
                    quality: count / total_sessions
                    for quality, count in quality_counts.items()
                }
            
            # Average bitrate
            bitrates = [s.average_bitrate for s in sessions if s.average_bitrate is not None]
            if bitrates:
                metrics.average_bitrate = np.mean(bitrates)
            
        except Exception as e:
            self.logger.error(f"Quality metrics calculation failed: {e}")
    
    async def _calculate_performance_metrics(self, sessions: List[StreamingSession],
                                           metrics: StreamingMetrics):
        """Calculate performance metrics"""
        try:
            # Completion rate
            completion_rates = [s.completion_rate for s in sessions if s.completion_rate is not None]
            if completion_rates:
                metrics.completion_rate = np.mean(completion_rates)
            
            # Error rate
            sessions_with_errors = sum(1 for s in sessions if s.error_events)
            if len(sessions) > 0:
                metrics.error_rate = sessions_with_errors / len(sessions)
            
            # Rebuffering frequency (events per hour)
            total_rebuffer_events = 0
            total_watch_hours = 0
            
            for session in sessions:
                rebuffer_events = [
                    event for event in session.buffer_events
                    if event.get('event_type') == BufferingEvent.RE_BUFFERING.value
                ]
                total_rebuffer_events += len(rebuffer_events)
                total_watch_hours += session.total_watch_time / 3600.0
            
            if total_watch_hours > 0:
                metrics.rebuffering_frequency = total_rebuffer_events / total_watch_hours
            
            # Quality switch frequency
            total_quality_switches = sum(len(s.quality_switches) for s in sessions)
            if total_watch_hours > 0:
                metrics.quality_switch_frequency = total_quality_switches / total_watch_hours
            
        except Exception as e:
            self.logger.error(f"Performance metrics calculation failed: {e}")
    
    async def _calculate_bandwidth_analytics(self, sessions: List[StreamingSession],
                                           metrics: StreamingMetrics):
        """Calculate bandwidth analytics"""
        try:
            all_bandwidths = []
            
            for session in sessions:
                bandwidths = [bw for _, bw in session.bandwidth_samples]
                all_bandwidths.extend(bandwidths)
            
            if all_bandwidths:
                metrics.bandwidth_stats = {
                    'average': np.mean(all_bandwidths),
                    'median': np.median(all_bandwidths),
                    'min': np.min(all_bandwidths),
                    'max': np.max(all_bandwidths),
                    'std': np.std(all_bandwidths),
                    'p95': np.percentile(all_bandwidths, 95),
                    'p99': np.percentile(all_bandwidths, 99)
                }
            
            # Peak concurrent viewers (simplified calculation)
            # In a real implementation, this would track concurrent sessions over time
            peak_concurrent = min(len(sessions), metrics.total_sessions)
            metrics.peak_concurrent_viewers = peak_concurrent
            
        except Exception as e:
            self.logger.error(f"Bandwidth analytics calculation failed: {e}")
    
    async def _calculate_distribution_metrics(self, sessions: List[StreamingSession],
                                            metrics: StreamingMetrics):
        """Calculate geographic and device distribution"""
        try:
            # Geographic distribution
            location_counts = defaultdict(int)
            for session in sessions:
                if session.location:
                    location_counts[session.location] += 1
            
            metrics.viewer_locations = dict(location_counts)
            
            # Device distribution
            device_counts = defaultdict(int)
            for session in sessions:
                if session.device_type:
                    device_counts[session.device_type] += 1
            
            metrics.device_distribution = dict(device_counts)
            
        except Exception as e:
            self.logger.error(f"Distribution metrics calculation failed: {e}")
    
    async def _calculate_real_time_insights(self, sessions: List[StreamingSession],
                                          metrics: StreamingMetrics):
        """Calculate real-time insights and scores"""
        try:
            # Current viewers (active sessions)
            metrics.current_viewers = len(self.active_sessions)
            
            # Trending score based on recent session growth
            recent_sessions = [
                s for s in sessions
                if s.start_time >= datetime.now() - timedelta(hours=1)
            ]
            
            if len(sessions) > 0:
                recent_ratio = len(recent_sessions) / len(sessions)
                metrics.trending_score = min(recent_ratio * 2.0, 1.0)  # Scale recent activity
            
            # Engagement score based on completion rates and watch time
            if metrics.completion_rate and metrics.average_session_duration:
                engagement_factors = [
                    metrics.completion_rate,
                    min(metrics.average_session_duration / 30.0, 1.0),  # Normalize to 30 minutes
                    max(0.0, 1.0 - metrics.buffer_ratio),  # Lower buffer ratio is better
                    max(0.0, 1.0 - metrics.error_rate)  # Lower error rate is better
                ]
                
                metrics.engagement_score = np.mean(engagement_factors)
            
        except Exception as e:
            self.logger.error(f"Real-time insights calculation failed: {e}")


class BandwidthAnalyzer:
    """Bandwidth analysis and optimization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def analyze_bandwidth_patterns(self, sessions: List[StreamingSession]) -> Dict[str, Any]:
        """Analyze bandwidth usage patterns"""
        try:
            analysis = {
                'peak_usage_hours': [],
                'bandwidth_by_quality': {},
                'bandwidth_efficiency': 0.0,
                'congestion_periods': [],
                'optimization_recommendations': []
            }
            
            # Collect all bandwidth data with timestamps
            hourly_usage = defaultdict(list)
            quality_bandwidth = defaultdict(list)
            
            for session in sessions:
                for timestamp, bandwidth in session.bandwidth_samples:
                    hour = timestamp.hour
                    hourly_usage[hour].append(bandwidth)
                    
                    if session.actual_quality:
                        quality_bandwidth[session.actual_quality.value].append(bandwidth)
            
            # Find peak usage hours
            hourly_averages = {
                hour: np.mean(bandwidths) 
                for hour, bandwidths in hourly_usage.items()
            }
            
            sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
            analysis['peak_usage_hours'] = [hour for hour, avg in sorted_hours[:3]]
            
            # Bandwidth by quality
            analysis['bandwidth_by_quality'] = {
                quality: {
                    'average': np.mean(bandwidths),
                    'median': np.median(bandwidths),
                    'efficiency': self._calculate_bandwidth_efficiency(quality, bandwidths)
                }
                for quality, bandwidths in quality_bandwidth.items()
                if bandwidths
            }
            
            # Overall bandwidth efficiency
            all_bandwidths = []
            for bandwidths in quality_bandwidth.values():
                all_bandwidths.extend(bandwidths)
            
            if all_bandwidths:
                theoretical_optimal = self._calculate_theoretical_optimal_bandwidth(quality_bandwidth)
                actual_average = np.mean(all_bandwidths)
                analysis['bandwidth_efficiency'] = theoretical_optimal / actual_average if actual_average > 0 else 0
            
            # Identify congestion periods
            congestion_threshold = np.percentile(all_bandwidths, 90) if all_bandwidths else 0
            
            for hour, bandwidths in hourly_usage.items():
                if bandwidths:
                    avg_bandwidth = np.mean(bandwidths)
                    if avg_bandwidth > congestion_threshold:
                        analysis['congestion_periods'].append({
                            'hour': hour,
                            'average_bandwidth': avg_bandwidth,
                            'peak_bandwidth': np.max(bandwidths)
                        })
            
            # Generate recommendations
            analysis['optimization_recommendations'] = self._generate_bandwidth_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Bandwidth pattern analysis failed: {e}")
            return {}
    
    def _calculate_bandwidth_efficiency(self, quality: str, bandwidths: List[float]) -> float:
        """Calculate bandwidth efficiency for a quality level"""
        if not bandwidths:
            return 0.0
        
        # Define ideal bandwidths for each quality level
        ideal_bandwidths = {
            '144p': 0.5,   # 500 kbps
            '240p': 1.0,   # 1 Mbps
            '480p': 2.5,   # 2.5 Mbps
            '720p': 5.0,   # 5 Mbps
            '1080p': 8.0,  # 8 Mbps
            '1440p': 16.0, # 16 Mbps
            '2160p': 35.0  # 35 Mbps
        }
        
        ideal_bandwidth = ideal_bandwidths.get(quality, 5.0)
        actual_average = np.mean(bandwidths)
        
        # Efficiency is how close actual bandwidth is to ideal
        if actual_average > 0:
            efficiency = min(ideal_bandwidth / actual_average, 1.0)
            return efficiency
        
        return 0.0
    
    def _calculate_theoretical_optimal_bandwidth(self, quality_bandwidth: Dict[str, List[float]]) -> float:
        """Calculate theoretical optimal total bandwidth"""
        ideal_bandwidths = {
            '144p': 0.5, '240p': 1.0, '480p': 2.5, '720p': 5.0,
            '1080p': 8.0, '1440p': 16.0, '2160p': 35.0
        }
        
        total_optimal = 0.0
        total_samples = 0
        
        for quality, bandwidths in quality_bandwidth.items():
            if quality in ideal_bandwidths:
                optimal_bandwidth = ideal_bandwidths[quality]
                sample_count = len(bandwidths)
                total_optimal += optimal_bandwidth * sample_count
                total_samples += sample_count
        
        return total_optimal / total_samples if total_samples > 0 else 0.0
    
    def _generate_bandwidth_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate bandwidth optimization recommendations"""
        recommendations = []
        
        # Check efficiency
        if analysis.get('bandwidth_efficiency', 0) < 0.8:
            recommendations.append("Optimize encoding settings to improve bandwidth efficiency")
        
        # Check congestion periods
        if len(analysis.get('congestion_periods', [])) > 3:
            recommendations.append("Implement load balancing during peak hours")
            recommendations.append("Consider adaptive bitrate streaming")
        
        # Check quality-specific efficiency
        for quality, stats in analysis.get('bandwidth_by_quality', {}).items():
            if stats.get('efficiency', 0) < 0.7:
                recommendations.append(f"Optimize {quality} encoding for better bandwidth usage")
        
        return recommendations