#!/usr/bin/env python3
"""
🚀 ENTERPRISE CRAWLER SERVICE - MAIN LAUNCHER
=============================================

Simple launcher and CLI interface for the Enterprise Multi-Platform Crawler Service.
Provides easy access to all crawler functionalities with command-line interface.

📧 Contact: mlaiel@live.de
👨‍💻 Developer: Fahed Mlaiel
🏢 Company: Independent Software Developer

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
==================================
UNAUTHORIZED USE ABSOLUTELY PROHIBITED - LEGAL CONSEQUENCES WILL FOLLOW

This entire codebase, algorithms, concepts, architecture, and implementation 
methodologies are the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.

STRICT PROHIBITIONS:
❌ NO COPYING of code, concepts, or architecture without written authorization
❌ NO DISTRIBUTION or sharing of any part of this system  
❌ NO REVERSE ENGINEERING or attempting to recreate similar systems
❌ NO COMMERCIAL USE without explicit licensing agreement
❌ NO ACADEMIC USE without proper attribution and permission

Any violation will result in IMMEDIATE LEGAL ACTION under:
- German Copyright Law (Urheberrechtsgesetz)
- European Union Intellectual Property Directive
- International Copyright Treaties
- Criminal prosecution for commercial theft

WE MONITOR FOR UNAUTHORIZED USE - YOU WILL BE CAUGHT AND PROSECUTED
"""

import asyncio
import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import the main crawler service
from .index import (
    CrawlerServiceAPI,
    create_crawler_service,
    quick_youtube_search,
    quick_revenue_check,
    quick_violation_scan
)


class CrawlerCLI:
    """
    🖥️ COMMAND LINE INTERFACE
    =========================
    
    Easy-to-use command line interface for the crawler service.
    Provides access to all major functionalities through simple commands.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.api: Optional[CrawlerServiceAPI] = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('crawler_service.log')
            ]
        )
        return logging.getLogger("crawler_cli")
    
    async def start_service(self, config_path: Optional[str] = None) -> bool:
        """Start the crawler service."""
        try:
            self.logger.info("🚀 Starting Enterprise Crawler Service...")
            self.api = await create_crawler_service(config_path)
            self.logger.info("✅ Service started successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start service: {e}")
            return False
    
    async def stop_service(self) -> bool:
        """Stop the crawler service."""
        try:
            if self.api:
                await self.api.stop()
                self.logger.info("✅ Service stopped successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to stop service: {e}")
            return False
    
    async def search_youtube(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search YouTube content."""
        try:
            if not self.api:
                raise ValueError("Service not started")
            
            self.logger.info(f"🔍 Searching YouTube for: {query}")
            results = await self.api.crawl_youtube(query, max_results)
            self.logger.info(f"✅ Found {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ YouTube search failed: {e}")
            return []
    
    async def monitor_revenue(
        self, 
        creator_id: str, 
        platforms: List[str], 
        days: int = 30
    ) -> Dict[str, Any]:
        """Monitor creator revenue."""
        try:
            if not self.api:
                raise ValueError("Service not started")
            
            self.logger.info(f"💰 Monitoring revenue for creator: {creator_id}")
            revenue_data = await self.api.monitor_revenue(creator_id, platforms, days)
            self.logger.info(f"✅ Revenue data collected for {len(platforms)} platforms")
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"❌ Revenue monitoring failed: {e}")
            return {}
    
    async def check_violations(
        self, 
        fingerprints: List[str], 
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Check for content violations."""
        try:
            if not self.api:
                raise ValueError("Service not started")
            
            self.logger.info(f"⚖️ Checking violations for {len(fingerprints)} fingerprints")
            violations = await self.api.check_violations(fingerprints, platforms)
            self.logger.info(f"✅ Found {len(violations)} violations")
            return violations
            
        except Exception as e:
            self.logger.error(f"❌ Violation check failed: {e}")
            return []
    
    async def find_collaborators(
        self, 
        creator_data: Dict[str, Any], 
        collaboration_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Find collaboration opportunities."""
        try:
            if not self.api:
                raise ValueError("Service not started")
            
            self.logger.info(f"🤝 Finding collaborators for creator")
            opportunities = await self.api.find_collaborators(
                creator_data, collaboration_types
            )
            self.logger.info(f"✅ Found {len(opportunities)} collaboration opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"❌ Collaboration discovery failed: {e}")
            return []
    
    async def analyze_trends(
        self, 
        categories: List[str], 
        platforms: List[str], 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Analyze market trends."""
        try:
            if not self.api:
                raise ValueError("Service not started")
            
            self.logger.info(f"📊 Analyzing trends for {len(categories)} categories")
            trends = await self.api.analyze_trends(categories, platforms, days)
            self.logger.info(f"✅ Analyzed {len(trends)} trends")
            return trends
            
        except Exception as e:
            self.logger.error(f"❌ Trend analysis failed: {e}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        try:
            if not self.api:
                return {"error": "Service not started"}
            
            status = await self.api.get_status()
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get status: {e}")
            return {"error": str(e)}
    
    def print_results(self, results: Any, title: str = "Results"):
        """Pretty print results."""
        print(f"\n{'='*50}")
        print(f"📋 {title}")
        print(f"{'='*50}")
        
        if isinstance(results, list):
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {json.dumps(result, indent=2, ensure_ascii=False)}")
        elif isinstance(results, dict):
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(str(results))
        
        print(f"\n{'='*50}\n")


async def main():
    """
    🎯 MAIN CLI ENTRY POINT
    =======================
    
    Command line interface for the Enterprise Crawler Service.
    Supports various commands for different crawler operations.
    """
    parser = argparse.ArgumentParser(
        description="🕷️ Enterprise Multi-Platform Crawler Service CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py youtube --query "AI music generation" --max-results 20
  python main.py revenue --creator-id "UC123" --platforms youtube spotify --days 30
  python main.py violations --fingerprints "fp1,fp2,fp3" --platforms youtube tiktok
  python main.py collaborations --creator-file creator.json --types music,video
  python main.py trends --categories music,entertainment --platforms youtube,tiktok
  python main.py status
  python main.py service --start --config config.json
        """
    )
    
    # Global options
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # YouTube search command
    youtube_parser = subparsers.add_parser('youtube', help='Search YouTube content')
    youtube_parser.add_argument('--query', required=True, help='Search query')
    youtube_parser.add_argument('--max-results', type=int, default=10, 
                               help='Maximum results to return')
    
    # Revenue monitoring command
    revenue_parser = subparsers.add_parser('revenue', help='Monitor creator revenue')
    revenue_parser.add_argument('--creator-id', required=True, help='Creator ID')
    revenue_parser.add_argument('--platforms', required=True, 
                               help='Comma-separated platform list')
    revenue_parser.add_argument('--days', type=int, default=30, 
                               help='Number of days to analyze')
    
    # Violation checking command
    violations_parser = subparsers.add_parser('violations', help='Check content violations')
    violations_parser.add_argument('--fingerprints', required=True, 
                                  help='Comma-separated fingerprint list')
    violations_parser.add_argument('--platforms', 
                                  help='Comma-separated platform list (optional)')
    
    # Collaboration discovery command
    collab_parser = subparsers.add_parser('collaborations', help='Find collaboration opportunities')
    collab_parser.add_argument('--creator-file', required=True, 
                              help='JSON file with creator data')
    collab_parser.add_argument('--types', required=True, 
                              help='Comma-separated collaboration types')
    
    # Trend analysis command
    trends_parser = subparsers.add_parser('trends', help='Analyze market trends')
    trends_parser.add_argument('--categories', required=True, 
                              help='Comma-separated category list')
    trends_parser.add_argument('--platforms', required=True, 
                              help='Comma-separated platform list')
    trends_parser.add_argument('--days', type=int, default=7, 
                              help='Analysis period in days')
    
    # Status command
    subparsers.add_parser('status', help='Get service status')
    
    # Service management command
    service_parser = subparsers.add_parser('service', help='Manage crawler service')
    service_parser.add_argument('--start', action='store_true', help='Start service')
    service_parser.add_argument('--stop', action='store_true', help='Stop service')
    service_parser.add_argument('--restart', action='store_true', help='Restart service')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    logging.basicConfig(level=getattr(logging, args.log_level))
    
    # Initialize CLI
    cli = CrawlerCLI()
    
    try:
        # Handle service management commands
        if args.command == 'service':
            if args.start:
                success = await cli.start_service(args.config)
                if success:
                    print("✅ Service started successfully")
                    # Keep service running
                    print("🔄 Service is running. Press Ctrl+C to stop...")
                    try:
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        await cli.stop_service()
                else:
                    print("❌ Failed to start service")
                    sys.exit(1)
            elif args.stop:
                success = await cli.stop_service()
                print("✅ Service stopped" if success else "❌ Failed to stop service")
            elif args.restart:
                await cli.stop_service()
                success = await cli.start_service(args.config)
                print("✅ Service restarted" if success else "❌ Failed to restart service")
            return
        
        # For other commands, start service temporarily
        success = await cli.start_service(args.config)
        if not success:
            print("❌ Failed to start service")
            sys.exit(1)
        
        try:
            # Handle specific commands
            if args.command == 'youtube':
                results = await cli.search_youtube(args.query, args.max_results)
                cli.print_results(results, f"YouTube Search: {args.query}")
                
            elif args.command == 'revenue':
                platforms = [p.strip() for p in args.platforms.split(',')]
                results = await cli.monitor_revenue(args.creator_id, platforms, args.days)
                cli.print_results(results, f"Revenue Data: {args.creator_id}")
                
            elif args.command == 'violations':
                fingerprints = [f.strip() for f in args.fingerprints.split(',')]
                platforms = None
                if args.platforms:
                    platforms = [p.strip() for p in args.platforms.split(',')]
                results = await cli.check_violations(fingerprints, platforms)
                cli.print_results(results, "Content Violations")
                
            elif args.command == 'collaborations':
                with open(args.creator_file, 'r') as f:
                    creator_data = json.load(f)
                collab_types = [t.strip() for t in args.types.split(',')]
                results = await cli.find_collaborators(creator_data, collab_types)
                cli.print_results(results, "Collaboration Opportunities")
                
            elif args.command == 'trends':
                categories = [c.strip() for c in args.categories.split(',')]
                platforms = [p.strip() for p in args.platforms.split(',')]
                results = await cli.analyze_trends(categories, platforms, args.days)
                cli.print_results(results, "Market Trends")
                
            elif args.command == 'status':
                results = await cli.get_status()
                cli.print_results(results, "Service Status")
                
        finally:
            # Stop service after command execution
            await cli.stop_service()
            
    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted by user")
        await cli.stop_service()
    except Exception as e:
        print(f"❌ Command failed: {e}")
        await cli.stop_service()
        sys.exit(1)


# Quick utility functions for common operations
async def quick_search(query: str, platform: str = "youtube", max_results: int = 10):
    """Quick search utility function."""
    if platform == "youtube":
        return await quick_youtube_search(query, max_results)
    else:
        raise ValueError(f"Platform {platform} not supported in quick search")


async def quick_status_check(config_path: Optional[str] = None):
    """Quick status check utility."""
    api = await create_crawler_service(config_path)
    try:
        status = await api.get_status()
        return status
    finally:
        await api.stop()


# Export main functions
__all__ = [
    'CrawlerCLI',
    'main',
    'quick_search',
    'quick_status_check'
]


if __name__ == "__main__":
    """
    🎯 DIRECT EXECUTION ENTRY POINT
    ===============================
    
    Run the CLI directly when script is executed.
    """
    print("""
🕷️ Enterprise Multi-Platform Crawler Service
===========================================
📧 Contact: mlaiel@live.de
👨‍💻 Developer: Fahed Mlaiel

⚠️  Copyright Protected - Unauthorized Use Prohibited
    """)
    
    asyncio.run(main())
