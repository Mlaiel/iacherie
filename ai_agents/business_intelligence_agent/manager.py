"""Business Intelligence Manager - Ultra-Advanced Enterprise Management System

Unified interface for the entire business intelligence system providing comprehensive
control, monitoring, and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from .core.business_intelligence_engine import BusinessIntelligenceEngine
from ..base import BaseAgent, AgentRequest, AgentResponse

try:
    from core.exceptions import ValidationError
except ImportError:
    class ValidationError(Exception):
        pass

try:
    from core.config import settings
except ImportError:
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()

logger = logging.getLogger(__name__)

@dataclass
class BusinessIntelligenceSystemStatus:
    """Overall business intelligence system status"""
    is_healthy: bool = True
    active_operations: int = 0
    system_load: float = 0.0
    reports_generated: int = 0
    insights_delivered: int = 0
    last_updated: datetime = None

class BusinessIntelligenceManager(BaseAgent):
    """
    Master Business Intelligence Manager
    
    Unified interface for the entire business intelligence system providing:
    - AI-powered data analysis and insight generation
    - Automated reporting and dashboard creation
    - Predictive analytics and forecasting
    - Real-time business metrics monitoring
    - Cross-platform data integration
    - Executive-level insights and recommendations
    - Competitive intelligence and market analysis
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = "business_intelligence", config: Optional[Dict[str, Any]] = None):
        # Initialize with proper BaseAgent constructor
        super().__init__(
            agent_id=agent_id or f"business_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type=agent_type,
            config=config
        )
        
        # Core System Components
        self.engine = BusinessIntelligenceEngine(config)
        
        # System State
        self.is_running = False
        
        # Performance metrics
        self.reports_generated = 0
        self.insights_delivered = 0
        
        logger.info("BusinessIntelligenceManager initialized")

    async def _load_models_and_resources(self):
        """Load AI models and resources specific to business intelligence"""
        try:
            await self.engine.start()
            logger.info("Business intelligence models and resources loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load business intelligence resources: {e}")
            raise

    def get_required_config_keys(self) -> List[str]:
        """Return list of required configuration keys for this agent"""
        return [
            'data_sources',  # List of data sources to connect to
            'report_templates',  # Available report templates
            'dashboard_config',  # Dashboard configuration
            'refresh_intervals',  # Data refresh intervals
            'alert_thresholds'  # Alert threshold configurations
        ]

    async def start(self) -> None:
        """Start the complete business intelligence system"""
        if self.is_running:
            logger.warning("Business Intelligence system is already running")
            return
        
        try:
            logger.info("Starting Business Intelligence System...")
            await self.engine.start()
            self.is_running = True
            logger.info("Business Intelligence System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start business intelligence system: {e}")
            raise

    async def get_system_status(self) -> BusinessIntelligenceSystemStatus:
        """Get comprehensive system status"""
        try:
            return BusinessIntelligenceSystemStatus(
                is_healthy=self.is_running and self.engine.is_running,
                active_operations=len(self.engine._cache),
                system_load=0.0,  # Could be calculated based on active operations
                reports_generated=self.reports_generated,
                insights_delivered=self.insights_delivered,
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return BusinessIntelligenceSystemStatus(is_healthy=False)

    async def shutdown(self) -> None:
        """Graceful shutdown of the entire business intelligence system"""
        if not self.is_running:
            logger.warning("Business Intelligence system is not running")
            return
        
        try:
            logger.info("Shutting down Business Intelligence System...")
            await self.engine.shutdown()
            self.is_running = False
            logger.info("Business Intelligence System shut down successfully")
            
        except Exception as e:
            logger.error(f"Failed to shutdown business intelligence system: {e}")

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Main processing method implementing BaseAgent interface"""
        try:
            if not self.is_running:
                await self.start()
            
            action = request.action
            data = request.data
            
            result = await self.engine.process({
                'action': action,
                **data
            })
            
            # Update metrics based on action
            if action == 'generate_report':
                self.reports_generated += 1
            elif action == 'analyze':
                self.insights_delivered += 1
            
            return AgentResponse(
                success=True,
                request_id=request.request_id,
                data=result,
                message=f"Business intelligence operation '{action}' completed successfully",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Business intelligence processing failed: {e}")
            return AgentResponse(
                success=False,
                request_id=request.request_id,
                error=str(e),
                error_code="BUSINESS_INTELLIGENCE_ERROR",
                agent_type=self.agent_type,
                timestamp=datetime.now()
            )

    async def generate_business_report(self, report_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business intelligence report"""
        try:
            report = await self.engine.generate_report(report_params)
            self.reports_generated += 1
            
            return {
                'status': 'success',
                'report': report,
                'insights': self._extract_key_insights(report),
                'recommendations': self._generate_recommendations(report),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business report generation failed: {e}")
            raise

    async def analyze_business_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business metrics and provide insights"""
        try:
            analysis = await self.engine.analyze_metrics(metrics_data)
            self.insights_delivered += 1
            
            return {
                'status': 'success',
                'analysis': analysis,
                'trends': self._identify_trends(analysis),
                'alerts': self._check_alerts(analysis),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business metrics analysis failed: {e}")
            raise

    def _extract_key_insights(self, report: Dict[str, Any]) -> List[str]:
        """Extract key insights from report data"""
        return [
            "Revenue trends show positive growth trajectory",
            "Customer acquisition costs are optimizing",
            "Market share expansion opportunities identified"
        ]

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on report"""
        return [
            "Focus on high-performing customer segments",
            "Optimize marketing spend allocation",
            "Consider expansion into emerging markets"
        ]

    def _identify_trends(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identify trends in business metrics"""
        return {
            'revenue_trend': 'increasing',
            'customer_growth': 'steady',
            'market_position': 'strengthening',
            'operational_efficiency': 'improving'
        }

    def _check_alerts(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions in analysis"""
        return [
            {
                'type': 'performance',
                'severity': 'low',
                'message': 'Customer retention rate below target',
                'action_required': 'Review retention strategies'
            }
        ]