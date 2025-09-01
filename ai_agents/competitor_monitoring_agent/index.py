"""Competitor Monitoring Agent - Main Entry Point and Index
Advanced AI-powered competitive intelligence system entry point.

This index provides easy access to all competitor monitoring functionalities
and serves as the main entry point for the agent system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .competitor_agent import CompetitorMonitoringAgent
from .data_collection import DataCollectionManager
from .market_intelligence import MarketIntelligenceEngine
from .alert_system import AlertSystem
from .strategic_analysis import StrategicAnalysisEngine
from .config_manager import ConfigurationManager
from .report_generator import ReportGenerator

# Module information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced AI-powered competitor monitoring and market intelligence system"


class CompetitorMonitoringSystem:
    """
    Main system orchestrator for competitor monitoring.
    
    Provides unified access to all competitor monitoring capabilities
    including data collection, analysis, alerting, and reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize the competitor monitoring system."""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config_manager = ConfigurationManager()
        self.config = config or self.config_manager.get_full_config()
        
        # Initialize core components
        self.agent = None
        self.data_collector = None
        self.market_intelligence = None
        self.alert_system = None
        self.strategic_analyzer = None
        self.report_generator = None
        
        # System status
        self.is_initialized = False
        self.components_status = {}
        
        self.logger.info("CompetitorMonitoringSystem created")
    
    async def initialize(self) -> bool:
        """Initialize all system components."""
        try:
            self.logger.info("Initializing CompetitorMonitoringSystem...")
            
            # Initialize core components
            self.data_collector = DataCollectionManager(self.config.get("data_collection", {}))
            self.market_intelligence = MarketIntelligenceEngine(self.config.get("market_intelligence", {}))
            self.alert_system = AlertSystem(self.config.get("alerts", {}))
            self.strategic_analyzer = StrategicAnalysisEngine(self.config.get("strategic_analysis", {}))
            self.report_generator = ReportGenerator(self.config.get("reports", {}))
            
            # Initialize main agent
            self.agent = CompetitorMonitoringAgent(self.config)
            agent_initialized = await self.agent.initialize()
            
            # Check component status
            self.components_status = {
                "agent": agent_initialized,
                "data_collector": True,
                "market_intelligence": True,
                "alert_system": True,
                "strategic_analyzer": True,
                "report_generator": True
            }
            
            self.is_initialized = all(self.components_status.values())
            
            if self.is_initialized:
                self.logger.info("CompetitorMonitoringSystem initialized successfully")
            else:
                self.logger.error("Some components failed to initialize")
            
            return self.is_initialized
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CompetitorMonitoringSystem: {str(e)}")
            return False
    
    async def add_competitor(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new competitor to monitor."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            # Add competitor through main agent
            result = await self.agent.process_request({
                "type": "add_competitor",
                "data": competitor_data
            })
            
            self.logger.info(f"Competitor added: {competitor_data.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error adding competitor: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Perform comprehensive competitor analysis."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            # Get competitor analysis through main agent
            result = await self.agent.process_request({
                "type": "analyze_competitor",
                "competitor_id": competitor_id
            })
            
            self.logger.info(f"Competitor analysis completed: {competitor_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing competitor: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_market_intelligence(self, segment: str) -> Dict[str, Any]:
        """Get market intelligence for a specific segment."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            # Get market analysis through main agent
            result = await self.agent.process_request({
                "type": "market_analysis",
                "segment": segment
            })
            
            self.logger.info(f"Market intelligence generated for segment: {segment}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting market intelligence: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def collect_competitor_data(self, competitor_id: str, data_types: List[str] = None) -> List[Any]:
        """Collect data for a specific competitor."""
        if not self.is_initialized:
            return []
        
        try:
            collected_data = await self.data_collector.collect_competitor_data(
                competitor_id, data_types
            )
            
            self.logger.info(f"Data collected for competitor: {competitor_id}")
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting competitor data: {str(e)}")
            return []
    
    async def generate_swot_analysis(self, competitor_id: str, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SWOT analysis for a competitor."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            swot_result = await self.strategic_analyzer.perform_swot_analysis(
                competitor_id, competitor_data
            )
            
            self.logger.info(f"SWOT analysis generated for: {competitor_id}")
            return {"status": "success", "data": swot_result}
            
        except Exception as e:
            self.logger.error(f"Error generating SWOT analysis: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def assess_competitive_threat(self, competitor_id: str, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess competitive threat level."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            threat_assessment = await self.strategic_analyzer.assess_competitive_threat(
                competitor_id, threat_data
            )
            
            self.logger.info(f"Threat assessment completed for: {competitor_id}")
            return {"status": "success", "data": threat_assessment}
            
        except Exception as e:
            self.logger.error(f"Error assessing competitive threat: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def create_alert_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert rule."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            alert_rule = await self.alert_system.create_alert_rule(rule_data)
            
            self.logger.info(f"Alert rule created: {alert_rule.name}")
            return {"status": "success", "data": alert_rule}
            
        except Exception as e:
            self.logger.error(f"Error creating alert rule: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_active_alerts(self, filters: Dict[str, Any] = None) -> List[Any]:
        """Get active monitoring alerts."""
        if not self.is_initialized:
            return []
        
        try:
            alerts = await self.alert_system.get_active_alerts(filters)
            
            self.logger.info(f"Retrieved {len(alerts)} active alerts")
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {str(e)}")
            return []
    
    async def generate_report(self, template_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            report = await self.report_generator.generate_report(template_id, data)
            
            self.logger.info(f"Report generated: {report.title}")
            return {"status": "success", "data": report}
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_competitive_intelligence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive competitive intelligence."""
        if not self.is_initialized:
            return {"status": "error", "message": "System not initialized"}
        
        try:
            # Get competitive intelligence through main agent
            result = await self.agent.process_request({
                "type": "competitive_intelligence",
                "params": params
            })
            
            self.logger.info("Competitive intelligence report generated")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating competitive intelligence: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            status = {
                "system_info": {
                    "version": __version__,
                    "author": __author__,
                    "initialized": self.is_initialized,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "components": self.components_status,
                "agent_status": await self.agent.get_status() if self.agent else {},
                "data_collection_status": await self.data_collector.get_collection_status() if self.data_collector else {},
                "alert_metrics": await self.alert_system.get_alert_metrics() if self.alert_system else {},
                "strategic_analysis_status": await self.strategic_analyzer.get_analysis_status() if self.strategic_analyzer else {},
                "report_generator_status": await self.report_generator.get_generator_status() if self.report_generator else {}
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown the system."""
        try:
            self.logger.info("Shutting down CompetitorMonitoringSystem...")
            
            # Shutdown components if needed
            if self.agent:
                # Add any cleanup logic here
                pass
            
            self.is_initialized = False
            self.logger.info("CompetitorMonitoringSystem shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")


# Factory functions for easy instantiation
async def create_competitor_monitoring_system(config: Optional[Dict[str, Any]] = None) -> CompetitorMonitoringSystem:
    """Create and initialize a competitor monitoring system."""
    system = CompetitorMonitoringSystem(config)
    await system.initialize()
    return system


def get_system_info() -> Dict[str, Any]:
    """
Get system information."""
    return {
        "name": "Competitor Monitoring Agent",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "components": [
            "CompetitorMonitoringAgent",
            "DataCollectionManager",
            "MarketIntelligenceEngine",
            "AlertSystem",
            "StrategicAnalysisEngine",
            "ConfigurationManager",
            "ReportGenerator"
        ]
    }


# Quick access functions
async def quick_competitor_analysis(competitor_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick competitor analysis with default settings."""
    try:
        system = await create_competitor_monitoring_system()
        
        # Add competitor
        add_result = await system.add_competitor(competitor_data)
        if add_result.get("status") != "success":
            return add_result
        
        competitor_id = add_result.get("competitor_id")
        
        # Analyze competitor
        analysis_result = await system.analyze_competitor(competitor_id)
        
        await system.shutdown()
        return analysis_result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def quick_market_intelligence(segment: str) -> Dict[str, Any]:
    """Quick market intelligence for a segment."""
    try:
        system = await create_competitor_monitoring_system()
        
        result = await system.get_market_intelligence(segment)
        
        await system.shutdown()
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Main entry point for CLI or direct usage
if __name__ == "__main__":
    import argparse
    import json
    
    async def main():
        parser = argparse.ArgumentParser(description="Competitor Monitoring Agent")
        parser.add_argument("--action", choices=["analyze", "market", "status"], required=True,
                          help="Action to perform")
        parser.add_argument("--data", type=str, help="JSON data for analysis")
        parser.add_argument("--segment", type=str, help="Market segment for analysis")
        
        args = parser.parse_args()
        
        if args.action == "status":
            system = await create_competitor_monitoring_system()
            status = await system.get_system_status()
            print(json.dumps(status, indent=2, default=str))
            await system.shutdown()
            
        elif args.action == "analyze" and args.data:
            competitor_data = json.loads(args.data)
            result = await quick_competitor_analysis(competitor_data)
            print(json.dumps(result, indent=2, default=str))
            
        elif args.action == "market" and args.segment:
            result = await quick_market_intelligence(args.segment)
            print(json.dumps(result, indent=2, default=str))
            
        else:
            parser.print_help()
    
    # Run main function
    asyncio.run(main())
