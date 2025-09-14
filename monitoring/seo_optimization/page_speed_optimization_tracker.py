"""
Page Speed Optimization Tracker - Enterprise Web Performance Monitoring

This module implements comprehensive page speed optimization tracking for the Ainflue platform,
monitoring Core Web Vitals, performance metrics, and automated optimization recommendations.

Author: Fahed Mlaiel
Role: Lead Dev IA + Performance Engineer + Web Optimization Expert + DevOps Engineer
Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import requests
import time
from urllib.parse import urlparse
import subprocess
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Core Web Vitals and performance metrics"""
    LARGEST_CONTENTFUL_PAINT = "lcp"  # LCP
    FIRST_INPUT_DELAY = "fid"         # FID
    CUMULATIVE_LAYOUT_SHIFT = "cls"   # CLS
    FIRST_CONTENTFUL_PAINT = "fcp"    # FCP
    TIME_TO_INTERACTIVE = "tti"       # TTI
    TOTAL_BLOCKING_TIME = "tbt"       # TBT
    SPEED_INDEX = "si"                # SI

class PerformanceGrade(Enum):
    """Performance grade classification"""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 75-89
    NEEDS_IMPROVEMENT = "needs_improvement"  # 50-74
    POOR = "poor"           # 0-49

class OptimizationType(Enum):
    """Types of optimization recommendations"""
    IMAGE_OPTIMIZATION = "image_optimization"
    CODE_SPLITTING = "code_splitting"
    RESOURCE_COMPRESSION = "resource_compression"
    CACHING_STRATEGY = "caching_strategy"
    CDN_OPTIMIZATION = "cdn_optimization"
    MINIFICATION = "minification"
    LAZY_LOADING = "lazy_loading"
    CRITICAL_CSS = "critical_css"
    PRELOADING = "preloading"
    SERVER_OPTIMIZATION = "server_optimization"

@dataclass
class CoreWebVitals:
    """Core Web Vitals measurements"""
    lcp: float  # Largest Contentful Paint (seconds)
    fid: float  # First Input Delay (milliseconds)
    cls: float  # Cumulative Layout Shift (score)
    fcp: float  # First Contentful Paint (seconds)
    tti: float  # Time to Interactive (seconds)
    tbt: float  # Total Blocking Time (milliseconds)
    si: float   # Speed Index (score)

@dataclass
class PerformanceTest:
    """Performance test result"""
    test_id: str
    url: str
    timestamp: datetime
    device_type: str  # desktop, mobile, tablet
    connection_type: str  # 4g, 3g, slow-3g, wifi
    core_web_vitals: CoreWebVitals
    performance_score: float
    performance_grade: PerformanceGrade
    opportunities: List[Dict[str, Any]]
    diagnostics: List[Dict[str, Any]]
    resource_summary: Dict[str, Any]
    lab_data: Dict[str, Any]
    field_data: Optional[Dict[str, Any]]

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    recommendation_id: str
    url: str
    optimization_type: OptimizationType
    priority: str  # critical, high, medium, low
    title: str
    description: str
    potential_savings: float  # seconds
    implementation_effort: str  # easy, medium, hard
    technical_details: Dict[str, Any]
    code_examples: List[str]
    tools_required: List[str]
    estimated_impact: float  # 0-1 scale

class PageSpeedOptimizationTracker:
    """
    Enterprise page speed optimization tracking system for Ainflue platform.
    
    Features:
    - Core Web Vitals monitoring
    - Real User Monitoring (RUM) integration
    - Automated performance testing
    - Progressive Web App (PWA) optimization
    - Resource optimization tracking
    - Performance budget monitoring
    - Competitive performance analysis
    - Automated optimization recommendations
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize page speed optimization tracker"""
        self.config = config or {}
        self.performance_tests: Dict[str, List[PerformanceTest]] = {}
        self.optimization_recommendations: Dict[str, List[OptimizationRecommendation]] = {}
        self.performance_budgets: Dict[str, Dict[str, float]] = {}
        self.monitoring_endpoints: List[str] = []
        
        # Performance thresholds (Core Web Vitals)
        self.cwv_thresholds = {
            "lcp": {"good": 2.5, "needs_improvement": 4.0},
            "fid": {"good": 100, "needs_improvement": 300},
            "cls": {"good": 0.1, "needs_improvement": 0.25},
            "fcp": {"good": 1.8, "needs_improvement": 3.0},
            "tti": {"good": 3.8, "needs_improvement": 7.3},
            "tbt": {"good": 200, "needs_improvement": 600},
            "si": {"good": 3.4, "needs_improvement": 5.8}
        }
        
        # Initialize tracking system
        self._initialize_performance_tracking()
        logger.info("Page Speed Optimization Tracker initialized")
    
    def _initialize_performance_tracking(self) -> None:
        """Initialize performance tracking components"""
        try:
            # Setup performance testing tools
            self._setup_performance_tools()
            
            # Initialize monitoring configuration
            self._setup_monitoring_config()
            
            # Setup optimization analyzers
            self._setup_optimization_analyzers()
            
            # Initialize performance budgets
            self._setup_performance_budgets()
            
            logger.info("Performance tracking initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance tracking: {e}")
            raise
    
    def _setup_performance_tools(self) -> None:
        """Setup performance testing tools configuration"""
        self.tools_config = {
            "lighthouse": {
                "strategy": "desktop",
                "categories": ["performance", "accessibility", "best-practices", "seo"],
                "throttling": "simulated3G"
            },
            "pagespeed_insights": {
                "api_key": self.config.get("pagespeed_api_key", ""),
                "strategy": "mobile"
            },
            "webpagetest": {
                "api_key": self.config.get("webpagetest_api_key", ""),
                "location": "Dulles:Chrome",
                "connectivity": "3G"
            },
            "gtmetrix": {
                "api_key": self.config.get("gtmetrix_api_key", ""),
                "location": "vancouver",
                "browser": "chrome"
            }
        }
    
    def _setup_monitoring_config(self) -> None:
        """Setup continuous monitoring configuration"""
        self.monitoring_config = {
            "test_frequency": 3600,  # Test every hour
            "devices": ["desktop", "mobile"],
            "connections": ["4g", "3g", "slow-3g"],
            "locations": ["us-east", "us-west", "europe", "asia"],
            "real_user_monitoring": True,
            "synthetic_monitoring": True
        }
    
    def _setup_optimization_analyzers(self) -> None:
        """Setup optimization analysis algorithms"""
        self.optimization_analyzers = {
            "image_optimization": {
                "formats": ["webp", "avif", "jpeg", "png"],
                "compression_levels": [80, 85, 90, 95],
                "responsive_images": True,
                "lazy_loading": True
            },
            "code_optimization": {
                "minification": ["html", "css", "js"],
                "tree_shaking": True,
                "code_splitting": True,
                "bundle_analysis": True
            },
            "resource_optimization": {
                "compression": ["gzip", "brotli"],
                "caching_strategies": ["browser", "cdn", "service_worker"],
                "preloading": ["critical_resources", "above_fold"]
            }
        }
    
    def _setup_performance_budgets(self) -> None:
        """Setup default performance budgets"""
        self.default_budgets = {
            "desktop": {
                "lcp": 2.0,      # seconds
                "fid": 50,       # milliseconds
                "cls": 0.05,     # score
                "fcp": 1.5,      # seconds
                "tti": 3.0,      # seconds
                "performance_score": 85
            },
            "mobile": {
                "lcp": 2.5,      # seconds
                "fid": 100,      # milliseconds
                "cls": 0.1,      # score
                "fcp": 1.8,      # seconds
                "tti": 3.8,      # seconds
                "performance_score": 80
            }
        }
    
    async def run_performance_test(self, url: str, device_type: str = "mobile", test_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run comprehensive performance test for URL
        
        Args:
            url: URL to test
            device_type: Device type (desktop, mobile, tablet)
            test_options: Additional test configuration
            
        Returns:
            Comprehensive performance test results
        """
        try:
            test_options = test_options or {}
            
            # Run multiple performance tests
            lighthouse_result = await self._run_lighthouse_test(url, device_type, test_options)
            pagespeed_result = await self._run_pagespeed_test(url, device_type)
            
            # Analyze Core Web Vitals
            core_web_vitals = self._extract_core_web_vitals(lighthouse_result)
            
            # Calculate performance score and grade
            performance_score = self._calculate_performance_score(core_web_vitals)
            performance_grade = self._classify_performance_grade(performance_score)
            
            # Generate optimization opportunities
            opportunities = await self._analyze_optimization_opportunities(lighthouse_result, core_web_vitals)
            
            # Extract diagnostics
            diagnostics = self._extract_diagnostics(lighthouse_result)
            
            # Analyze resource summary
            resource_summary = self._analyze_resource_summary(lighthouse_result)
            
            # Get field data (Real User Monitoring)
            field_data = await self._get_field_data(url)
            
            # Create performance test record
            test = PerformanceTest(
                test_id=f"test_{int(time.time())}",
                url=url,
                timestamp=datetime.now(),
                device_type=device_type,
                connection_type=test_options.get("connection", "4g"),
                core_web_vitals=core_web_vitals,
                performance_score=performance_score,
                performance_grade=performance_grade,
                opportunities=opportunities,
                diagnostics=diagnostics,
                resource_summary=resource_summary,
                lab_data=lighthouse_result,
                field_data=field_data
            )
            
            # Store test result
            if url not in self.performance_tests:
                self.performance_tests[url] = []
            self.performance_tests[url].append(test)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(test)
            
            # Check performance budget compliance
            budget_analysis = await self._check_performance_budget(test)
            
            result = {
                "test_id": test.test_id,
                "url": url,
                "device_type": device_type,
                "performance_summary": {
                    "score": performance_score,
                    "grade": performance_grade.value,
                    "core_web_vitals": asdict(core_web_vitals),
                    "budget_compliance": budget_analysis
                },
                "optimization_opportunities": opportunities[:10],  # Top 10
                "recommendations": recommendations[:5],  # Top 5
                "resource_analysis": resource_summary,
                "historical_trend": await self._calculate_performance_trend(url),
                "competitive_analysis": await self._get_competitive_analysis(url),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Performance test completed for {url}: {performance_score:.1f} score, {performance_grade.value} grade")
            return result
            
        except Exception as e:
            logger.error(f"Failed to run performance test for {url}: {e}")
            return {"error": str(e)}
    
    async def _run_lighthouse_test(self, url: str, device_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Run Lighthouse performance test"""
        # Simulate Lighthouse test results
        # In a real implementation, this would use the Lighthouse CLI or API
        
        # Simulate realistic Core Web Vitals based on typical performance
        base_lcp = np.random.uniform(1.5, 4.0)
        base_fid = np.random.uniform(50, 200)
        base_cls = np.random.uniform(0.05, 0.25)
        
        # Adjust for device type
        if device_type == "mobile":
            base_lcp *= 1.2
            base_fid *= 1.1
            base_cls *= 1.1
        
        lighthouse_result = {
            "categories": {
                "performance": {"score": np.random.uniform(0.6, 0.95)},
                "accessibility": {"score": np.random.uniform(0.8, 0.98)},
                "best-practices": {"score": np.random.uniform(0.75, 0.95)},
                "seo": {"score": np.random.uniform(0.85, 0.98)}
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": base_lcp * 1000},
                "first-input-delay": {"numericValue": base_fid},
                "cumulative-layout-shift": {"numericValue": base_cls},
                "first-contentful-paint": {"numericValue": (base_lcp * 0.6) * 1000},
                "interactive": {"numericValue": (base_lcp * 1.5) * 1000},
                "total-blocking-time": {"numericValue": base_fid * 2},
                "speed-index": {"numericValue": (base_lcp * 1.2) * 1000},
                "unused-css-rules": {
                    "numericValue": np.random.uniform(0, 500),
                    "details": {"overallSavingsMs": np.random.uniform(100, 1000)}
                },
                "unused-javascript": {
                    "numericValue": np.random.uniform(0, 800),
                    "details": {"overallSavingsMs": np.random.uniform(200, 1500)}
                },
                "modern-image-formats": {
                    "numericValue": np.random.uniform(0, 300),
                    "details": {"overallSavingsBytes": np.random.uniform(50000, 500000)}
                },
                "efficient-animated-content": {
                    "numericValue": np.random.uniform(0, 200),
                    "details": {"overallSavingsBytes": np.random.uniform(20000, 200000)}
                }
            }
        }
        
        return lighthouse_result
    
    async def _run_pagespeed_test(self, url: str, device_type: str) -> Dict[str, Any]:
        """Run PageSpeed Insights test"""
        # Simulate PageSpeed Insights API call
        # In a real implementation, this would call the actual API
        
        pagespeed_result = {
            "loadingExperience": {
                "metrics": {
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": np.random.uniform(2000, 4000)},
                    "FIRST_INPUT_DELAY_MS": {"percentile": np.random.uniform(50, 150)},
                    "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": np.random.uniform(0.05, 0.2)}
                },
                "overall_category": "AVERAGE"
            },
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": np.random.uniform(0.6, 0.9)}
                }
            }
        }
        
        return pagespeed_result
    
    def _extract_core_web_vitals(self, lighthouse_result: Dict[str, Any]) -> CoreWebVitals:
        """Extract Core Web Vitals from Lighthouse results"""
        audits = lighthouse_result.get("audits", {})
        
        return CoreWebVitals(
            lcp=audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
            fid=audits.get("first-input-delay", {}).get("numericValue", 0),
            cls=audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
            fcp=audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000,
            tti=audits.get("interactive", {}).get("numericValue", 0) / 1000,
            tbt=audits.get("total-blocking-time", {}).get("numericValue", 0),
            si=audits.get("speed-index", {}).get("numericValue", 0) / 1000
        )
    
    def _calculate_performance_score(self, cwv: CoreWebVitals) -> float:
        """Calculate overall performance score based on Core Web Vitals"""
        # Weight factors for different metrics
        weights = {
            "lcp": 0.25,
            "fid": 0.25,
            "cls": 0.25,
            "fcp": 0.10,
            "tti": 0.10,
            "si": 0.05
        }
        
        # Calculate individual scores
        scores = {}
        
        # LCP Score
        if cwv.lcp <= self.cwv_thresholds["lcp"]["good"]:
            scores["lcp"] = 100
        elif cwv.lcp <= self.cwv_thresholds["lcp"]["needs_improvement"]:
            scores["lcp"] = 75
        else:
            scores["lcp"] = 25
        
        # FID Score
        if cwv.fid <= self.cwv_thresholds["fid"]["good"]:
            scores["fid"] = 100
        elif cwv.fid <= self.cwv_thresholds["fid"]["needs_improvement"]:
            scores["fid"] = 75
        else:
            scores["fid"] = 25
        
        # CLS Score
        if cwv.cls <= self.cwv_thresholds["cls"]["good"]:
            scores["cls"] = 100
        elif cwv.cls <= self.cwv_thresholds["cls"]["needs_improvement"]:
            scores["cls"] = 75
        else:
            scores["cls"] = 25
        
        # FCP Score
        if cwv.fcp <= self.cwv_thresholds["fcp"]["good"]:
            scores["fcp"] = 100
        elif cwv.fcp <= self.cwv_thresholds["fcp"]["needs_improvement"]:
            scores["fcp"] = 75
        else:
            scores["fcp"] = 25
        
        # TTI Score
        if cwv.tti <= self.cwv_thresholds["tti"]["good"]:
            scores["tti"] = 100
        elif cwv.tti <= self.cwv_thresholds["tti"]["needs_improvement"]:
            scores["tti"] = 75
        else:
            scores["tti"] = 25
        
        # SI Score  
        if cwv.si <= self.cwv_thresholds["si"]["good"]:
            scores["si"] = 100
        elif cwv.si <= self.cwv_thresholds["si"]["needs_improvement"]:
            scores["si"] = 75
        else:
            scores["si"] = 25
        
        # Calculate weighted average
        overall_score = sum(scores[metric] * weights[metric] for metric in weights.keys())
        
        return overall_score
    
    def _classify_performance_grade(self, score: float) -> PerformanceGrade:
        """Classify performance grade based on score"""
        if score >= 90:
            return PerformanceGrade.EXCELLENT
        elif score >= 75:
            return PerformanceGrade.GOOD
        elif score >= 50:
            return PerformanceGrade.NEEDS_IMPROVEMENT
        else:
            return PerformanceGrade.POOR
    
    async def _analyze_optimization_opportunities(self, lighthouse_result: Dict[str, Any], cwv: CoreWebVitals) -> List[Dict[str, Any]]:
        """Analyze optimization opportunities from test results"""
        opportunities = []
        audits = lighthouse_result.get("audits", {})
        
        # Image optimization opportunities
        if "modern-image-formats" in audits:
            audit = audits["modern-image-formats"]
            savings_bytes = audit.get("details", {}).get("overallSavingsBytes", 0)
            if savings_bytes > 10000:  # 10KB threshold
                opportunities.append({
                    "type": OptimizationType.IMAGE_OPTIMIZATION.value,
                    "title": "Serve images in modern formats",
                    "description": "Use WebP or AVIF for better compression",
                    "potential_savings_bytes": savings_bytes,
                    "potential_savings_ms": savings_bytes / 1000,  # Rough estimate
                    "priority": "high" if savings_bytes > 100000 else "medium",
                    "implementation": "Convert images to WebP/AVIF format"
                })
        
        # Unused CSS opportunities
        if "unused-css-rules" in audits:
            audit = audits["unused-css-rules"]
            savings_ms = audit.get("details", {}).get("overallSavingsMs", 0)
            if savings_ms > 100:
                opportunities.append({
                    "type": OptimizationType.CODE_SPLITTING.value,
                    "title": "Remove unused CSS",
                    "description": "Remove or defer non-critical CSS",
                    "potential_savings_ms": savings_ms,
                    "priority": "high" if savings_ms > 500 else "medium",
                    "implementation": "Implement critical CSS and defer non-critical styles"
                })
        
        # Unused JavaScript opportunities
        if "unused-javascript" in audits:
            audit = audits["unused-javascript"]
            savings_ms = audit.get("details", {}).get("overallSavingsMs", 0)
            if savings_ms > 200:
                opportunities.append({
                    "type": OptimizationType.CODE_SPLITTING.value,
                    "title": "Remove unused JavaScript",
                    "description": "Split code and load only what's needed",
                    "potential_savings_ms": savings_ms,
                    "priority": "high" if savings_ms > 1000 else "medium",
                    "implementation": "Implement code splitting and tree shaking"
                })
        
        # LCP optimization
        if cwv.lcp > self.cwv_thresholds["lcp"]["good"]:
            opportunities.append({
                "type": OptimizationType.PRELOADING.value,
                "title": "Optimize Largest Contentful Paint",
                "description": "Preload critical resources and optimize largest element",
                "potential_savings_ms": (cwv.lcp - self.cwv_thresholds["lcp"]["good"]) * 1000,
                "priority": "critical",
                "implementation": "Preload LCP image/resource, optimize server response time"
            })
        
        # CLS optimization
        if cwv.cls > self.cwv_thresholds["cls"]["good"]:
            opportunities.append({
                "type": OptimizationType.LAZY_LOADING.value,
                "title": "Reduce Cumulative Layout Shift",
                "description": "Reserve space for images and ads, avoid layout shifts",
                "potential_savings_score": cwv.cls - self.cwv_thresholds["cls"]["good"],
                "priority": "high",
                "implementation": "Set image dimensions, reserve space for dynamic content"
            })
        
        # Sort by potential impact
        opportunities.sort(key=lambda x: x.get("potential_savings_ms", 0), reverse=True)
        
        return opportunities
    
    def _extract_diagnostics(self, lighthouse_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract performance diagnostics"""
        diagnostics = []
        audits = lighthouse_result.get("audits", {})
        
        # Common diagnostic audits
        diagnostic_audits = [
            "server-response-time",
            "dom-size",
            "critical-request-chains",
            "uses-text-compression",
            "uses-rel-preconnect",
            "font-display",
            "third-party-summary"
        ]
        
        for audit_name in diagnostic_audits:
            if audit_name in audits:
                audit = audits[audit_name]
                diagnostics.append({
                    "audit": audit_name,
                    "score": audit.get("score", 0),
                    "displayValue": audit.get("displayValue", ""),
                    "description": audit.get("description", "")
                })
        
        return diagnostics
    
    def _analyze_resource_summary(self, lighthouse_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resource summary from test results"""
        # Simulate resource analysis
        # In a real implementation, this would parse actual Lighthouse resource data
        
        return {
            "total_bytes": np.random.randint(500000, 3000000),
            "image_bytes": np.random.randint(200000, 1500000),
            "script_bytes": np.random.randint(100000, 800000),
            "stylesheet_bytes": np.random.randint(50000, 300000),
            "font_bytes": np.random.randint(20000, 150000),
            "other_bytes": np.random.randint(30000, 100000),
            "total_requests": np.random.randint(20, 100),
            "image_requests": np.random.randint(5, 40),
            "script_requests": np.random.randint(3, 20),
            "stylesheet_requests": np.random.randint(2, 10),
            "font_requests": np.random.randint(1, 8),
            "other_requests": np.random.randint(5, 25)
        }
    
    async def _get_field_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get field data (Real User Monitoring) for URL"""
        # Simulate Chrome UX Report data
        # In a real implementation, this would query the CrUX API
        
        return {
            "origin_fallback": False,
            "metrics": {
                "largest_contentful_paint": {
                    "histogram": [
                        {"start": 0, "end": 2500, "density": 0.6},
                        {"start": 2500, "end": 4000, "density": 0.3},
                        {"start": 4000, "density": 0.1}
                    ],
                    "percentiles": {
                        "p75": np.random.uniform(2000, 3500)
                    }
                },
                "first_input_delay": {
                    "histogram": [
                        {"start": 0, "end": 100, "density": 0.8},
                        {"start": 100, "end": 300, "density": 0.15},
                        {"start": 300, "density": 0.05}
                    ],
                    "percentiles": {
                        "p75": np.random.uniform(50, 150)
                    }
                },
                "cumulative_layout_shift": {
                    "histogram": [
                        {"start": 0, "end": 0.1, "density": 0.7},
                        {"start": 0.1, "end": 0.25, "density": 0.2},
                        {"start": 0.25, "density": 0.1}
                    ],
                    "percentiles": {
                        "p75": np.random.uniform(0.05, 0.15)
                    }
                }
            }
        }
    
    async def _generate_optimization_recommendations(self, test: PerformanceTest) -> List[OptimizationRecommendation]:
        """Generate specific optimization recommendations"""
        recommendations = []
        cwv = test.core_web_vitals
        
        # LCP optimization
        if cwv.lcp > self.cwv_thresholds["lcp"]["good"]:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"lcp_opt_{test.test_id}",
                url=test.url,
                optimization_type=OptimizationType.PRELOADING,
                priority="critical" if cwv.lcp > 4.0 else "high",
                title="Optimize Largest Contentful Paint",
                description="Improve LCP by preloading critical resources and optimizing the largest element",
                potential_savings=(cwv.lcp - self.cwv_thresholds["lcp"]["good"]),
                implementation_effort="medium",
                technical_details={
                    "current_lcp": cwv.lcp,
                    "target_lcp": self.cwv_thresholds["lcp"]["good"],
                    "optimization_areas": ["preload_critical_resources", "optimize_server_response", "optimize_images"]
                },
                code_examples=[
                    '<link rel="preload" href="hero-image.jpg" as="image">',
                    '<link rel="preconnect" href="https://fonts.googleapis.com">'
                ],
                tools_required=["Lighthouse", "WebPageTest", "Chrome DevTools"],
                estimated_impact=0.8
            ))
        
        # CLS optimization
        if cwv.cls > self.cwv_thresholds["cls"]["good"]:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"cls_opt_{test.test_id}",
                url=test.url,
                optimization_type=OptimizationType.LAZY_LOADING,
                priority="high",
                title="Reduce Cumulative Layout Shift",
                description="Prevent layout shifts by reserving space for dynamic content",
                potential_savings=cwv.cls - self.cwv_thresholds["cls"]["good"],
                implementation_effort="easy",
                technical_details={
                    "current_cls": cwv.cls,
                    "target_cls": self.cwv_thresholds["cls"]["good"],
                    "common_causes": ["images_without_dimensions", "dynamic_ads", "web_fonts"]
                },
                code_examples=[
                    '<img src="image.jpg" width="400" height="300" alt="Description">',
                    'img { aspect-ratio: 16 / 9; }'
                ],
                tools_required=["Chrome DevTools", "Layout Shift GIF Generator"],
                estimated_impact=0.9
            ))
        
        # FID optimization
        if cwv.fid > self.cwv_thresholds["fid"]["good"]:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"fid_opt_{test.test_id}",
                url=test.url,
                optimization_type=OptimizationType.CODE_SPLITTING,
                priority="high",
                title="Improve First Input Delay",
                description="Reduce JavaScript execution time and improve interactivity",
                potential_savings=(cwv.fid - self.cwv_thresholds["fid"]["good"]) / 1000,
                implementation_effort="hard",
                technical_details={
                    "current_fid": cwv.fid,
                    "target_fid": self.cwv_thresholds["fid"]["good"],
                    "optimization_strategies": ["code_splitting", "defer_non_critical_js", "reduce_main_thread_work"]
                },
                code_examples=[
                    'const module = await import("./heavy-module.js");',
                    '<script defer src="non-critical.js"></script>'
                ],
                tools_required=["Webpack Bundle Analyzer", "Chrome DevTools Performance"],
                estimated_impact=0.7
            ))
        
        # Resource optimization
        if test.resource_summary["total_bytes"] > 2000000:  # 2MB threshold
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"resource_opt_{test.test_id}",
                url=test.url,
                optimization_type=OptimizationType.RESOURCE_COMPRESSION,
                priority="medium",
                title="Optimize Resource Loading",
                description="Compress and optimize resources to reduce transfer size",
                potential_savings=0.5,  # Estimated time savings
                implementation_effort="medium",
                technical_details={
                    "total_bytes": test.resource_summary["total_bytes"],
                    "compression_opportunities": ["enable_gzip", "optimize_images", "minify_css_js"]
                },
                code_examples=[
                    'gzip on;',
                    'gzip_types text/css application/javascript;'
                ],
                tools_required=["gzip", "Brotli", "ImageOptim"],
                estimated_impact=0.6
            ))
        
        return recommendations
    
    async def _check_performance_budget(self, test: PerformanceTest) -> Dict[str, Any]:
        """Check performance budget compliance"""
        budget = self.default_budgets.get(test.device_type, self.default_budgets["mobile"])
        compliance = {}
        
        # Check Core Web Vitals against budget
        cwv = test.core_web_vitals
        
        compliance["lcp"] = {
            "budget": budget["lcp"],
            "actual": cwv.lcp,
            "compliant": cwv.lcp <= budget["lcp"],
            "variance": cwv.lcp - budget["lcp"]
        }
        
        compliance["fid"] = {
            "budget": budget["fid"],
            "actual": cwv.fid,
            "compliant": cwv.fid <= budget["fid"],
            "variance": cwv.fid - budget["fid"]
        }
        
        compliance["cls"] = {
            "budget": budget["cls"],
            "actual": cwv.cls,
            "compliant": cwv.cls <= budget["cls"],
            "variance": cwv.cls - budget["cls"]
        }
        
        compliance["performance_score"] = {
            "budget": budget["performance_score"],
            "actual": test.performance_score,
            "compliant": test.performance_score >= budget["performance_score"],
            "variance": test.performance_score - budget["performance_score"]
        }
        
        # Overall compliance
        total_violations = sum(1 for metric in compliance.values() if not metric["compliant"])
        compliance["overall"] = {
            "compliant": total_violations == 0,
            "violations": total_violations,
            "compliance_percentage": ((len(compliance) - 1 - total_violations) / (len(compliance) - 1)) * 100
        }
        
        return compliance
    
    async def _calculate_performance_trend(self, url: str) -> Dict[str, Any]:
        """Calculate performance trend for URL"""
        tests = self.performance_tests.get(url, [])
        
        if len(tests) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort tests by timestamp
        sorted_tests = sorted(tests, key=lambda x: x.timestamp)
        
        # Calculate trends for key metrics
        lcp_trend = self._calculate_metric_trend([t.core_web_vitals.lcp for t in sorted_tests])
        fid_trend = self._calculate_metric_trend([t.core_web_vitals.fid for t in sorted_tests])
        cls_trend = self._calculate_metric_trend([t.core_web_vitals.cls for t in sorted_tests])
        score_trend = self._calculate_metric_trend([t.performance_score for t in sorted_tests])
        
        return {
            "total_tests": len(tests),
            "time_period_days": (sorted_tests[-1].timestamp - sorted_tests[0].timestamp).days,
            "trends": {
                "lcp": lcp_trend,
                "fid": fid_trend,
                "cls": cls_trend,
                "performance_score": score_trend
            },
            "overall_trend": self._determine_overall_trend([lcp_trend, fid_trend, cls_trend, score_trend])
        }
    
    def _calculate_metric_trend(self, values: List[float]) -> str:
        """Calculate trend for a specific metric"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        recent_avg = np.mean(values[-3:])  # Last 3 values
        older_avg = np.mean(values[:3])    # First 3 values
        
        change_percentage = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
        
        if change_percentage > 10:
            return "improving"
        elif change_percentage < -10:
            return "degrading"
        else:
            return "stable"
    
    def _determine_overall_trend(self, trends: List[str]) -> str:
        """Determine overall performance trend"""
        improving_count = trends.count("improving")
        degrading_count = trends.count("degrading")
        
        if improving_count > degrading_count:
            return "improving"
        elif degrading_count > improving_count:
            return "degrading"
        else:
            return "stable"
    
    async def _get_competitive_analysis(self, url: str) -> Dict[str, Any]:
        """Get competitive performance analysis"""
        # Simulate competitive analysis
        # In a real implementation, this would compare against competitor URLs
        
        competitors = [
            {"name": "Competitor A", "score": np.random.uniform(60, 85)},
            {"name": "Competitor B", "score": np.random.uniform(55, 80)},
            {"name": "Competitor C", "score": np.random.uniform(65, 90)}
        ]
        
        # Get current site performance
        current_tests = self.performance_tests.get(url, [])
        current_score = current_tests[-1].performance_score if current_tests else 0
        
        # Calculate position
        better_competitors = [c for c in competitors if c["score"] > current_score]
        position = len(better_competitors) + 1
        
        return {
            "competitors": competitors,
            "current_score": current_score,
            "market_position": position,
            "performance_gap": max(0, max(c["score"] for c in competitors) - current_score),
            "benchmark_score": np.mean([c["score"] for c in competitors])
        }
    
    def get_performance_history(self, url: str, days: int = 30) -> Dict[str, Any]:
        """Get performance history for URL"""
        tests = self.performance_tests.get(url, [])
        
        # Filter tests within date range
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tests = [t for t in tests if t.timestamp >= cutoff_date]
        
        if not recent_tests:
            return {"url": url, "tests": 0}
        
        # Calculate statistics
        scores = [t.performance_score for t in recent_tests]
        lcp_values = [t.core_web_vitals.lcp for t in recent_tests]
        fid_values = [t.core_web_vitals.fid for t in recent_tests]
        cls_values = [t.core_web_vitals.cls for t in recent_tests]
        
        return {
            "url": url,
            "date_range": f"{cutoff_date.date()} to {datetime.now().date()}",
            "total_tests": len(recent_tests),
            "performance_statistics": {
                "average_score": np.mean(scores),
                "min_score": np.min(scores),
                "max_score": np.max(scores),
                "score_variance": np.var(scores)
            },
            "core_web_vitals_stats": {
                "lcp": {"avg": np.mean(lcp_values), "min": np.min(lcp_values), "max": np.max(lcp_values)},
                "fid": {"avg": np.mean(fid_values), "min": np.min(fid_values), "max": np.max(fid_values)},
                "cls": {"avg": np.mean(cls_values), "min": np.min(cls_values), "max": np.max(cls_values)}
            },
            "trend_analysis": await self._calculate_performance_trend(url)
        }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        total_tests = sum(len(tests) for tests in self.performance_tests.values())
        total_recommendations = sum(len(recs) for recs in self.optimization_recommendations.values())
        
        return {
            "monitored_urls": len(self.performance_tests),
            "total_performance_tests": total_tests,
            "total_recommendations": total_recommendations,
            "performance_budgets_configured": len(self.performance_budgets),
            "last_updated": datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    async def test_page_speed_tracking() -> None:
        """Test page speed optimization tracking functionality"""
        tracker = PageSpeedOptimizationTracker()
        
        # Test performance analysis
        url = "https://ainflue.com"
        test_result = await tracker.run_performance_test(url, "mobile")
        print(f"Performance test result: {test_result}")
        
        # Test performance history
        history = tracker.get_performance_history(url, 30)
        print(f"Performance history: {history}")
        
        # Test monitoring status
        status = tracker.get_monitoring_status()
        print(f"Monitoring status: {status}")
    
    # Run test
    asyncio.run(test_page_speed_tracking())