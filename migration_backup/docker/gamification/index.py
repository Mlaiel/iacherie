"""
Gamification Services Index - Main Interface
===========================================

Central interface for all gamification microservices orchestration.
Handles service discovery, load balancing, and coordination between
different gamification components.

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 3.0.0
"""

from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import logging
from datetime import datetime
from dataclasses import dataclass
from . import gamification_orchestrator, health_check

logger = logging.getLogger(__name__)

@dataclass
class ServiceHealth:
    """Service health status"""
    service_name: str
    status: str
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None

class GamificationServiceManager:
    """
    Main service manager for gamification module.
    
    Provides high-level interface for all gamification operations
    including challenge management, rewards, leaderboards, and social features.
    """
    
    def __init__(self):
        self.orchestrator = gamification_orchestrator
        self.service_registry = {}
        self._initialize_service_registry()
    
    def _initialize_service_registry(self):
        """Initialize service registry with all gamification services"""
        self.service_registry = {
            'challenge_engine': {
                'url': 'http://challenge-engine:8080',
                'description': 'Challenge creation and management',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'reward_system': {
                'url': 'http://reward-system:8081',
                'description': 'Reward calculation and distribution',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'leaderboard_manager': {
                'url': 'http://leaderboard-manager:8082',
                'description': 'Leaderboard management and rankings',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'achievement_tracker': {
                'url': 'http://achievement-tracker:8083',
                'description': 'Achievement tracking and unlocking',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'social_features': {
                'url': 'http://social-features:8084',
                'description': 'Social interaction and community features',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'tournament_organizer': {
                'url': 'http://tournament-organizer:8085',
                'description': 'Tournament creation and management',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'badge_system': {
                'url': 'http://badge-system:8086',
                'description': 'Badge creation and award system',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'engagement_optimizer': {
                'url': 'http://engagement-optimizer:8087',
                'description': 'Engagement analysis and optimization',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'community_builder': {
                'url': 'http://community-builder:8088',
                'description': 'Community building and management',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'point_calculator': {
                'url': 'http://point-calculator:8089',
                'description': 'Point calculation and management',
                'health_endpoint': '/health',
                'api_version': 'v1'
            },
            'level_progression': {
                'url': 'http://level-progression:8090',
                'description': 'Level progression and experience management',
                'health_endpoint': '/health',
                'api_version': 'v1'
            }
        }
    
    async def check_all_services_health(self) -> Dict[str, ServiceHealth]:
        """Check health of all gamification services"""
        health_results = {}
        
        async with aiohttp.ClientSession() as session:
            for service_name, config in self.service_registry.items():
                try:
                    start_time = datetime.now()
                    url = f"{config['url']}{config['health_endpoint']}"
                    
                    async with session.get(url, timeout=5) as response:
                        response_time = (datetime.now() - start_time).total_seconds()
                        
                        if response.status == 200:
                            health_results[service_name] = ServiceHealth(
                                service_name=service_name,
                                status="healthy",
                                response_time=response_time,
                                last_check=datetime.now()
                            )
                        else:
                            health_results[service_name] = ServiceHealth(
                                service_name=service_name,
                                status="unhealthy",
                                response_time=response_time,
                                last_check=datetime.now(),
                                error_message=f"HTTP {response.status}"
                            )
                            
                except Exception as e:
                    health_results[service_name] = ServiceHealth(
                        service_name=service_name,
                        status="error",
                        response_time=0.0,
                        last_check=datetime.now(),
                        error_message=str(e)
                    )
        
        return health_results
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for all services"""
        health_status = await self.check_all_services_health()
        
        healthy_services = sum(1 for h in health_status.values() if h.status == "healthy")
        total_services = len(health_status)
        
        avg_response_time = sum(h.response_time for h in health_status.values()) / total_services
        
        return {
            'total_services': total_services,
            'healthy_services': healthy_services,
            'unhealthy_services': total_services - healthy_services,
            'health_percentage': (healthy_services / total_services) * 100,
            'average_response_time': avg_response_time,
            'service_details': {
                name: {
                    'status': health.status,
                    'response_time': health.response_time,
                    'last_check': health.last_check.isoformat(),
                    'error': health.error_message
                }
                for name, health in health_status.items()
            }
        }
    
    async def create_challenge(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new gamification challenge"""
        try:
            # This would call the actual challenge engine service
            logger.info(f"Creating challenge: {challenge_data.get('title', 'Unknown')}")
            
            # Mock implementation - replace with actual service call
            challenge_id = f"challenge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                'challenge_id': challenge_id,
                'status': 'created',
                'message': 'Challenge created successfully',
                'challenge_data': challenge_data
            }
            
        except Exception as e:
            logger.error(f"Error creating challenge: {e}")
            raise
    
    async def calculate_rewards(self, creator_id: str, action_type: str, action_data: Dict) -> Dict[str, Any]:
        """Calculate and distribute rewards for creator actions"""
        try:
            # This would call the actual reward system service
            logger.info(f"Calculating rewards for creator {creator_id}, action: {action_type}")
            
            # Mock implementation
            base_points = {
                'upload_content': 100,
                'complete_challenge': 500,
                'collaboration': 300,
                'social_interaction': 50,
                'achievement_unlock': 1000
            }
            
            points_earned = base_points.get(action_type, 10)
            
            return {
                'creator_id': creator_id,
                'action_type': action_type,
                'points_earned': points_earned,
                'bonus_multiplier': 1.0,
                'total_points': points_earned,
                'badges_earned': [],
                'achievements_unlocked': []
            }
            
        except Exception as e:
            logger.error(f"Error calculating rewards: {e}")
            raise
    
    async def get_leaderboards(self, category: str = "global", timeframe: str = "monthly") -> Dict[str, Any]:
        """Get leaderboard data"""
        try:
            # This would call the actual leaderboard manager service
            logger.info(f"Getting leaderboard for category: {category}, timeframe: {timeframe}")
            
            # Mock implementation
            return {
                'category': category,
                'timeframe': timeframe,
                'leaderboard': [
                    {'rank': 1, 'creator_id': 'creator_001', 'username': 'TopCreator', 'points': 15000},
                    {'rank': 2, 'creator_id': 'creator_002', 'username': 'MusicMaster', 'points': 12500},
                    {'rank': 3, 'creator_id': 'creator_003', 'username': 'PhotoPro', 'points': 11200}
                ],
                'total_participants': 1247,
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting leaderboards: {e}")
            raise

# Initialize the service manager
service_manager = GamificationServiceManager()

# FastAPI-style route handlers (for when integrated with FastAPI)
async def get_gamification_status():
    """Get overall gamification system status"""
    return await service_manager.get_service_metrics()

async def get_creator_engagement(creator_id: str):
    """Get creator engagement status"""
    return await service_manager.orchestrator.get_creator_engagement_status(creator_id)

async def create_new_challenge(challenge_data: Dict[str, Any]):
    """Create new challenge"""
    return await service_manager.create_challenge(challenge_data)

async def calculate_creator_rewards(creator_id: str, action_type: str, action_data: Dict):
    """Calculate rewards for creator action"""
    return await service_manager.calculate_rewards(creator_id, action_type, action_data)

async def get_global_leaderboards(category: str = "global", timeframe: str = "monthly"):
    """Get leaderboard data"""
    return await service_manager.get_leaderboards(category, timeframe)

if __name__ == "__main__":
    # Example usage
    async def main():
        # Check service health
        metrics = await service_manager.get_service_metrics()
        print(f"Service Metrics: {metrics}")
        
        # Get creator engagement
        engagement = await get_creator_engagement("creator_123")
        print(f"Creator Engagement: {engagement}")
    
    asyncio.run(main())