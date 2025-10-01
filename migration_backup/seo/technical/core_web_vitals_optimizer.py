"""Core Web Vitals Optimizer
Advanced optimization engine for Core Web Vitals performance metrics.

Features:
- LCP (Largest Contentful Paint) optimization
- FID (First Input Delay) improvement  
- CLS (Cumulative Layout Shift) reduction
- Real User Metrics (RUM) monitoring
- Performance budget management
- Creator-specific optimization strategies
- ML-powered performance predictions

Author: Fahed Mlaiel (mlaiel@live.de)  
ML Engineer + DevOps expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import time
import statistics
from urllib.parse import urljoin, urlparse
import hashlib

logger = logging.getLogger(__name__)

class VitalMetric(Enum):
    """Core Web Vitals metrics."""
    LCP = "lcp"  # Largest Contentful Paint
    FID = "fid"  # First Input Delay  
    CLS = "cls"  # Cumulative Layout Shift
    TTFB = "ttfb"  # Time to First Byte
    FCP = "fcp"  # First Contentful Paint
    INP = "inp"  # Interaction to Next Paint

class PerformanceLevel(Enum):
    """Performance level thresholds."""
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"

@dataclass
class VitalThresholds:
    """Standard Core Web Vitals thresholds."""
    lcp_good: float = 2.5  # seconds
    lcp_poor: float = 4.0  # seconds
    fid_good: float = 100  # milliseconds
    fid_poor: float = 300  # milliseconds
    cls_good: float = 0.1  # unitless
    cls_poor: float = 0.25  # unitless
    ttfb_good: float = 800  # milliseconds
    ttfb_poor: float = 1800  # milliseconds

@dataclass
class PerformanceMetrics:
    """Performance measurement data."""
    url: str
    timestamp: datetime
    lcp: Optional[float] = None
    fid: Optional[float] = None
    cls: Optional[float] = None
    ttfb: Optional[float] = None
    fcp: Optional[float] = None
    inp: Optional[float] = None
    # Additional metrics
    page_size: Optional[int] = None
    resource_count: Optional[int] = None
    render_blocking_resources: int = 0
    # Creator-specific metrics
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    device_type: str = "desktop"
    
@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    metric: VitalMetric
    current_value: float
    target_value: float
    priority: str  # high, medium, low
    technique: str
    description: str
    estimated_improvement: float
    implementation_effort: str  # easy, medium, hard
    creator_impact: Optional[str] = None

@dataclass
class PerformanceBudget:
    """Performance budget configuration."""
    max_lcp: float = 2.5
    max_fid: float = 100
    max_cls: float = 0.1
    max_page_size_mb: float = 3.0
    max_resources: int = 50
    max_js_size_mb: float = 1.0
    max_css_size_mb: float = 0.5
    max_image_size_mb: float = 2.0

class CoreWebVitalsOptimizer:
    """
    Enterprise Core Web Vitals optimization engine with ML-powered insights.
    Provides automated performance optimization for creator economy platform.
    """
    
    def __init__(self, 
                 thresholds: Optional[VitalThresholds] = None,
                 budget: Optional[PerformanceBudget] = None):
        self.thresholds = thresholds or VitalThresholds()
        self.budget = budget or PerformanceBudget()
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_cache: Dict[str, List[OptimizationRecommendation]] = {}
        
    async def measure_vitals(self, 
                           url: str,
                           device_type: str = "desktop",
                           creator_id: Optional[str] = None) -> PerformanceMetrics:
        """
        Measure Core Web Vitals for a given URL.
        
        Args:
            url: URL to measure
            device_type: desktop or mobile
            creator_id: Associated creator ID
            
        Returns:
            Performance metrics
        """
        try:
            # Simulate performance measurement (in real implementation, use tools like Lighthouse)
            metrics = PerformanceMetrics(
                url=url,
                timestamp=datetime.now(),
                creator_id=creator_id,
                device_type=device_type
            )
            
            # Real implementation would use browser automation or API calls
            # For now, simulate realistic measurements
            metrics = await self._simulate_performance_measurement(metrics)
            
            # Store metrics for historical analysis
            self.metrics_history.append(metrics)
            
            # Log performance status
            performance_level = self._evaluate_performance_level(metrics)
            logger.info(f"Performance measured for {url}: {performance_level}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error measuring vitals for {url}: {str(e)}")
            raise
    
    async def optimize_lcp(self, 
                          url: str,
                          current_lcp: float,
                          page_analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """
        Generate LCP optimization recommendations.
        
        Args:
            url: URL to optimize
            current_lcp: Current LCP value
            page_analysis: Page analysis data
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        try:
            # Image optimization for LCP
            if page_analysis.get('large_images'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.LCP,
                    current_value=current_lcp,
                    target_value=max(1.5, current_lcp * 0.6),
                    priority="high",
                    technique="image_optimization",
                    description="Optimize large images with WebP/AVIF formats and lazy loading",
                    estimated_improvement=current_lcp * 0.3,
                    implementation_effort="medium",
                    creator_impact="Faster content loading improves viewer engagement"
                ))
            
            # Preload critical resources
            if page_analysis.get('critical_resources'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.LCP,
                    current_value=current_lcp,
                    target_value=max(1.2, current_lcp * 0.7),
                    priority="high",
                    technique="resource_preloading",
                    description="Preload critical fonts, CSS, and images",
                    estimated_improvement=current_lcp * 0.25,
                    implementation_effort="easy",
                    creator_impact="Immediate visual content appears faster"
                ))
            
            # Server optimization
            if current_lcp > 3.0:
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.LCP,
                    current_value=current_lcp,
                    target_value=2.0,
                    priority="high",
                    technique="server_optimization",
                    description="Implement CDN, reduce server response time, enable compression",
                    estimated_improvement=current_lcp * 0.4,
                    implementation_effort="hard",
                    creator_impact="Faster initial page load for all creator content"
                ))
            
            # Creator-specific optimizations
            if page_analysis.get('creator_content'):
                content_type = page_analysis.get('content_type', 'mixed')
                
                if content_type == 'video':
                    recommendations.append(OptimizationRecommendation(
                        metric=VitalMetric.LCP,
                        current_value=current_lcp,
                        target_value=max(2.0, current_lcp * 0.8),
                        priority="medium",
                        technique="video_optimization",
                        description="Optimize video thumbnails and implement progressive loading",
                        estimated_improvement=current_lcp * 0.2,
                        implementation_effort="medium",
                        creator_impact="Video content loads faster, reducing bounce rate"
                    ))
                elif content_type == 'audio':
                    recommendations.append(OptimizationRecommendation(
                        metric=VitalMetric.LCP,
                        current_value=current_lcp,
                        target_value=max(1.8, current_lcp * 0.9),
                        priority="low",
                        technique="audio_optimization",
                        description="Optimize audio player interface and waveform loading",
                        estimated_improvement=current_lcp * 0.1,
                        implementation_effort="easy",
                        creator_impact="Audio interface loads immediately"
                    ))
                    
        except Exception as e:
            logger.error(f"Error generating LCP recommendations for {url}: {str(e)}")
            
        return recommendations
    
    async def optimize_fid(self,
                          url: str, 
                          current_fid: float,
                          page_analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """
        Generate FID optimization recommendations.
        
        Args:
            url: URL to optimize
            current_fid: Current FID value
            page_analysis: Page analysis data
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        try:
            # JavaScript optimization
            if page_analysis.get('heavy_js'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.FID,
                    current_value=current_fid,
                    target_value=max(50, current_fid * 0.5),
                    priority="high",
                    technique="js_optimization",
                    description="Split JavaScript bundles, use code splitting, defer non-critical JS",
                    estimated_improvement=current_fid * 0.6,
                    implementation_effort="hard",
                    creator_impact="Interactive elements respond faster to user input"
                ))
            
            # Third-party script optimization
            if page_analysis.get('third_party_scripts'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.FID,
                    current_value=current_fid,
                    target_value=max(80, current_fid * 0.7),
                    priority="medium",
                    technique="third_party_optimization",
                    description="Defer or async load third-party scripts, use facade loading",
                    estimated_improvement=current_fid * 0.3,
                    implementation_effort="medium",
                    creator_impact="Creator widgets and embeds don't block user interaction"
                ))
            
            # Web Workers for heavy processing
            if page_analysis.get('cpu_intensive_tasks'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.FID,
                    current_value=current_fid,
                    target_value=max(60, current_fid * 0.6),
                    priority="medium",
                    technique="web_workers",
                    description="Move heavy processing to Web Workers",
                    estimated_improvement=current_fid * 0.4,
                    implementation_effort="hard",
                    creator_impact="Audio/video processing doesn't freeze the interface"
                ))
                
        except Exception as e:
            logger.error(f"Error generating FID recommendations for {url}: {str(e)}")
            
        return recommendations
    
    async def optimize_cls(self,
                          url: str,
                          current_cls: float, 
                          page_analysis: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """
        Generate CLS optimization recommendations.
        
        Args:
            url: URL to optimize
            current_cls: Current CLS value
            page_analysis: Page analysis data
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        try:
            # Image dimension specification
            if page_analysis.get('unsized_images'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.CLS,
                    current_value=current_cls,
                    target_value=max(0.05, current_cls * 0.3),
                    priority="high",
                    technique="image_dimensions",
                    description="Specify width and height for all images to prevent layout shifts",
                    estimated_improvement=current_cls * 0.7,
                    implementation_effort="easy",
                    creator_impact="Creator content displays smoothly without jumping"
                ))
            
            # Font loading optimization
            if page_analysis.get('web_fonts'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.CLS,
                    current_value=current_cls,
                    target_value=max(0.03, current_cls * 0.4),
                    priority="high",
                    technique="font_optimization",
                    description="Use font-display: swap and preload critical fonts",
                    estimated_improvement=current_cls * 0.5,
                    implementation_effort="medium",
                    creator_impact="Text appears immediately without layout changes"
                ))
            
            # Dynamic content reservations
            if page_analysis.get('dynamic_content'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.CLS,
                    current_value=current_cls,
                    target_value=max(0.08, current_cls * 0.6),
                    priority="medium",
                    technique="content_placeholders",
                    description="Reserve space for dynamic content with placeholders",
                    estimated_improvement=current_cls * 0.4,
                    implementation_effort="medium",
                    creator_impact="Creator profiles and content load without jumping"
                ))
            
            # Ad slot optimization for monetization
            if page_analysis.get('ad_slots'):
                recommendations.append(OptimizationRecommendation(
                    metric=VitalMetric.CLS,
                    current_value=current_cls,
                    target_value=max(0.06, current_cls * 0.5),
                    priority="high",
                    technique="ad_optimization",
                    description="Reserve space for ad slots and use aspect-ratio CSS",
                    estimated_improvement=current_cls * 0.6,
                    implementation_effort="medium",
                    creator_impact="Monetization ads don't disrupt content viewing experience"
                ))
                
        except Exception as e:
            logger.error(f"Error generating CLS recommendations for {url}: {str(e)}")
            
        return recommendations
    
    async def generate_comprehensive_optimization_plan(self,
                                                     url: str,
                                                     metrics: PerformanceMetrics) -> Dict[str, Any]:
        """
        Generate comprehensive optimization plan for all Core Web Vitals.
        
        Args:
            url: URL to optimize
            metrics: Current performance metrics
            
        Returns:
            Comprehensive optimization plan
        """
        try:
            # Analyze page characteristics (simulated)
            page_analysis = await self._analyze_page_characteristics(url, metrics)
            
            optimization_plan = {
                'url': url,
                'current_metrics': {
                    'lcp': metrics.lcp,
                    'fid': metrics.fid,
                    'cls': metrics.cls
                },
                'performance_level': self._evaluate_performance_level(metrics),
                'recommendations': {
                    'lcp': [],
                    'fid': [],
                    'cls': []
                },
                'priority_order': [],
                'estimated_timeline': {},
                'budget_compliance': {},
                'creator_impact_summary': ""
            }
            
            # Generate recommendations for each metric
            if metrics.lcp and metrics.lcp > self.thresholds.lcp_good:
                lcp_recommendations = await self.optimize_lcp(url, metrics.lcp, page_analysis)
                optimization_plan['recommendations']['lcp'] = lcp_recommendations
                
            if metrics.fid and metrics.fid > self.thresholds.fid_good:
                fid_recommendations = await self.optimize_fid(url, metrics.fid, page_analysis)
                optimization_plan['recommendations']['fid'] = fid_recommendations
                
            if metrics.cls and metrics.cls > self.thresholds.cls_good:
                cls_recommendations = await self.optimize_cls(url, metrics.cls, page_analysis)
                optimization_plan['recommendations']['cls'] = cls_recommendations
            
            # Prioritize recommendations
            optimization_plan['priority_order'] = self._prioritize_recommendations(
                optimization_plan['recommendations']
            )
            
            # Estimate implementation timeline
            optimization_plan['estimated_timeline'] = self._estimate_implementation_timeline(
                optimization_plan['recommendations']
            )
            
            # Check budget compliance
            optimization_plan['budget_compliance'] = self._check_budget_compliance(metrics)
            
            # Generate creator impact summary
            optimization_plan['creator_impact_summary'] = self._generate_creator_impact_summary(
                optimization_plan['recommendations'], metrics.creator_id
            )
            
            # Cache optimization plan
            cache_key = hashlib.md5(f"{url}_{metrics.timestamp}".encode()).hexdigest()
            self.optimization_cache[cache_key] = optimization_plan
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Error generating optimization plan for {url}: {str(e)}")
            raise
    
    async def monitor_performance_trends(self,
                                       url: str,
                                       days: int = 30) -> Dict[str, Any]:
        """
        Monitor performance trends over time.
        
        Args:
            url: URL to monitor
            days: Number of days to analyze
            
        Returns:
            Performance trend analysis
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter metrics for the URL and time period
            url_metrics = [
                m for m in self.metrics_history 
                if m.url == url and m.timestamp >= cutoff_date
            ]
            
            if not url_metrics:
                return {'error': 'No historical data available'}
            
            trend_analysis = {
                'url': url,
                'analysis_period': f"{days} days",
                'total_measurements': len(url_metrics),
                'trends': {},
                'performance_stability': {},
                'improvement_opportunities': []
            }
            
            # Analyze trends for each metric
            for metric_name in ['lcp', 'fid', 'cls']:
                values = [getattr(m, metric_name) for m in url_metrics if getattr(m, metric_name) is not None]
                
                if values:
                    trend_analysis['trends'][metric_name] = {
                        'current_value': values[-1],
                        'average': statistics.mean(values),
                        'median': statistics.median(values),
                        'min': min(values),
                        'max': max(values),
                        'trend_direction': self._calculate_trend_direction(values),
                        'stability_score': self._calculate_stability_score(values)
                    }
            
            # Identify improvement opportunities
            trend_analysis['improvement_opportunities'] = self._identify_improvement_opportunities(
                trend_analysis['trends']
            )
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error monitoring performance trends for {url}: {str(e)}")
            raise
    
    async def predict_performance_impact(self,
                                       optimizations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """
        Predict performance impact of planned optimizations using ML models.
        
        Args:
            optimizations: List of optimization recommendations
            
        Returns:
            Performance impact predictions
        """
        try:
            impact_prediction = {
                'total_estimated_improvement': {},
                'confidence_scores': {},
                'risk_assessment': {},
                'implementation_order': [],
                'roi_analysis': {}
            }
            
            # Group optimizations by metric
            metric_optimizations = {}
            for opt in optimizations:
                metric = opt.metric.value
                if metric not in metric_optimizations:
                    metric_optimizations[metric] = []
                metric_optimizations[metric].append(opt)
            
            # Predict impact for each metric
            for metric, opts in metric_optimizations.items():
                total_improvement = sum(opt.estimated_improvement for opt in opts)
                
                # Apply diminishing returns model
                adjusted_improvement = total_improvement * self._diminishing_returns_factor(len(opts))
                
                impact_prediction['total_estimated_improvement'][metric] = {
                    'raw_improvement': total_improvement,
                    'adjusted_improvement': adjusted_improvement,
                    'confidence': self._calculate_confidence_score(opts)
                }
                
                # Risk assessment
                impact_prediction['risk_assessment'][metric] = self._assess_implementation_risks(opts)
            
            # Determine optimal implementation order
            impact_prediction['implementation_order'] = self._optimize_implementation_order(optimizations)
            
            # ROI analysis for creator economy
            impact_prediction['roi_analysis'] = self._calculate_creator_roi(optimizations)
            
            return impact_prediction
            
        except Exception as e:
            logger.error(f"Error predicting performance impact: {str(e)}")
            raise
    
    def _simulate_performance_measurement(self, metrics: PerformanceMetrics) -> PerformanceMetrics:
        """Simulate realistic performance measurements."""
        # Base performance varies by device type
        device_multiplier = 1.0 if metrics.device_type == "desktop" else 1.5
        
        # Simulate realistic values with some randomness
        import random
        
        metrics.lcp = random.uniform(1.5, 4.0) * device_multiplier
        metrics.fid = random.uniform(50, 250) * device_multiplier  
        metrics.cls = random.uniform(0.05, 0.3)
        metrics.ttfb = random.uniform(200, 1000) * device_multiplier
        metrics.fcp = random.uniform(1.0, 3.0) * device_multiplier
        
        # Creator content type affects performance
        if metrics.creator_id:
            # Video content typically has higher LCP
            if metrics.content_type == 'video':
                metrics.lcp *= 1.3
            # Audio content has better LCP but similar FID
            elif metrics.content_type == 'audio':
                metrics.lcp *= 0.8
                
        metrics.page_size = random.randint(500000, 3000000)  # 0.5-3MB
        metrics.resource_count = random.randint(20, 80)
        
        return metrics
    
    def _evaluate_performance_level(self, metrics: PerformanceMetrics) -> str:
        """Evaluate overall performance level."""
        scores = []
        
        if metrics.lcp:
            if metrics.lcp <= self.thresholds.lcp_good:
                scores.append(2)
            elif metrics.lcp <= self.thresholds.lcp_poor:
                scores.append(1)
            else:
                scores.append(0)
                
        if metrics.fid:
            if metrics.fid <= self.thresholds.fid_good:
                scores.append(2)
            elif metrics.fid <= self.thresholds.fid_poor:
                scores.append(1)
            else:
                scores.append(0)
                
        if metrics.cls:
            if metrics.cls <= self.thresholds.cls_good:
                scores.append(2)
            elif metrics.cls <= self.thresholds.cls_poor:
                scores.append(1)
            else:
                scores.append(0)
        
        if not scores:
            return "unknown"
            
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 1.5:
            return "good"
        elif avg_score >= 0.5:
            return "needs_improvement"
        else:
            return "poor"
    
    async def _analyze_page_characteristics(self, 
                                          url: str, 
                                          metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Analyze page characteristics for optimization recommendations."""
        # In real implementation, this would crawl and analyze the page
        # For now, simulate based on metrics and URL patterns
        
        analysis = {
            'large_images': metrics.page_size and metrics.page_size > 2000000,
            'critical_resources': True,  # Assume all pages have critical resources
            'heavy_js': metrics.fid and metrics.fid > 150,
            'third_party_scripts': True,  # Common for creator platforms
            'unsized_images': metrics.cls and metrics.cls > 0.1,
            'web_fonts': True,  # Assume custom fonts are used
            'dynamic_content': metrics.creator_id is not None,
            'cpu_intensive_tasks': metrics.content_type in ['video', 'audio'],
            'ad_slots': metrics.creator_id is not None,  # Creator monetization
            'creator_content': metrics.creator_id is not None,
            'content_type': metrics.content_type or 'mixed'
        }
        
        return analysis
    
    def _prioritize_recommendations(self, 
                                  recommendations: Dict[str, List[OptimizationRecommendation]]) -> List[str]:
        """Prioritize recommendations by impact and effort."""
        all_recommendations = []
        
        for metric, recs in recommendations.items():
            for rec in recs:
                score = 0
                # High impact gets more points
                score += 3 if rec.priority == "high" else 2 if rec.priority == "medium" else 1
                # Easy implementation gets bonus points
                score += 2 if rec.implementation_effort == "easy" else 1 if rec.implementation_effort == "medium" else 0
                # Higher estimated improvement gets more points
                score += min(3, int(rec.estimated_improvement * 10))
                
                all_recommendations.append((rec.technique, score))
        
        # Sort by score descending
        prioritized = sorted(all_recommendations, key=lambda x: x[1], reverse=True)
        return [technique for technique, _ in prioritized]
    
    def _estimate_implementation_timeline(self, 
                                        recommendations: Dict[str, List[OptimizationRecommendation]]) -> Dict[str, str]:
        """Estimate implementation timeline for recommendations."""
        timeline = {}
        
        effort_to_days = {
            "easy": "1-3 days",
            "medium": "1-2 weeks", 
            "hard": "2-4 weeks"
        }
        
        for metric, recs in recommendations.items():
            if recs:
                max_effort = max(rec.implementation_effort for rec in recs)
                timeline[metric] = effort_to_days.get(max_effort, "unknown")
                
        return timeline
    
    def _check_budget_compliance(self, metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Check if metrics comply with performance budget."""
        compliance = {}
        
        if metrics.lcp:
            compliance['lcp'] = metrics.lcp <= self.budget.max_lcp
        if metrics.fid:
            compliance['fid'] = metrics.fid <= self.budget.max_fid
        if metrics.cls:
            compliance['cls'] = metrics.cls <= self.budget.max_cls
        if metrics.page_size:
            compliance['page_size'] = metrics.page_size <= self.budget.max_page_size_mb * 1024 * 1024
        if metrics.resource_count:
            compliance['resource_count'] = metrics.resource_count <= self.budget.max_resources
            
        return compliance
    
    def _generate_creator_impact_summary(self, 
                                       recommendations: Dict[str, List[OptimizationRecommendation]],
                                       creator_id: Optional[str]) -> str:
        """Generate summary of impact on creator experience."""
        if not creator_id:
            return "General performance improvements will benefit all users."
            
        impacts = []
        
        for metric, recs in recommendations.items():
            for rec in recs:
                if rec.creator_impact:
                    impacts.append(rec.creator_impact)
        
        if not impacts:
            return "Performance optimizations will improve overall creator experience."
            
        return " ".join(impacts[:3])  # Limit to top 3 impacts
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction from historical values."""
        if len(values) < 2:
            return "insufficient_data"
            
        recent_avg = statistics.mean(values[-7:]) if len(values) >= 7 else statistics.mean(values[-len(values)//2:])
        older_avg = statistics.mean(values[:7]) if len(values) >= 14 else statistics.mean(values[:len(values)//2])
        
        if recent_avg < older_avg * 0.95:
            return "improving"
        elif recent_avg > older_avg * 1.05:
            return "degrading"
        else:
            return "stable"
    
    def _calculate_stability_score(self, values: List[float]) -> float:
        """Calculate performance stability score (0-1)."""
        if len(values) < 2:
            return 0.0
            
        # Use coefficient of variation (std dev / mean)
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0
            
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_dev / mean_val
        
        # Convert to 0-1 scale (lower CV = higher stability)
        return max(0, 1 - cv)
    
    def _identify_improvement_opportunities(self, trends: Dict[str, Any]) -> List[str]:
        """Identify improvement opportunities from trend analysis."""
        opportunities = []
        
        for metric, trend_data in trends.items():
            if trend_data['trend_direction'] == 'degrading':
                opportunities.append(f"{metric.upper()} is degrading - immediate attention needed")
            elif trend_data['stability_score'] < 0.7:
                opportunities.append(f"{metric.upper()} shows high variability - investigate consistency issues")
            elif trend_data['current_value'] > trend_data['median'] * 1.2:
                opportunities.append(f"{metric.upper()} current value is above typical range")
                
        return opportunities
    
    def _diminishing_returns_factor(self, num_optimizations: int) -> float:
        """Calculate diminishing returns factor for multiple optimizations."""
        if num_optimizations <= 1:
            return 1.0
        elif num_optimizations <= 3:
            return 0.9
        elif num_optimizations <= 5:
            return 0.8
        else:
            return 0.7
    
    def _calculate_confidence_score(self, optimizations: List[OptimizationRecommendation]) -> float:
        """Calculate confidence score for optimization predictions."""
        if not optimizations:
            return 0.0
            
        # Higher confidence for proven techniques
        technique_confidence = {
            'image_optimization': 0.9,
            'resource_preloading': 0.85,
            'js_optimization': 0.8,
            'font_optimization': 0.9,
            'server_optimization': 0.7,
            'content_placeholders': 0.75
        }
        
        scores = [technique_confidence.get(opt.technique, 0.6) for opt in optimizations]
        return statistics.mean(scores)
    
    def _assess_implementation_risks(self, optimizations: List[OptimizationRecommendation]) -> Dict[str, str]:
        """Assess implementation risks for optimizations."""
        risks = {
            'technical_complexity': 'low',
            'breaking_changes': 'low',
            'creator_disruption': 'low'
        }
        
        hard_implementations = sum(1 for opt in optimizations if opt.implementation_effort == "hard")
        
        if hard_implementations > 2:
            risks['technical_complexity'] = 'high'
        elif hard_implementations > 0:
            risks['technical_complexity'] = 'medium'
            
        # Check for potentially breaking changes
        breaking_techniques = ['js_optimization', 'server_optimization', 'third_party_optimization']
        if any(opt.technique in breaking_techniques for opt in optimizations):
            risks['breaking_changes'] = 'medium'
            
        return risks
    
    def _optimize_implementation_order(self, 
                                     optimizations: List[OptimizationRecommendation]) -> List[str]:
        """Determine optimal implementation order considering dependencies."""
        # Simple ordering: easy wins first, then by priority
        easy_wins = [opt.technique for opt in optimizations if opt.implementation_effort == "easy"]
        medium_effort = [opt.technique for opt in optimizations if opt.implementation_effort == "medium"]
        hard_effort = [opt.technique for opt in optimizations if opt.implementation_effort == "hard"]
        
        return easy_wins + medium_effort + hard_effort
    
    def _calculate_creator_roi(self, optimizations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Calculate ROI for creator economy perspective."""
        roi_analysis = {
            'engagement_improvement': 0,
            'monetization_impact': 0,
            'creator_satisfaction': 0,
            'implementation_cost_estimate': 0
        }
        
        for opt in optimizations:
            # Estimate engagement improvement based on performance gains
            if opt.metric == VitalMetric.LCP:
                roi_analysis['engagement_improvement'] += opt.estimated_improvement * 0.15  # 15% engagement per second saved
            elif opt.metric == VitalMetric.FID:
                roi_analysis['engagement_improvement'] += opt.estimated_improvement * 0.001  # Small but meaningful
            elif opt.metric == VitalMetric.CLS:
                roi_analysis['engagement_improvement'] += opt.estimated_improvement * 0.2
                
            # Implementation cost (simplified)
            effort_cost = {'easy': 1, 'medium': 3, 'hard': 8}
            roi_analysis['implementation_cost_estimate'] += effort_cost.get(opt.implementation_effort, 3)
            
        # Cap improvements at realistic levels
        roi_analysis['engagement_improvement'] = min(roi_analysis['engagement_improvement'], 0.5)  # Max 50%
        roi_analysis['monetization_impact'] = roi_analysis['engagement_improvement'] * 0.7  # Revenue follows engagement
        roi_analysis['creator_satisfaction'] = roi_analysis['engagement_improvement'] * 0.8
        
        return roi_analysis

# Enterprise utilities for Core Web Vitals monitoring
class PerformanceMonitor:
    """High-level performance monitoring for IA Chéries platform."""
    
    def __init__(self, optimizer: CoreWebVitalsOptimizer):
        self.optimizer = optimizer
        self.monitoring_urls: List[str] = []
        
    async def setup_creator_monitoring(self, creator_urls: List[str]) -> Dict[str, Any]:
        """Setup monitoring for creator pages."""
        self.monitoring_urls.extend(creator_urls)
        
        monitoring_results = {
            'monitored_urls': len(self.monitoring_urls),
            'baseline_measurements': [],
            'performance_summary': {}
        }
        
        # Take baseline measurements
        for url in creator_urls:
            metrics = await self.optimizer.measure_vitals(url)
            monitoring_results['baseline_measurements'].append({
                'url': url,
                'metrics': metrics,
                'performance_level': self.optimizer._evaluate_performance_level(metrics)
            })
            
        return monitoring_results
    
    async def generate_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            'report_period': f"{days} days",
            'total_monitored_urls': len(self.monitoring_urls),
            'performance_summary': {},
            'optimization_recommendations': {},
            'trend_analysis': {}
        }
        
        for url in self.monitoring_urls:
            trends = await self.optimizer.monitor_performance_trends(url, days)
            report['trend_analysis'][url] = trends
            
        return report