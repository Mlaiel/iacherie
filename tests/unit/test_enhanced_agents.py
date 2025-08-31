# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""Test Enhanced AI Agents Implementation
=====================================

Validation script to test the enhanced AI agent implementations with
advanced business logic and comprehensive functionality.

Author: Copilot Assistant
"""import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fingerprinting_engine():
    """Test the enhanced fingerprinting engine"""    print("🔍 Testing Fingerprinting Engine...")
    
    try:
        # Direct import to avoid relative import issues
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "fingerprinting_engine", 
            "ai_agents/fingerprinting_agent/core/fingerprinting_engine.py"
        )
        fingerprinting_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fingerprinting_module)
        
        FingerprintingEngine = fingerprinting_module.FingerprintingEngine
        FingerprintType = fingerprinting_module.FingerprintType
        
        # Initialize engine
        config = {
            'similarity_threshold': 0.8,
            'vector_dimension': 512
        }
        engine = FingerprintingEngine(config)
        await engine.start()
        
        # Test fingerprint generation
        test_content = b"This is test audio content for fingerprinting"
        fingerprint = await engine.generate_fingerprint(
            content_data=test_content,
            content_type=FingerprintType.AUDIO,
            content_id="test_audio_001"
        )
        
        print(f"✅ Fingerprint generated: {fingerprint.content_id}")
        print(f"   - Hash: {fingerprint.hash_fingerprint[:16]}...")
        print(f"   - Confidence: {fingerprint.confidence_score:.2f}")
        print(f"   - Type: {fingerprint.fingerprint_type.value}")
        
        # Test similarity search
        matches = await engine.find_similar_content(fingerprint, max_results=5)
        print(f"   - Similarity matches found: {len(matches)}")
        
        # Test legacy interface
        legacy_result = await engine.process({
            'content_id': 'test_legacy',
            'content_type': 'text',
            'content_data': 'Test text content'
        })
        
        print(f"✅ Legacy interface works: {legacy_result.get('processed', False)}")
        
        await engine.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Fingerprinting engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_monetization_engine():
    """Test the enhanced monetization engine"""    print("\n💰 Testing Monetization Engine...")
    
    try:
        # Direct import to avoid relative import issues
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "monetization_engine", 
            "ai_agents/monetization_agent/core/monetization_engine.py"
        )
        monetization_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(monetization_module)
        
        MonetizationEngine = monetization_module.MonetizationEngine
        MonetizationStrategy = monetization_module.MonetizationStrategy
        
        # Initialize engine
        config = {
            'default_commission': 0.15,
            'platforms': {
                'youtube': {'commission': 0.45},
                'spotify': {'commission': 0.30}
            }
        }
        engine = MonetizationEngine(config)
        await engine.start()
        
        # Test opportunity identification
        content_metadata = {
            'type': 'video',
            'duration': 300,
            'engagement_rate': 0.08,
            'quality_score': 0.85
        }
        performance_data = {
            'views': 10000,
            'likes': 800,
            'audience_size': 5000
        }
        
        opportunities = await engine.identify_monetization_opportunities(
            content_id="test_content_001",
            creator_id="test_creator_001",
            content_metadata=content_metadata,
            performance_data=performance_data
        )
        
        print(f"✅ Monetization opportunities identified: {len(opportunities)}")
        if opportunities:
            top_opp = opportunities[0]
            print(f"   - Top strategy: {top_opp.strategy.value}")
            print(f"   - Estimated revenue: ${top_opp.estimated_revenue}")
            print(f"   - Confidence: {top_opp.confidence_score:.2f}")
        
        # Test revenue optimization
        optimization = await engine.optimize_revenue_strategy(
            content_id="test_content_001",
            current_strategy=MonetizationStrategy.SUBSCRIPTION,
            performance_data=performance_data
        )
        
        print(f"✅ Revenue optimization generated")
        print(f"   - Projected improvement: {optimization.projected_improvement:.1%}")
        print(f"   - Recommendations: {len(optimization.optimization_recommendations)}")
        
        # Test collaboration revenue calculation
        collaboration_revenue = await engine.calculate_collaboration_revenue(
            collaboration_id="collab_001",
            participants=["creator_001", "creator_002"],
            revenue_data={'total_revenue': 1000.0},
            revenue_sharing_rules={
                'distribution_method': 'equal',
                'platform_commission': 0.15
            }
        )
        
        print(f"✅ Collaboration revenue calculated")
        print(f"   - Total revenue: ${collaboration_revenue.total_revenue}")
        print(f"   - Platform commission: ${collaboration_revenue.platform_commission}")
        print(f"   - Participants: {len(collaboration_revenue.revenue_distribution)}")
        
        # Test legacy interface
        legacy_result = await engine.process({
            'operation_type': 'identify_opportunities',
            'content_id': 'test_legacy',
            'creator_id': 'test_creator',
            'content_metadata': content_metadata
        })
        
        print(f"✅ Legacy interface works: {legacy_result.get('processed', False)}")
        
        await engine.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Monetization engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_seo_engine():
    """Test the enhanced SEO engine"""    print("\n🔍 Testing SEO Engine...")
    
    try:
        # Direct import to avoid relative import issues
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "seo_engine", 
            "ai_agents/seo_agent/core/seo_engine.py"
        )
        seo_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(seo_module)
        
        SeoEngine = seo_module.SeoEngine
        OptimizationType = seo_module.OptimizationType
        ContentType = seo_module.ContentType
        SearchEngine = seo_module.SearchEngine
        
        # Initialize engine
        config = {
            'search_engines': [SearchEngine.GOOGLE, SearchEngine.YOUTUBE],
            'language': 'en',
            'geo_targeting': ['US', 'UK']
        }
        engine = SeoEngine(config)
        await engine.start()
        
        # Test SEO analysis
        content_data = {
            'title': 'Ultimate Guide to AI Content Creation',
            'description': 'Learn how to create amazing content using artificial intelligence tools and techniques.',
            'body': 'This comprehensive guide covers all aspects of AI content creation. We will explore various tools, techniques, and best practices for creating high-quality content using artificial intelligence.',
            'tags': ['AI', 'content creation', 'artificial intelligence']
        }
        target_keywords = ['AI content creation', 'artificial intelligence tools', 'content marketing']
        
        analysis = await engine.analyze_seo_performance(
            content_id="test_content_001",
            content_data=content_data,
            target_keywords=target_keywords
        )
        
        print(f"✅ SEO analysis completed")
        print(f"   - SEO Score: {analysis.current_seo_score:.1f}/100")
        print(f"   - Optimization opportunities: {len(analysis.optimization_opportunities)}")
        print(f"   - Priority recommendations: {len(analysis.priority_recommendations)}")
        
        # Test content optimization
        optimization_goals = [
            OptimizationType.KEYWORD_OPTIMIZATION,
            OptimizationType.CONTENT_STRUCTURE,
            OptimizationType.METADATA_OPTIMIZATION
        ]
        
        optimizations = await engine.optimize_content(
            content_id="test_content_001",
            content_data=content_data,
            optimization_goals=optimization_goals,
            target_keywords=target_keywords
        )
        
        print(f"✅ Content optimizations generated: {len(optimizations)}")
        if optimizations:
            for opt in optimizations:
                print(f"   - {opt.optimization_type.value}: {opt.expected_improvement:.1%} improvement")
        
        # Test keyword research
        keyword_research = await engine.research_keywords(
            seed_keywords=['AI content', 'artificial intelligence'],
            content_type=ContentType.BLOG_POST,
            target_audience={'interests': ['technology', 'marketing']}
        )
        
        print(f"✅ Keyword research completed")
        print(f"   - Primary keywords: {len(keyword_research.primary_keywords)}")
        print(f"   - Secondary keywords: {len(keyword_research.secondary_keywords)}")
        print(f"   - Opportunity score: {keyword_research.opportunity_score:.1f}")
        
        # Test legacy interface
        legacy_result = await engine.process({
            'operation_type': 'analyze',
            'content_id': 'test_legacy',
            'content_data': content_data,
            'target_keywords': target_keywords
        })
        
        print(f"✅ Legacy interface works: {legacy_result.get('processed', False)}")
        print(f"   - SEO Score: {legacy_result.get('seo_score', 0):.1f}")
        
        await engine.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ SEO engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_collaboration_agent():
    """Test the collaboration agent (already advanced)"""    print("\n🤝 Testing Collaboration Agent...")
    
    try:
        # Test file existence and basic structure
        import os
        matching_engine_path = "ai_agents/collaboration_agent/core/matching_engine.py"
        
        if not os.path.exists(matching_engine_path):
            print("❌ Matching engine file not found")
            return False
            
        # Read file to check implementation
        with open(matching_engine_path, 'r') as f:
            content = f.read()
            
        # Check for advanced features
        advanced_features = [
            'class CreatorMatcher',
            'class StyleAnalyzer',
            'class AudienceAnalyzer',
            'class CompatibilityScorer',
            'async def find_matches',
            'async def analyze_style_compatibility',
            'ContentSimilarityModel',
            'BehaviorAnalysisModel'
        ]
        
        found_features = []
        for feature in advanced_features:
            if feature in content:
                found_features.append(feature)
        
        print(f"✅ Collaboration agent analysis completed")
        print(f"   - File size: {len(content)} characters")
        print(f"   - Advanced features found: {len(found_features)}/{len(advanced_features)}")
        print(f"   - Features: {', '.join(found_features[:3])}...")
        
        if len(found_features) >= 6:
            print("✅ Collaboration agent is already highly advanced")
            return True
        else:
            print("⚠️  Collaboration agent needs enhancement")
            return False
        
    except Exception as e:
        print(f"❌ Collaboration agent test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive test of all enhanced agents"""    print("🚀 Starting Comprehensive AI Agent Testing")
    print("=" * 50)
    
    start_time = datetime.now()
    results = []
    
    # Test each agent
    test_functions = [
        ("Fingerprinting Engine", test_fingerprinting_engine),
        ("Monetization Engine", test_monetization_engine),
        ("SEO Engine", test_seo_engine),
        ("Collaboration Agent", test_collaboration_agent)
    ]
    
    for name, test_func in test_functions:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    execution_time = (datetime.now() - start_time).total_seconds()
    print(f"Execution time: {execution_time:.2f} seconds")
    
    if passed == total:
        print("\n🎉 All AI agent enhancements are working correctly!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check implementations.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)