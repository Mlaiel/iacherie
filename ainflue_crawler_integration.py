"""Ainflue Platform Crawlers Integration
=====================================

Integration script showing how to use the main platform crawlers
within the Ainflue content protection ecosystem.
"""

import asyncio
import logging
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AinflueCrawlerManager:
    """
    Manages platform crawlers for the Ainflue content protection system.
    
    Integrates the 10 main platform crawlers with Ainflue's content protection,
    monitoring, and violation detection systems.
    """
    
    def __init__(self):
        """
Initialize the crawler manager."""
        self.orchestrator = None
        self.monitoring_tasks = {}
        self.violation_handlers = []
        self.content_database = []  # Mock database
        
    async def initialize(self):
        """
Initialize the crawler orchestrator."""
        try:
            # Import with proper path resolution
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            crawlers_dir = os.path.join(current_dir, 'crawlers')
            sys.path.insert(0, crawlers_dir)
            
            from main_platform_crawlers import CrawlerOrchestrator
            self.orchestrator = CrawlerOrchestrator()
            
            logger.info("✅ Ainflue Crawler Manager initialized successfully")
            logger.info(f"📱 Supported platforms: {', '.join(self.orchestrator.get_supported_platforms())}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize crawler manager: {e}")
            raise
    
    async def search_protected_content(self, search_terms: List[str], max_results_per_platform: int = 20) -> Dict[str, List[Dict]]:
        """
        Search for protected content across all platforms.
        
        Args:
            search_terms: List of terms to search for
            max_results_per_platform: Maximum results per platform
            
        Returns:
            Dictionary of results by platform
        """
        logger.info(f"🔍 Searching for protected content: {search_terms}")
        
        all_results = {}
        
        for search_term in search_terms:
            logger.info(f"  🔎 Searching for: '{search_term}'")
            
            platform_results = await self.orchestrator.search_all_platforms(
                search_term, 
                max_results=max_results_per_platform
            )
            
            # Process and analyze results
            for platform, results in platform_results.items():
                if platform not in all_results:
                    all_results[platform] = []
                
                for result in results:
                    # Add analysis metadata
                    analyzed_result = {
                        'search_term': search_term,
                        'platform': result.platform,
                        'content_id': result.content_id,
                        'title': result.title,
                        'description': result.description,
                        'url': result.url,
                        'author': result.author,
                        'discovered_at': datetime.now().isoformat(),
                        'similarity_score': self._calculate_content_similarity(search_term, result.title),
                        'risk_level': self._assess_risk_level(result),
                        'metadata': result.metadata,
                        'raw_data': result.raw_data
                    }
                    
                    all_results[platform].append(analyzed_result)
                    
                    # Store in mock database
                    self.content_database.append(analyzed_result)
                
                logger.info(f"    📊 {platform}: {len(results)} results")
        
        logger.info(f"✅ Search completed. Total results: {sum(len(results) for results in all_results.values())}")
        return all_results
    
    async def start_real_time_monitoring(self, protected_content: List[str], platforms: Optional[List[str]] = None):
        """
        Start real-time monitoring for protected content across platforms.
        
        Args:
            protected_content: List of content to monitor
            platforms: Specific platforms to monitor (default: all)
        """
        logger.info(f"🚨 Starting real-time monitoring for: {protected_content}")
        
        if platforms is None:
            platforms = self.orchestrator.get_supported_platforms()
        
        # Start YouTube copyright monitoring
        if 'youtube' in platforms:
            youtube_crawler = await self.orchestrator.get_crawler('youtube')
            if youtube_crawler:
                task = asyncio.create_task(
                    youtube_crawler.monitor_copyright_violations(
                        protected_content, 
                        self._handle_copyright_violation
                    )
                )
                self.monitoring_tasks['youtube_copyright'] = task
                logger.info("  📺 YouTube copyright monitoring started")
        
        # Start Instagram story monitoring (for brand accounts)
        if 'instagram' in platforms:
            instagram_crawler = await self.orchestrator.get_crawler('instagram')
            if instagram_crawler:
                # Monitor stories from competitor or suspicious accounts
                suspicious_accounts = ['competitor1', 'suspicious_user']
                task = asyncio.create_task(
                    instagram_crawler.monitor_stories(
                        suspicious_accounts,
                        self._handle_instagram_story_update
                    )
                )
                self.monitoring_tasks['instagram_stories'] = task
                logger.info("  📸 Instagram story monitoring started")
        
        # Start Twitter real-time monitoring
        if 'twitter' in platforms:
            twitter_crawler = await self.orchestrator.get_crawler('twitter')
            if twitter_crawler:
                task = asyncio.create_task(
                    twitter_crawler.monitor_real_time_stream(
                        protected_content,
                        self._handle_twitter_update
                    )
                )
                self.monitoring_tasks['twitter_stream'] = task
                logger.info("  🐦 Twitter real-time monitoring started")
        
        # Start Facebook page monitoring
        if 'facebook' in platforms:
            facebook_crawler = await self.orchestrator.get_crawler('facebook')
            if facebook_crawler:
                # Monitor competitor pages
                competitor_pages = ['competitor_page1', 'competitor_page2']
                task = asyncio.create_task(
                    facebook_crawler.monitor_pages(
                        competitor_pages,
                        self._handle_facebook_page_update
                    )
                )
                self.monitoring_tasks['facebook_pages'] = task
                logger.info("  📘 Facebook page monitoring started")
        
        # Start Discord server monitoring
        if 'discord' in platforms:
            discord_crawler = await self.orchestrator.get_crawler('discord')
            if discord_crawler:
                # Monitor servers where content might be shared
                target_servers = ['gaming_community', 'content_sharing']
                task = asyncio.create_task(
                    discord_crawler.monitor_servers(
                        target_servers,
                        self._handle_discord_server_update
                    )
                )
                self.monitoring_tasks['discord_servers'] = task
                logger.info("  💬 Discord server monitoring started")
        
        # Start Telegram channel monitoring
        if 'telegram' in platforms:
            telegram_crawler = await self.orchestrator.get_crawler('telegram')
            if telegram_crawler:
                # Monitor channels where content might be shared
                target_channels = ['piracy_channel', 'content_sharing_channel']
                task = asyncio.create_task(
                    telegram_crawler.monitor_channels(
                        target_channels,
                        self._handle_telegram_channel_update
                    )
                )
                self.monitoring_tasks['telegram_channels'] = task
                logger.info("  📱 Telegram channel monitoring started")
        
        logger.info(f"✅ Real-time monitoring started for {len(self.monitoring_tasks)} services")
    
    async def stop_monitoring(self):
        """Stop all monitoring tasks."""
        logger.info("🛑 Stopping all monitoring tasks...")
        
        for service_name, task in self.monitoring_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"  ✅ {service_name} monitoring stopped")
        
        self.monitoring_tasks.clear()
        logger.info("✅ All monitoring stopped")
    
    async def generate_violation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive violation report."""
        logger.info("📊 Generating violation report...")
        
        # Analyze stored content
        high_risk_content = [
            item for item in self.content_database 
            if item.get('risk_level') == 'HIGH'
        ]
        
        medium_risk_content = [
            item for item in self.content_database 
            if item.get('risk_level') == 'MEDIUM'
        ]
        
        # Platform distribution
        platform_stats = {}
        for item in self.content_database:
            platform = item['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {'total': 0, 'high_risk': 0, 'medium_risk': 0}
            
            platform_stats[platform]['total'] += 1
            if item.get('risk_level') == 'HIGH':
                platform_stats[platform]['high_risk'] += 1
            elif item.get('risk_level') == 'MEDIUM':
                platform_stats[platform]['medium_risk'] += 1
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_content_monitored': len(self.content_database),
                'high_risk_violations': len(high_risk_content),
                'medium_risk_violations': len(medium_risk_content),
                'platforms_monitored': len(platform_stats)
            },
            'platform_breakdown': platform_stats,
            'high_risk_content': high_risk_content[:10],  # Top 10
            'recommendations': self._generate_recommendations(high_risk_content, medium_risk_content)
        }
        
        logger.info(f"📋 Report generated: {report['summary']}")
        return report
    
    def _calculate_content_similarity(self, protected_term: str, content_title: str) -> float:
        """Calculate similarity between protected content and found content."""
        # Simple Jaccard similarity
        words1 = set(protected_term.lower().split())
        words2 = set(content_title.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _assess_risk_level(self, result) -> str:
        """
Assess the risk level of found content."""
        # Simple risk assessment based on title similarity
        if hasattr(result, 'title') and result.title:
            # Check for exact matches or high similarity patterns
            title_lower = result.title.lower()
            
            # High risk indicators
            high_risk_terms = ['download', 'free', 'pirated', 'cracked', 'leaked']
            if any(term in title_lower for term in high_risk_terms):
                return 'HIGH'
            
            # Medium risk indicators
            medium_risk_terms = ['share', 'watch', 'stream', 'online']
            if any(term in title_lower for term in medium_risk_terms):
                return 'MEDIUM'
        
        return 'LOW'
    
    def _generate_recommendations(self, high_risk: List[Dict], medium_risk: List[Dict]) -> List[str]:
        """
Generate recommendations based on violations found."""
        recommendations = []
        
        if high_risk:
            recommendations.append(f"🚨 {len(high_risk)} high-risk violations detected - immediate action required")
            recommendations.append("📋 Review high-risk content for DMCA takedown requests")
        
        if medium_risk:
            recommendations.append(f"⚠️ {len(medium_risk)} medium-risk items require monitoring")
            recommendations.append("👀 Increase monitoring frequency for suspicious accounts")
        
        if len(high_risk) + len(medium_risk) > 50:
            recommendations.append("🤖 Consider implementing automated takedown procedures")
        
        recommendations.append("📈 Regular monitoring and reporting should continue")
        
        return recommendations
    
    # Event handlers for different platform updates
    async def _handle_copyright_violation(self, violation):
        """Handle YouTube copyright violations."""
        logger.warning(f"🚨 COPYRIGHT VIOLATION: {violation['type']}")
        logger.warning(f"  Content: {violation['content'].title}")
        logger.warning(f"  Similarity: {violation['similarity_score']:.2%}")
        logger.warning(f"  URL: {violation['content'].url}")
        
        # Add to database with HIGH risk
        violation_record = {
            'type': 'copyright_violation',
            'platform': violation['platform'],
            'content': violation['content'].__dict__,
            'similarity_score': violation['similarity_score'],
            'detected_at': datetime.now().isoformat(),
            'risk_level': 'HIGH'
        }
        self.content_database.append(violation_record)
    
    async def _handle_instagram_story_update(self, update):
        """Handle Instagram story updates."""
        logger.info(f"📸 Instagram story update: {update['type']} for {update['user_id']}")
    
    async def _handle_twitter_update(self, update):
        """Handle Twitter real-time updates."""
        logger.info(f"🐦 Twitter update: {update['type']} for '{update['keyword']}'")
        logger.info(f"  Found {len(update['results'])} new tweets")
    
    async def _handle_facebook_page_update(self, update):
        """Handle Facebook page updates."""
        logger.info(f"📘 Facebook page update: {update['type']} for {update['page_id']}")
    
    async def _handle_discord_server_update(self, update):
        """Handle Discord server updates."""
        logger.info(f"💬 Discord server update: {update['type']} for {update['server_id']}")
    
    async def _handle_telegram_channel_update(self, update):
        """Handle Telegram channel updates."""
        logger.info(f"📱 Telegram channel update: {update['type']} for {update['channel_id']}")


async def demo_ainflue_integration():
    """Demonstrate the Ainflue crawler integration."""
    logger.info("🚀 Starting Ainflue Platform Crawlers Integration Demo")
    logger.info("=" * 60)
    
    # Initialize the manager
    manager = AinflueCrawlerManager()
    await manager.initialize()
    
    # Define protected content
    protected_content = [
        "My Exclusive Song",
        "Protected Video Content",
        "Brand Name Product"
    ]
    
    logger.info(f"🛡️ Protected content: {protected_content}")
    
    try:
        # 1. Search for existing violations
        logger.info("\n📍 Phase 1: Searching for existing violations")
        search_results = await manager.search_protected_content(protected_content, max_results_per_platform=5)
        
        # 2. Start real-time monitoring
        logger.info("\n📍 Phase 2: Starting real-time monitoring")
        await manager.start_real_time_monitoring(protected_content)
        
        # 3. Let monitoring run for a short period
        logger.info("\n📍 Phase 3: Monitoring for 10 seconds...")
        await asyncio.sleep(10)
        
        # 4. Generate violation report
        logger.info("\n📍 Phase 4: Generating violation report")
        report = await manager.generate_violation_report()
        
        # Display report summary
        logger.info(f"\n📊 VIOLATION REPORT SUMMARY:")
        logger.info(f"  Total content monitored: {report['summary']['total_content_monitored']}")
        logger.info(f"  High-risk violations: {report['summary']['high_risk_violations']}")
        logger.info(f"  Medium-risk violations: {report['summary']['medium_risk_violations']}")
        logger.info(f"  Platforms monitored: {report['summary']['platforms_monitored']}")
        
        logger.info(f"\n📋 RECOMMENDATIONS:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            logger.info(f"  {i}. {recommendation}")
        
        # 5. Stop monitoring
        logger.info("\n📍 Phase 5: Stopping monitoring")
        await manager.stop_monitoring()
        
        logger.info("\n✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        await manager.stop_monitoring()
        raise


if __name__ == "__main__":
    asyncio.run(demo_ainflue_integration())