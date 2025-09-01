#!/usr/bin/env python3
"""🚀 Industrialization Metrics Startup Script
==============================================

Startup script to initialize and run the industrialization success metrics
monitoring system as part of the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import asyncio
import logging
import signal
from pathlib import Path

# Add monitoring directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitoring'))

try:
    from monitoring.industrialization_metrics_integration import integration
    from monitoring.industrialization_dashboard import industrialization_dashboard
    from monitoring.industrialization_success_metrics import industrialization_metrics
except ImportError as e:
    print(f"Failed to import industrialization metrics: {e}")
    print("Please ensure all dependencies are installed and paths are correct.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/industrialization_metrics.log')
    ]
)

logger = logging.getLogger(__name__)


class IndustrializationMetricsService:
    """Service to run industrialization metrics monitoring"""
    
    def __init__(self):
        self.running = False
        self.integration = integration
        
    async def start(self):
        """Start the industrialization metrics service"""
        logger.info("🚀 Starting Industrialization Metrics Service...")
        
        try:
            # Start metrics collection
            self.running = True
            
            # Run initial data collection
            await self.integration.collect_and_update_metrics()
            logger.info("✅ Initial metrics collection completed")
            
            # Generate initial dashboard
            dashboard_path = "/tmp/industrialization_dashboard.html"
            await self.integration.export_dashboard_html(dashboard_path)
            logger.info(f"📊 Initial dashboard generated: {dashboard_path}")
            
            # Start continuous monitoring
            logger.info("🔄 Starting continuous monitoring (5-minute intervals)...")
            await self.integration.start_monitoring(interval=300)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Received shutdown signal")
        except Exception as e:
            logger.error(f"❌ Error in metrics service: {str(e)}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the industrialization metrics service"""
        logger.info("🛑 Stopping Industrialization Metrics Service...")
        self.running = False
        self.integration.stop_monitoring()
        logger.info("✅ Service stopped")
    
    async def generate_report(self):
        """Generate a one-time industrialization report"""
        logger.info("📈 Generating industrialization report...")
        
        try:
            # Collect latest metrics
            await self.integration.collect_and_update_metrics()
            
            # Generate full report
            report = await self.integration.generate_full_report()
            
            # Export dashboard
            dashboard_path = "/tmp/industrialization_dashboard.html"
            await self.integration.export_dashboard_html(dashboard_path)
            
            # Get status summary
            summary = await self.integration.get_kpi_status_summary()
            
            print("\n" + "="*80)
            print("📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION - RAPPORT")
            print("="*80)
            print(f"Score Global d'Industrialisation: {summary['overall_score']:.1f}%")
            print(f"Score KPIs Techniques: {summary['technical_score']:.1f}%")
            print(f"Score KPIs Business: {summary['business_score']:.1f}%")
            print(f"KPIs Atteints: {summary['kpis_on_target']}/{summary['total_kpis']}")
            print(f"Alertes Actives: {summary['active_alerts']} (Critiques: {summary['critical_alerts']})")
            print(f"Dashboard HTML: {dashboard_path}")
            print("="*80)
            
            # Show recommendations
            if report.get('recommendations'):
                print("\n📋 RECOMMANDATIONS:")
                for rec in report['recommendations']:
                    print(f"  • {rec}")
            
            logger.info("✅ Report generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {str(e)}")
            raise


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    service = IndustrializationMetricsService()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "report":
            # Generate one-time report
            await service.generate_report()
        elif command == "start":
            # Start continuous monitoring
            await service.start()
        elif command == "help":
            print_help()
        else:
            print(f"Unknown command: {command}")
            print_help()
            sys.exit(1)
    else:
        # Default: generate report
        await service.generate_report()


def print_help():
    """Print usage help"""
    print("""
🚀 Industrialization Metrics Service

Usage:
    python start_industrialization_metrics.py [command]

Commands:
    report  - Generate one-time metrics report and dashboard (default)
    start   - Start continuous monitoring service
    help    - Show this help message

Examples:
    python start_industrialization_metrics.py report
    python start_industrialization_metrics.py start
    """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {str(e)}")
        sys.exit(1)