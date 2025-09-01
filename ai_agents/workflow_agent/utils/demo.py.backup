"""IA-Influencer Agent - Workflow Agent Demo

Demonstration script showing how to use the Workflow Agent module for various use cases.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import workflow agent components
from . import (
    WorkflowAgent,
    WorkflowAgentFactory,
    WorkflowTemplateLibrary,
    QuickWorkflowBuilder,
    WorkflowUtilities,
    quick_setup,
    create_simple_workflow,
    ExecutionMode,
    TemplateType,
    ScheduleType,
    Priority
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_setup():
    """Demonstrate basic workflow agent setup."""
    print("\n" + "="*60)
    print("🚀 DEMO: Basic Workflow Agent Setup")
    print("="*60)
    
    try:
        # Quick setup for content creator
        agent = await quick_setup("content_creator")
        
        # Get agent status
        status = await agent.get_status()
        print(f"✅ Agent initialized successfully!")
        print(f"   - Status: {status['status']}")
        print(f"   - Components: {len(status['components'])} active")
        print(f"   - Templates: {len(status['templates'])} available")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error in basic setup demo: {str(e)}")
        return False


async def demo_template_recommendations():
    """Demonstrate template recommendations based on user profile."""
    print("\n" + "="*60)
    print("📋 DEMO: Template Recommendations")
    print("="*60)
    
    try:
        # Test different user profiles
        profiles = [
            {
                'name': 'Musician',
                'profile': {'type': 'musician', 'interests': ['music', 'audio', 'streaming']}
            },
            {
                'name': 'Influencer',
                'profile': {'type': 'influencer', 'interests': ['social_media', 'video', 'engagement']}
            },
            {
                'name': 'Photographer',
                'profile': {'type': 'photographer', 'interests': ['photography', 'portfolio', 'image_processing']}
            }
        ]
        
        for profile_info in profiles:
            recommendations = WorkflowTemplateLibrary.get_template_recommendations(
                profile_info['profile']
            )
            
            print(f"\n🎯 {profile_info['name']} Recommendations:")
            for i, template in enumerate(recommendations, 1):
                print(f"   {i}. {template}")
        
        # Show templates by category
        print("\n📂 Templates by Category:")
        categories = ['music', 'social_media', 'content_protection', 'analytics']
        
        for category in categories:
            templates = WorkflowTemplateLibrary.get_template_by_category(category)
            print(f"\n   {category.upper()}:")
            for template in templates:
                print(f"     • {template}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in template recommendations demo: {str(e)}")
        return False


async def demo_simple_workflow_creation():
    """Demonstrate creating and executing a simple workflow."""
    print("\n" + "="*60)
    print("⚡ DEMO: Simple Workflow Creation & Execution")
    print("="*60)
    
    try:
        # Setup agent
        agent = await quick_setup("content_creator")
        
        # Define simple content creation workflow
        tasks = [
            {
                'name': 'Research Topic',
                'type': 'research_agent',
                'executor': 'research_topic'
            },
            {
                'name': 'Create Content',
                'type': 'content_agent',
                'executor': 'create_content'
            },
            {
                'name': 'Optimize for SEO',
                'type': 'seo_agent',
                'executor': 'optimize_content'
            },
            {
                'name': 'Publish Content',
                'type': 'distribution_agent',
                'executor': 'publish_content'
            }
        ]
        
        # Create workflow
        print("📝 Creating simple content workflow...")
        workflow_id = await create_simple_workflow(
            agent=agent,
            name="Content Creation Pipeline",
            tasks=tasks
        )
        
        print(f"✅ Workflow created with ID: {workflow_id}")
        
        # Get workflow details
        workflow_info = await agent.get_workflow_info(workflow_id)
        print(f"   - Nodes: {len(workflow_info.get('nodes', []))}")
        print(f"   - Category: {workflow_info.get('category', 'N/A')}")
        
        # Execute workflow (simulation mode)
        print("\n🎯 Executing workflow...")
        execution_context = {
            'topic': 'AI in Content Creation',
            'target_audience': 'content creators',
            'platforms': ['blog', 'social_media']
        }
        
        execution_id = await agent.execute_workflow(
            workflow_id=workflow_id,
            execution_context=execution_context,
            execution_mode=ExecutionMode.ASYNCHRONOUS
        )
        
        print(f"✅ Workflow execution started: {execution_id}")
        
        # Monitor execution (simplified)
        await asyncio.sleep(2)  # Simulate execution time
        
        execution_status = await agent.get_execution_status(execution_id)
        print(f"   - Status: {execution_status.get('status', 'unknown')}")
        print(f"   - Progress: {execution_status.get('progress', {}).get('percentage', 0)}%")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error in simple workflow demo: {str(e)}")
        return False


async def demo_music_release_workflow():
    """Demonstrate creating a complete music release workflow."""
    print("\n" + "="*60)
    print("🎵 DEMO: Music Release Workflow")
    print("="*60)
    
    try:
        # Setup music-focused agent
        agent = await WorkflowAgentFactory.create_quick_setup("musician")
        
        # Define release platforms
        release_platforms = ['spotify', 'apple_music', 'youtube_music', 'soundcloud']
        
        print(f"🎼 Creating music release workflow for platforms: {', '.join(release_platforms)}")
        
        # Create comprehensive music release workflow
        workflow_id = await QuickWorkflowBuilder.create_music_release_workflow(
            agent=agent,
            release_platforms=release_platforms,
            protection_enabled=True
        )
        
        print(f"✅ Music release workflow created: {workflow_id}")
        
        # Get workflow structure
        workflow_info = await agent.get_workflow_info(workflow_id)
        print(f"   - Total nodes: {len(workflow_info.get('nodes', []))}")
        print(f"   - Protection enabled: ✅")
        print(f"   - Distribution platforms: {len(release_platforms)}")
        
        # Show workflow structure
        print("\n📋 Workflow Structure:")
        for i, node in enumerate(workflow_info.get('nodes', []), 1):
            print(f"   {i}. {node.get('name', 'Unknown Node')}")
        
        # Schedule for future release
        print("\n⏰ Scheduling for release...")
        schedule_id = await agent.schedule_workflow(
            workflow_id=workflow_id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.now() + timedelta(hours=24),  # Release in 24 hours
            priority=Priority.HIGH,
            execution_context={
                'album': 'Demo Album',
                'artist': 'Demo Artist',
                'release_date': '2025-01-15',
                'genre': 'Electronic'
            }
        )
        
        print(f"✅ Release scheduled: {schedule_id}")
        print(f"   - Scheduled for: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')}")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error in music release demo: {str(e)}")
        return False


async def demo_bulk_workflow_execution():
    """Demonstrate bulk workflow execution and monitoring."""
    print("\n" + "="*60)
    print("⚡ DEMO: Bulk Workflow Execution & Monitoring")
    print("="*60)
    
    try:
        # Setup agent
        agent = await quick_setup("influencer")
        
        # Create multiple simple workflows
        workflow_configs = []
        
        for i in range(3):
            # Create a simple workflow
            tasks = [
                {'name': f'Task 1 - Workflow {i+1}', 'type': 'prep', 'executor': 'prepare'},
                {'name': f'Task 2 - Workflow {i+1}', 'type': 'process', 'executor': 'process'},
                {'name': f'Task 3 - Workflow {i+1}', 'type': 'finish', 'executor': 'complete'}
            ]
            
            workflow_id = await create_simple_workflow(
                agent=agent,
                name=f"Demo Workflow {i+1}",
                tasks=tasks
            )
            
            # Add to bulk execution config
            workflow_configs.append({
                'workflow_id': workflow_id,
                'context': {'batch_id': i+1, 'priority': 'normal'},
                'mode': 'asynchronous',
                'strategy': 'adaptive'
            })
        
        print(f"📝 Created {len(workflow_configs)} workflows for bulk execution")
        
        # Execute all workflows in parallel
        print("\n🚀 Executing workflows in parallel...")
        results = await WorkflowUtilities.bulk_execute_workflows(
            agent=agent,
            workflow_configs=workflow_configs
        )
        
        print(f"✅ Bulk execution completed: {len(results)} results")
        
        # Monitor workflow health
        workflow_ids = [config['workflow_id'] for config in workflow_configs]
        
        print("\n📊 Monitoring workflow health...")
        health_statuses = await WorkflowUtilities.monitor_workflow_health(
            agent=agent,
            workflow_ids=workflow_ids
        )
        
        # Generate performance summary
        performance_summary = WorkflowUtilities.get_performance_summary(health_statuses)
        
        print("\n📈 Performance Summary:")
        print(f"   - Total workflows: {performance_summary.get('total_workflows', 0)}")
        print(f"   - Healthy workflows: {performance_summary.get('healthy_workflows', 0)}")
        print(f"   - Health percentage: {performance_summary.get('health_percentage', 0):.1f}%")
        print(f"   - Performance score: {performance_summary.get('performance_score', 0):.1f}")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error in bulk execution demo: {str(e)}")
        return False


async def demo_advanced_scheduling():
    """Demonstrate advanced workflow scheduling features."""
    print("\n" + "="*60)
    print("⏰ DEMO: Advanced Workflow Scheduling")
    print("="*60)
    
    try:
        # Setup agent
        agent = await quick_setup("content_creator")
        
        # Create a simple workflow for scheduling
        tasks = [
            {'name': 'Generate Content', 'type': 'content', 'executor': 'generate'},
            {'name': 'Review Content', 'type': 'review', 'executor': 'review'},
            {'name': 'Publish Content', 'type': 'publish', 'executor': 'publish'}
        ]
        
        workflow_id = await create_simple_workflow(
            agent=agent,
            name="Scheduled Content Pipeline",
            tasks=tasks
        )
        
        print(f"📝 Created workflow for scheduling: {workflow_id}")
        
        # Schedule different types of executions
        schedules = []
        
        # 1. One-time execution
        schedule_id_once = await agent.schedule_workflow(
            workflow_id=workflow_id,
            schedule_type=ScheduleType.ONCE,
            start_time=datetime.now() + timedelta(minutes=30),
            priority=Priority.HIGH,
            execution_context={'type': 'one_time', 'content': 'Special announcement'}
        )
        schedules.append(('Once', schedule_id_once))
        
        # 2. Daily execution
        schedule_id_daily = await agent.schedule_workflow(
            workflow_id=workflow_id,
            schedule_type=ScheduleType.DAILY,
            start_time=datetime.now() + timedelta(hours=1),
            priority=Priority.MEDIUM,
            execution_context={'type': 'daily', 'content': 'Daily update'}
        )
        schedules.append(('Daily', schedule_id_daily))
        
        # 3. Cron-based execution (every weekday at 9 AM)
        schedule_id_cron = await agent.schedule_workflow(
            workflow_id=workflow_id,
            schedule_type=ScheduleType.CRON,
            cron_expression='0 9 * * 1-5',  # Monday to Friday at 9 AM
            priority=Priority.LOW,
            execution_context={'type': 'weekday', 'content': 'Business update'}
        )
        schedules.append(('Weekday 9AM', schedule_id_cron))
        
        print("\n📅 Created schedules:")
        for schedule_type, schedule_id in schedules:
            print(f"   - {schedule_type}: {schedule_id}")
        
        # Get active schedules
        active_schedules = await agent.get_active_schedules()
        print(f"\n✅ Total active schedules: {len(active_schedules)}")
        
        # Show schedule details
        for schedule in active_schedules[-3:]:  # Show last 3 created
            print(f"   - Schedule: {schedule.get('id', 'N/A')}")
            print(f"     Type: {schedule.get('schedule_type', 'N/A')}")
            print(f"     Next run: {schedule.get('next_execution', 'N/A')}")
            print(f"     Priority: {schedule.get('priority', 'N/A')}")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced scheduling demo: {str(e)}")
        return False


async def demo_content_publishing_workflow():
    """Demonstrate content publishing workflow creation."""
    print("\n" + "="*60)
    print("📢 DEMO: Content Publishing Workflow")
    print("="*60)
    
    try:
        # Setup agent
        agent = await quick_setup("influencer")
        
        # Define platforms for publishing
        platforms = ['instagram', 'tiktok', 'youtube', 'twitter', 'linkedin']
        content_type = "video"
        
        print(f"📱 Creating content publishing workflow for: {content_type}")
        print(f"   Platforms: {', '.join(platforms)}")
        
        # Create content publishing workflow
        workflow_id = await QuickWorkflowBuilder.create_content_publishing_workflow(
            agent=agent,
            platforms=platforms,
            content_type=content_type
        )
        
        print(f"✅ Content publishing workflow created: {workflow_id}")
        
        # Get workflow details
        workflow_info = await agent.get_workflow_info(workflow_id)
        nodes = workflow_info.get('nodes', [])
        
        print(f"\n📋 Workflow contains {len(nodes)} nodes:")
        for node in nodes:
            print(f"   • {node.get('name', 'Unknown')}")
        
        # Create execution context for the workflow
        execution_context = {
            'content': {
                'title': 'My Amazing Video',
                'description': 'Check out this amazing content!',
                'tags': ['amazing', 'video', 'content'],
                'category': 'entertainment'
            },
            'publishing': {
                'schedule_time': datetime.now() + timedelta(hours=2),
                'visibility': 'public',
                'comments_enabled': True
            },
            'seo': {
                'target_keywords': ['amazing video', 'content creation', 'viral'],
                'optimize_for_mobile': True
            }
        }
        
        # Execute workflow
        print("\n🚀 Executing content publishing workflow...")
        execution_id = await agent.execute_workflow(
            workflow_id=workflow_id,
            execution_context=execution_context,
            execution_mode=ExecutionMode.ASYNCHRONOUS
        )
        
        print(f"✅ Execution started: {execution_id}")
        
        # Monitor progress
        await asyncio.sleep(1)  # Simulate processing time
        status = await agent.get_execution_status(execution_id)
        
        print(f"   - Status: {status.get('status', 'unknown')}")
        print(f"   - Progress: {status.get('progress', {}).get('percentage', 0)}%")
        
        await agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error in content publishing demo: {str(e)}")
        return False


async def run_all_demos():
    """Run all demonstration functions."""
    print("🎭" + "="*59)
    print("    IA-INFLUENCER AGENT - WORKFLOW MODULE DEMO")
    print("🎭" + "="*59)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    demos = [
        ("Basic Setup", demo_basic_setup),
        ("Template Recommendations", demo_template_recommendations),
        ("Simple Workflow Creation", demo_simple_workflow_creation),
        ("Music Release Workflow", demo_music_release_workflow),
        ("Bulk Execution & Monitoring", demo_bulk_workflow_execution),
        ("Advanced Scheduling", demo_advanced_scheduling),
        ("Content Publishing", demo_content_publishing_workflow)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n🎯 Running: {demo_name}")
            success = await demo_func()
            results.append((demo_name, success))
            
            if success:
                print(f"✅ {demo_name} completed successfully!")
            else:
                print(f"❌ {demo_name} failed!")
                
        except Exception as e:
            print(f"💥 {demo_name} crashed: {str(e)}")
            results.append((demo_name, False))
        
        # Brief pause between demos
        await asyncio.sleep(1)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 DEMO SUMMARY")
    print("="*60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Total demos: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {(successful/total)*100:.1f}%")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return successful == total


# Main execution function
if __name__ == "__main__":
    asyncio.run(run_all_demos())


# Export demo functions for individual testing
__all__ = [
    'demo_basic_setup',
    'demo_template_recommendations', 
    'demo_simple_workflow_creation',
    'demo_music_release_workflow',
    'demo_bulk_workflow_execution',
    'demo_advanced_scheduling',
    'demo_content_publishing_workflow',
    'run_all_demos'
]
