#!/usr/bin/env python3
"""
Basic usage example for Ainflue Python SDK
Demonstrates content analysis and AI agent interaction.

Run: python basic_usage.py
"""

import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables
load_dotenv()

# Import SDK (adjust import based on installation method)
try:
    from ainflue_sdk import AinflueSdk
except ImportError:
    import sys
    sys.path.append('..')
    from ainflue_sdk import AinflueSdk

console = Console()

async def main():
    """Main example function."""
    
    # Get API key from environment
    api_key = os.getenv("AINFLUE_API_KEY")
    if not api_key:
        console.print("❌ Please set AINFLUE_API_KEY environment variable", style="red")
        return
    
    console.print(Panel.fit(
        "🚀 Ainflue SDK Basic Usage Example",
        title="Example",
        border_style="blue"
    ))
    
    try:
        # Initialize SDK
        async with AinflueSdk(api_key) as sdk:
            console.print("✅ SDK initialized successfully")
            
            # 1. Validate API key
            console.print("\n🔑 Validating API key...")
            try:
                validation = await sdk.auth.validate_api_key()
                console.print(f"✅ API key valid. User: {validation['user']['name']}")
                console.print(f"📊 Plan: {validation['user']['plan']}")
            except Exception as e:
                console.print(f"❌ API key validation failed: {e}", style="red")
                return
            
            # 2. List available AI agents
            console.print("\n🤖 Listing available AI agents...")
            try:
                agents = await sdk.ai_agents.list_agents()
                console.print(f"✅ Found {len(agents)} available agents:")
                for agent in agents[:3]:  # Show first 3
                    console.print(f"  - {agent['name']}: {agent['description']}")
            except Exception as e:
                console.print(f"⚠️ Could not list agents: {e}", style="yellow")
            
            # 3. Chat with an AI agent
            console.print("\n💬 Chatting with AI agent...")
            try:
                response = await sdk.ai_agents.chat(
                    agent_name="content_analyzer",
                    message="Hello! Can you help me understand content analysis?",
                    context={"example": True}
                )
                console.print(f"🤖 Agent response: {response['response']['content'][:200]}...")
                console.print(f"🎯 Confidence: {response['confidence']:.2%}")
            except Exception as e:
                console.print(f"⚠️ Agent chat failed: {e}", style="yellow")
            
            # 4. Get performance metrics
            console.print("\n📊 Getting performance metrics...")
            try:
                metrics = await sdk.analytics.get_performance_metrics(
                    metric_type="all",
                    time_period="7d"
                )
                console.print(f"✅ Metrics retrieved:")
                console.print(f"  - Total API calls: {metrics.get('total_api_calls', 'N/A')}")
                console.print(f"  - Success rate: {metrics.get('success_rate', 'N/A')}")
                console.print(f"  - Average response time: {metrics.get('avg_response_time', 'N/A')}ms")
            except Exception as e:
                console.print(f"⚠️ Could not get metrics: {e}", style="yellow")
            
            # 5. Check usage limits
            console.print("\n📈 Checking usage limits...")
            try:
                limits = await sdk.auth.get_usage_limits()
                console.print(f"✅ Usage limits:")
                console.print(f"  - Requests remaining: {limits.get('requests_remaining', 'N/A')}")
                console.print(f"  - Daily limit: {limits.get('daily_limit', 'N/A')}")
                console.print(f"  - Reset time: {limits.get('reset_time', 'N/A')}")
            except Exception as e:
                console.print(f"⚠️ Could not get limits: {e}", style="yellow")
            
        console.print("\n🎉 Example completed successfully!", style="green")
        
    except Exception as e:
        console.print(f"\n❌ Example failed: {e}", style="red")

if __name__ == "__main__":
    # Create .env file template if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Ainflue SDK Configuration\n")
            f.write("AINFLUE_API_KEY=your-api-key-here\n")
            f.write("# Optional: Set environment\n")
            f.write("# AINFLUE_ENVIRONMENT=development  # or staging, production\n")
        
        console.print("📝 Created .env file template. Please add your API key.", style="yellow")
    
    asyncio.run(main())