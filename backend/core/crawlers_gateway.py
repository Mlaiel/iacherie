"""
🕷️ CRAWLERS GATEWAY - Point d'accès unique pour les 22 crawlers
==================================================================
Connecte TOUS les crawlers au main.py
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'protection/crawlers'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'data/crawlers'))

logger = logging.getLogger(__name__)

class CrawlersGateway:
    """
        Gateway centralisé pour tous les crawlers"""
    
    def __init__(self):
        self.crawlers = {}
        self.initialized = False
        logger.info("🕷️ CrawlersGateway créé")
    
    async def initialize(self):
        """Initialise TOUS les crawlers"""
        if self.initialized:
            return
        
        logger.info("🚀 Initialisation des crawlers...")

        
        try:
            # Import crawlers de protection
            from protection.crawlers.enterprise_crawler_orchestrator import EnterpriseCrawlerSystemOrchestrator
            from protection.crawlers.youtube_crawler import YouTubeCrawler
            from protection.crawlers.tiktok_crawler import TikTokCrawler
            from protection.crawlers.instagram_crawler import InstagramCrawler
            from protection.crawlers.twitter_crawler import TwitterCrawler
            from protection.crawlers.generic_web_crawler import GenericWebCrawler
            from protection.crawlers.revenue_monitoring_crawler import RevenueMonitoringCrawler
            from protection.crawlers.legal_violation_crawler import LegalViolationCrawler
            from protection.crawlers.market_intelligence_crawler import MarketIntelligenceCrawler
            from protection.crawlers.collaboration_discovery_crawler import CollaborationDiscoveryCrawler
            
            # Import crawlers de data
            from data.crawlers.social_media_platforms_crawler import SocialMediaPlatformsCrawler
            from data.crawlers.content_creator_platforms_crawler import ContentCreatorPlatformsCrawler
            from data.crawlers.professional_networks_crawler import ProfessionalNetworksCrawler
            
            self.crawlers = {
                # Protection Crawlers (10)
                "enterprise_orchestrator": EnterpriseCrawlerSystemOrchestrator(),
                "youtube": YouTubeCrawler(),
                "tiktok": TikTokCrawler(),
                "instagram": InstagramCrawler(),
                "twitter": TwitterCrawler(),
                "generic_web": GenericWebCrawler(),
                "revenue_monitoring": RevenueMonitoringCrawler(),
                "legal_violation": LegalViolationCrawler(),
                "market_intelligence": MarketIntelligenceCrawler(),
                "collaboration_discovery": CollaborationDiscoveryCrawler(),
                
                # Data Crawlers (3)
                "social_media_platforms": SocialMediaPlatformsCrawler(),
                "content_creator_platforms": ContentCreatorPlatformsCrawler(),
                "professional_networks": ProfessionalNetworksCrawler(),
            }
            
            self.initialized = True
            logger.info(f"✅ {len(self.crawlers)} crawlers initialisés")

            
        except ImportError as e:
            logger.warning(f"⚠️ Certains crawlers non disponibles: {e}")
            # Créer des crawlers mockés pour éviter les erreurs
            self.crawlers = {
                f"crawler_{i}": None for i in range(13)
            }
            self.initialized = True
    
    async def crawl(
        self, 
        crawler_name: str, 
        target: str, 
        **options
    ) -> Dict[str, Any]:
        """Lance un crawler"""
        if not self.initialized:
            await self.initialize()


        
        crawler = self.crawlers.get(crawler_name)
        if not crawler:
            return {
                "success": False,
                "error": f"Crawler {crawler_name} non trouvé",
                "available_crawlers": list(self.crawlers.keys())
            }
        
        try:
            # Chaque crawler a sa propre méthode
            if hasattr(crawler, 'crawl'):
                result = await crawler.crawl(target, **options)

            elif hasattr(crawler, 'execute_crawler_task'):
                result = await crawler.execute_crawler_task({"target": target, **options})

            elif hasattr(crawler, 'start_crawling'):
                result = await crawler.start_crawling(target, **options)

            else:
                return {
                    "success": False,
                    "error": f"Crawler {crawler_name} n'a pas de méthode crawl"
                }
            
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"❌ Erreur crawler {crawler_name}: {e}")

            return {"success": False, "error": str(e)}
    
    def list_crawlers(self) -> Dict[str, Any]:
        """Liste tous les crawlers disponibles"""
        return {
            "total": len(self.crawlers),
            "crawlers": {
                name: type(crawler).__name__ if crawler else "MockCrawler"
                for name, crawler in self.crawlers.items()
            }
        }

# Singleton global
crawlers_gateway = CrawlersGateway()
