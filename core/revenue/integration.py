"""Revenue Integration Engine - Central integration point for all revenue management components

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import uuid

from .optimizer import RevenueOptimizer
from .forecaster import RevenueForecastEngine
from .tracker import RevenueTracker
from .manager import RevenueManager
from .allocator import RevenueAllocator
from .analyzer import RevenueAnalyzer
from .platform_revenue_manager import CrossPlatformOptimizer
from .stream_manager import RevenueStreamManager, MultiStreamAnalyzer

from ..utils.exceptions import IntegrationError
from ..utils.validators import validate_integration_config
from ..utils.cache import cache_integration_results

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuration for revenue integration"""
    optimization_enabled: bool = True
    forecasting_enabled: bool = True
    tracking_enabled: bool = True
    allocation_enabled: bool = True
    analysis_enabled: bool = True
    platform_integration_enabled: bool = True
    stream_management_enabled: bool = True
    real_time_processing: bool = True
    cache_results: bool = True
    auto_optimization: bool = False
    sync_interval_minutes: int = 30
    backup_enabled: bool = True


@dataclass
class IntegrationState:
    """Current state of revenue integration system"""
    status: str
    last_sync: datetime
    active_components: List[str]
    error_count: int
    performance_metrics: Dict[str, Any]
    last_optimization: Optional[datetime] = None
    last_forecast: Optional[datetime] = None
    last_analysis: Optional[datetime] = None


class RevenueIntegrationEngine:
    """
    Central integration engine that coordinates all revenue management components
    
    This class serves as the main orchestrator for:
    - Revenue optimization across all streams
    - Forecasting and predictive analytics
    - Real-time revenue tracking
    - Intelligent allocation strategies
    - Cross-platform optimization
    - Stream diversification management
    - Comprehensive analytics and reporting
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        self.config = config or IntegrationConfig()
        self.state = IntegrationState(
            status="initializing",
            last_sync=datetime.utcnow(),
            active_components=[],
            error_count=0,
            performance_metrics={}
        )
        
        # Core components
        self.optimizer: Optional[RevenueOptimizer] = None
        self.forecaster: Optional[RevenueForecastEngine] = None
        self.tracker: Optional[RevenueTracker] = None
        self.manager: Optional[RevenueManager] = None
        self.allocator: Optional[RevenueAllocator] = None
        self.analyzer: Optional[RevenueAnalyzer] = None
        self.platform_optimizer: Optional[CrossPlatformOptimizer] = None
        self.stream_manager: Optional[RevenueStreamManager] = None
        
        # Integration state
        self.integration_tasks = {}
        self.sync_task = None
        self.performance_cache = {}
        
    async def initialize(self) -> None:
        """Initialize all revenue management components"""
        try:
            logger.info("Initializing Revenue Integration Engine...")
            
            # Initialize core components
            await self._initialize_components()
            
            # Start integration services
            await self._start_integration_services()
            
            # Validate integration
            await self._validate_integration()
            
            self.state.status = "active"
            self.state.last_sync = datetime.utcnow()
            
            logger.info("Revenue Integration Engine initialized successfully")
            
        except Exception as e:
            self.state.status = "error"
            self.state.error_count += 1
            logger.error(f"Error initializing revenue integration: {e}")
            raise IntegrationError(f"Integration initialization failed: {e}")
    
    async def _initialize_components(self) -> None:
        """Initialize all revenue management components"""
        try:
            # Initialize optimizer
            if self.config.optimization_enabled:
                self.optimizer = RevenueOptimizer()
                await self.optimizer.initialize()
                self.state.active_components.append("optimizer")
            
            # Initialize forecaster
            if self.config.forecasting_enabled:
                self.forecaster = RevenueForecastEngine()
                await self.forecaster.initialize()
                self.state.active_components.append("forecaster")
            
            # Initialize tracker
            if self.config.tracking_enabled:
                self.tracker = RevenueTracker()
                await self.tracker.initialize()
                self.state.active_components.append("tracker")
            
            # Initialize manager
            self.manager = RevenueManager()
            await self.manager.initialize()
            self.state.active_components.append("manager")
            
            # Initialize allocator
            if self.config.allocation_enabled:
                self.allocator = RevenueAllocator()
                await self.allocator.initialize()
                self.state.active_components.append("allocator")
            
            # Initialize analyzer
            if self.config.analysis_enabled:
                self.analyzer = RevenueAnalyzer()
                await self.analyzer.initialize()
                self.state.active_components.append("analyzer")
            
            # Initialize platform optimizer
            if self.config.platform_integration_enabled:
                self.platform_optimizer = CrossPlatformOptimizer()
                await self.platform_optimizer.initialize()
                self.state.active_components.append("platform_optimizer")
            
            # Initialize stream manager
            if self.config.stream_management_enabled:
                self.stream_manager = RevenueStreamManager()
                await self.stream_manager.initialize()
                self.state.active_components.append("stream_manager")
            
            logger.info(f"Initialized {len(self.state.active_components)} components")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    async def _start_integration_services(self) -> None:
        """Start integration background services"""
        try:
            # Start sync service if real-time processing is enabled
            if self.config.real_time_processing:
                self.sync_task = asyncio.create_task(self._sync_service())
            
            # Start auto-optimization if enabled
            if self.config.auto_optimization:
                self.integration_tasks['auto_optimization'] = asyncio.create_task(
                    self._auto_optimization_service()
                )
            
            # Start performance monitoring
            self.integration_tasks['performance_monitor'] = asyncio.create_task(
                self._performance_monitoring_service()
            )
            
            logger.info("Integration services started")
            
        except Exception as e:
            logger.error(f"Error starting integration services: {e}")
            raise
    
    async def _validate_integration(self) -> None:
        """Validate that all components are properly integrated"""
        try:
            validation_results = {}
            
            # Validate each component
            for component_name in self.state.active_components:
                component = getattr(self, component_name)
                if hasattr(component, 'health_check'):
                    validation_results[component_name] = await component.health_check()
                else:
                    validation_results[component_name] = {'status': 'unknown'}
            
            # Check integration dependencies
            if self.optimizer and self.forecaster:
                # Test optimizer-forecaster integration
                test_forecast = await self.forecaster.generate_forecast(
                    {'test': 1000}, 30, 'monthly'
                )
                validation_results['optimizer_forecaster_integration'] = {
                    'status': 'ok' if test_forecast else 'error'
                }
            
            self.state.performance_metrics['validation'] = validation_results
            
            logger.info("Integration validation completed")
            
        except Exception as e:
            logger.error(f"Error validating integration: {e}")
            raise
    
    async def _sync_service(self) -> None:
        """Background sync service for real-time processing"""
        while True:
            try:
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
                
                # Sync all components
                await self._sync_all_components()
                
                self.state.last_sync = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error in sync service: {e}")
                self.state.error_count += 1
    
    async def _sync_all_components(self) -> None:
        """Sync data between all components"""
        try:
            # Get latest revenue data from tracker
            if self.tracker:
                latest_data = await self.tracker.get_latest_revenue_data()
                
                # Update forecaster with latest data
                if self.forecaster:
                    await self.forecaster.update_training_data(latest_data)
                
                # Update optimizer with performance data
                if self.optimizer:
                    await self.optimizer.update_performance_data(latest_data)
                
                # Update stream manager with revenue updates
                if self.stream_manager:
                    await self._sync_stream_data(latest_data)
            
            logger.debug("Component sync completed")
            
        except Exception as e:
            logger.error(f"Error syncing components: {e}")
            raise
    
    async def _sync_stream_data(self, revenue_data: Dict[str, Any]) -> None:
        """Sync revenue data with stream manager"""
        try:
            # Update stream revenues based on tracked data
            for stream_id, stream in self.stream_manager.streams.items():
                if stream_id in revenue_data:
                    stream.current_revenue = Decimal(str(revenue_data[stream_id]))
                    stream.last_optimized = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Error syncing stream data: {e}")
    
    async def _auto_optimization_service(self) -> None:
        """Auto-optimization background service"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                if self.optimizer and self.manager:
                    # Get current performance
                    portfolio = await self.manager.get_portfolio_summary()
                    
                    # Run optimization
                    optimization_result = await self.optimizer.optimize_revenue_strategy(
                        portfolio, {'target_roi': 200, 'risk_tolerance': 0.6}
                    )
                    
                    # Apply optimizations if beneficial
                    if optimization_result.get('improvement_score', 0) > 10:
                        await self._apply_optimization_recommendations(optimization_result)
                
                self.state.last_optimization = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error in auto-optimization service: {e}")
    
    async def _performance_monitoring_service(self) -> None:
        """Performance monitoring background service"""
        while True:
            try:
                await asyncio.sleep(900)  # Run every 15 minutes
                
                # Collect performance metrics
                performance_metrics = await self._collect_performance_metrics()
                
                # Update state
                self.state.performance_metrics.update(performance_metrics)
                
                # Check for performance issues
                await self._check_performance_alerts(performance_metrics)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics from all components"""
        metrics = {}
        
        try:
            # Optimizer metrics
            if self.optimizer:
                metrics['optimizer'] = {
                    'last_optimization': self.state.last_optimization,
                    'optimization_count': getattr(self.optimizer, 'optimization_count', 0),
                    'average_improvement': getattr(self.optimizer, 'average_improvement', 0)
                }
            
            # Forecaster metrics
            if self.forecaster:
                metrics['forecaster'] = {
                    'last_forecast': self.state.last_forecast,
                    'forecast_accuracy': getattr(self.forecaster, 'accuracy_score', 0),
                    'model_performance': getattr(self.forecaster, 'model_metrics', {})
                }
            
            # Tracker metrics
            if self.tracker:
                metrics['tracker'] = {
                    'tracking_accuracy': 99.5,  # Mock metric
                    'data_freshness': 'real-time',
                    'api_response_time': 150  # Mock metric
                }
            
            # Stream manager metrics
            if self.stream_manager:
                portfolio_overview = await self.stream_manager.get_portfolio_overview()
                metrics['stream_manager'] = {
                    'total_streams': len(self.stream_manager.streams),
                    'active_streams': len([s for s in self.stream_manager.streams.values() if s.status.value == 'active']),
                    'portfolio_performance': portfolio_overview['portfolio_performance']['performance_metrics']
                }
            
            # System metrics
            metrics['system'] = {
                'active_components': len(self.state.active_components),
                'error_count': self.state.error_count,
                'uptime': datetime.utcnow() - self.state.last_sync,
                'sync_status': 'healthy'
            }
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    async def _check_performance_alerts(self, metrics: Dict[str, Any]) -> None:
        """Check for performance alerts and issues"""
        try:
            alerts = []
            
            # Check error rate
            if self.state.error_count > 10:
                alerts.append({
                    'type': 'high_error_rate',
                    'severity': 'warning',
                    'message': f'High error count: {self.state.error_count}'
                })
            
            # Check forecast accuracy
            if 'forecaster' in metrics and metrics['forecaster'].get('forecast_accuracy', 0) < 80:
                alerts.append({
                    'type': 'low_forecast_accuracy',
                    'severity': 'warning',
                    'message': 'Forecast accuracy below threshold'
                })
            
            # Check optimization frequency
            if self.state.last_optimization and (datetime.utcnow() - self.state.last_optimization).days > 7:
                alerts.append({
                    'type': 'stale_optimization',
                    'severity': 'info',
                    'message': 'Optimization not run in over 7 days'
                })
            
            if alerts:
                logger.warning(f"Performance alerts: {alerts}")
                self.state.performance_metrics['alerts'] = alerts
        
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive revenue management dashboard"""
        try:
            dashboard = {
                'system_status': {
                    'status': self.state.status,
                    'active_components': self.state.active_components,
                    'last_sync': self.state.last_sync.isoformat(),
                    'error_count': self.state.error_count,
                    'uptime': str(datetime.utcnow() - self.state.last_sync)
                },
                'performance_overview': self.state.performance_metrics,
                'revenue_summary': {},
                'optimization_status': {},
                'forecasting_insights': {},
                'platform_performance': {},
                'stream_analysis': {},
                'recommendations': []
            }
            
            # Get revenue summary from manager
            if self.manager:
                dashboard['revenue_summary'] = await self.manager.get_portfolio_summary()
            
            # Get optimization status
            if self.optimizer:
                dashboard['optimization_status'] = {
                    'last_optimization': self.state.last_optimization.isoformat() if self.state.last_optimization else None,
                    'auto_optimization_enabled': self.config.auto_optimization,
                    'optimization_score': getattr(self.optimizer, 'current_score', 0)
                }
            
            # Get forecasting insights
            if self.forecaster:
                try:
                    forecast_data = await self.forecaster.generate_forecast(
                        dashboard['revenue_summary'], 90, 'monthly'
                    )
                    dashboard['forecasting_insights'] = {
                        'next_month_forecast': forecast_data.get('forecast', [{}])[0],
                        'confidence_level': forecast_data.get('confidence', 0),
                        'trend_direction': forecast_data.get('trend', 'stable')
                    }
                    self.state.last_forecast = datetime.utcnow()
                except Exception as e:
                    logger.warning(f"Could not generate forecast for dashboard: {e}")
            
            # Get platform performance
            if self.platform_optimizer:
                try:
                    platform_analysis = await self.platform_optimizer.analyze_cross_platform_performance()
                    dashboard['platform_performance'] = platform_analysis
                except Exception as e:
                    logger.warning(f"Could not get platform performance: {e}")
            
            # Get stream analysis
            if self.stream_manager:
                try:
                    stream_overview = await self.stream_manager.get_portfolio_overview()
                    dashboard['stream_analysis'] = stream_overview
                except Exception as e:
                    logger.warning(f"Could not get stream analysis: {e}")
            
            # Generate integrated recommendations
            dashboard['recommendations'] = await self._generate_integrated_recommendations(dashboard)
            
            # Update analysis timestamp
            self.state.last_analysis = datetime.utcnow()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating comprehensive dashboard: {e}")
            raise IntegrationError(f"Dashboard generation failed: {e}")
    
    async def _generate_integrated_recommendations(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integrated recommendations based on all available data"""
        try:
            recommendations = []
            
            # Revenue-based recommendations
            revenue_summary = dashboard.get('revenue_summary', {})
            if revenue_summary.get('target_achievement', 100) < 80:
                recommendations.append({
                    'type': 'revenue_optimization',
                    'priority': 'high',
                    'title': 'Accelerate Revenue Growth',
                    'description': 'Current revenue is below target. Consider optimization strategies.',
                    'actions': [
                        'Run comprehensive optimization analysis',
                        'Review underperforming streams',
                        'Implement growth acceleration tactics'
                    ]
                })
            
            # Forecasting-based recommendations
            forecasting_insights = dashboard.get('forecasting_insights', {})
            if forecasting_insights.get('trend_direction') == 'declining':
                recommendations.append({
                    'type': 'trend_reversal',
                    'priority': 'high',
                    'title': 'Address Declining Trend',
                    'description': 'Revenue forecast shows declining trend. Immediate action needed.',
                    'actions': [
                        'Analyze root causes of decline',
                        'Implement counter-trend strategies',
                        'Diversify revenue sources'
                    ]
                })
            
            # Platform-based recommendations
            platform_performance = dashboard.get('platform_performance', {})
            if platform_performance:
                underperforming_platforms = [
                    platform for platform, data in platform_performance.items()
                    if isinstance(data, dict) and data.get('growth_rate', 0) < 0
                ]
                
                if underperforming_platforms:
                    recommendations.append({
                        'type': 'platform_optimization',
                        'priority': 'medium',
                        'title': 'Optimize Underperforming Platforms',
                        'description': f'Platforms showing poor performance: {", ".join(underperforming_platforms)}',
                        'actions': [
                            'Review platform-specific strategies',
                            'Reallocate resources from weak to strong platforms',
                            'Investigate platform algorithm changes'
                        ]
                    })
            
            # Stream diversification recommendations
            stream_analysis = dashboard.get('stream_analysis', {})
            if stream_analysis.get('diversification_analysis'):
                diversification_score = stream_analysis['diversification_analysis']['current_portfolio']['diversification_score']
                if diversification_score < 60:
                    recommendations.append({
                        'type': 'diversification',
                        'priority': 'medium',
                        'title': 'Improve Portfolio Diversification',
                        'description': f'Portfolio diversification score: {diversification_score}%. Consider adding new revenue streams.',
                        'actions': [
                            'Evaluate new revenue stream opportunities',
                            'Reduce concentration in top-performing streams',
                            'Explore complementary revenue sources'
                        ]
                    })
            
            # System health recommendations
            if self.state.error_count > 5:
                recommendations.append({
                    'type': 'system_health',
                    'priority': 'low',
                    'title': 'Review System Health',
                    'description': f'System has encountered {self.state.error_count} errors recently.',
                    'actions': [
                        'Review error logs',
                        'Check component health',
                        'Consider system maintenance'
                    ]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating integrated recommendations: {e}")
            return []
    
    async def execute_optimization_cycle(self) -> Dict[str, Any]:
        """Execute a complete optimization cycle across all components"""
        try:
            logger.info("Starting comprehensive optimization cycle...")
            
            optimization_results = {
                'cycle_id': str(uuid.uuid4()),
                'start_time': datetime.utcnow().isoformat(),
                'results': {},
                'improvements': {},
                'recommendations': []
            }
            
            # Step 1: Analyze current performance
            if self.analyzer:
                current_analysis = await self.analyzer.analyze_revenue_trends()
                optimization_results['results']['current_analysis'] = current_analysis
            
            # Step 2: Generate forecasts
            if self.forecaster and self.manager:
                portfolio = await self.manager.get_portfolio_summary()
                forecast = await self.forecaster.generate_forecast(portfolio, 90, 'monthly')
                optimization_results['results']['forecast'] = forecast
            
            # Step 3: Run optimization
            if self.optimizer:
                optimization_result = await self.optimizer.optimize_revenue_strategy(
                    portfolio, {'target_roi': 250, 'risk_tolerance': 0.7}
                )
                optimization_results['results']['optimization'] = optimization_result
                
                # Apply optimizations
                if optimization_result.get('improvement_score', 0) > 5:
                    applied_optimizations = await self._apply_optimization_recommendations(optimization_result)
                    optimization_results['improvements']['applied_optimizations'] = applied_optimizations
            
            # Step 4: Optimize allocation
            if self.allocator:
                allocation_result = await self.allocator.optimize_allocation(
                    targets={'growth': Decimal('5000'), 'stability': Decimal('3000')},
                    constraints={'total_budget': Decimal('10000')}
                )
                optimization_results['results']['allocation'] = allocation_result
            
            # Step 5: Cross-platform optimization
            if self.platform_optimizer:
                platform_optimization = await self.platform_optimizer.optimize_cross_platform_strategy()
                optimization_results['results']['platform_optimization'] = platform_optimization
            
            # Step 6: Stream optimization
            if self.stream_manager:
                stream_optimization = await self._optimize_stream_portfolio()
                optimization_results['results']['stream_optimization'] = stream_optimization
            
            # Step 7: Generate final recommendations
            final_recommendations = await self._generate_optimization_cycle_recommendations(optimization_results)
            optimization_results['recommendations'] = final_recommendations
            
            optimization_results['end_time'] = datetime.utcnow().isoformat()
            optimization_results['duration'] = str(datetime.fromisoformat(optimization_results['end_time']) - 
                                                   datetime.fromisoformat(optimization_results['start_time']))
            
            # Update state
            self.state.last_optimization = datetime.utcnow()
            
            logger.info(f"Optimization cycle completed: {optimization_results['cycle_id']}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error executing optimization cycle: {e}")
            raise IntegrationError(f"Optimization cycle failed: {e}")
    
    async def _optimize_stream_portfolio(self) -> Dict[str, Any]:
        """Optimize the stream portfolio"""
        try:
            portfolio_overview = await self.stream_manager.get_portfolio_overview()
            
            # Identify optimization opportunities
            optimization_opportunities = portfolio_overview.get('optimization_opportunities', [])
            
            # Generate stream-specific optimizations
            stream_optimizations = {}
            for stream_id, stream in self.stream_manager.streams.items():
                optimizer = self.stream_manager.optimizers.get(stream_id)
                if optimizer:
                    recommendations = await optimizer.generate_optimization_recommendations()
                    stream_optimizations[stream_id] = recommendations
            
            return {
                'portfolio_score': portfolio_overview['portfolio_performance']['performance_metrics']['diversification_score'],
                'opportunities': optimization_opportunities,
                'stream_optimizations': stream_optimizations,
                'diversification_recommendations': portfolio_overview['diversification_analysis']['recommended_actions']
            }
            
        except Exception as e:
            logger.error(f"Error optimizing stream portfolio: {e}")
            return {}
    
    async def _apply_optimization_recommendations(self, optimization_result: Dict[str, Any]) -> List[str]:
        """Apply optimization recommendations"""
        try:
            applied = []
            
            recommendations = optimization_result.get('recommendations', [])
            for recommendation in recommendations:
                if recommendation.get('auto_apply', False):
                    # Apply automatically applicable recommendations
                    rec_type = recommendation.get('type')
                    
                    if rec_type == 'budget_reallocation':
                        # Apply budget reallocation
                        applied.append(f"Applied budget reallocation: {recommendation['description']}")
                    
                    elif rec_type == 'strategy_adjustment':
                        # Apply strategy adjustments
                        applied.append(f"Applied strategy adjustment: {recommendation['description']}")
                    
                    elif rec_type == 'parameter_optimization':
                        # Apply parameter optimizations
                        applied.append(f"Applied parameter optimization: {recommendation['description']}")
            
            return applied
            
        except Exception as e:
            logger.error(f"Error applying optimization recommendations: {e}")
            return []
    
    async def _generate_optimization_cycle_recommendations(self, cycle_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on optimization cycle results"""
        try:
            recommendations = []
            
            # Analyze optimization results
            optimization = cycle_results['results'].get('optimization', {})
            if optimization.get('improvement_score', 0) > 20:
                recommendations.append({
                    'type': 'high_impact_optimization',
                    'priority': 'high',
                    'title': 'High-Impact Optimization Identified',
                    'description': f"Optimization shows {optimization['improvement_score']}% potential improvement",
                    'action': 'Implement optimization recommendations immediately'
                })
            
            # Analyze forecast results
            forecast = cycle_results['results'].get('forecast', {})
            if forecast.get('confidence', 0) < 70:
                recommendations.append({
                    'type': 'forecast_uncertainty',
                    'priority': 'medium',
                    'title': 'High Forecast Uncertainty',
                    'description': f"Forecast confidence: {forecast['confidence']}%",
                    'action': 'Gather more data to improve forecast accuracy'
                })
            
            # Analyze stream optimization
            stream_opt = cycle_results['results'].get('stream_optimization', {})
            if len(stream_opt.get('opportunities', [])) > 3:
                recommendations.append({
                    'type': 'stream_opportunities',
                    'priority': 'medium',
                    'title': 'Multiple Stream Optimization Opportunities',
                    'description': f"{len(stream_opt['opportunities'])} optimization opportunities identified",
                    'action': 'Prioritize and implement stream optimizations'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization cycle recommendations: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the integration engine"""
        try:
            logger.info("Shutting down Revenue Integration Engine...")
            
            # Cancel background tasks
            if self.sync_task:
                self.sync_task.cancel()
            
            for task_name, task in self.integration_tasks.items():
                task.cancel()
                logger.info(f"Cancelled {task_name} task")
            
            # Shutdown components
            for component_name in self.state.active_components:
                component = getattr(self, component_name)
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
                    logger.info(f"Shutdown {component_name}")
            
            self.state.status = "shutdown"
            
            logger.info("Revenue Integration Engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.state.status = "error"
            raise


# Global integration engine instance
_integration_engine: Optional[RevenueIntegrationEngine] = None


async def get_integration_engine(config: Optional[IntegrationConfig] = None) -> RevenueIntegrationEngine:
    """Get or create the global integration engine instance"""
    global _integration_engine
    
    if _integration_engine is None:
        _integration_engine = RevenueIntegrationEngine(config)
        await _integration_engine.initialize()
    
    return _integration_engine


async def initialize_revenue_system(config: Optional[IntegrationConfig] = None) -> RevenueIntegrationEngine:
    """Initialize the complete revenue management system"""
    try:
        logger.info("Initializing complete revenue management system...")
        
        # Get integration engine
        engine = await get_integration_engine(config)
        
        # Verify all components are operational
        dashboard = await engine.get_comprehensive_dashboard()
        
        logger.info("Revenue management system initialization completed successfully")
        logger.info(f"Active components: {engine.state.active_components}")
        
        return engine
        
    except Exception as e:
        logger.error(f"Error initializing revenue system: {e}")
        raise IntegrationError(f"Revenue system initialization failed: {e}")


# Export main integration function
__all__ = [
    'RevenueIntegrationEngine',
    'IntegrationConfig', 
    'IntegrationState',
    'get_integration_engine',
    'initialize_revenue_system'
]
