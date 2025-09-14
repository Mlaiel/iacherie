"""Ainflue SDK Examples
Comprehensive examples for using the Ainflue Python SDK

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import os
from pathlib import Path

from ainflue_sdk import create_sdk, create_sync_sdk, AinflueSdkConfig


# Configuration
API_KEY = os.getenv("AINFLUE_API_KEY", "your-api-key-here")
BASE_URL = os.getenv("AINFLUE_BASE_URL", "https://api.ainflue.com")


async def public_api_health_check() -> None:
    """Example: Check public API health status"""
    print("🏥 Public API Health Check")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Check API health (no authentication required)
            health = await sdk.get("/public/health")
            
            print(f"✅ API Status: {health['status']}")
            print(f"   Version: {health['version']}")
            print(f"   Response Time: {health['response_time_ms']:.2f}ms")
            print(f"   Services: {', '.join([k for k, v in health['services'].items() if v == 'healthy'])}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def public_api_info_example() -> None:
    """Example: Get public API information"""
    print("\n📋 Public API Information")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Get API info (no authentication required)
            info = await sdk.get("/public/info")
            
            print(f"✅ SDK Version: {info['sdk_version']}")
            print(f"   Supported Languages: {', '.join(info['supported_languages'])}")
            print(f"   Available Endpoints: {len(info['endpoints'])} endpoints")
            print(f"   Rate Limits: {info['rate_limits']['requests_per_minute']}/min, {info['rate_limits']['requests_per_hour']}/hour")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def sandbox_testing_example() -> None:
    """Example: Test API endpoints in sandbox"""
    print("\n🧪 Sandbox Testing Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Test an endpoint in sandbox environment
            test_request = {
                "endpoint": "/public/health",
                "method": "GET"
            }
            
            test_result = await sdk.post("/public/sandbox/test", test_request)
            
            print(f"✅ Sandbox Test ID: {test_result['test_id']}")
            print(f"   Endpoint: {test_result['endpoint']}")
            print(f"   Status Code: {test_result['status_code']}")
            print(f"   Response Time: {test_result['response_time_ms']:.2f}ms")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def content_analysis_example() -> None:
    """Example: Analyze content for fingerprinting"""
    print("\n🔍 Content Analysis Example")
    print("-" * 30)
    
    # Create SDK instance
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Create a sample text file for analysis
            sample_file = Path("/tmp/sample_content.txt")
            sample_file.write_text("This is sample content for AI analysis and fingerprinting.")
            
            # Analyze content via public API
            with open(sample_file, "rb") as f:
                analysis_result = await sdk.post_file("/public/content/analyze", {"file": f})
            
            print(f"✅ Content analysis completed")
            print(f"   Content ID: {analysis_result['content_id']}")
            print(f"   File Size: {analysis_result['file_size']} bytes")
            print(f"   Quality Score: {analysis_result['analysis']['quality_score']:.2f}")
            print(f"   Protection Recommended: {analysis_result['analysis']['protection_recommended']}")
            
            # Clean up
            sample_file.unlink()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def fingerprint_generation_example() -> None:
    """Example: Generate content fingerprint"""
    print("\n🔒 Fingerprint Generation Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Create a sample audio file simulation
            sample_file = Path("/tmp/sample_audio.txt")
            sample_file.write_text("Simulated audio content for fingerprinting")
            
            # Generate fingerprint via public API
            with open(sample_file, "rb") as f:
                fingerprint_result = await sdk.post_file("/public/content/fingerprint", {"file": f})
            
            print(f"✅ Fingerprint generated")
            print(f"   Fingerprint ID: {fingerprint_result['fingerprint_id']}")
            print(f"   Algorithm: {fingerprint_result['algorithm']}")
            print(f"   Confidence Score: {fingerprint_result['confidence_score']:.2f}")
            print(f"   Processing Time: {fingerprint_result['processing_time']:.2f}s")
            print(f"   Protection Features: {', '.join(fingerprint_result['protection_features'])}")
            
            # Clean up
            sample_file.unlink()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def sdk_download_example() -> None:
    """Example: Download SDK and documentation"""
    print("\n💾 SDK Download Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Download Python SDK
            sdk_info = await sdk.get("/public/sdk/python")
            
            print(f"✅ SDK downloaded")
            print(f"   Filename: {sdk_info['filename']}")
            print(f"   Version: {sdk_info['version']}")
            print(f"   Installation: {sdk_info['installation']}")
            print(f"   Content size: {len(sdk_info['content'])} characters")
            
            # Download Postman collection
            postman_collection = await sdk.get("/public/docs/postman")
            
            print(f"✅ Postman collection downloaded")
            print(f"   Collection Name: {postman_collection['info']['name']}")
            print(f"   Requests: {len(postman_collection['item'])} endpoints")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def content_protection_example() -> None:
    """Example: Protect content across platforms"""
    print("\n🛡️ Content Protection Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # First analyze content to get content_id
            analysis_result = await sdk.analyze_content(
                content_data="My original music track",
                content_type="audio"
            )
            
            # Enable protection
            protection_result = await sdk.protect_content(
                content_id=analysis_result.content_id,
                platforms=["youtube", "spotify", "instagram"],
                protection_options={
                    "auto_takedown": True,
                    "notification_email": True,
                    "monitoring_frequency": "daily"
                }
            )
            
            print(f"✅ Protection enabled")
            print(f"   Protection ID: {protection_result.protection_id}")
            print(f"   Status: {protection_result.status}")
            print(f"   Platforms: {', '.join(protection_result.platforms)}")
            
            # Check protection status
            status = await sdk.check_protection_status(protection_result.protection_id)
            print(f"   Current Status: {status['status']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def monetization_example() -> None:
    """Example: Monetize content with licensing"""
    print("\n💰 Monetization Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Create content license
            license_result = await sdk.create_license(
                content_id="content-123",
                license_type="royalty_free",
                terms={
                    "usage_type": "commercial",
                    "duration": "perpetual",
                    "territories": ["worldwide"],
                    "price": 99.99,
                    "currency": "USD"
                }
            )
            
            print(f"✅ License created")
            print(f"   License ID: {license_result['license_id']}")
            print(f"   Type: {license_result['license_type']}")
            print(f"   Price: ${license_result['terms']['price']}")
            
            # Get revenue statistics
            revenue_stats = await sdk.get_revenue_stats(
                date_from="2024-01-01",
                date_to="2024-12-31"
            )
            
            print(f"✅ Revenue statistics")
            print(f"   Total Revenue: ${revenue_stats.get('total_revenue', 0)}")
            print(f"   Total Licenses: {revenue_stats.get('total_licenses', 0)}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def analytics_example() -> None:
    """Example: Get platform analytics"""
    print("\n📊 Analytics Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Get content performance analytics
            analytics_data = await sdk.get_analytics(
                metric_type="content_performance",
                date_from="2024-01-01",
                date_to="2024-12-31",
                filters={
                    "content_type": "music",
                    "platform": "youtube"
                }
            )
            
            print(f"✅ Analytics retrieved")
            print(f"   Total Views: {analytics_data.get('total_views', 0):,}")
            print(f"   Engagement Rate: {analytics_data.get('engagement_rate', 0):.2%}")
            print(f"   Revenue Generated: ${analytics_data.get('revenue', 0):.2f}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def sync_example() -> None:
    """Example: Using the synchronous SDK"""
    print("\n🔄 Synchronous SDK Example")
    print("-" * 30)
    
    # Create sync SDK instance
    sdk = create_sync_sdk(api_key=API_KEY, base_url=BASE_URL)
    
    try:
        # Health check
        health = sdk.health_check()
        print(f"✅ API Health: {health.get('status', 'unknown')}")
        
        # Analyze content synchronously
        result = sdk.analyze_content(
            content_data="Synchronous content analysis",
            content_type="text"
        )
        
        print(f"✅ Sync analysis completed")
        print(f"   Content ID: {result.content_id}")
        print(f"   Confidence: {result.confidence:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        sdk.close()


async def batch_processing_example() -> None:
    """Example: Process multiple content items"""
    print("\n📦 Batch Processing Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Content items to process
            content_items = [
                {"data": "First content item", "type": "text"},
                {"data": "Second content item", "type": "text"},
                {"data": "Third content item", "type": "text"}
            ]
            
            # Process items concurrently
            tasks = [
                sdk.analyze_content(
                    content_data=item["data"],
                    content_type=item["type"]
                )
                for item in content_items
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"✅ Processed {len(content_items)} items")
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   Item {i+1}: ❌ Error - {str(result)}")
                else:
                    print(f"   Item {i+1}: ✅ ID {result.content_id}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def file_upload_example() -> None:
    """Example: Upload and analyze a file"""
    print("\n📁 File Upload Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Upload content file
            upload_result = await sdk.upload_content(
                file_path="/path/to/your/file.mp3",  # Replace with actual path
                title="My Audio Track",
                description="Sample audio track for testing",
                tags=["music", "original", "demo"]
            )
            
            print(f"✅ File uploaded")
            print(f"   Upload ID: {upload_result['upload_id']}")
            print(f"   File Size: {upload_result.get('file_size', 0)} bytes")
            print(f"   Status: {upload_result['status']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def user_management_example() -> None:
    """Example: User profile management"""
    print("\n👤 User Management Example")
    print("-" * 30)
    
    async with create_sdk(api_key=API_KEY, base_url=BASE_URL) as sdk:
        try:
            # Get user profile
            profile = await sdk.get_user_profile()
            
            print(f"✅ User profile retrieved")
            print(f"   User ID: {profile.get('user_id')}")
            print(f"   Username: {profile.get('username')}")
            print(f"   Email: {profile.get('email')}")
            print(f"   Plan: {profile.get('subscription_plan')}")
            
            # Update profile
            updated_profile = await sdk.update_user_profile({
                "display_name": "Updated Display Name",
                "notification_preferences": {
                    "email_alerts": True,
                    "sms_alerts": False
                }
            })
            
            print(f"✅ Profile updated")
            print(f"   Display Name: {updated_profile.get('display_name')}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def error_handling_example() -> None:
    """Example: Error handling and retries"""
    print("\n⚠️ Error Handling Example")
    print("-" * 30)
    
    # Configure SDK with custom retry settings
    config = AinflueSdkConfig(
        api_key="invalid-key",  # Intentionally invalid
        base_url=BASE_URL,
        max_retries=2,
        retry_delay=0.5
    )
    
    async with create_sdk(config.api_key, config.base_url, 
                         max_retries=config.max_retries,
                         retry_delay=config.retry_delay) as sdk:
        try:
            # This should fail with authentication error
            await sdk.analyze_content("test content", "text")
            
        except Exception as e:
            print(f"✅ Handled expected error: {type(e).__name__}")
            print(f"   Message: {str(e)}")


async def main() -> None:
    """Run all examples"""
    print("🚀 Ainflue SDK Examples")
    print("=" * 50)
    
    try:
        # Run public API examples (no authentication required)
        await public_api_health_check()
        await public_api_info_example()
        await sdk_download_example()
        
        # Check if API key is set for authenticated examples
        if API_KEY == "your-api-key-here":
            print("\n⚠️ Skipping authenticated examples - Please set your API key")
            print("   export AINFLUE_API_KEY=your_actual_api_key")
            print("   Some examples require authentication")
        else:
            # Run authenticated public API examples
            await sandbox_testing_example()
            await content_analysis_example()
            await fingerprint_generation_example()
            
            # Run other authenticated examples
            await content_protection_example()
            await monetization_example()
            await analytics_example()
            await batch_processing_example()
            await file_upload_example()
            await user_management_example()
            await error_handling_example()
            
            # Run sync example
            sync_example()
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    
    print("\n✨ Examples completed!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())