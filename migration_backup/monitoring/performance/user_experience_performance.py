"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

User Experience Performance Monitor - Enterprise Performance Monitoring
Advanced UX performance monitoring for Creator Economy user experience

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import statistics
from prometheus_client import Gauge, Counter, Histogram
import aiohttp
import user_agents
from urllib.parse import urlparse, parse_qs
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)

@dataclass
class CoreWebVitalsMetrics:
    """Core Web Vitals performance metrics"""
    session_id: str
    page_url: str
    largest_contentful_paint_ms: float
    first_input_delay_ms: float
    cumulative_layout_shift: float
    first_contentful_paint_ms: float
    time_to_interactive_ms: float
    total_blocking_time_ms: float
    speed_index: float
    timestamp: datetime
    user_agent: Optional[str] = None
    connection_type: Optional[str] = None
    device_type: Optional[str] = None

@dataclass
class RealUserMonitoringMetrics:
    """Real User Monitoring (RUM) metrics"""
    session_id: str
    user_id: Optional[str]
    page_url: str
    page_load_time_ms: float
    dom_content_loaded_ms: float
    resource_load_time_ms: float
    javascript_execution_time_ms: float
    css_render_time_ms: float
    image_load_time_ms: float
    api_call_time_ms: float
    error_count: int
    timestamp: datetime
    geographic_location: Optional[str] = None
    device_type: str = 'unknown'
    browser_name: str = 'unknown'
    connection_speed: Optional[str] = None

@dataclass
class UserInteractionMetrics:
    """User interaction performance metrics"""
    session_id: str
    user_id: Optional[str]
    interaction_type: str  # click, scroll, input, navigation
    element_selector: str
    response_time_ms: float
    success: bool
    page_url: str
    timestamp: datetime
    user_flow_step: Optional[str] = None
    conversion_funnel_stage: Optional[str] = None

@dataclass
class MobilePerformanceMetrics:
    """Mobile-specific performance metrics"""
    session_id: str
    device_model: str
    os_version: str
    app_version: str
    network_type: str  # 3g, 4g, 5g, wifi
    battery_level: Optional[int]
    memory_usage_mb: float
    cpu_usage_percent: float
    app_launch_time_ms: float
    screen_render_time_ms: float
    touch_response_time_ms: float
    timestamp: datetime

@dataclass
class ConversionFunnelMetrics:
    """Conversion funnel performance metrics"""
    funnel_name: str
    stage_name: str
    stage_order: int
    session_id: str
    user_id: Optional[str]
    stage_load_time_ms: float
    stage_completion_time_ms: float
    stage_success: bool
    drop_off_reason: Optional[str]
    timestamp: datetime

@dataclass
class PerformanceInsight:
    """Performance insight and recommendation"""
    insight_type: str  # performance_bottleneck, user_experience_issue, optimization_opportunity
    severity: str  # low, medium, high, critical
    title: str
    description: str
    affected_metrics: List[str]
    impact_score: float  # 0-100
    recommendation: str
    estimated_improvement: str
    implementation_effort: str  # low, medium, high
    timestamp: datetime

class UserExperiencePerformance:
    """
    Enterprise-grade user experience performance monitor
    Tracks Core Web Vitals, Real User Monitoring, and conversion funnel performance
    """
    
    def __init__(self,
                 geoip_database_path: Optional[str] = None,
                 enable_real_user_monitoring: bool = True,
                 enable_conversion_tracking: bool = True,
                 enable_mobile_monitoring: bool = True,
                 core_web_vitals_thresholds: Optional[Dict] = None):
        """
        Initialize user experience performance monitor
        
        Args:
            geoip_database_path: Path to GeoIP database file
            enable_real_user_monitoring: Enable RUM data collection
            enable_conversion_tracking: Enable conversion funnel tracking
            enable_mobile_monitoring: Enable mobile-specific monitoring
            core_web_vitals_thresholds: Custom thresholds for Core Web Vitals
        """
        self.geoip_database_path = geoip_database_path
        self.enable_real_user_monitoring = enable_real_user_monitoring
        self.enable_conversion_tracking = enable_conversion_tracking
        self.enable_mobile_monitoring = enable_mobile_monitoring
        
        # Core Web Vitals thresholds (Google's recommended values)
        self.core_web_vitals_thresholds = core_web_vitals_thresholds or {
            'largest_contentful_paint_ms': {'good': 2500, 'needs_improvement': 4000},
            'first_input_delay_ms': {'good': 100, 'needs_improvement': 300},
            'cumulative_layout_shift': {'good': 0.1, 'needs_improvement': 0.25},
            'first_contentful_paint_ms': {'good': 1800, 'needs_improvement': 3000},
            'time_to_interactive_ms': {'good': 3800, 'needs_improvement': 7300}
        }
        
        # GeoIP database
        self.geoip_reader = None
        if geoip_database_path:
            try:
                self.geoip_reader = geoip2.database.Reader(geoip_database_path)
            except Exception as e:
                logger.warning(f"Could not load GeoIP database: {e}")
        
        # Metrics storage
        self.core_web_vitals: deque = deque(maxlen=10000)
        self.rum_metrics: deque = deque(maxlen=20000)
        self.interaction_metrics: deque = deque(maxlen=15000)
        self.mobile_metrics: deque = deque(maxlen=10000)
        self.conversion_metrics: deque = deque(maxlen=5000)
        self.performance_insights: deque = deque(maxlen=1000)
        
        # User session tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.user_journeys: Dict[str, List] = defaultdict(list)
        self.conversion_funnels: Dict[str, Dict] = {}
        
        # Performance analysis
        self.page_performance_cache: Dict[str, Dict] = defaultdict(dict)
        self.user_cohort_analysis: Dict[str, Dict] = defaultdict(dict)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_tasks = []
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.core_web_vitals_histogram = Histogram(
            'ux_core_web_vitals_seconds',
            'Core Web Vitals metrics',
            ['metric_name', 'page', 'device_type'],
            buckets=[0.1, 0.5, 1.0, 2.5, 4.0, 7.0, 10.0, 15.0, 30.0]
        )
        
        self.page_load_time_histogram = Histogram(
            'ux_page_load_time_seconds',
            'Page load time',
            ['page', 'device_type', 'connection_type'],
            buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0]
        )
        
        self.user_interaction_time_histogram = Histogram(
            'ux_interaction_response_time_seconds',
            'User interaction response time',
            ['interaction_type', 'page'],
            buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.conversion_funnel_gauge = Gauge(
            'ux_conversion_funnel_completion_rate',
            'Conversion funnel completion rate',
            ['funnel_name', 'stage_name']
        )
        
        self.mobile_performance_gauge = Gauge(
            'ux_mobile_performance_score',
            'Mobile performance score',
            ['metric_type', 'device_model']
        )
        
        self.ux_score_gauge = Gauge(
            'ux_overall_score',
            'Overall UX performance score',
            ['page', 'device_type']
        )
        
        self.error_rate_gauge = Gauge(
            'ux_error_rate_percent',
            'User experience error rate',
            ['page', 'error_type']
        )
    
    def record_core_web_vitals(self,
                             session_id: str,
                             page_url: str,
                             lcp: float,
                             fid: float,
                             cls: float,
                             fcp: float,
                             tti: float,
                             tbt: float,
                             speed_index: float,
                             user_agent: Optional[str] = None,
                             connection_type: Optional[str] = None):
        """Record Core Web Vitals metrics"""
        
        device_type = self._detect_device_type(user_agent)
        
        metrics = CoreWebVitalsMetrics(
            session_id=session_id,
            page_url=page_url,
            largest_contentful_paint_ms=lcp,
            first_input_delay_ms=fid,
            cumulative_layout_shift=cls,
            first_contentful_paint_ms=fcp,
            time_to_interactive_ms=tti,
            total_blocking_time_ms=tbt,
            speed_index=speed_index,
            timestamp=datetime.utcnow(),
            user_agent=user_agent,
            connection_type=connection_type,
            device_type=device_type
        )
        
        self.core_web_vitals.append(metrics)
        
        # Update Prometheus metrics
        page_path = urlparse(page_url).path
        
        self.core_web_vitals_histogram.labels(
            metric_name='lcp',
            page=page_path,
            device_type=device_type
        ).observe(lcp / 1000)
        
        self.core_web_vitals_histogram.labels(
            metric_name='fid',
            page=page_path,
            device_type=device_type
        ).observe(fid / 1000)
        
        self.core_web_vitals_histogram.labels(
            metric_name='fcp',
            page=page_path,
            device_type=device_type
        ).observe(fcp / 1000)
        
        # Calculate and record UX score
        ux_score = self._calculate_ux_score(metrics)
        self.ux_score_gauge.labels(
            page=page_path,
            device_type=device_type
        ).set(ux_score)
        
        # Store for session tracking
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['core_web_vitals'] = metrics
        
        # Analyze for insights
        asyncio.create_task(self._analyze_core_web_vitals_insights(metrics))
    
    def record_real_user_monitoring(self,
                                  session_id: str,
                                  user_id: Optional[str],
                                  page_url: str,
                                  page_load_time: float,
                                  dom_content_loaded: float,
                                  resource_load_time: float,
                                  js_execution_time: float,
                                  css_render_time: float,
                                  image_load_time: float,
                                  api_call_time: float,
                                  error_count: int,
                                  user_agent: Optional[str] = None,
                                  client_ip: Optional[str] = None):
        """Record Real User Monitoring metrics"""
        
        if not self.enable_real_user_monitoring:
            return
        
        device_type = self._detect_device_type(user_agent)
        browser_name = self._extract_browser_name(user_agent)
        geographic_location = self._get_geographic_location(client_ip)
        connection_speed = self._estimate_connection_speed(page_load_time, resource_load_time)
        
        metrics = RealUserMonitoringMetrics(
            session_id=session_id,
            user_id=user_id,
            page_url=page_url,
            page_load_time_ms=page_load_time,
            dom_content_loaded_ms=dom_content_loaded,
            resource_load_time_ms=resource_load_time,
            javascript_execution_time_ms=js_execution_time,
            css_render_time_ms=css_render_time,
            image_load_time_ms=image_load_time,
            api_call_time_ms=api_call_time,
            error_count=error_count,
            timestamp=datetime.utcnow(),
            geographic_location=geographic_location,
            device_type=device_type,
            browser_name=browser_name,
            connection_speed=connection_speed
        )
        
        self.rum_metrics.append(metrics)
        
        # Update Prometheus metrics
        page_path = urlparse(page_url).path
        
        self.page_load_time_histogram.labels(
            page=page_path,
            device_type=device_type,
            connection_type=connection_speed or 'unknown'
        ).observe(page_load_time / 1000)
        
        if error_count > 0:
            self.error_rate_gauge.labels(
                page=page_path,
                error_type='javascript'
            ).set((error_count / max(1, error_count)) * 100)
        
        # Track user journey
        if user_id:
            self.user_journeys[user_id].append({
                'page': page_url,
                'timestamp': datetime.utcnow(),
                'performance': page_load_time,
                'errors': error_count
            })
        
        # Update page performance cache
        self._update_page_performance_cache(page_url, metrics)
    
    def record_user_interaction(self,
                              session_id: str,
                              user_id: Optional[str],
                              interaction_type: str,
                              element_selector: str,
                              response_time: float,
                              success: bool,
                              page_url: str,
                              user_flow_step: Optional[str] = None,
                              conversion_funnel_stage: Optional[str] = None):
        """Record user interaction metrics"""
        
        metrics = UserInteractionMetrics(
            session_id=session_id,
            user_id=user_id,
            interaction_type=interaction_type,
            element_selector=element_selector,
            response_time_ms=response_time,
            success=success,
            page_url=page_url,
            timestamp=datetime.utcnow(),
            user_flow_step=user_flow_step,
            conversion_funnel_stage=conversion_funnel_stage
        )
        
        self.interaction_metrics.append(metrics)
        
        # Update Prometheus metrics
        page_path = urlparse(page_url).path
        
        self.user_interaction_time_histogram.labels(
            interaction_type=interaction_type,
            page=page_path
        ).observe(response_time / 1000)
        
        # Track conversion funnel progress
        if conversion_funnel_stage and self.enable_conversion_tracking:
            self._update_conversion_funnel(session_id, conversion_funnel_stage, success)
    
    def record_mobile_performance(self,
                                session_id: str,
                                device_model: str,
                                os_version: str,
                                app_version: str,
                                network_type: str,
                                battery_level: Optional[int],
                                memory_usage: float,
                                cpu_usage: float,
                                app_launch_time: float,
                                screen_render_time: float,
                                touch_response_time: float):
        """Record mobile-specific performance metrics"""
        
        if not self.enable_mobile_monitoring:
            return
        
        metrics = MobilePerformanceMetrics(
            session_id=session_id,
            device_model=device_model,
            os_version=os_version,
            app_version=app_version,
            network_type=network_type,
            battery_level=battery_level,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            app_launch_time_ms=app_launch_time,
            screen_render_time_ms=screen_render_time,
            touch_response_time_ms=touch_response_time,
            timestamp=datetime.utcnow()
        )
        
        self.mobile_metrics.append(metrics)
        
        # Calculate mobile performance scores
        launch_score = max(0, 100 - (app_launch_time / 50))  # 5s = 0 score
        render_score = max(0, 100 - (screen_render_time / 16))  # 16ms = 60fps
        touch_score = max(0, 100 - (touch_response_time / 10))  # 100ms = 0 score
        resource_score = max(0, 100 - cpu_usage - (memory_usage / 10))
        
        # Update Prometheus metrics
        self.mobile_performance_gauge.labels(
            metric_type='app_launch',
            device_model=device_model
        ).set(launch_score)
        
        self.mobile_performance_gauge.labels(
            metric_type='screen_render',
            device_model=device_model
        ).set(render_score)
        
        self.mobile_performance_gauge.labels(
            metric_type='touch_response',
            device_model=device_model
        ).set(touch_score)
        
        self.mobile_performance_gauge.labels(
            metric_type='resource_usage',
            device_model=device_model
        ).set(resource_score)
    
    def _detect_device_type(self, user_agent: Optional[str]) -> str:
        """Detect device type from user agent"""
        if not user_agent:
            return 'unknown'
        
        try:
            ua = user_agents.parse(user_agent)
            
            if ua.is_mobile:
                return 'mobile'
            elif ua.is_tablet:
                return 'tablet'
            elif ua.is_pc:
                return 'desktop'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _extract_browser_name(self, user_agent: Optional[str]) -> str:
        """Extract browser name from user agent"""
        if not user_agent:
            return 'unknown'
        
        try:
            ua = user_agents.parse(user_agent)
            return ua.browser.family.lower()
        except:
            return 'unknown'
    
    def _get_geographic_location(self, client_ip: Optional[str]) -> Optional[str]:
        """Get geographic location from IP address"""
        if not client_ip or not self.geoip_reader:
            return None
        
        try:
            response = self.geoip_reader.city(client_ip)
            return f"{response.city.name}, {response.country.name}"
        except (geoip2.errors.AddressNotFoundError, Exception):
            return None
    
    def _estimate_connection_speed(self, page_load_time: float, resource_load_time: float) -> str:
        """Estimate connection speed based on load times"""
        total_load_time = page_load_time + resource_load_time
        
        if total_load_time < 1000:  # < 1s
            return 'fast'
        elif total_load_time < 3000:  # < 3s
            return 'medium'
        elif total_load_time < 8000:  # < 8s
            return 'slow'
        else:
            return 'very_slow'
    
    def _calculate_ux_score(self, cwv_metrics: CoreWebVitalsMetrics) -> float:
        """Calculate overall UX score based on Core Web Vitals"""
        scores = []
        
        # LCP score
        if cwv_metrics.largest_contentful_paint_ms <= self.core_web_vitals_thresholds['largest_contentful_paint_ms']['good']:
            scores.append(100)
        elif cwv_metrics.largest_contentful_paint_ms <= self.core_web_vitals_thresholds['largest_contentful_paint_ms']['needs_improvement']:
            scores.append(75)
        else:
            scores.append(50)
        
        # FID score
        if cwv_metrics.first_input_delay_ms <= self.core_web_vitals_thresholds['first_input_delay_ms']['good']:
            scores.append(100)
        elif cwv_metrics.first_input_delay_ms <= self.core_web_vitals_thresholds['first_input_delay_ms']['needs_improvement']:
            scores.append(75)
        else:
            scores.append(50)
        
        # CLS score
        if cwv_metrics.cumulative_layout_shift <= self.core_web_vitals_thresholds['cumulative_layout_shift']['good']:
            scores.append(100)
        elif cwv_metrics.cumulative_layout_shift <= self.core_web_vitals_thresholds['cumulative_layout_shift']['needs_improvement']:
            scores.append(75)
        else:
            scores.append(50)
        
        # FCP score
        if cwv_metrics.first_contentful_paint_ms <= self.core_web_vitals_thresholds['first_contentful_paint_ms']['good']:
            scores.append(100)
        elif cwv_metrics.first_contentful_paint_ms <= self.core_web_vitals_thresholds['first_contentful_paint_ms']['needs_improvement']:
            scores.append(75)
        else:
            scores.append(50)
        
        return statistics.mean(scores)
    
    def _update_page_performance_cache(self, page_url: str, rum_metrics: RealUserMonitoringMetrics):
        """Update page performance cache for analysis"""
        page_path = urlparse(page_url).path
        
        if page_path not in self.page_performance_cache:
            self.page_performance_cache[page_path] = {
                'load_times': deque(maxlen=100),
                'error_counts': deque(maxlen=100),
                'device_breakdown': defaultdict(list),
                'geographic_breakdown': defaultdict(list)
            }
        
        cache = self.page_performance_cache[page_path]
        cache['load_times'].append(rum_metrics.page_load_time_ms)
        cache['error_counts'].append(rum_metrics.error_count)
        cache['device_breakdown'][rum_metrics.device_type].append(rum_metrics.page_load_time_ms)
        
        if rum_metrics.geographic_location:
            cache['geographic_breakdown'][rum_metrics.geographic_location].append(rum_metrics.page_load_time_ms)
    
    def _update_conversion_funnel(self, session_id: str, stage: str, success: bool):
        """Update conversion funnel tracking"""
        if session_id not in self.conversion_funnels:
            self.conversion_funnels[session_id] = {
                'stages': {},
                'current_stage': None,
                'start_time': datetime.utcnow()
            }
        
        funnel = self.conversion_funnels[session_id]
        funnel['stages'][stage] = {
            'success': success,
            'timestamp': datetime.utcnow()
        }
        funnel['current_stage'] = stage
        
        # Calculate completion rate for this stage
        total_sessions = len(self.conversion_funnels)
        completed_sessions = len([f for f in self.conversion_funnels.values() 
                                if stage in f['stages'] and f['stages'][stage]['success']])
        
        completion_rate = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        self.conversion_funnel_gauge.labels(
            funnel_name='creator_onboarding',  # Default funnel name
            stage_name=stage
        ).set(completion_rate)
    
    async def _analyze_core_web_vitals_insights(self, cwv_metrics: CoreWebVitalsMetrics):
        """Analyze Core Web Vitals for performance insights"""
        insights = []
        
        # LCP analysis
        if cwv_metrics.largest_contentful_paint_ms > self.core_web_vitals_thresholds['largest_contentful_paint_ms']['needs_improvement']:
            insights.append(PerformanceInsight(
                insight_type='performance_bottleneck',
                severity='high' if cwv_metrics.largest_contentful_paint_ms > 6000 else 'medium',
                title='Slow Largest Contentful Paint',
                description=f'LCP is {cwv_metrics.largest_contentful_paint_ms:.0f}ms, exceeding recommended thresholds',
                affected_metrics=['largest_contentful_paint_ms'],
                impact_score=min(100, (cwv_metrics.largest_contentful_paint_ms - 2500) / 100),
                recommendation='Optimize images, implement lazy loading, improve server response times',
                estimated_improvement='30-50% LCP reduction',
                implementation_effort='medium',
                timestamp=datetime.utcnow()
            ))
        
        # FID analysis
        if cwv_metrics.first_input_delay_ms > self.core_web_vitals_thresholds['first_input_delay_ms']['needs_improvement']:
            insights.append(PerformanceInsight(
                insight_type='user_experience_issue',
                severity='high',
                title='High First Input Delay',
                description=f'FID is {cwv_metrics.first_input_delay_ms:.0f}ms, causing poor interactivity',
                affected_metrics=['first_input_delay_ms'],
                impact_score=min(100, cwv_metrics.first_input_delay_ms / 5),
                recommendation='Reduce JavaScript execution time, use web workers, code splitting',
                estimated_improvement='50-70% FID reduction',
                implementation_effort='high',
                timestamp=datetime.utcnow()
            ))
        
        # CLS analysis
        if cwv_metrics.cumulative_layout_shift > self.core_web_vitals_thresholds['cumulative_layout_shift']['needs_improvement']:
            insights.append(PerformanceInsight(
                insight_type='user_experience_issue',
                severity='medium',
                title='Layout Instability Detected',
                description=f'CLS score is {cwv_metrics.cumulative_layout_shift:.3f}, causing visual instability',
                affected_metrics=['cumulative_layout_shift'],
                impact_score=min(100, cwv_metrics.cumulative_layout_shift * 200),
                recommendation='Reserve space for images/ads, avoid inserting content above existing content',
                estimated_improvement='80-90% CLS reduction',
                implementation_effort='low',
                timestamp=datetime.utcnow()
            ))
        
        # Store insights
        self.performance_insights.extend(insights)
    
    def get_ux_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive UX performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Core Web Vitals summary
        recent_cwv = [cwv for cwv in self.core_web_vitals if cwv.timestamp >= cutoff_time]
        cwv_summary = {}
        
        if recent_cwv:
            cwv_summary = {
                'total_measurements': len(recent_cwv),
                'avg_lcp_ms': statistics.mean([cwv.largest_contentful_paint_ms for cwv in recent_cwv]),
                'avg_fid_ms': statistics.mean([cwv.first_input_delay_ms for cwv in recent_cwv]),
                'avg_cls': statistics.mean([cwv.cumulative_layout_shift for cwv in recent_cwv]),
                'avg_fcp_ms': statistics.mean([cwv.first_contentful_paint_ms for cwv in recent_cwv]),
                'device_breakdown': self._get_device_breakdown(recent_cwv)
            }
        
        # RUM summary
        recent_rum = [rum for rum in self.rum_metrics if rum.timestamp >= cutoff_time]
        rum_summary = {}
        
        if recent_rum:
            rum_summary = {
                'total_page_views': len(recent_rum),
                'avg_page_load_time_ms': statistics.mean([rum.page_load_time_ms for rum in recent_rum]),
                'total_errors': sum([rum.error_count for rum in recent_rum]),
                'avg_error_rate': statistics.mean([rum.error_count for rum in recent_rum]),
                'geographic_breakdown': self._get_geographic_breakdown(recent_rum),
                'browser_breakdown': self._get_browser_breakdown(recent_rum)
            }
        
        # User interactions summary
        recent_interactions = [interaction for interaction in self.interaction_metrics 
                             if interaction.timestamp >= cutoff_time]
        interaction_summary = {}
        
        if recent_interactions:
            interaction_summary = {
                'total_interactions': len(recent_interactions),
                'avg_response_time_ms': statistics.mean([i.response_time_ms for i in recent_interactions]),
                'success_rate': len([i for i in recent_interactions if i.success]) / len(recent_interactions) * 100,
                'interaction_types': self._get_interaction_type_breakdown(recent_interactions)
            }
        
        # Performance insights summary
        recent_insights = [insight for insight in self.performance_insights 
                         if insight.timestamp >= cutoff_time]
        
        return {
            'time_window_hours': hours,
            'core_web_vitals': cwv_summary,
            'real_user_monitoring': rum_summary,
            'user_interactions': interaction_summary,
            'performance_insights': {
                'total_insights': len(recent_insights),
                'critical_issues': len([i for i in recent_insights if i.severity == 'critical']),
                'high_priority_issues': len([i for i in recent_insights if i.severity == 'high']),
                'top_recommendations': [i.recommendation for i in recent_insights[:5]]
            },
            'overall_ux_score': self._calculate_overall_ux_score(recent_cwv, recent_rum, recent_interactions)
        }
    
    def _get_device_breakdown(self, cwv_metrics: List[CoreWebVitalsMetrics]) -> Dict[str, Any]:
        """Get device type breakdown for Core Web Vitals"""
        by_device = defaultdict(list)
        for cwv in cwv_metrics:
            by_device[cwv.device_type or 'unknown'].append(cwv.largest_contentful_paint_ms)
        
        return {
            device: {
                'count': len(lcp_values),
                'avg_lcp_ms': statistics.mean(lcp_values)
            }
            for device, lcp_values in by_device.items()
        }
    
    def _get_geographic_breakdown(self, rum_metrics: List[RealUserMonitoringMetrics]) -> Dict[str, Any]:
        """Get geographic breakdown for RUM metrics"""
        by_location = defaultdict(list)
        for rum in rum_metrics:
            location = rum.geographic_location or 'unknown'
            by_location[location].append(rum.page_load_time_ms)
        
        return {
            location: {
                'count': len(load_times),
                'avg_load_time_ms': statistics.mean(load_times)
            }
            for location, load_times in by_location.items()
        }
    
    def _get_browser_breakdown(self, rum_metrics: List[RealUserMonitoringMetrics]) -> Dict[str, Any]:
        """Get browser breakdown for RUM metrics"""
        by_browser = defaultdict(list)
        for rum in rum_metrics:
            by_browser[rum.browser_name].append(rum.page_load_time_ms)
        
        return {
            browser: {
                'count': len(load_times),
                'avg_load_time_ms': statistics.mean(load_times)
            }
            for browser, load_times in by_browser.items()
        }
    
    def _get_interaction_type_breakdown(self, interactions: List[UserInteractionMetrics]) -> Dict[str, Any]:
        """Get interaction type breakdown"""
        by_type = defaultdict(list)
        for interaction in interactions:
            by_type[interaction.interaction_type].append(interaction.response_time_ms)
        
        return {
            interaction_type: {
                'count': len(response_times),
                'avg_response_time_ms': statistics.mean(response_times)
            }
            for interaction_type, response_times in by_type.items()
        }
    
    def _calculate_overall_ux_score(self, 
                                  cwv_metrics: List[CoreWebVitalsMetrics],
                                  rum_metrics: List[RealUserMonitoringMetrics],
                                  interactions: List[UserInteractionMetrics]) -> float:
        """Calculate overall UX performance score"""
        scores = []
        
        # Core Web Vitals score (40% weight)
        if cwv_metrics:
            cwv_scores = [self._calculate_ux_score(cwv) for cwv in cwv_metrics]
            scores.append(('cwv', statistics.mean(cwv_scores), 0.4))
        
        # Page load performance score (30% weight)
        if rum_metrics:
            load_times = [rum.page_load_time_ms for rum in rum_metrics]
            avg_load_time = statistics.mean(load_times)
            load_score = max(0, 100 - (avg_load_time / 100))  # 10s = 0 score
            scores.append(('load', load_score, 0.3))
        
        # Interaction responsiveness score (20% weight)
        if interactions:
            response_times = [i.response_time_ms for i in interactions]
            avg_response_time = statistics.mean(response_times)
            interaction_score = max(0, 100 - (avg_response_time / 10))  # 1s = 0 score
            scores.append(('interaction', interaction_score, 0.2))
        
        # Error rate score (10% weight)
        if rum_metrics:
            total_errors = sum([rum.error_count for rum in rum_metrics])
            error_rate = total_errors / len(rum_metrics)
            error_score = max(0, 100 - (error_rate * 20))  # 5 errors = 0 score
            scores.append(('error', error_score, 0.1))
        
        if not scores:
            return 0.0
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in scores)
        weighted_sum = sum(score * weight for _, score, weight in scores)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def start_monitoring(self):
        """Start UX performance monitoring"""
        if self.monitoring_active:
            logger.warning("UX monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks
        tasks = [
            self._insights_analysis_loop(),
            self._session_cleanup_loop(),
            self._performance_optimization_loop()
        ]
        
        self._monitoring_tasks = [asyncio.create_task(task) for task in tasks]
        logger.info("UX performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop UX performance monitoring"""
        self.monitoring_active = False
        
        for task in self._monitoring_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        if self.geoip_reader:
            self.geoip_reader.close()
        
        self._monitoring_tasks.clear()
        logger.info("UX performance monitoring stopped")
    
    async def _insights_analysis_loop(self):
        """Performance insights analysis loop"""
        while self.monitoring_active:
            try:
                # Analyze patterns and generate insights
                await self._analyze_performance_patterns()
                await asyncio.sleep(300)  # Every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in insights analysis loop: {e}")
                await asyncio.sleep(300)
    
    async def _session_cleanup_loop(self):
        """Session cleanup loop"""
        while self.monitoring_active:
            try:
                # Clean up old sessions and data
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Clean up user journeys
                for user_id in list(self.user_journeys.keys()):
                    self.user_journeys[user_id] = [
                        journey for journey in self.user_journeys[user_id]
                        if journey['timestamp'] > cutoff_time
                    ]
                    if not self.user_journeys[user_id]:
                        del self.user_journeys[user_id]
                
                await asyncio.sleep(3600)  # Every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _performance_optimization_loop(self):
        """Performance optimization recommendations loop"""
        while self.monitoring_active:
            try:
                # Generate optimization recommendations
                await self._generate_optimization_recommendations()
                await asyncio.sleep(1800)  # Every 30 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(1800)
    
    async def _analyze_performance_patterns(self):
        """Analyze performance patterns for insights"""
        # This would implement more sophisticated pattern analysis
        # For now, we'll do basic analysis
        pass
    
    async def _generate_optimization_recommendations(self):
        """Generate performance optimization recommendations"""
        # This would implement ML-based optimization recommendations
        # For now, we'll do basic rule-based recommendations
        pass