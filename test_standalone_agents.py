"""
Standalone test for new SEO & Marketing agents

This test validates the core functionality without depending on the existing base agent system.
"""

import asyncio
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_keyword_engine():
    """Test keyword engine core functionality"""
    print("Testing Keyword Research Engine...")
    
    try:
        # Import the core engine directly
        from ai_agents.keyword_research_agent.core.keyword_engine import KeywordEngine, KeywordJob, KeywordResult
        
        # Test initialization
        engine = KeywordEngine()
        print("✓ KeywordEngine initialized successfully")
        
        # Test basic functionality
        async def test_async():
            await engine.start()
            
            # Test keyword discovery
            keywords = await engine.discover_primary_keywords("artificial intelligence", "general", "en")
            print(f"✓ Discovered {len(keywords)} primary keywords")
            
            # Test keyword analysis
            if keywords:
                metrics = await engine.analyze_keyword_metrics(keywords[:3])
                print(f"✓ Analyzed metrics for {len(metrics)} keywords")
            
            # Test competition analysis
            competition = await engine.analyze_keyword_competition("AI", "general")
            print(f"✓ Competition analysis completed: {competition['competition_level']}")
            
            await engine.stop()
            print("✓ KeywordEngine tests completed successfully")
        
        # Run async tests
        asyncio.run(test_async())
        return True
        
    except Exception as e:
        print(f"✗ KeywordEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optimization_engine():
    """Test content optimization engine core functionality"""
    print("\nTesting Content Optimization Engine...")
    
    try:
        # Import the core engine directly
        from ai_agents.content_optimization_agent.core.optimization_engine import OptimizationEngine, OptimizationJob, OptimizationResult
        
        # Test initialization
        engine = OptimizationEngine()
        print("✓ OptimizationEngine initialized successfully")
        
        # Test basic functionality
        async def test_async():
            await engine.start()
            
            sample_content = """
            This is a sample article about artificial intelligence and machine learning.
            AI has become very important in today's world. Many companies are using AI.
            Machine learning is a subset of AI. It helps computers learn from data.
            Artificial intelligence is revolutionizing industries across the globe.
            """
            
            # Test content analysis
            analysis = await engine.analyze_content(sample_content)
            print(f"✓ Content analysis completed - SEO score: {analysis['seo_score']:.1f}")
            
            # Test SEO optimization
            seo_result = await engine.optimize_for_seo(sample_content, ["artificial intelligence", "machine learning"], "general")
            print(f"✓ SEO optimization completed with {len(seo_result['steps'])} improvements")
            
            # Test readability improvement
            readability_result = await engine.improve_readability(sample_content)
            print(f"✓ Readability improvement completed with {len(readability_result['steps'])} changes")
            
            # Test platform adaptation
            adaptation_result = await engine.adapt_content_for_platform(sample_content, "general", "twitter")
            print(f"✓ Platform adaptation completed - score: {adaptation_result['optimization_score']:.1f}")
            
            await engine.stop()
            print("✓ OptimizationEngine tests completed successfully")
        
        # Run async tests
        asyncio.run(test_async())
        return True
        
    except Exception as e:
        print(f"✗ OptimizationEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_integration():
    """Test integration between keyword research and content optimization"""
    print("\nTesting Agent Integration...")
    
    try:
        from ai_agents.keyword_research_agent.core.keyword_engine import KeywordEngine
        from ai_agents.content_optimization_agent.core.optimization_engine import OptimizationEngine
        
        async def test_workflow():
            # Initialize engines
            keyword_engine = KeywordEngine()
            content_engine = OptimizationEngine()
            
            await keyword_engine.start()
            await content_engine.start()
            
            # Step 1: Research keywords
            topic = "sustainable technology"
            discovered_keywords = await keyword_engine.discover_primary_keywords(topic, "general", "en")
            print(f"✓ Discovered {len(discovered_keywords)} keywords for '{topic}'")
            
            # Step 2: Analyze keyword competition
            top_keywords = discovered_keywords[:3]
            keyword_metrics = await keyword_engine.analyze_keyword_metrics(top_keywords)
            print(f"✓ Analyzed competition for top {len(top_keywords)} keywords")
            
            # Step 3: Optimize content using discovered keywords
            sample_content = f"""
            {topic} is becoming increasingly important in our modern world.
            Companies are investing heavily in green technologies and sustainable solutions.
            This article explores the latest trends and innovations.
            """
            
            optimized_result = await content_engine.optimize_for_seo(sample_content, top_keywords, "general")
            print(f"✓ Content optimized using discovered keywords with {len(optimized_result['steps'])} improvements")
            
            # Step 4: Generate metadata using optimized content
            metadata = await content_engine.generate_optimized_metadata(
                optimized_result['optimized_content'], "general", top_keywords
            )
            print(f"✓ Generated metadata with title: '{metadata['title'][:50]}...'")
            
            await keyword_engine.stop()
            await content_engine.stop()
            print("✓ Integration workflow completed successfully")
        
        asyncio.run(test_workflow())
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SEO & MARKETING AGENTS - STANDALONE VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Test individual engines
    results.append(test_keyword_engine())
    results.append(test_optimization_engine())
    results.append(test_agent_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The new SEO & Marketing agents are working correctly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)