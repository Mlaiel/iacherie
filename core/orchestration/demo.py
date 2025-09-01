"""Orchestration Module Demo - Usage Examples

Demonstration script showing how to use the IA Influencer Agent
orchestration module for various content processing workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from backend.core.orchestration import (
    initialize_orchestration_system,
    get_orchestration_system,
    shutdown_orchestration_system,
    submit_content_processing_workflow,
    submit_protection_workflow,
    submit_monetization_workflow,
    OrchestrationSystemConfig
)


async def demo_content_processing():
    """
Demonstrate content processing workflow."""
    print("\n🎵 CONTENT PROCESSING WORKFLOW DEMO")
    print("=" * 50)
    
    # Sample audio content data
    content_data = {
        "content_type": "audio",
        "file_path": "/uploads/music/song.wav",
        "metadata": {
            "title": "Amazing Song",
            "artist": "Demo Artist",
            "genre": "Electronic",
            "duration": 180.5
        },
        "processing_options": {
            "quality_level": "high",
            "ai_enhancement": True,
            "protection_required": True,
            "seo_optimization": True
        }
    }
    
    try:
        # Submit content processing workflow
        execution_id = await submit_content_processing_workflow(
            content_data=content_data,
            user_id="user_123",
            tenant_id="tenant_456",
            priority="normal"
        )
        
        print(f"✅ Content processing workflow submitted: {execution_id}")
        
        # Get workflow status
        system = get_orchestration_system()
        if system:
            status = await system.get_workflow_status(execution_id)
            print(f"📊 Workflow Status: {status['status']}")
            print(f"🏷️  Workflow Name: {status['workflow_name']}")
            print(f"⏱️  Submitted At: {status['submitted_at']}")
        
        return execution_id
        
    except Exception as e:
        print(f"❌ Error in content processing demo: {str(e)}")
        return None


async def demo_protection_workflow():
    """Demonstrate content protection workflow."""
    print("\n🛡️  CONTENT PROTECTION WORKFLOW DEMO")
    print("=" * 50)
    
    # Sample content for protection
    content_data = {
        "content_type": "video",
        "file_path": "/uploads/videos/my_video.mp4",
        "metadata": {
            "title": "My Creative Video",
            "creator": "Demo Creator",
            "duration": 300,
            "resolution": "1080p"
        },
        "protection_settings": {
            "fingerprint_types": ["visual", "audio", "metadata"],
            "monitoring_enabled": True,
            "alert_threshold": 0.85,
            "automatic_takedown": False
        }
    }
    
    try:
        # Submit protection workflow
        execution_id = await submit_protection_workflow(
            content_data=content_data,
            user_id="creator_789",
            tenant_id="tenant_456",
            priority="high"
        )
        
        print(f"✅ Protection workflow submitted: {execution_id}")
        
        # Get workflow status
        system = get_orchestration_system()
        if system:
            status = await system.get_workflow_status(execution_id)
            print(f"📊 Workflow Status: {status['status']}")
            print(f"🔒 Protection Level: High")
        
        return execution_id
        
    except Exception as e:
        print(f"❌ Error in protection demo: {str(e)}")
        return None


async def demo_monetization_workflow():
    """Demonstrate monetization workflow."""
    print("\n💰 MONETIZATION WORKFLOW DEMO")
    print("=" * 50)
    
    # Sample monetization data
    content_data = {
        "content_id": "content_123",
        "content_type": "music",
        "platforms": ["spotify", "youtube", "instagram", "tiktok"],
        "monetization_settings": {
            "revenue_sharing": {
                "creator": 0.7,
                "platform": 0.3
            },
            "pricing_strategy": "dynamic",
            "territory_restrictions": [],
            "collaboration_splits": {
                "primary_artist": 0.6,
                "producer": 0.3,
                "songwriter": 0.1
            }
        },
        "analytics_tracking": {
            "conversion_tracking": True,
            "audience_insights": True,
            "performance_optimization": True
        }
    }
    
    try:
        # Submit monetization workflow
        execution_id = await submit_monetization_workflow(
            content_data=content_data,
            user_id="artist_456",
            tenant_id="tenant_456",
            priority="normal"
        )
        
        print(f"✅ Monetization workflow submitted: {execution_id}")
        
        # Get workflow status
        system = get_orchestration_system()
        if system:
            status = await system.get_workflow_status(execution_id)
            print(f"📊 Workflow Status: {status['status']}")
            print(f"💵 Revenue Strategy: Dynamic")
        
        return execution_id
        
    except Exception as e:
        print(f"❌ Error in monetization demo: {str(e)}")
        return None


async def demo_dynamic_pipeline():
    """Demonstrate dynamic pipeline creation."""
    print("\n🔧 DYNAMIC PIPELINE CREATION DEMO")
    print("=" * 50)
    
    system = get_orchestration_system()
    if not system:
        print("❌ Orchestration system not available")
        return
    
    # Create dynamic pipeline for image content
    requirements = {
        "content_type": "image",
        "resolution": "4k",
        "format_priority": ["png", "jpg"],
        "protection_required": True,
        "seo_optimization": True,
        "stage_config": {
            "ai_fingerprinting": {
                "algorithms": ["perceptual_hash", "deep_learning"],
                "precision": "high"
            }
        }
    }
    
    try:
        execution_id = await system.create_dynamic_pipeline(
            content_type="image",
            requirements=requirements,
            optimization_level="quality"
        )
        
        print(f"✅ Dynamic pipeline created and submitted: {execution_id}")
        
        status = await system.get_workflow_status(execution_id)
        print(f"📊 Pipeline Status: {status['status']}")
        print(f"🎨 Content Type: Image (4K)")
        print(f"🔧 Optimization: Quality-focused")
        
        return execution_id
        
    except Exception as e:
        print(f"❌ Error in dynamic pipeline demo: {str(e)}")
        return None


async def demo_system_monitoring():
    """Demonstrate system monitoring capabilities."""
    print("\n📊 SYSTEM MONITORING DEMO")
    print("=" * 50)
    
    system = get_orchestration_system()
    if not system:
        print("❌ Orchestration system not available")
        return
    
    try:
        # Get system metrics
        metrics = await system.get_system_metrics()
        
        print("📈 SYSTEM METRICS:")
        print(f"  ⚡ Active Workflows: {metrics['orchestration_metrics']['active_workflows']}")
        print(f"  ✅ Completed Workflows: {metrics['orchestration_metrics']['completed_workflows']}")
        print(f"  ❌ Failed Workflows: {metrics['orchestration_metrics']['failed_workflows']}")
        print(f"  📊 Success Rate: {metrics['orchestration_metrics']['success_rate']:.2%}")
        print(f"  ⏱️  Avg Execution Time: {metrics['orchestration_metrics']['average_execution_time']:.2f}s")
        print(f"  🔄 Throughput: {metrics['orchestration_metrics']['throughput']:.2f} workflows/hour")
        
        print("\n🏥 COMPONENT HEALTH:")
        for component, healthy in metrics['component_health'].items():
            status_icon = "✅" if healthy else "❌"
            print(f"  {status_icon} {component}")
        
        print(f"\n⏰ System Uptime: {metrics['system_uptime']:.2f} seconds")
        print(f"🎯 System Status: {metrics['system_status']}")
        
        # List active workflows
        active_workflows = await system.list_active_workflows()
        print(f"\n🔄 ACTIVE WORKFLOWS ({len(active_workflows)}):")
        for workflow in active_workflows:
            print(f"  📋 {workflow['name']} - {workflow['status']} ({workflow['progress']:.1%})")
        
    except Exception as e:
        print(f"❌ Error in monitoring demo: {str(e)}")


async def main():
    """Run the complete orchestration demo."""
    print("🚀 IA INFLUENCER AGENT - ORCHESTRATION MODULE DEMO")
    print("=" * 80)
    print("Author: Fahed Mlaiel <mlaiel@live.de>")
    print("Copyright (c) 2025 Fahed Mlaiel. All rights reserved.")
    print("=" * 80)
    
    try:
        # Initialize orchestration system
        print("\n🔧 INITIALIZING ORCHESTRATION SYSTEM...")
        config = OrchestrationSystemConfig(
            environment="demo",
            debug_mode=True,
            log_level="INFO"
        )
        
        system = await initialize_orchestration_system(config)
        print("✅ Orchestration system initialized successfully!")
        
        # Wait a moment for system to be ready
        await asyncio.sleep(1)
        
        # Run demos
        execution_ids = []
        
        # Content processing demo
        content_id = await demo_content_processing()
        if content_id:
            execution_ids.append(content_id)
        
        await asyncio.sleep(0.5)
        
        # Protection workflow demo
        protection_id = await demo_protection_workflow()
        if protection_id:
            execution_ids.append(protection_id)
        
        await asyncio.sleep(0.5)
        
        # Monetization workflow demo
        monetization_id = await demo_monetization_workflow()
        if monetization_id:
            execution_ids.append(monetization_id)
        
        await asyncio.sleep(0.5)
        
        # Dynamic pipeline demo
        dynamic_id = await demo_dynamic_pipeline()
        if dynamic_id:
            execution_ids.append(dynamic_id)
        
        await asyncio.sleep(1)
        
        # System monitoring demo
        await demo_system_monitoring()
        
        # Summary
        print("\n" + "=" * 80)
        print("📝 DEMO SUMMARY")
        print("=" * 80)
        print(f"🎯 Total Workflows Submitted: {len(execution_ids)}")
        print("📋 Workflow Types Demonstrated:")
        print("  • Content Processing (Audio)")
        print("  • Content Protection (Video)")
        print("  • Monetization Optimization")
        print("  • Dynamic Pipeline Creation (Image)")
        print("\n✅ All orchestration features demonstrated successfully!")
        
        # Final system status
        print("\n🏁 FINAL SYSTEM STATUS:")
        final_metrics = await system.get_system_metrics()
        print(f"  📊 Total Workflows: {final_metrics['orchestration_metrics']['completed_workflows']}")
        print(f"  🎯 Success Rate: {final_metrics['orchestration_metrics']['success_rate']:.2%}")
        print(f"  🏥 System Health: {final_metrics['system_status']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 CLEANING UP...")
        try:
            await shutdown_orchestration_system()
            print("✅ Orchestration system shutdown complete")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
