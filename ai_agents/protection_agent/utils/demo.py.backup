#!/usr/bin/env python3
"""Protection Agent Demo - Usage Examples
Demonstrates the capabilities of the Advanced Protection Agent

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited

This demonstration shows how to:
- Protect single and multiple content files
- Monitor protection status
- Get performance metrics
- Use bulk processing for enterprise scenarios

IMPORTANT: This is demonstration code for the proprietary Protection Agent
developed by Fahed Mlaiel. All usage requires explicit licensing.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List

# Note: In production, these would be real file bytes
DEMO_AUDIO_BYTES = b"DEMO_AUDIO_CONTENT_BYTES_HERE"
DEMO_VIDEO_BYTES = b"DEMO_VIDEO_CONTENT_BYTES_HERE"
DEMO_IMAGE_BYTES = b"DEMO_IMAGE_CONTENT_BYTES_HERE"


async def demo_single_content_protection():
    """Demonstrate protecting a single piece of content"""
    print("🎵 Demo: Single Content Protection")
    print("-" * 40)
    
    try:
        # Import the protection functions
        from protection_agent import protect_content, get_status
        
        # Content metadata
        content_metadata = {
            'type': 'audio/mp3',
            'title': 'My Amazing Song',
            'duration': 180,
            'genre': 'Electronic',
            'artist': 'Demo Artist'
        }
        
        # Owner information
        owner_info = {
            'name': 'Demo Artist',
            'email': 'demo@example.com',
            'user_id': 'demo_user_123',
            'subscription': 'premium'
        }
        
        # Protect the content
        print("📋 Protecting content...")
        result = await protect_content(
            content_data=DEMO_AUDIO_BYTES,
            content_metadata=content_metadata,
            owner_info=owner_info
        )
        
        print(f"✅ Protection completed!")
        print(f"   Request ID: {result.get('request_id')}")
        print(f"   Processing time: {result.get('processing_time_seconds', 0):.2f}s")
        print(f"   Files processed: {result.get('total_files', 0)}")
        print(f"   Success rate: {result.get('summary', {}).get('successful', 0)}/{result.get('total_files', 0)}")
        
        # Get protection status
        if result.get('protection_results') and len(result['protection_results']) > 0:
            content_id = result['protection_results'][0].get('content_id')
            if content_id:
                print(f"\n📊 Checking protection status for: {content_id}")
                status = await get_status(content_id)
                print(f"   Overall health: {status.get('overall_status', {}).get('health', 'unknown')}")
                
        return result
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return None


async def demo_multi_format_protection():
    """Demonstrate protecting multiple content formats"""
    print("\n🎨 Demo: Multi-Format Content Protection")
    print("-" * 40)
    
    try:
        from protection_agent import ProtectionAgentIndex
        
        # Initialize the protection index
        config = {
            'protection_level': 'premium',
            'monitoring': {'real_time': True, 'platforms': ['youtube', 'spotify']},
            'watermarking': {'invisible': True, 'strength': 'high'}
        }
        
        index = ProtectionAgentIndex(config)
        
        # Multiple content files
        content_data = [DEMO_AUDIO_BYTES, DEMO_VIDEO_BYTES, DEMO_IMAGE_BYTES]
        content_metadata = [
            {'type': 'audio/mp3', 'title': 'Demo Song', 'artist': 'Demo Artist'},
            {'type': 'video/mp4', 'title': 'Demo Video', 'duration': 120},
            {'type': 'image/jpeg', 'title': 'Demo Artwork', 'resolution': '1920x1080'}
        ]
        
        owner_info = {
            'name': 'Multi-Format Creator',
            'email': 'creator@example.com',
            'company': 'Demo Creative Studio'
        }
        
        # Protect all content
        print("📋 Protecting multi-format content...")
        result = await index.protect_multi_format_content(
            content_data=content_data,
            content_metadata=content_metadata,
            owner_info=owner_info
        )
        
        print(f"✅ Multi-format protection completed!")
        print(f"   Request ID: {result.get('request_id')}")
        print(f"   Total files: {result.get('total_files', 0)}")
        print(f"   Successful: {result.get('summary', {}).get('successful', 0)}")
        print(f"   Failed: {result.get('summary', {}).get('failed', 0)}")
        print(f"   Processing time: {result.get('processing_time_seconds', 0):.2f}s")
        
        return result
        
    except Exception as e:
        print(f"❌ Multi-format demo failed: {str(e)}")
        return None


async def demo_bulk_processing():
    """Demonstrate bulk content processing for enterprise"""
    print("\n🏢 Demo: Enterprise Bulk Processing")
    print("-" * 40)
    
    try:
        from protection_agent import ProtectionAgentIndex
        
        # Enterprise configuration
        config = {
            'protection_level': 'enterprise',
            'monitoring': {'platforms': 'all', 'real_time': True},
            'legal': {'auto_dmca': True, 'evidence_collection': True},
            'performance': {'batch_optimization': True}
        }
        
        index = ProtectionAgentIndex(config)
        
        # Simulate a batch of content
        content_batch = []
        for i in range(5):  # 5 items for demo
            content_batch.append({
                'data': DEMO_AUDIO_BYTES,
                'metadata': {
                    'type': 'audio/mp3',
                    'title': f'Batch Song {i+1}',
                    'artist': 'Batch Artist',
                    'album': 'Demo Album'
                },
                'protection_config': {
                    'watermarking': {'invisible': True},
                    'monitoring': {'priority': 'high'}
                }
            })
        
        owner_info = {
            'name': 'Enterprise Creator',
            'email': 'enterprise@example.com',
            'organization': 'Demo Music Label',
            'subscription': 'enterprise'
        }
        
        batch_config = {
            'chunk_size': 3,  # Process 3 items at a time
            'priority': 'high',
            'notification': True
        }
        
        print(f"📋 Processing batch of {len(content_batch)} items...")
        result = await index.bulk_content_protection(
            content_batch=content_batch,
            owner_info=owner_info,
            batch_config=batch_config
        )
        
        print(f"✅ Bulk processing completed!")
        print(f"   Batch ID: {result.get('batch_id')}")
        print(f"   Total items: {result.get('total_items', 0)}")
        print(f"   Successful: {result.get('successful', 0)}")
        print(f"   Failed: {result.get('failed', 0)}")
        print(f"   Success rate: {result.get('batch_summary', {}).get('success_rate', 0):.1f}%")
        print(f"   Average time per item: {result.get('batch_summary', {}).get('average_time_per_item', 0):.2f}s")
        
        return result
        
    except Exception as e:
        print(f"❌ Bulk processing demo failed: {str(e)}")
        return None


def demo_performance_metrics():
    """Demonstrate getting performance metrics"""
    print("\n📈 Demo: Performance Metrics")
    print("-" * 40)
    
    try:
        from protection_agent import get_metrics
        
        # Get current metrics
        metrics = get_metrics()
        
        print("📊 Current Performance Metrics:")
        print(f"   Timestamp: {metrics.get('timestamp', 'N/A')}")
        
        system_metrics = metrics.get('metrics', {})
        print(f"   Total requests: {system_metrics.get('total_requests', 0)}")
        print(f"   Successful protections: {system_metrics.get('successful_protections', 0)}")
        print(f"   Failed protections: {system_metrics.get('failed_protections', 0)}")
        print(f"   Average processing time: {system_metrics.get('average_processing_time', 0):.3f}s")
        print(f"   Total content protected: {system_metrics.get('total_content_protected', 0)}")
        
        service_health = metrics.get('service_health', {})
        print(f"   Service health: {len([s for s in service_health.values() if s == 'healthy'])}/{len(service_health)} healthy")
        
        uptime = metrics.get('uptime_info', {})
        print(f"   System ready: {uptime.get('system_ready', False)}")
        print(f"   All services available: {uptime.get('all_services_available', False)}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Metrics demo failed: {str(e)}")
        return None


async def demo_protection_status_monitoring():
    """Demonstrate protection status monitoring"""
    print("\n🔍 Demo: Protection Status Monitoring")
    print("-" * 40)
    
    try:
        from protection_agent import ProtectionAgentIndex
        
        index = ProtectionAgentIndex()
        
        # Simulate content ID (in real scenario, this comes from protection result)
        content_id = "demo_content_12345"
        
        print(f"📋 Checking protection status for: {content_id}")
        
        # Note: In real scenario, this would return actual status
        # For demo, we'll show the expected structure
        status = await index.get_protection_status(content_id)
        
        print(f"✅ Protection status retrieved!")
        print(f"   Content ID: {status.get('content_id', 'N/A')}")
        print(f"   Timestamp: {status.get('timestamp', 'N/A')}")
        
        overall = status.get('overall_status', {})
        print(f"   Overall health: {overall.get('health', 'unknown')}")
        print(f"   Issues: {len(overall.get('issues', []))}")
        print(f"   Warnings: {len(overall.get('warnings', []))}")
        
        if overall.get('recommendations'):
            print("   Recommendations:")
            for rec in overall.get('recommendations', [])[:3]:  # Show first 3
                print(f"     - {rec}")
        
        return status
        
    except Exception as e:
        print(f"❌ Status monitoring demo failed: {str(e)}")
        return None


async def main():
    """Run all demonstrations"""
    print("🚀 Advanced Protection Agent - Comprehensive Demo")
    print("=" * 60)
    print("Author: Fahed Mlaiel (mlaiel@live.de)")
    print("Project: IA Influencer Agent Protection System")
    print("⚠️  Proprietary Software - All Rights Reserved")
    print("=" * 60)
    
    # Run demonstrations
    demos = [
        ("Single Content Protection", demo_single_content_protection),
        ("Multi-Format Protection", demo_multi_format_protection),
        ("Enterprise Bulk Processing", demo_bulk_processing),
        ("Protection Status Monitoring", demo_protection_status_monitoring)
    ]
    
    results = {}
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n🎯 Running: {demo_name}")
            result = await demo_func()
            results[demo_name] = "✅ Success" if result else "❌ Failed"
        except Exception as e:
            print(f"❌ {demo_name} failed with exception: {str(e)}")
            results[demo_name] = "❌ Exception"
    
    # Performance metrics (synchronous)
    print(f"\n🎯 Running: Performance Metrics")
    try:
        metrics_result = demo_performance_metrics()
        results["Performance Metrics"] = "✅ Success" if metrics_result else "❌ Failed"
    except Exception as e:
        print(f"❌ Performance Metrics failed: {str(e)}")
        results["Performance Metrics"] = "❌ Exception"
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DEMO SUMMARY")
    print("=" * 60)
    
    for demo_name, status in results.items():
        print(f"{demo_name}: {status}")
    
    successful = sum(1 for status in results.values() if status == "✅ Success")
    total = len(results)
    
    print(f"\n📊 Overall: {successful}/{total} demos successful")
    
    if successful == total:
        print("🎉 All demonstrations completed successfully!")
        print("🛡️ Protection Agent is ready for production use!")
    else:
        print("⚠️ Some demonstrations had issues - check logs above")
    
    print("\n💼 For licensing and business inquiries: mlaiel@live.de")
    print("🔒 This is proprietary software - unauthorized use prohibited")


if __name__ == "__main__":
    asyncio.run(main())
