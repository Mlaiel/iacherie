"""Gamification Agent Index - Central Orchestrator for Gamification Intelligence

Provides unified access point and orchestration for all gamification AI modules,
enabling seamless integration with the IA-Influencer-Agent platform ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This orchestration system and integration patterns are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Import all gamification components
from .gamification_agent import GamificationAgent, GamificationConfig
from .challenge_ai import ChallengeGenerator
from .reward_optimization_ai import RewardOptimizer
from .user_engagement_predictor import EngagementPredictor
from .social_competition_ai import SocialCompetitionManager
from .badge_generation_ai import BadgeGenerator
from .progression_analyzer import ProgressionAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class GamificationIndexConfig:
    """Configuration for gamification index orchestrator"""
    enable_challenge_generation: bool = True
    enable_reward_optimization: bool = True
    enable_engagement_prediction: bool = True
    enable_social_competition: bool = True
    enable_badge_generation: bool = True
    enable_progression_analysis: bool = True
    max_concurrent_operations: int = 10
    cache_ttl_seconds: int = 300
    analytics_enabled: bool = True
    monitoring_enabled: bool = True

class GamificationIndex:
    """
    Central orchestrator for all gamification intelligence modules.
    
    Provides unified interface for:
    - Challenge generation and management
    - Reward optimization and distribution
    - User engagement prediction and enhancement
    - Social competition orchestration
    - Badge generation and achievement tracking
    - Progression analysis and recommendations
    """
    
    def __init__(self, config: Optional[GamificationIndexConfig] = None):
        self.config = config or GamificationIndexConfig()
        self.initialized = False
        self.agents = {}
        self.metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'average_response_time': 0.0
        }
        
        # Initialize components
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all gamification agents"""
        try:
            # Main gamification agent
            self.agents['main'] = GamificationAgent(
                agent_id="gamification_orchestrator",
                agent_type="gamification_index",
                config={"orchestrator_mode": True}
            )
            
            # Specialized AI modules
            if self.config.enable_challenge_generation:
                self.agents['challenge_generator'] = ChallengeGenerator()
            
            if self.config.enable_reward_optimization:
                self.agents['reward_optimizer'] = RewardOptimizer()
            
            if self.config.enable_engagement_prediction:
                self.agents['engagement_predictor'] = EngagementPredictor()
            
            if self.config.enable_social_competition:
                self.agents['social_competition'] = SocialCompetitionManager()
            
            if self.config.enable_badge_generation:
                self.agents['badge_generator'] = BadgeGenerator()
            
            if self.config.enable_progression_analysis:
                self.agents['progression_analyzer'] = ProgressionAnalyzer()
            
            self.initialized = True
            logger.info("Gamification Index initialized successfully with all agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gamification Index: {str(e)}")
            raise
    
    async def process_user_activity(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user activity through all gamification modules.
        
        Args:
            user_id: Unique user identifier
            activity_data: User activity information
            
        Returns:
            Comprehensive gamification response
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            if not self.initialized:
                raise ValueError("Gamification Index not initialized")
            
            results = {
                'user_id': user_id,
                'timestamp': start_time.isoformat(),
                'processed_modules': [],
                'challenges': {},
                'rewards': {},
                'engagement_prediction': {},
                'competitions': {},
                'badges': {},
                'progression': {},
                'status': 'processing'
            }
            
            # Process through all enabled modules
            tasks = []
            
            # Challenge generation
            if 'challenge_generator' in self.agents:
                tasks.append(self._process_challenges(user_id, activity_data))
            
            # Reward optimization
            if 'reward_optimizer' in self.agents:
                tasks.append(self._process_rewards(user_id, activity_data))
            
            # Engagement prediction
            if 'engagement_predictor' in self.agents:
                tasks.append(self._process_engagement(user_id, activity_data))
            
            # Social competition
            if 'social_competition' in self.agents:
                tasks.append(self._process_competitions(user_id, activity_data))
            
            # Badge generation
            if 'badge_generator' in self.agents:
                tasks.append(self._process_badges(user_id, activity_data))
            
            # Progression analysis
            if 'progression_analyzer' in self.agents:
                tasks.append(self._process_progression(user_id, activity_data))
            
            # Execute all tasks concurrently
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            module_names = ['challenges', 'rewards', 'engagement_prediction', 
                          'competitions', 'badges', 'progression']
            
            for i, result in enumerate(task_results):
                if i < len(module_names):
                    module_name = module_names[i]
                    if isinstance(result, Exception):
                        logger.error(f"Error in {module_name}: {str(result)}")
                        results[module_name] = {'error': str(result)}
                    else:
                        results[module_name] = result
                        results['processed_modules'].append(module_name)
            
            # Calculate metrics
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            results.update({
                'status': 'completed',
                'processing_time_seconds': processing_time,
                'processed_at': end_time.isoformat()
            })
            
            # Update metrics
            self.metrics['total_operations'] += 1
            self.metrics['successful_operations'] += 1
            self.metrics['average_response_time'] = (
                (self.metrics['average_response_time'] * (self.metrics['total_operations'] - 1) + processing_time) /
                self.metrics['total_operations']
            )
            
            return results
            
        except Exception as e:
            self.metrics['total_operations'] += 1
            self.metrics['failed_operations'] += 1
            logger.error(f"Error processing user activity: {str(e)}")
            raise
    
    async def _process_challenges(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process challenge generation for user"""
        try:
            generator = self.agents['challenge_generator']
            return await generator.generate_personalized_challenges(user_id, activity_data)
        except Exception as e:
            logger.error(f"Challenge processing error: {str(e)}")
            return {'error': str(e)}
    
    async def _process_rewards(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process reward optimization for user"""
        try:
            optimizer = self.agents['reward_optimizer']
            return await optimizer.optimize_rewards(user_id, activity_data)
        except Exception as e:
            logger.error(f"Reward processing error: {str(e)}")
            return {'error': str(e)}
    
    async def _process_engagement(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process engagement prediction for user"""
        try:
            predictor = self.agents['engagement_predictor']
            return await predictor.predict_engagement(user_id, activity_data)
        except Exception as e:
            logger.error(f"Engagement processing error: {str(e)}")
            return {'error': str(e)}
    
    async def _process_competitions(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process social competition for user"""
        try:
            manager = self.agents['social_competition']
            return await manager.process_competition_data(user_id, activity_data)
        except Exception as e:
            logger.error(f"Competition processing error: {str(e)}")
            return {'error': str(e)}
    
    async def _process_badges(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process badge generation for user"""
        try:
            generator = self.agents['badge_generator']
            return await generator.generate_badges(user_id, activity_data)
        except Exception as e:
            logger.error(f"Badge processing error: {str(e)}")
            return {'error': str(e)}
    
    async def _process_progression(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process progression analysis for user"""
        try:
            analyzer = self.agents['progression_analyzer']
            return await analyzer.analyze_progression(user_id, activity_data)
        except Exception as e:
            logger.error(f"Progression processing error: {str(e)}")
            return {'error': str(e)}
    
    async def get_user_gamification_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification status for user"""
        try:
            status = {
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'active_challenges': [],
                'current_rewards': {},
                'engagement_score': 0.0,
                'active_competitions': [],
                'earned_badges': [],
                'progression_level': 1,
                'status': 'active'
            }
            
            # Gather status from all modules
            tasks = []
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'get_user_status'):
                    tasks.append(agent.get_user_status(user_id))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                # Process and aggregate results
                for result in results:
                    if not isinstance(result, Exception) and isinstance(result, dict):
                        status.update(result)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting user gamification status: {str(e)}")
            return {'user_id': user_id, 'error': str(e), 'status': 'error'}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'metrics': self.metrics.copy(),
            'agents_status': {
                name: 'active' if agent else 'inactive'
                for name, agent in self.agents.items()
            },
            'config': {
                'max_concurrent_operations': self.config.max_concurrent_operations,
                'cache_ttl_seconds': self.config.cache_ttl_seconds,
                'analytics_enabled': self.config.analytics_enabled
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Global instance for easy access
gamification_index = GamificationIndex()

# Export for external use
__all__ = ['GamificationIndex', 'GamificationIndexConfig', 'gamification_index']