"""AI Agents Usage Examples

Complete examples demonstrating how to use the IA Influencer AI Agents system.
Shows initialization, configuration, agent usage, and advanced workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Import the AI Agents system
from . import (
    # System management
    initialize_system,
    get_system,
    shutdown_system,
    AIAgentsSystem,
    
    # Configuration
    get_config,
    load_config,
    get_default_config,
    AIAgentsConfig,
    
    # Agents
    ContentCreatorAgent,
    SocialMediaManagerAgent,
    AnalyticsAgent,
    EngagementSpecialistAgent,
    AudioSpecialistAgent,
    
    # Core infrastructure
    AgentConfiguration,
    AgentCapability,
    
    # Communication and workflow
    WorkflowEngine,
    TaskManager,
    AgentCommunicationHub
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAgentsExamples:
    """
    Comprehensive examples for using the AI Agents system
    """
    
    def __init__(self):
        self.system: AIAgentsSystem = None
    
    async def example_1_basic_initialization(self):
        """
        Example 1: Basic system initialization and health check
        """
        print("\n=== Example 1: Basic System Initialization ===")
        
        try:
            # Load configuration
            config = get_default_config()
            config.environment = "development"
            config.debug = True
            
            # Initialize the system
            self.system = await initialize_system(config.__dict__)
            
            if self.system.initialized:
                print("✅ AI Agents System initialized successfully!")
                
                # Get system status
                status = await self.system.get_system_status()
                print(f"System Health: {status['system_health']}")
                print(f"Uptime: {status['uptime_seconds']:.2f} seconds")
                print(f"Active Agents: {len(status['agents'])}")
                
                for agent_name, agent_status in status['agents'].items():
                    print(f"  - {agent_name}: {agent_status['status']}")
            
            else:
                print("❌ Failed to initialize AI Agents System")
        
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}")
    
    async def example_2_content_creation_workflow(self):
        """
        Example 2: Content creation workflow
        """
        print("\n=== Example 2: Content Creation Workflow ===")
        
        if not self.system or not self.system.initialized:
            print("⚠️  System not initialized. Run example_1 first.")
            return
        
        try:
            # Get the content creator agent
            content_agent = self.system.agents.get("content_creator")
            if not content_agent:
                print("❌ Content Creator Agent not available")
                return
            
            # Create content request
            content_request = {
                "content_type": "social_post",
                "topic": "AI and the future of content creation",
                "target_platform": "instagram",
                "style": "engaging_educational",
                "length": "medium",
                "include_hashtags": True,
                "include_call_to_action": True
            }
            
            print("📝 Creating content...")
            print(f"Topic: {content_request['topic']}")
            print(f"Platform: {content_request['target_platform']}")
            
            # Process content creation (simulated)
            result = await content_agent.process_task({
                "task_type": "content_creation",
                "request": content_request
            })
            
            if result.get("success"):
                print("✅ Content created successfully!")
                content = result.get("content", {})
                print(f"Generated Text: {content.get('text', 'N/A')[:100]}...")
                print(f"Hashtags: {content.get('hashtags', [])}")
                print(f"Quality Score: {content.get('quality_score', 'N/A')}")
            else:
                print(f"❌ Content creation failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Content creation error: {str(e)}")
    
    async def example_3_multi_agent_collaboration(self):
        """
        Example 3: Multi-agent collaboration for campaign creation
        """
        print("\n=== Example 3: Multi-Agent Campaign Collaboration ===")
        
        if not self.system or not self.system.initialized:
            print("⚠️  System not initialized. Run example_1 first.")
            return
        
        try:
            # Get agents
            content_agent = self.system.agents.get("content_creator")
            social_agent = self.system.agents.get("social_media_manager")
            analytics_agent = self.system.agents.get("analytics")
            
            if not all([content_agent, social_agent, analytics_agent]):
                print("❌ Required agents not available")
                return
            
            print("🚀 Starting multi-agent campaign collaboration...")
            
            # Step 1: Analytics agent analyzes current trends
            print("\n📊 Step 1: Trend Analysis")
            trend_analysis = await analytics_agent.process_task({
                "task_type": "trend_analysis",
                "scope": "current_week",
                "platforms": ["instagram", "tiktok", "youtube"]
            })
            
            if trend_analysis.get("success"):
                trends = trend_analysis.get("trends", [])
                print(f"Found {len(trends)} trending topics")
                for i, trend in enumerate(trends[:3], 1):
                    print(f"  {i}. {trend.get('topic', 'Unknown')} (score: {trend.get('score', 0)})")
            
            # Step 2: Content agent creates content based on trends
            print("\n📝 Step 2: Content Creation")
            if trend_analysis.get("success") and trends:
                top_trend = trends[0]
                content_result = await content_agent.process_task({
                    "task_type": "content_creation",
                    "request": {
                        "topic": top_trend.get("topic", "AI trends"),
                        "content_type": "multi_format",
                        "platforms": ["instagram", "tiktok"],
                        "trend_context": top_trend
                    }
                })
                
                if content_result.get("success"):
                    print("✅ Multi-format content created successfully")
                    formats = content_result.get("content", {}).get("formats", [])
                    print(f"Generated formats: {', '.join(formats)}")
            
            # Step 3: Social media manager optimizes and schedules
            print("\n📅 Step 3: Content Optimization and Scheduling")
            if content_result and content_result.get("success"):
                optimization_result = await social_agent.process_task({
                    "task_type": "content_optimization",
                    "content": content_result.get("content"),
                    "schedule_optimization": True,
                    "cross_platform": True
                })
                
                if optimization_result.get("success"):
                    print("✅ Content optimized and scheduled")
                    schedule = optimization_result.get("schedule", {})
                    print(f"Scheduled posts: {len(schedule.get('posts', []))}")
                    print(f"Optimal posting times identified: {schedule.get('optimal_times', [])}")
            
            print("\n🎉 Campaign collaboration completed successfully!")
        
        except Exception as e:
            logger.error(f"Multi-agent collaboration error: {str(e)}")
    
    async def example_4_audio_music_production(self):
        """
        Example 4: Audio and music production workflow
        """
        print("\n=== Example 4: Audio and Music Production ===")
        
        if not self.system or not self.system.initialized:
            print("⚠️  System not initialized. Run example_1 first.")
            return
        
        try:
            # Get audio specialist agent
            audio_agent = self.system.agents.get("audio_specialist")
            if not audio_agent:
                print("❌ Audio Specialist Agent not available")
                return
            
            print("🎵 Starting audio production workflow...")
            
            # Audio analysis task
            print("\n🔍 Analyzing audio requirements")
            audio_request = {
                "task_type": "music_composition",
                "genre": "electronic",
                "mood": "energetic",
                "duration": 30,  # seconds
                "purpose": "social_media_background",
                "tempo": "fast",
                "instruments": ["synth", "drums", "bass"]
            }
            
            composition_result = await audio_agent.process_task({
                "task_type": "music_composition",
                "request": audio_request
            })
            
            if composition_result.get("success"):
                print("✅ Music composition created")
                composition = composition_result.get("composition", {})
                print(f"Duration: {composition.get('duration', 'N/A')} seconds")
                print(f"Key: {composition.get('key', 'N/A')}")
                print(f"BPM: {composition.get('bpm', 'N/A')}")
                print(f"Instruments: {', '.join(composition.get('instruments', []))}")
                
                # Copyright check
                print("\n📋 Running copyright analysis")
                copyright_result = await audio_agent.process_task({
                    "task_type": "copyright_analysis",
                    "audio_data": composition
                })
                
                if copyright_result.get("success"):
                    copyright_info = copyright_result.get("analysis", {})
                    print(f"Copyright Status: {copyright_info.get('status', 'Unknown')}")
                    print(f"Originality Score: {copyright_info.get('originality_score', 'N/A')}")
                    print(f"Similar Content Found: {copyright_info.get('similar_content_count', 0)}")
        
        except Exception as e:
            logger.error(f"Audio production error: {str(e)}")
    
    async def example_5_engagement_optimization(self):
        """
        Example 5: Engagement optimization and community management
        """
        print("\n=== Example 5: Engagement Optimization ===")
        
        if not self.system or not self.system.initialized:
            print("⚠️  System not initialized. Run example_1 first.")
            return
        
        try:
            # Get engagement specialist
            engagement_agent = self.system.agents.get("engagement_specialist")
            if not engagement_agent:
                print("❌ Engagement Specialist Agent not available")
                return
            
            print("💬 Starting engagement optimization...")
            
            # Analyze current engagement
            print("\n📈 Analyzing current engagement patterns")
            engagement_analysis = await engagement_agent.process_task({
                "task_type": "engagement_analysis",
                "platforms": ["instagram", "tiktok", "youtube"],
                "time_range": "last_7_days"
            })
            
            if engagement_analysis.get("success"):
                metrics = engagement_analysis.get("metrics", {})
                print("✅ Engagement analysis completed")
                print(f"Average Engagement Rate: {metrics.get('avg_engagement_rate', 'N/A')}%")
                print(f"Best Performing Content Type: {metrics.get('best_content_type', 'N/A')}")
                print(f"Peak Engagement Hours: {metrics.get('peak_hours', [])}")
                
                # Optimize engagement strategy
                print("\n🎯 Optimizing engagement strategy")
                optimization_result = await engagement_agent.process_task({
                    "task_type": "strategy_optimization",
                    "current_metrics": metrics,
                    "goals": {
                        "increase_engagement_rate": 20,  # 20% increase
                        "improve_response_time": 50,     # 50% improvement
                        "boost_community_growth": 30     # 30% growth
                    }
                })
                
                if optimization_result.get("success"):
                    strategy = optimization_result.get("strategy", {})
                    print("✅ Strategy optimization completed")
                    print(f"Recommended Actions: {len(strategy.get('actions', []))}")
                    
                    for i, action in enumerate(strategy.get('actions', [])[:3], 1):
                        print(f"  {i}. {action.get('description', 'N/A')} (Priority: {action.get('priority', 'N/A')})")
        
        except Exception as e:
            logger.error(f"Engagement optimization error: {str(e)}")
    
    async def example_6_system_monitoring_and_analytics(self):
        """
        Example 6: System monitoring and performance analytics
        """
        print("\n=== Example 6: System Monitoring and Analytics ===")
        
        if not self.system or not self.system.initialized:
            print("⚠️  System not initialized. Run example_1 first.")
            return
        
        try:
            print("📊 Gathering system performance metrics...")
            
            # Get comprehensive system status
            status = await self.system.get_system_status()
            
            print(f"\n🏥 System Health Report")
            print(f"Overall Health: {status['system_health']}")
            print(f"Uptime: {status['uptime_seconds']:.2f} seconds")
            print(f"Total Errors: {status['error_count']}")
            
            # Agent performance breakdown
            print(f"\n🤖 Agent Performance Summary")
            for agent_name, agent_status in status['agents'].items():
                metrics = agent_status.get('metrics', {})
                print(f"\n{agent_name.replace('_', ' ').title()}:")
                print(f"  Status: {agent_status.get('status', 'Unknown')}")
                print(f"  Tasks Completed: {metrics.get('tasks_completed', 0)}")
                print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
                print(f"  Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")
            
            # Performance metrics
            if status.get('performance_metrics'):
                latest_metrics = list(status['performance_metrics'].values())[-1] if status['performance_metrics'] else {}
                print(f"\n⚡ Latest Performance Metrics")
                print(f"System Load: {latest_metrics.get('system_load', 'N/A')}")
                print(f"Memory Usage: {latest_metrics.get('memory_usage', 'N/A')}")
                print(f"Active Tasks: {latest_metrics.get('active_tasks', 'N/A')}")
            
            # Recent errors (if any)
            if status.get('recent_errors'):
                print(f"\n⚠️  Recent Errors ({len(status['recent_errors'])})")
                for error in status['recent_errors'][-3:]:
                    print(f"  - {error.get('timestamp', 'N/A')}: {error.get('message', 'N/A')}")
            else:
                print("\n✅ No recent errors detected")
        
        except Exception as e:
            logger.error(f"System monitoring error: {str(e)}")
    
    async def run_all_examples(self):
        """
        Run all examples in sequence
        """
        print("🚀 Starting AI Agents System Examples")
        print("=" * 50)
        
        try:
            # Run examples in order
            await self.example_1_basic_initialization()
            await asyncio.sleep(2)  # Brief pause between examples
            
            await self.example_2_content_creation_workflow()
            await asyncio.sleep(2)
            
            await self.example_3_multi_agent_collaboration()
            await asyncio.sleep(2)
            
            await self.example_4_audio_music_production()
            await asyncio.sleep(2)
            
            await self.example_5_engagement_optimization()
            await asyncio.sleep(2)
            
            await self.example_6_system_monitoring_and_analytics()
            
            print("\n" + "=" * 50)
            print("🎉 All examples completed successfully!")
            
        except Exception as e:
            logger.error(f"Error running examples: {str(e)}")
        
        finally:
            # Clean shutdown
            if self.system:
                print("\n🔄 Shutting down system...")
                await shutdown_system()
                print("✅ System shutdown complete")


async def quick_demo():
    """
    Quick demonstration of the AI Agents system
    """
    print("🚀 Quick AI Agents Demo")
    print("-" * 30)
    
    try:
        # Initialize with minimal config
        system = await initialize_system({
            "environment": "demo",
            "debug": True
        })
        
        if system and system.initialized:
            print("✅ System initialized for demo")
            
            # Quick status check
            status = await system.get_system_status()
            print(f"Health: {status['system_health']}")
            print(f"Agents: {len(status['agents'])}")
            
            # Demo content creation
            if "content_creator" in system.agents:
                print("\n📝 Creating demo content...")
                agent = system.agents["content_creator"]
                result = await agent.process_task({
                    "task_type": "content_creation",
                    "request": {
                        "topic": "AI revolution in social media",
                        "platform": "instagram"
                    }
                })
                
                if result.get("success"):
                    print("✅ Demo content created successfully!")
        
        await shutdown_system()
        print("✅ Demo completed")
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")


# Example configurations for different use cases
EXAMPLE_CONFIGS = {
    "content_creator_focused": {
        "environment": "production",
        "agents": {
            "content_creator": {
                "max_concurrent_tasks": 5,
                "creativity_level": 0.9,
                "quality_threshold": 0.9
            }
        },
        "ai": {
            "openai_model": "gpt-4",
            "temperature": 0.8
        }
    },
    
    "analytics_heavy": {
        "environment": "production",
        "agents": {
            "analytics": {
                "max_concurrent_tasks": 10,
                "real_time_monitoring": True,
                "deep_analysis": True
            }
        },
        "performance": {
            "max_concurrent_tasks": 50,
            "cache_enabled": True
        }
    },
    
    "music_production": {
        "environment": "production",
        "agents": {
            "audio_specialist": {
                "max_concurrent_tasks": 3,
                "high_quality_mode": True,
                "copyright_protection": True
            }
        }
    }
}


if __name__ == "__main__":
    # Choose which example to run
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "quick":
            asyncio.run(quick_demo())
        elif mode == "full":
            examples = AIAgentsExamples()
            asyncio.run(examples.run_all_examples())
        else:
            print("Usage: python examples.py [quick|full]")
    else:
        # Run quick demo by default
        asyncio.run(quick_demo())
