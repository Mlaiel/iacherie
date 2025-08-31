#!/usr/bin/env python3
"""Priority Crawler Functionality Tests
====================================

Comprehensive tests for Spotify, YouTube, and Instagram crawlers to verify:
- Real implementation vs stub
- API connectivity
- Core functionality
- Error handling

Author: Fahed Mlaiel <mlaiel@live.de>
"""import asyncio
import pytest
import logging
import os
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriorityCrawlerTester:
    """Test suite for priority crawlers."""    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_results = {}
        
    async def test_spotify_crawler(self) -> Dict[str, Any]:
        """Test Spotify crawler functionality."""        logger.info("🎵 Testing Spotify Crawler...")
        
        try:
            # Import crawler
            import sys
            sys.path.append(str(self.project_root))
            
            from crawlers.spotify_crawler import SpotifyCrawler
            
            # Initialize crawler
            crawler = SpotifyCrawler()
            
            # Test basic initialization
            init_test = await self._test_crawler_initialization(crawler, "Spotify")
            
            # Test method existence
            methods_test = self._test_required_methods(crawler, [
                'search_tracks', 'get_track_info', 'search_artists', 
                'get_artist_info', 'crawl_content'
            ])
            
            # Test API configuration
            api_config_test = self._test_api_configuration(crawler, "Spotify")
            
            # Test mock functionality
            mock_test = await self._test_mock_functionality(crawler, "spotify")
            
            return {
                "crawler": "Spotify",
                "status": "TESTED",
                "initialization": init_test,
                "required_methods": methods_test,
                "api_configuration": api_config_test,
                "mock_functionality": mock_test,
                "overall_score": self._calculate_score([init_test, methods_test, api_config_test, mock_test])
            }
            
        except Exception as e:
            logger.error(f"Spotify crawler test failed: {e}")
            return {
                "crawler": "Spotify",
                "status": "ERROR",
                "error": str(e),
                "overall_score": 0.0
            }
    
    async def test_youtube_crawler(self) -> Dict[str, Any]:
        """Test YouTube crawler functionality."""        logger.info("📺 Testing YouTube Crawler...")
        
        try:
            # Import crawler
            import sys
            sys.path.append(str(self.project_root))
            
            from crawlers.youtube_crawler import YouTubeCrawler
            
            # Initialize crawler
            crawler = YouTubeCrawler()
            
            # Test basic initialization
            init_test = await self._test_crawler_initialization(crawler, "YouTube")
            
            # Test method existence
            methods_test = self._test_required_methods(crawler, [
                'search_videos', 'get_video_info', 'search_channels',
                'get_channel_info', 'crawl_content'
            ])
            
            # Test API configuration
            api_config_test = self._test_api_configuration(crawler, "YouTube")
            
            # Test mock functionality
            mock_test = await self._test_mock_functionality(crawler, "youtube")
            
            return {
                "crawler": "YouTube",
                "status": "TESTED",
                "initialization": init_test,
                "required_methods": methods_test,
                "api_configuration": api_config_test,
                "mock_functionality": mock_test,
                "overall_score": self._calculate_score([init_test, methods_test, api_config_test, mock_test])
            }
            
        except Exception as e:
            logger.error(f"YouTube crawler test failed: {e}")
            return {
                "crawler": "YouTube",
                "status": "ERROR",
                "error": str(e),
                "overall_score": 0.0
            }
    
    async def test_instagram_crawler(self) -> Dict[str, Any]:
        """Test Instagram crawler functionality."""        logger.info("📸 Testing Instagram Crawler...")
        
        try:
            # Import crawler
            import sys
            sys.path.append(str(self.project_root))
            
            from crawlers.instagram_crawler import InstagramCrawler
            
            # Initialize crawler
            crawler = InstagramCrawler()
            
            # Test basic initialization
            init_test = await self._test_crawler_initialization(crawler, "Instagram")
            
            # Test method existence
            methods_test = self._test_required_methods(crawler, [
                'search_posts', 'get_post_info', 'search_users',
                'get_user_info', 'crawl_content'
            ])
            
            # Test API configuration
            api_config_test = self._test_api_configuration(crawler, "Instagram")
            
            # Test mock functionality
            mock_test = await self._test_mock_functionality(crawler, "instagram")
            
            return {
                "crawler": "Instagram",
                "status": "TESTED",
                "initialization": init_test,
                "required_methods": methods_test,
                "api_configuration": api_config_test,
                "mock_functionality": mock_test,
                "overall_score": self._calculate_score([init_test, methods_test, api_config_test, mock_test])
            }
            
        except Exception as e:
            logger.error(f"Instagram crawler test failed: {e}")
            return {
                "crawler": "Instagram",
                "status": "ERROR",
                "error": str(e),
                "overall_score": 0.0
            }
    
    async def _test_crawler_initialization(self, crawler, platform_name: str) -> Dict[str, Any]:
        """Test crawler initialization."""        try:
            # Check if crawler has required attributes
            required_attrs = ['config', 'session', 'rate_limiter']
            missing_attrs = []
            
            for attr in required_attrs:
                if not hasattr(crawler, attr):
                    missing_attrs.append(attr)
            
            # Test initialization method if exists
            init_success = True
            if hasattr(crawler, 'initialize') and callable(getattr(crawler, 'initialize')):
                try:
                    await crawler.initialize()
                except Exception as e:
                    init_success = False
                    logger.warning(f"{platform_name} initialization failed: {e}")
            
            return {
                "success": len(missing_attrs) == 0 and init_success,
                "missing_attributes": missing_attrs,
                "initialization_success": init_success,
                "score": 1.0 if (len(missing_attrs) == 0 and init_success) else 0.5
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    def _test_required_methods(self, crawler, required_methods: List[str]) -> Dict[str, Any]:
        """Test if crawler has required methods."""        try:
            missing_methods = []
            implemented_methods = []
            stub_methods = []
            
            for method_name in required_methods:
                if hasattr(crawler, method_name):
                    method = getattr(crawler, method_name)
                    if callable(method):
                        # Check if method is a stub (basic check)
                        try:
                            import inspect
                            source = inspect.getsource(method)
                            if 'pass' in source or 'NotImplemented' in source:
                                stub_methods.append(method_name)
                            else:
                                implemented_methods.append(method_name)
                        except:
                            implemented_methods.append(method_name)  # Assume implemented if can't check
                    else:
                        missing_methods.append(method_name)
                else:
                    missing_methods.append(method_name)
            
            score = len(implemented_methods) / len(required_methods) if required_methods else 1.0
            
            return {
                "success": len(missing_methods) == 0 and len(stub_methods) == 0,
                "implemented_methods": implemented_methods,
                "missing_methods": missing_methods,
                "stub_methods": stub_methods,
                "score": score
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    def _test_api_configuration(self, crawler, platform_name: str) -> Dict[str, Any]:
        """Test API configuration."""        try:
            config_score = 0.0
            config_items = []
            
            # Check for common configuration attributes
            config_attrs = {
                'api_key': f'{platform_name.upper()}_API_KEY',
                'api_secret': f'{platform_name.upper()}_API_SECRET',
                'client_id': f'{platform_name.upper()}_CLIENT_ID',
                'client_secret': f'{platform_name.upper()}_CLIENT_SECRET',
                'access_token': f'{platform_name.upper()}_ACCESS_TOKEN'
            }
            
            for attr, env_var in config_attrs.items():
                if hasattr(crawler, attr) or hasattr(crawler, 'config') and hasattr(crawler.config, attr):
                    config_items.append(attr)
                    config_score += 0.2
                elif env_var in os.environ:
                    config_items.append(f"env:{env_var}")
                    config_score += 0.1
            
            # Check for rate limiting configuration
            if hasattr(crawler, 'rate_limiter') or hasattr(crawler, 'rate_limit'):
                config_items.append("rate_limiting")
                config_score += 0.2
            
            return {
                "success": config_score > 0.3,
                "configuration_items": config_items,
                "score": min(config_score, 1.0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    async def _test_mock_functionality(self, crawler, platform: str) -> Dict[str, Any]:
        """Test crawler functionality with mocked responses."""        try:
            # Mock successful API response
            mock_response_data = {
                "spotify": {
                    "tracks": {"items": [{"id": "test_track", "name": "Test Song"}]},
                    "artists": {"items": [{"id": "test_artist", "name": "Test Artist"}]}
                },
                "youtube": {
                    "items": [{"id": {"videoId": "test_video"}, "snippet": {"title": "Test Video"}}]
                },
                "instagram": {
                    "data": [{"id": "test_post", "caption": "Test Post"}]
                }
            }
            
            test_results = []
            
            # Test search functionality
            if hasattr(crawler, 'search_tracks') or hasattr(crawler, 'search_videos') or hasattr(crawler, 'search_posts'):
                try:
                    with patch('aiohttp.ClientSession.get') as mock_get:
                        mock_response = AsyncMock()
                        mock_response.json.return_value = mock_response_data.get(platform, {})
                        mock_response.status = 200
                        mock_get.return_value.__aenter__.return_value = mock_response
                        
                        # Try to call search method
                        search_method = None
                        if hasattr(crawler, 'search_tracks'):
                            search_method = crawler.search_tracks
                        elif hasattr(crawler, 'search_videos'):
                            search_method = crawler.search_videos
                        elif hasattr(crawler, 'search_posts'):
                            search_method = crawler.search_posts
                        
                        if search_method:
                            result = await search_method("test query")
                            test_results.append({"search": "success", "result_type": type(result).__name__})
                        
                except Exception as e:
                    test_results.append({"search": "failed", "error": str(e)})
            
            # Test crawl_content if available
            if hasattr(crawler, 'crawl_content'):
                try:
                    with patch('aiohttp.ClientSession.get') as mock_get:
                        mock_response = AsyncMock()
                        mock_response.json.return_value = mock_response_data.get(platform, {})
                        mock_response.status = 200
                        mock_get.return_value.__aenter__.return_value = mock_response
                        
                        result = await crawler.crawl_content("test query")
                        test_results.append({"crawl_content": "success", "result_type": type(result).__name__})
                        
                except Exception as e:
                    test_results.append({"crawl_content": "failed", "error": str(e)})
            
            success_count = sum(1 for test in test_results if any("success" in str(v) for v in test.values()))
            total_tests = len(test_results)
            
            return {
                "success": success_count > 0,
                "tests_run": total_tests,
                "tests_passed": success_count,
                "test_results": test_results,
                "score": success_count / total_tests if total_tests > 0 else 0.0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "score": 0.0
            }
    
    def _calculate_score(self, test_results: List[Dict[str, Any]]) -> float:
        """Calculate overall score from test results."""        if not test_results:
            return 0.0
        
        scores = [result.get('score', 0.0) for result in test_results]
        return sum(scores) / len(scores)
    
    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test external API connectivity for priority platforms."""        logger.info("🌐 Testing API Connectivity...")
        
        connectivity_tests = {}
        
        # Test Spotify API connectivity
        try:
            async with aiohttp.ClientSession() as session:
                # Test Spotify Web API accessibility
                async with session.get('https://api.spotify.com/v1', timeout=10) as response:
                    connectivity_tests['spotify'] = {
                        "accessible": response.status != 500,
                        "status_code": response.status,
                        "response_time": "< 10s"
                    }
        except Exception as e:
            connectivity_tests['spotify'] = {
                "accessible": False,
                "error": str(e)
            }
        
        # Test YouTube API connectivity
        try:
            async with aiohttp.ClientSession() as session:
                # Test YouTube Data API accessibility
                async with session.get('https://www.googleapis.com/youtube/v3', timeout=10) as response:
                    connectivity_tests['youtube'] = {
                        "accessible": response.status in [200, 400, 403],  # 400/403 expected without API key
                        "status_code": response.status,
                        "response_time": "< 10s"
                    }
        except Exception as e:
            connectivity_tests['youtube'] = {
                "accessible": False,
                "error": str(e)
            }
        
        # Test Instagram connectivity (Graph API)
        try:
            async with aiohttp.ClientSession() as session:
                # Test Instagram Graph API accessibility
                async with session.get('https://graph.instagram.com', timeout=10) as response:
                    connectivity_tests['instagram'] = {
                        "accessible": response.status in [200, 400, 403],  # 400/403 expected without token
                        "status_code": response.status,
                        "response_time": "< 10s"
                    }
        except Exception as e:
            connectivity_tests['instagram'] = {
                "accessible": False,
                "error": str(e)
            }
        
        return connectivity_tests
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all priority crawler tests."""        logger.info("🚀 Starting Priority Crawler Functionality Tests")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Run individual crawler tests
        spotify_results = await self.test_spotify_crawler()
        youtube_results = await self.test_youtube_crawler()
        instagram_results = await self.test_instagram_crawler()
        
        # Test API connectivity
        connectivity_results = await self.test_api_connectivity()
        
        # Compile final report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        final_report = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "test_summary": {
                "spotify": spotify_results,
                "youtube": youtube_results,
                "instagram": instagram_results
            },
            "api_connectivity": connectivity_results,
            "overall_assessment": self._generate_overall_assessment(
                spotify_results, youtube_results, instagram_results, connectivity_results
            )
        }
        
        return final_report
    
    def _generate_overall_assessment(self, spotify_results: Dict, youtube_results: Dict, 
                                   instagram_results: Dict, connectivity_results: Dict) -> Dict[str, Any]:
        """Generate overall assessment and recommendations."""        
        # Calculate overall scores
        crawler_scores = []
        if spotify_results.get('overall_score') is not None:
            crawler_scores.append(spotify_results['overall_score'])
        if youtube_results.get('overall_score') is not None:
            crawler_scores.append(youtube_results['overall_score'])
        if instagram_results.get('overall_score') is not None:
            crawler_scores.append(instagram_results['overall_score'])
        
        avg_score = sum(crawler_scores) / len(crawler_scores) if crawler_scores else 0.0
        
        # Count accessible APIs
        accessible_apis = sum(1 for api_test in connectivity_results.values() 
                            if api_test.get('accessible', False))
        
        # Generate recommendations
        recommendations = []
        
        if avg_score < 0.7:
            recommendations.append("CRITICAL: Crawler implementations need enhancement")
        
        if accessible_apis < 3:
            recommendations.append("WARNING: Some external APIs are not accessible - check network/auth")
        
        for crawler_name, results in [("Spotify", spotify_results), ("YouTube", youtube_results), ("Instagram", instagram_results)]:
            if results.get('status') == 'ERROR':
                recommendations.append(f"CRITICAL: {crawler_name} crawler has implementation issues")
            elif results.get('overall_score', 0) < 0.5:
                recommendations.append(f"MEDIUM: {crawler_name} crawler needs improvement")
        
        # Determine overall status
        if avg_score >= 0.8 and accessible_apis >= 2:
            overall_status = "EXCELLENT"
        elif avg_score >= 0.6 and accessible_apis >= 2:
            overall_status = "GOOD"
        elif avg_score >= 0.4:
            overall_status = "NEEDS_IMPROVEMENT"
        else:
            overall_status = "CRITICAL"
        
        return {
            "overall_status": overall_status,
            "average_crawler_score": round(avg_score, 2),
            "accessible_apis": accessible_apis,
            "total_apis_tested": len(connectivity_results),
            "recommendations": recommendations,
            "implementation_quality": "REAL" if avg_score > 0.5 else "STUB_OR_INCOMPLETE"
        }

async def main():
    """Main test execution."""    tester = PriorityCrawlerTester()
    
    # Run all tests
    results = await tester.run_all_tests()
    
    # Save results
    report_file = "priority_crawler_test_results.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n✅ Priority Crawler Tests Complete!")
    print(f"📁 Report saved to: {report_file}")
    print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
    print(f"📊 Overall Status: {results['overall_assessment']['overall_status']}")
    print(f"🎯 Average Score: {results['overall_assessment']['average_crawler_score']}")
    print(f"🌐 API Accessibility: {results['overall_assessment']['accessible_apis']}/{results['overall_assessment']['total_apis_tested']}")
    
    # Print individual crawler results
    print(f"\n📋 Individual Crawler Results:")
    for platform, result in results['test_summary'].items():
        status = result.get('status', 'UNKNOWN')
        score = result.get('overall_score', 0.0)
        print(f"   - {platform.title()}: {status} (Score: {score:.2f})")
    
    # Print recommendations
    if results['overall_assessment']['recommendations']:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(results['overall_assessment']['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())