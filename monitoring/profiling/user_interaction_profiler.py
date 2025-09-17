"""⚡ User Interaction Profiling System
===================================

Advanced user interaction performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for user behavior, UI performance, and user experience metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization  
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of user interactions"""
    CLICK = "click"
    SCROLL = "scroll"
    HOVER = "hover"
    FORM_SUBMIT = "form_submit"
    FORM_INPUT = "form_input"
    NAVIGATION = "navigation"
    SEARCH = "search"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    VIDEO_PLAY = "video_play"
    VIDEO_PAUSE = "video_pause"
    SHARE = "share"
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"


class PageType(Enum):
    """Types of pages/views"""
    HOMEPAGE = "homepage"
    DASHBOARD = "dashboard"
    PROFILE = "profile"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_VIEW = "content_view"
    SEARCH_RESULTS = "search_results"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    COLLABORATION = "collaboration"
    PAYMENT = "payment"
    HELP = "help"


class UserType(Enum):
    """Types of users"""
    GUEST = "guest"
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    ADMIN = "admin"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class DeviceType(Enum):
    """Device types"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    SMART_TV = "smart_tv"


@dataclass
class UserSessionMetadata:
    """Metadata for user sessions"""
    session_id: str
    user_id: Optional[str]
    user_type: UserType
    device_type: DeviceType
    browser: str
    os: str
    screen_resolution: str
    timezone: str
    location: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class UserInteractionMetrics:
    """User interaction performance metrics"""
    interaction_id: str
    session_id: str
    user_id: Optional[str]
    user_type: UserType
    interaction_type: InteractionType
    page_type: PageType
    element_id: Optional[str]
    element_type: Optional[str]
    page_url: str
    interaction_time_ms: float
    page_load_time_ms: float
    dom_ready_time_ms: float
    first_paint_time_ms: float
    largest_contentful_paint_ms: float
    cumulative_layout_shift: float
    first_input_delay_ms: float
    time_on_page_ms: float
    scroll_depth_percent: float
    click_accuracy: float
    form_completion_time_ms: float
    error_count: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserExperienceBottleneck:
    """User experience bottleneck information"""
    bottleneck_type: str
    severity: str
    page_type: PageType
    interaction_type: InteractionType
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class UserInteractionProfiler:
    """
    User interaction performance profiler for Creator Economy platform
    """
    
    def __init__(self, 
                 monitoring_interval: float = 30.0,
                 max_history_size: int = 100000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.interaction_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.active_sessions: Dict[str, Dict] = {}
        self.page_performance_cache: Dict[str, Dict] = {}
        
        # Performance thresholds (Web Vitals + UX)
        self.thresholds = {
            'slow_page_load_threshold': 3000.0,      # 3 seconds
            'slow_interaction_threshold': 300.0,     # 300ms
            'lcp_threshold': 2500.0,                 # 2.5s (LCP)
            'fid_threshold': 100.0,                  # 100ms (FID)
            'cls_threshold': 0.1,                    # 0.1 (CLS)
            'bounce_rate_threshold': 70.0,           # 70%
            'low_engagement_threshold': 30.0,        # 30 seconds
            'form_abandonment_threshold': 60.0       # 60%
        }
        
        # User behavior analytics
        self.user_journeys: Dict[str, List[str]] = defaultdict(list)
        self.conversion_funnels: Dict[str, List[str]] = {}
        
        logger.info("UserInteractionProfiler initialized")

    def start_monitoring(self):
        """Start background user interaction monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("User interaction monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("User interaction monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._analyze_user_sessions()
                self._calculate_page_performance()
                self._detect_user_patterns()
                self._cleanup_old_sessions()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in user interaction monitoring loop: {e}")

    def _analyze_user_sessions(self):
        """Analyze active user sessions"""
        try:
            current_time = datetime.utcnow()
            
            for session_id, session_data in self.active_sessions.items():
                session_start = session_data.get('start_time')
                if session_start:
                    session_duration = (current_time - session_start).total_seconds()
                    
                    # Check for long sessions (potential issues)
                    if session_duration > 3600:  # 1 hour
                        logger.info(f"Long user session detected: {session_id} ({session_duration:.0f}s)")
                        
        except Exception as e:
            logger.error(f"Error analyzing user sessions: {e}")

    def _calculate_page_performance(self):
        """Calculate page performance metrics"""
        try:
            # Group recent metrics by page
            recent_metrics = [
                m for m in list(self.interaction_metrics_history)[-1000:]
                if (datetime.utcnow() - m.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            page_metrics = defaultdict(list)
            for metrics in recent_metrics:
                page_key = f"{metrics.page_type.value}_{metrics.page_url}"
                page_metrics[page_key].append(metrics)
            
            # Calculate averages for each page
            for page_key, metrics_list in page_metrics.items():
                avg_load_time = statistics.mean([m.page_load_time_ms for m in metrics_list if m.page_load_time_ms > 0])
                avg_lcp = statistics.mean([m.largest_contentful_paint_ms for m in metrics_list if m.largest_contentful_paint_ms > 0])
                avg_cls = statistics.mean([m.cumulative_layout_shift for m in metrics_list if m.cumulative_layout_shift > 0])
                
                self.page_performance_cache[page_key] = {
                    'avg_load_time_ms': avg_load_time,
                    'avg_lcp_ms': avg_lcp,
                    'avg_cls': avg_cls,
                    'sample_count': len(metrics_list),
                    'last_updated': datetime.utcnow()
                }
                
        except Exception as e:
            logger.error(f"Error calculating page performance: {e}")

    def _detect_user_patterns(self):
        """Detect user behavior patterns"""
        try:
            # Analyze user journeys
            recent_metrics = list(self.interaction_metrics_history)[-500:]
            
            # Group by session
            session_journeys = defaultdict(list)
            for metrics in recent_metrics:
                session_journeys[metrics.session_id].append({
                    'page_type': metrics.page_type.value,
                    'interaction_type': metrics.interaction_type.value,
                    'timestamp': metrics.timestamp
                })
            
            # Identify common patterns
            for session_id, journey in session_journeys.items():
                if len(journey) > 1:
                    # Sort by timestamp
                    journey.sort(key=lambda x: x['timestamp'])
                    
                    # Extract page sequence
                    page_sequence = [step['page_type'] for step in journey]
                    self.user_journeys[session_id] = page_sequence
                    
        except Exception as e:
            logger.error(f"Error detecting user patterns: {e}")

    def _cleanup_old_sessions(self):
        """Clean up old inactive sessions"""
        try:
            current_time = datetime.utcnow()
            inactive_threshold = timedelta(hours=2)
            
            inactive_sessions = []
            for session_id, session_data in self.active_sessions.items():
                last_activity = session_data.get('last_activity', session_data.get('start_time'))
                if last_activity and (current_time - last_activity) > inactive_threshold:
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                self.active_sessions.pop(session_id, None)
                
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")

    def start_user_session(self,
                          user_id: Optional[str],
                          user_type: UserType,
                          device_type: DeviceType,
                          browser: str,
                          os: str,
                          screen_resolution: str,
                          timezone: str,
                          **kwargs) -> str:
        """
        Start tracking a user session
        
        Args:
            user_id: User identifier (None for guest)
            user_type: Type of user
            device_type: Device type
            browser: Browser name
            os: Operating system
            screen_resolution: Screen resolution
            timezone: User timezone
            **kwargs: Additional metadata
            
        Returns:
            Session ID for tracking
        """
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'user_type': user_type,
            'device_type': device_type,
            'browser': browser,
            'os': os,
            'screen_resolution': screen_resolution,
            'timezone': timezone,
            'start_time': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'page_views': 0,
            'interactions': 0,
            'metadata': kwargs
        }
        
        logger.info(f"Started user session: {session_id} for user: {user_id or 'guest'}")
        return session_id

    def track_user_interaction(self,
                             session_id: str,
                             interaction_type: InteractionType,
                             page_type: PageType,
                             page_url: str,
                             interaction_time_ms: float = 0.0,
                             page_load_time_ms: float = 0.0,
                             element_id: Optional[str] = None,
                             element_type: Optional[str] = None,
                             **kwargs) -> UserInteractionMetrics:
        """
        Track a user interaction
        
        Args:
            session_id: Session ID from start_user_session
            interaction_type: Type of interaction
            page_type: Type of page
            page_url: URL of the page
            interaction_time_ms: Time taken for interaction
            page_load_time_ms: Page load time
            element_id: ID of interacted element
            element_type: Type of interacted element
            **kwargs: Additional interaction metadata
            
        Returns:
            UserInteractionMetrics with interaction data
        """
        interaction_id = str(uuid.uuid4())
        
        # Get session info
        session_info = self.active_sessions.get(session_id)
        if not session_info:
            raise ValueError(f"Session ID {session_id} not found")
        
        # Update session activity
        session_info['last_activity'] = datetime.utcnow()
        session_info['interactions'] += 1
        
        # Create metrics
        metrics = UserInteractionMetrics(
            interaction_id=interaction_id,
            session_id=session_id,
            user_id=session_info.get('user_id'),
            user_type=session_info['user_type'],
            interaction_type=interaction_type,
            page_type=page_type,
            element_id=element_id,
            element_type=element_type,
            page_url=page_url,
            interaction_time_ms=interaction_time_ms,
            page_load_time_ms=page_load_time_ms,
            dom_ready_time_ms=kwargs.get('dom_ready_time_ms', 0.0),
            first_paint_time_ms=kwargs.get('first_paint_time_ms', 0.0),
            largest_contentful_paint_ms=kwargs.get('largest_contentful_paint_ms', 0.0),
            cumulative_layout_shift=kwargs.get('cumulative_layout_shift', 0.0),
            first_input_delay_ms=kwargs.get('first_input_delay_ms', 0.0),
            time_on_page_ms=kwargs.get('time_on_page_ms', 0.0),
            scroll_depth_percent=kwargs.get('scroll_depth_percent', 0.0),
            click_accuracy=kwargs.get('click_accuracy', 1.0),
            form_completion_time_ms=kwargs.get('form_completion_time_ms', 0.0),
            error_count=kwargs.get('error_count', 0),
            timestamp=datetime.utcnow(),
            metadata={
                **session_info.get('metadata', {}),
                **kwargs,
                'device_type': session_info['device_type'].value,
                'browser': session_info['browser'],
                'os': session_info['os']
            }
        )
        
        # Store metrics
        self.interaction_metrics_history.append(metrics)
        
        # Check for UX bottlenecks
        self._analyze_ux_bottlenecks(metrics)
        
        return metrics

    def _analyze_ux_bottlenecks(self, metrics: UserInteractionMetrics):
        """Analyze user experience bottlenecks"""
        bottlenecks = []
        
        # Check page load performance
        if metrics.page_load_time_ms > self.thresholds['slow_page_load_threshold']:
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="slow_page_load",
                severity="high" if metrics.page_load_time_ms > 5000 else "medium",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"Page load too slow: {metrics.page_load_time_ms:.1f}ms",
                impact="Poor user experience, high bounce rate",
                recommendations=[
                    "Optimize page resources",
                    "Implement lazy loading",
                    "Use CDN for static assets",
                    "Minimize JavaScript execution"
                ],
                detected_at=datetime.utcnow(),
                metrics={'page_load_time_ms': metrics.page_load_time_ms}
            ))
        
        # Check interaction responsiveness
        if metrics.interaction_time_ms > self.thresholds['slow_interaction_threshold']:
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="slow_interaction",
                severity="medium",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"Interaction response too slow: {metrics.interaction_time_ms:.1f}ms",
                impact="Poor perceived performance, user frustration",
                recommendations=[
                    "Optimize event handlers",
                    "Reduce main thread blocking",
                    "Use request throttling",
                    "Implement progressive loading"
                ],
                detected_at=datetime.utcnow(),
                metrics={'interaction_time_ms': metrics.interaction_time_ms}
            ))
        
        # Check Core Web Vitals
        if metrics.largest_contentful_paint_ms > self.thresholds['lcp_threshold']:
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="poor_lcp",
                severity="high",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"Largest Contentful Paint too slow: {metrics.largest_contentful_paint_ms:.1f}ms",
                impact="Poor loading performance, SEO impact",
                recommendations=[
                    "Optimize largest content element",
                    "Preload critical resources",
                    "Optimize server response time",
                    "Use efficient image formats"
                ],
                detected_at=datetime.utcnow(),
                metrics={'lcp_ms': metrics.largest_contentful_paint_ms}
            ))
        
        if metrics.first_input_delay_ms > self.thresholds['fid_threshold']:
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="poor_fid",
                severity="medium",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"First Input Delay too high: {metrics.first_input_delay_ms:.1f}ms",
                impact="Poor interactivity, user frustration",
                recommendations=[
                    "Reduce JavaScript execution time",
                    "Split long tasks",
                    "Use web workers",
                    "Defer non-critical JavaScript"
                ],
                detected_at=datetime.utcnow(),
                metrics={'fid_ms': metrics.first_input_delay_ms}
            ))
        
        if metrics.cumulative_layout_shift > self.thresholds['cls_threshold']:
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="poor_cls",
                severity="medium",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"Cumulative Layout Shift too high: {metrics.cumulative_layout_shift:.3f}",
                impact="Visual instability, poor user experience",
                recommendations=[
                    "Reserve space for dynamic content",
                    "Use size attributes for media",
                    "Avoid inserting content above existing content",
                    "Use transform animations"
                ],
                detected_at=datetime.utcnow(),
                metrics={'cls': metrics.cumulative_layout_shift}
            ))
        
        # Check form completion performance
        if (metrics.interaction_type == InteractionType.FORM_SUBMIT and 
            metrics.form_completion_time_ms > 300000):  # 5 minutes
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="slow_form_completion",
                severity="low",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"Form completion too slow: {metrics.form_completion_time_ms/1000:.1f}s",
                impact="Form abandonment, conversion loss",
                recommendations=[
                    "Simplify form fields",
                    "Add progress indicators",
                    "Implement auto-save",
                    "Provide clear validation"
                ],
                detected_at=datetime.utcnow(),
                metrics={'form_completion_time_ms': metrics.form_completion_time_ms}
            ))
        
        # Check for errors
        if metrics.error_count > 0:
            bottlenecks.append(UserExperienceBottleneck(
                bottleneck_type="user_errors",
                severity="medium",
                page_type=metrics.page_type,
                interaction_type=metrics.interaction_type,
                description=f"User errors detected: {metrics.error_count}",
                impact="Poor user experience, task failure",
                recommendations=[
                    "Improve error messages",
                    "Add input validation",
                    "Provide help documentation",
                    "Implement error recovery"
                ],
                detected_at=datetime.utcnow(),
                metrics={'error_count': metrics.error_count}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get user interaction performance summary"""
        if not self.interaction_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.interaction_metrics_history)[-5000:]  # Last 5000 interactions
        
        # Calculate Core Web Vitals
        lcp_values = [m.largest_contentful_paint_ms for m in recent_metrics if m.largest_contentful_paint_ms > 0]
        fid_values = [m.first_input_delay_ms for m in recent_metrics if m.first_input_delay_ms > 0]
        cls_values = [m.cumulative_layout_shift for m in recent_metrics if m.cumulative_layout_shift > 0]
        
        # Calculate other metrics
        page_load_times = [m.page_load_time_ms for m in recent_metrics if m.page_load_time_ms > 0]
        interaction_times = [m.interaction_time_ms for m in recent_metrics if m.interaction_time_ms > 0]
        time_on_page_values = [m.time_on_page_ms for m in recent_metrics if m.time_on_page_ms > 0]
        
        return {
            "summary": {
                "total_interactions": len(recent_metrics),
                "active_sessions": len(self.active_sessions),
                "avg_page_load_time_ms": statistics.mean(page_load_times) if page_load_times else 0,
                "avg_interaction_time_ms": statistics.mean(interaction_times) if interaction_times else 0,
                "avg_time_on_page_ms": statistics.mean(time_on_page_values) if time_on_page_values else 0,
                "p75_page_load_time_ms": statistics.quantiles(page_load_times, n=4)[2] if len(page_load_times) > 4 else 0,
                "interactions_per_session": len(recent_metrics) / max(1, len(self.active_sessions))
            },
            "core_web_vitals": {
                "avg_lcp_ms": statistics.mean(lcp_values) if lcp_values else 0,
                "avg_fid_ms": statistics.mean(fid_values) if fid_values else 0,
                "avg_cls": statistics.mean(cls_values) if cls_values else 0,
                "good_lcp_percentage": (sum(1 for v in lcp_values if v <= 2500) / len(lcp_values)) * 100 if lcp_values else 0,
                "good_fid_percentage": (sum(1 for v in fid_values if v <= 100) / len(fid_values)) * 100 if fid_values else 0,
                "good_cls_percentage": (sum(1 for v in cls_values if v <= 0.1) / len(cls_values)) * 100 if cls_values else 0
            },
            "by_page_type": self._get_metrics_by_page_type(),
            "by_interaction_type": self._get_metrics_by_interaction_type(),
            "by_device_type": self._get_metrics_by_device_type(),
            "by_user_type": self._get_metrics_by_user_type(),
            "user_journeys": self._get_common_user_journeys(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_ux_optimization_recommendations()
        }

    def _get_metrics_by_page_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by page type"""
        metrics_by_page = defaultdict(list)
        
        for metrics in list(self.interaction_metrics_history)[-2000:]:
            metrics_by_page[metrics.page_type.value].append(metrics)
        
        result = {}
        for page_type, metrics_list in metrics_by_page.items():
            page_load_times = [m.page_load_time_ms for m in metrics_list if m.page_load_time_ms > 0]
            lcp_values = [m.largest_contentful_paint_ms for m in metrics_list if m.largest_contentful_paint_ms > 0]
            
            result[page_type] = {
                "interactions": len(metrics_list),
                "avg_page_load_time_ms": statistics.mean(page_load_times) if page_load_times else 0,
                "avg_lcp_ms": statistics.mean(lcp_values) if lcp_values else 0,
                "unique_sessions": len(set(m.session_id for m in metrics_list))
            }
        
        return result

    def _get_metrics_by_interaction_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by interaction type"""
        metrics_by_interaction = defaultdict(list)
        
        for metrics in list(self.interaction_metrics_history)[-2000:]:
            metrics_by_interaction[metrics.interaction_type.value].append(metrics)
        
        result = {}
        for interaction_type, metrics_list in metrics_by_interaction.items():
            interaction_times = [m.interaction_time_ms for m in metrics_list if m.interaction_time_ms > 0]
            
            result[interaction_type] = {
                "count": len(metrics_list),
                "avg_interaction_time_ms": statistics.mean(interaction_times) if interaction_times else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_device_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by device type"""
        metrics_by_device = defaultdict(list)
        
        for metrics in list(self.interaction_metrics_history)[-2000:]:
            device_type = metrics.metadata.get('device_type', 'unknown')
            metrics_by_device[device_type].append(metrics)
        
        result = {}
        for device_type, metrics_list in metrics_by_device.items():
            page_load_times = [m.page_load_time_ms for m in metrics_list if m.page_load_time_ms > 0]
            
            result[device_type] = {
                "interactions": len(metrics_list),
                "avg_page_load_time_ms": statistics.mean(page_load_times) if page_load_times else 0,
                "unique_users": len(set(m.user_id for m in metrics_list if m.user_id))
            }
        
        return result

    def _get_metrics_by_user_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by user type"""
        metrics_by_user_type = defaultdict(list)
        
        for metrics in list(self.interaction_metrics_history)[-2000:]:
            metrics_by_user_type[metrics.user_type.value].append(metrics)
        
        result = {}
        for user_type, metrics_list in metrics_by_user_type.items():
            time_on_page_values = [m.time_on_page_ms for m in metrics_list if m.time_on_page_ms > 0]
            
            result[user_type] = {
                "interactions": len(metrics_list),
                "avg_time_on_page_ms": statistics.mean(time_on_page_values) if time_on_page_values else 0,
                "unique_sessions": len(set(m.session_id for m in metrics_list))
            }
        
        return result

    def _get_common_user_journeys(self) -> Dict[str, int]:
        """Get common user journey patterns"""
        journey_counts = defaultdict(int)
        
        for session_id, journey in self.user_journeys.items():
            if len(journey) > 1:
                journey_key = " → ".join(journey[:5])  # First 5 steps
                journey_counts[journey_key] += 1
        
        # Return top 10 most common journeys
        sorted_journeys = sorted(journey_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_journeys[:10])

    def _get_ux_optimization_recommendations(self) -> List[str]:
        """Get UX optimization recommendations"""
        recommendations = []
        
        if not self.interaction_metrics_history:
            return ["Start tracking user interactions to get recommendations"]
        
        recent_metrics = list(self.interaction_metrics_history)[-1000:]
        
        # Calculate key UX metrics
        avg_page_load = statistics.mean([m.page_load_time_ms for m in recent_metrics if m.page_load_time_ms > 0])
        avg_lcp = statistics.mean([m.largest_contentful_paint_ms for m in recent_metrics if m.largest_contentful_paint_ms > 0])
        avg_cls = statistics.mean([m.cumulative_layout_shift for m in recent_metrics if m.cumulative_layout_shift > 0])
        error_rate = (sum(1 for m in recent_metrics if m.error_count > 0) / len(recent_metrics)) * 100
        
        if avg_page_load > 3000:
            recommendations.append("High page load times - optimize critical resources")
        if avg_lcp > 2500:
            recommendations.append("Poor LCP scores - optimize largest content element")
        if avg_cls > 0.1:
            recommendations.append("High CLS values - improve visual stability")
        if error_rate > 5:
            recommendations.append("High error rate - improve error handling and UX")
        
        # Check device-specific issues
        device_metrics = self._get_metrics_by_device_type()
        mobile_load_time = device_metrics.get('mobile', {}).get('avg_page_load_time_ms', 0)
        if mobile_load_time > 4000:
            recommendations.append("Poor mobile performance - optimize for mobile devices")
        
        # Check page-specific issues
        page_metrics = self._get_metrics_by_page_type()
        slow_pages = [page for page, data in page_metrics.items() if data.get('avg_page_load_time_ms', 0) > 5000]
        if slow_pages:
            recommendations.append(f"Slow pages detected: {', '.join(slow_pages[:3])}")
        
        if not recommendations:
            recommendations.append("User experience metrics are within acceptable ranges")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[UserExperienceBottleneck]:
        """Get recent UX bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def end_user_session(self, session_id: str):
        """End a user session"""
        if session_id in self.active_sessions:
            session_info = self.active_sessions.pop(session_id)
            session_duration = (datetime.utcnow() - session_info['start_time']).total_seconds()
            logger.info(f"Ended user session: {session_id} (duration: {session_duration:.0f}s, "
                       f"interactions: {session_info['interactions']})")

    def export_metrics(self, format: str = "json") -> str:
        """Export user interaction metrics"""
        data = {
            "interaction_metrics": [
                {
                    "interaction_id": m.interaction_id,
                    "session_id": m.session_id,
                    "user_type": m.user_type.value,
                    "interaction_type": m.interaction_type.value,
                    "page_type": m.page_type.value,
                    "page_load_time_ms": m.page_load_time_ms,
                    "lcp_ms": m.largest_contentful_paint_ms,
                    "cls": m.cumulative_layout_shift,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.interaction_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "page_type": b.page_type.value,
                    "interaction_type": b.interaction_type.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ],
            "active_sessions": len(self.active_sessions)
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_user_interaction_profiler(monitoring_interval: float = 30.0,
                                   max_history_size: int = 100000,
                                   start_monitoring: bool = True) -> UserInteractionProfiler:
    """
    Create and configure a user interaction profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured UserInteractionProfiler instance
    """
    profiler = UserInteractionProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_user_interaction_profiler()
    
    try:
        # Start a user session
        session_id = profiler.start_user_session(
            user_id="creator_123",
            user_type=UserType.CREATOR,
            device_type=DeviceType.DESKTOP,
            browser="Chrome",
            os="Windows",
            screen_resolution="1920x1080",
            timezone="UTC"
        )
        
        # Track some interactions
        metrics1 = profiler.track_user_interaction(
            session_id=session_id,
            interaction_type=InteractionType.NAVIGATION,
            page_type=PageType.DASHBOARD,
            page_url="/dashboard",
            page_load_time_ms=1200.0,
            largest_contentful_paint_ms=800.0,
            cumulative_layout_shift=0.05
        )
        
        metrics2 = profiler.track_user_interaction(
            session_id=session_id,
            interaction_type=InteractionType.CLICK,
            page_type=PageType.CONTENT_UPLOAD,
            page_url="/upload",
            interaction_time_ms=150.0,
            element_id="upload-btn",
            element_type="button"
        )
        
        print(f"Page load time: {metrics1.page_load_time_ms:.2f}ms")
        print(f"LCP: {metrics1.largest_contentful_paint_ms:.2f}ms")
        print(f"Click interaction time: {metrics2.interaction_time_ms:.2f}ms")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"UX performance summary: {json.dumps(summary, indent=2)}")
        
        # End session
        profiler.end_user_session(session_id)
        
    finally:
        profiler.stop_monitoring()