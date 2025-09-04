#!/usr/bin/env python3
"""Ainflue Public API Demo
Simple demonstration of the public API endpoints without requiring full SDK installation.
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️ httpx not available - install with: pip install httpx")

# Configuration
API_BASE_URL = "https://api.ainflue.com/api/v1"
API_KEY = "demo-api-key"  # Replace with actual API key

async def demo_health_check():
    """Demo: Check API health (no authentication)"""
    print("🏥 Testing API Health Check")
    print("-" * 40)
    
    if not HTTPX_AVAILABLE:
        print("❌ httpx required for this demo")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/public/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Status: {data['status']}")
                print(f"   Version: {data['version']}")
                print(f"   Response Time: {data['response_time_ms']:.1f}ms")
                
                services = data['services']
                healthy_services = [k for k, v in services.items() if v == 'healthy']
                print(f"   Healthy Services: {', '.join(healthy_services)}")
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")

async def demo_api_info():
    """Demo: Get API information (no authentication)"""
    print("\n📋 Testing API Information")
    print("-" * 40)
    
    if not HTTPX_AVAILABLE:
        print("❌ httpx required for this demo")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/public/info")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SDK Version: {data['sdk_version']}")
                print(f"   Supported Languages: {', '.join(data['supported_languages'])}")
                print(f"   Available Endpoints: {len(data['endpoints'])}")
                
                rate_limits = data['rate_limits']
                print(f"   Rate Limits: {rate_limits['requests_per_minute']}/min")
            else:
                print(f"❌ API info failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")

async def demo_sandbox_test():
    """Demo: Test sandbox endpoint (requires authentication)"""
    print("\n🧪 Testing Sandbox Environment")
    print("-" * 40)
    
    if not HTTPX_AVAILABLE:
        print("❌ httpx required for this demo")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {API_KEY}"}
            payload = {
                "endpoint": "/public/health",
                "method": "GET"
            }
            
            response = await client.post(
                f"{API_BASE_URL}/public/sandbox/test",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sandbox Test ID: {data['test_id']}")
                print(f"   Tested Endpoint: {data['endpoint']}")
                print(f"   Status Code: {data['status_code']}")
                print(f"   Response Time: {data['response_time_ms']:.1f}ms")
            elif response.status_code == 401:
                print("🔑 Sandbox test requires valid API key")
                print("   Get your API key at: https://app.ainflue.com")
            else:
                print(f"❌ Sandbox test failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")

async def demo_content_analysis():
    """Demo: Content analysis (requires authentication)"""
    print("\n🔍 Testing Content Analysis")
    print("-" * 40)
    
    if not HTTPX_AVAILABLE:
        print("❌ httpx required for this demo")
        return
    
    # Create a sample file for testing
    sample_file = Path("/tmp/demo_content.txt")
    sample_file.write_text("This is sample content for AI analysis demonstration.")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {API_KEY}"}
            
            with open(sample_file, "rb") as f:
                files = {"file": ("demo_content.txt", f, "text/plain")}
                
                response = await client.post(
                    f"{API_BASE_URL}/public/content/analyze",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Content ID: {data['content_id']}")
                print(f"   File Size: {data['file_size']} bytes")
                print(f"   Quality Score: {data['analysis']['quality_score']:.2f}")
                print(f"   Protection Recommended: {data['analysis']['protection_recommended']}")
            elif response.status_code == 401:
                print("🔑 Content analysis requires valid API key")
                print("   Get your API key at: https://app.ainflue.com")
            else:
                print(f"❌ Content analysis failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
        finally:
            # Clean up
            if sample_file.exists():
                sample_file.unlink()

def demo_documentation_access():
    """Demo: Show how to access documentation"""
    print("\n📚 Accessing Documentation")
    print("-" * 40)
    
    print("✅ Available Documentation:")
    print(f"   Interactive API Docs: {API_BASE_URL}/public/docs")
    print(f"   Python SDK Download: {API_BASE_URL}/public/sdk/python")
    print(f"   Postman Collection: {API_BASE_URL}/public/docs/postman")
    print("   Complete Documentation: docs/api/PUBLIC_API_DOCUMENTATION.md")

async def main():
    """Run all public API demonstrations"""
    print("🚀 Ainflue Public API Demo")
    print("=" * 50)
    print("Demonstrating public API endpoints and developer tools")
    print()
    
    # Test public endpoints (no auth required)
    await demo_health_check()
    await demo_api_info()
    
    # Test authenticated endpoints
    await demo_sandbox_test()
    await demo_content_analysis()
    
    # Show documentation access
    demo_documentation_access()
    
    print("\n" + "=" * 50)
    print("✨ Demo completed!")
    print()
    print("Next steps:")
    print("1. Get your API key: https://app.ainflue.com")
    print("2. Install SDK: pip install ainflue-sdk")
    print("3. Read docs: docs/api/PUBLIC_API_DOCUMENTATION.md")
    print("4. Try examples: python sdk/python/examples.py")

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Ainflue Public API Demo")
        print("Usage: python public_api_demo.py")
        print()
        print("Environment variables:")
        print("  AINFLUE_API_KEY - Your API key for authenticated endpoints")
        print("  AINFLUE_BASE_URL - API base URL (default: https://api.ainflue.com/api/v1)")
        sys.exit(0)
    
    # Allow override via environment variables
    import os
    API_KEY = os.getenv("AINFLUE_API_KEY", API_KEY)
    API_BASE_URL = os.getenv("AINFLUE_BASE_URL", API_BASE_URL)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo error: {str(e)}")
        sys.exit(1)