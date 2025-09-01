"""AI Core Module Usage Examples

Comprehensive examples demonstrating how to use the AI core module
for different creator types and business scenarios.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

# Import AI core components
from . import (
    config,
    validation,
    metrics,
    performance,
    ai_engine,
    content_processor,
    setup,
    tests
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_setup():
    """
Example: Basic module setup and configuration"""
    print("=== AI Core Module Setup Example ===")
    
    # Quick setup with default configuration
    print("1. Running quick setup...")
    success = setup.quick_setup()
    
    if success:
        print("✅ Setup completed successfully!")
        
        # Load configuration
        core_config = config.get_config()
        print(f"   Environment: {core_config.environment}")
        print(f"   Debug mode: {core_config.debug_mode}")
        print(f"   AI Engine max models: {core_config.ai_engine.max_concurrent_models}")
        
    else:
        print("❌ Setup failed!")
        
    return success


def example_content_validation():
    """Example: Content validation for different creator types"""
    print("\n=== Content Validation Examples ===")
    
    # Get validator instance
    validator = validation.content_validator
    
    # Example 1: Musician uploading audio content
    print("1. Musician - Audio Content Validation")
    audio_content = {
        "type": "audio",
        "format": "mp3",
        "duration": 180,
        "file_size": 5242880,  # 5MB
        "metadata": {
            "title": "Summer Vibes",
            "artist": "DJ Creator",
            "genre": "Electronic"
        }
    }
    
    audio_result = validator.validate_content(audio_content)
    print(f"   Valid: {audio_result.is_valid}")
    print(f"   Score: {audio_result.score:.2f}")
    print(f"   Issues: {len(audio_result.issues)}")
    
    # Example 2: Photographer uploading image content
    print("\n2. Photographer - Image Content Validation")
    image_content = {
        "type": "image",
        "format": "jpg",
        "resolution": "4K",
        "file_size": 8388608,  # 8MB
        "metadata": {
            "title": "Mountain Landscape",
            "photographer": "Nature Pro",
            "location": "Alps"
        }
    }
    
    image_result = validator.validate_content(image_content)
    print(f"   Valid: {image_result.is_valid}")
    print(f"   Score: {image_result.score:.2f}")
    print(f"   Issues: {len(image_result.issues)}")
    
    # Example 3: Blogger uploading text content
    print("\n3. Blogger - Text Content Validation")
    text_content = "This is a comprehensive blog post about digital creativity and content creation in the modern era."
    
    text_result = validator.validate_text(text_content)
    print(f"   Valid: {text_result.is_valid}")
    print(f"   Score: {text_result.score:.2f}")
    print(f"   Issues: {len(text_result.issues)}")


def example_performance_monitoring():
    """Example: Performance monitoring during content processing"""
    print("\n=== Performance Monitoring Example ===")
    
    # Get performance monitor
    monitor = performance.performance_monitor
    
    # Start monitoring
    print("1. Starting performance monitoring...")
    monitor.start_monitoring()
    
    # Simulate some work
    print("2. Simulating content processing workload...")
    
    # Get metrics collector for timing
    metrics_collector = metrics.metrics_collector
    
    # Simulate multiple content processing tasks
    for i in range(5):
        with metrics_collector.timer(f"content_processing_{i}"):
            # Simulate processing time
            import time
            time.sleep(0.1)
            
            # Record business metrics
            metrics_collector.record_metric("content_processed", 1, {
                "type": "audio" if i % 2 == 0 else "image",
                "creator_type": "musician" if i % 2 == 0 else "photographer"
            })
    
    # Check performance
    print("3. Checking performance metrics...")
    perf_metrics = monitor.collect_metrics()
    print(f"   CPU Usage: {perf_metrics.cpu_percent:.1f}%")
    print(f"   Memory Usage: {perf_metrics.memory_percent:.1f}%")
    
    # Check for alerts
    alerts = monitor.check_alerts()
    if alerts:
        print(f"   ⚠️  Performance alerts: {len(alerts)}")
        for alert in alerts:
            print(f"      - {alert.message}")
    else:
        print("   ✅ No performance alerts")
    
    # Stop monitoring
    monitor.stop_monitoring()
    print("4. Performance monitoring stopped")


def example_ai_engine_usage():
    """Example: AI engine for content analysis"""
    print("\n=== AI Engine Usage Example ===")
    
    # Get AI engine
    engine = ai_engine.ai_engine
    
    # Example: Content quality analysis
    print("1. AI-powered content quality analysis")
    
    content_samples = [
        {"type": "text", "data": "High-quality professional content with great value"},
        {"type": "text", "data": "low quality content"},
        {"type": "audio", "data": "professional_music_track.mp3"},
        {"type": "image", "data": "high_res_photo.jpg"}
    ]
    
    for i, content in enumerate(content_samples):
        print(f"\n   Sample {i+1}: {content['type']}")
        
        # Simulate AI analysis
        try:
            # In a real scenario, this would use actual AI models
            analysis_result = {
                "quality_score": 85.0,
                "content_type": content["type"],
                "safety_score": 95.0,
                "seo_potential": 80.0
            }
            
            print(f"      Quality Score: {analysis_result['quality_score']:.1f}/100")
            print(f"      Safety Score: {analysis_result['safety_score']:.1f}/100")
            print(f"      SEO Potential: {analysis_result['seo_potential']:.1f}/100")
            
        except Exception as e:
            print(f"      Analysis failed: {e}")


async def example_content_pipeline():
    """Example: Complete content processing pipeline"""
    print("\n=== Content Processing Pipeline Example ===")
    
    # Get pipeline
    pipeline = content_processor.content_pipeline
    
    # Example: Musician uploading a new track
    print("1. Musician Upload Workflow")
    
    # Create processing context
    context = content_processor.ProcessingContext(
        content={
            "type": "audio",
            "file_path": "uploads/summer_vibes.mp3",
            "metadata": {
                "title": "Summer Vibes",
                "artist": "DJ Creator",
                "genre": "Electronic",
                "duration": 180
            }
        },
        user_id="musician_123",
        creator_type="musician"
    )
    
    print("   Processing stages:")
    print("   📋 1. Validation → 🛡️  2. AI Protection → 🔍 3. SEO → 🤝 4. Collaboration → 📤 5. Distribution")
    
    try:
        # Process content through pipeline
        result = await pipeline.process_content_async(context)
        
        print(f"\n   Pipeline Result:")
        print(f"   ✅ Success: {result.success}")
        print(f"   ⏱️  Processing Time: {result.processing_time:.2f}s")
        print(f"   📊 Stages Completed: {len(result.stage_results)}")
        
        # Show stage results
        for stage_name, stage_result in result.stage_results.items():
            status = "✅" if stage_result.success else "❌"
            print(f"      {status} {stage_name}: {stage_result.message}")
            
    except Exception as e:
        print(f"   ❌ Pipeline failed: {e}")


def example_business_metrics():
    """Example: Business metrics tracking"""
    print("\n=== Business Metrics Example ===")
    
    # Get business metrics tracker
    business_tracker = metrics.BusinessMetricsTracker()
    
    # Simulate different creator activities
    print("1. Tracking creator activities...")
    
    # Musicians
    business_tracker.track_user_upload("audio", 5242880, "musician")
    business_tracker.track_user_upload("audio", 7340032, "musician")
    
    # Photographers
    business_tracker.track_user_upload("image", 8388608, "photographer")
    business_tracker.track_user_upload("image", 12582912, "photographer")
    
    # Bloggers
    business_tracker.track_user_upload("text", 50000, "blogger")
    
    # Influencers
    business_tracker.track_user_upload("video", 104857600, "influencer")
    
    # Get business summary
    print("2. Business metrics summary:")
    summary = business_tracker.get_business_summary()
    
    print(f"   Total Uploads: {summary['uploads']['total_count']}")
    print(f"   Content Types: {list(summary['content_types'].keys())}")
    print(f"   Creator Types: {list(summary['creator_types'].keys())}")
    print(f"   Total Data: {summary['uploads']['total_size_mb']:.1f} MB")
    
    # Show breakdown by creator type
    print("\n3. Breakdown by creator type:")
    for creator_type, data in summary['creator_types'].items():
        print(f"   {creator_type.title()}:")
        print(f"      Uploads: {data['count']}")
        print(f"      Average Size: {data['avg_size_mb']:.1f} MB")


def example_seo_optimization():
    """Example: SEO optimization for content"""
    print("\n=== SEO Optimization Example ===")
    
    # Get validator for SEO checks
    validator = validation.content_validator
    
    # Example SEO data for different content types
    seo_examples = [
        {
            "title": "Amazing Jazz Piano Solo - Relaxing Music for Study",
            "description": "Beautiful jazz piano music perfect for studying, working, or relaxing. Professional recording with high audio quality.",
            "tags": ["jazz", "piano", "study music", "relaxing", "instrumental"],
            "content_type": "audio"
        },
        {
            "title": "Stunning Mountain Landscape Photography Tips",
            "description": "Learn professional techniques for capturing breathtaking mountain landscapes. Complete guide with camera settings and composition tips.",
            "tags": ["photography", "landscape", "mountains", "tutorial", "nature"],
            "content_type": "image"
        },
        {
            "title": "The Ultimate Guide to Content Creation in 2025",
            "description": "Comprehensive guide covering all aspects of modern content creation, from planning to distribution. Essential tips for creators.",
            "tags": ["content creation", "digital marketing", "social media", "creator economy"],
            "content_type": "text"
        }
    ]
    
    for i, seo_data in enumerate(seo_examples):
        print(f"\n{i+1}. SEO Analysis - {seo_data['content_type'].title()} Content")
        
        result = validator.validate_seo(seo_data)
        print(f"   SEO Score: {result.score:.1f}/100")
        
        if result.issues:
            print("   Recommendations:")
            for issue in result.issues:
                print(f"      • {issue.description}")
        else:
            print("   ✅ Great SEO optimization!")


def example_error_handling():
    """Example: Error handling and recovery"""
    print("\n=== Error Handling Example ===")
    
    try:
        # Simulate various error scenarios
        print("1. Testing validation error handling...")
        
        # Invalid content should trigger validation error
        validator = validation.content_validator
        result = validator.validate_content(None)  # This should fail gracefully
        
    except validation.ValidationError as e:
        print(f"   ✅ Validation error handled: {e.error_code}")
        print(f"      Message: {e}")
        print(f"      Context: {e.context}")
        
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")
    
    try:
        print("\n2. Testing AI engine error handling...")
        
        # Try to use non-existent model
        engine = ai_engine.ai_engine
        result = engine.run_inference("non_existent_model", {"input": "test"})
        
    except ai_engine.AIEngineError as e:
        print(f"   ✅ AI engine error handled: {e.error_code}")
        print(f"      Message: {e}")
        
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")


def example_configuration_management():
    """Example: Configuration management"""
    print("\n=== Configuration Management Example ===")
    
    # Get current configuration
    current_config = config.get_config()
    print(f"1. Current environment: {current_config.environment}")
    print(f"   Debug mode: {current_config.debug_mode}")
    
    # Update configuration
    print("\n2. Updating configuration...")
    success = config.update_config({
        "debug_mode": True,
        "ai_engine": {
            "max_concurrent_models": 3
        }
    })
    
    if success:
        print("   ✅ Configuration updated successfully!")
        updated_config = config.get_config()
        print(f"   Max models: {updated_config.ai_engine.max_concurrent_models}")
    else:
        print("   ❌ Configuration update failed!")
    
    # Show configuration summary
    print("\n3. Configuration summary:")
    config_dict = current_config.to_dict()
    print(f"   AI Engine: {len(config_dict['ai_engine'])} settings")
    print(f"   Validation: {len(config_dict['validation'])} settings")
    print(f"   Performance: {len(config_dict['performance'])} settings")
    print(f"   Metrics: {len(config_dict['metrics'])} settings")


def run_all_examples():
    """Run all usage examples"""
    print("🚀 AI Core Module - Usage Examples")
    print("=" * 50)
    
    try:
        # Run synchronous examples
        example_basic_setup()
        example_content_validation()
        example_performance_monitoring()
        example_ai_engine_usage()
        example_business_metrics()
        example_seo_optimization()
        example_error_handling()
        example_configuration_management()
        
        # Run async example
        print("\nRunning async pipeline example...")
        asyncio.run(example_content_pipeline())
        
        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("\nFor more information, check the documentation:")
        print("   • README.md (English)")
        print("   • README.de.md (German)")
        print("   • README.fr.md (French)")
        
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        logger.exception("Error in examples")


def run_quick_demo():
    """Run a quick demonstration of key features"""
    print("⚡ AI Core Module - Quick Demo")
    print("=" * 30)
    
    # Quick setup
    print("1. Setup...")
    success = example_basic_setup()
    if not success:
        return
    
    # Content validation
    print("\n2. Content validation...")
    validator = validation.content_validator
    result = validator.validate_text("Sample content for testing")
    print(f"   Validation score: {result.score:.1f}")
    
    # Metrics collection
    print("\n3. Metrics collection...")
    metrics_collector = metrics.metrics_collector
    metrics_collector.record_metric("demo_metric", 100)
    print("   ✅ Metric recorded")
    
    # Performance check
    print("\n4. Performance check...")
    monitor = performance.performance_monitor
    perf_metrics = monitor.collect_metrics()
    print(f"   CPU: {perf_metrics.cpu_percent:.1f}%, Memory: {perf_metrics.memory_percent:.1f}%")
    
    print("\n✅ Quick demo completed!")


if __name__ == "__main__":
    # Run examples when script is executed
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_demo()
    else:
        run_all_examples()
