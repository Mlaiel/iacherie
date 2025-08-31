"""SEO Agent Examples - Industrial-Grade Implementation Examples

Comprehensive collection of real-world, production-ready examples demonstrating
the full capabilities of the SEO Agent system for various content types and use cases.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Project Team Specializations:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + AI Prompt Engineer
- Expert: Fahed Mlaiel <mlaiel@live.de>

🚨 STRONG WARNING FOR COPYRIGHT VIOLATORS:
Any attempt to steal, copy, reverse-engineer, or commercialize this code without explicit written authorization 
will result in immediate legal action under German and international intellectual property law.
Contact mlaiel@live.de for licensing inquiries only.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .seo_agent import SEOAgent, ContentType, OptimizationType
from .seo_manager import SEOAgentManager, CampaignType, CampaignStatus
from .index import SEOSystem
from .keyword_research import KeywordAnalyzer

logger = logging.getLogger(__name__)

class SEOAgentExamples:
    """    Industrial-grade examples demonstrating SEO Agent capabilities
    
    This class provides comprehensive, real-world examples for:
    - Music industry SEO optimization
    - Video content optimization
    - Blog and article optimization
    - E-commerce product optimization
    - Podcast episode optimization
    - Social media content optimization
    """    
    def __init__(self):
        self.seo_system = None
        self.results_cache = {}

    async def initialize(self):
        """Initialize the SEO system for examples"""        self.seo_system = SEOSystem({
            'environment': 'development',
            'ai_optimization': True,
            'real_time_monitoring': True,
            'comprehensive_analysis': True
        })
        await self.seo_system.initialize()

    async def music_industry_seo_example(self) -> Dict[str, Any]:
        """        Comprehensive music industry SEO optimization example
        
        Demonstrates optimization for:
        - Music tracks and albums
        - Artist profiles and bios
        - Music video content
        - Playlist optimization
        - Cross-platform music discovery
        """        print("🎵 Music Industry SEO Optimization Example")
        print("=" * 50)
        
        try:
            # Example: New music track optimization
            music_track_content = {
                'id': 'track_indie_dreams_2025',
                'type': ContentType.MUSIC_TRACK.value,
                'title': 'Indie Dreams - Midnight Sessions',
                'artist': 'The Neon Collective',
                'album': 'Urban Anthology',
                'genre': 'Indie Rock',
                'release_date': '2025-01-15',
                'duration': '4:23',
                'content': '''
                "Indie Dreams" is a captivating indie rock masterpiece that embodies the raw energy 
                and emotional depth of underground music culture. This track features haunting guitar 
                melodies, powerful drum patterns, and introspective lyrics that explore themes of 
                artistic authenticity and creative freedom.
                
                Recorded during late-night studio sessions, the song captures the essence of indie 
                rock's rebellious spirit while maintaining sophisticated musical arrangements. The 
                track's dynamic shifts between intimate verses and explosive choruses create an 
                immersive listening experience that resonates with both casual listeners and dedicated 
                indie music enthusiasts.
                
                Perfect for indie rock playlists, alternative radio stations, and music discovery 
                platforms seeking authentic, guitar-driven content with emotional depth and artistic integrity.
                ''',
                'tags': [
                    'indie rock', 'alternative music', 'new release', 'guitar-driven',
                    'emotional lyrics', 'underground music', 'authentic sound', 'indie artist'
                ],
                'metadata': {
                    'bpm': 128,
                    'key': 'E minor',
                    'mood': 'introspective',
                    'energy_level': 'medium-high',
                    'vocal_style': 'emotive',
                    'instrumentation': ['electric guitar', 'bass', 'drums', 'vocals']
                },
                'url': 'https://example.com/indie-dreams-midnight-sessions',
                'streaming_platforms': [
                    'spotify', 'apple_music', 'youtube_music', 'soundcloud', 'bandcamp'
                ]
            }
            
            # Perform comprehensive SEO analysis
            print("🔍 Analyzing music track SEO performance...")
            seo_analysis = await self.seo_system.analyze_content(
                content=music_track_content,
                analysis_options={
                    'depth': 'expert',
                    'target_keywords': [
                        'indie rock music', 'new indie releases', 'underground music',
                        'alternative rock songs', 'indie music 2025', 'guitar-driven music'
                    ],
                    'competitor_analysis': True,
                    'trend_analysis': True,
                    'platform_optimization': music_track_content['streaming_platforms']
                }
            )
            
            print(f"✅ SEO Analysis Results:")
            print(f"   • Current Score: {seo_analysis.current_score:.1f}/100")
            print(f"   • Potential Score: {seo_analysis.potential_score:.1f}/100")
            print(f"   • Traffic Impact Estimate: +{seo_analysis.estimated_traffic_impact.get('percentage_increase', 0):.1f}%")
            
            # Advanced keyword research for music content
            print("
🎯 Performing music-specific keyword research...")
            music_keywords = await self.seo_system.research_keywords(
                seed_keywords=[
                    'indie rock', 'alternative music', 'underground bands',
                    'new music releases', 'indie artists 2025'
                ],
                content_type=ContentType.MUSIC_TRACK,
                research_options={
                    'depth': 'comprehensive',
                    'include_long_tail': True,
                    'analyze_music_trends': True,
                    'platform_specific': True,
                    'seasonal_analysis': True,
                    'demographic_targeting': {
                        'age_groups': ['18-24', '25-34', '35-44'],
                        'interests': ['indie music', 'alternative rock', 'music discovery']
                    }
                }
            )
            
            print(f"✅ Music Keyword Research:")
            print(f"   • Total Keywords: {len(music_keywords)}")
            
            # Display top performing keywords
            top_keywords = sorted(
                music_keywords.items(),
                key=lambda x: (x[1].relevance_score * x[1].search_volume * (1 - x[1].keyword_difficulty/10)),
                reverse=True
            )[:8]
            
            print("   • Top Opportunity Keywords:")
            for keyword, data in top_keywords:
                opportunity_score = data.relevance_score * data.search_volume * (1 - data.keyword_difficulty/10)
                print(f"     - '{keyword}': {data.search_volume:,} searches, "
                      f"difficulty {data.keyword_difficulty:.1f}/10, "
                      f"opportunity: {opportunity_score:.0f}")
            
            # Content optimization for music platforms
            print("
⚡ Optimizing content for music platforms...")
            music_optimization = await self.seo_system.optimize_content(
                content=music_track_content,
                optimization_goals=[
                    OptimizationType.KEYWORD_OPTIMIZATION,
                    OptimizationType.METADATA_OPTIMIZATION,
                    OptimizationType.CONTENT_STRUCTURE,
                    OptimizationType.AUDIO_SEO,
                    OptimizationType.SOCIAL_SIGNALS
                ],
                target_keywords=[kw for kw, _ in top_keywords[:5]],
                platform_specific_optimization={
                    'spotify': True,
                    'apple_music': True,
                    'youtube_music': True,
                    'soundcloud': True
                }
            )
            
            print(f"✅ Music Content Optimization:")
            print(f"   • Optimizations Applied: {len(music_optimization['applied_optimizations'])}")
            print(f"   • Estimated Discoverability Increase: {music_optimization['improvement_metrics']['discoverability_score']:.1f}%")
            
            # Create music marketing campaign
            print("
📈 Creating music marketing SEO campaign...")
            music_campaign_config = {
                'name': 'Indie Dreams - Music Discovery Campaign',
                'description': 'Comprehensive SEO campaign for indie rock track promotion and discovery',
                'type': CampaignType.MUSIC_SEO.value,
                'priority': 1,
                'target_content_ids': [music_track_content['id']],
                'target_keywords': [kw for kw, _ in top_keywords[:10]],
                'optimization_goals': [
                    'keyword_optimization',
                    'content_structure',
                    'audio_seo',
                    'social_signals',
                    'playlist_optimization'
                ],
                'platform_focus': music_track_content['streaming_platforms'],
                'target_audience': {
                    'demographics': ['18-34'],
                    'interests': ['indie music', 'alternative rock', 'music discovery'],
                    'geographic_focus': ['US', 'UK', 'Canada', 'Australia']
                },
                'budget_allocation': {
                    'keyword_optimization': 25.0,
                    'content_optimization': 30.0,
                    'playlist_placement': 20.0,
                    'social_media_optimization': 15.0,
                    'influencer_outreach': 10.0
                },
                'timeline': {
                    'start_date': datetime.now(),
                    'end_date': datetime.now() + timedelta(days=60)
                },
                'success_metrics': [
                    'streaming_plays_increase',
                    'playlist_additions',
                    'social_media_mentions',
                    'artist_follower_growth',
                    'geographic_reach_expansion'
                ]
            }
            
            music_campaign = await self.seo_system.create_seo_campaign(
                campaign_config=music_campaign_config,
                auto_start=False
            )
            
            print(f"✅ Music Campaign Created:")
            print(f"   • Campaign ID: {music_campaign.campaign_id}")
            print(f"   • Duration: {music_campaign_config['timeline']['end_date'] - music_campaign_config['timeline']['start_date']}")
            print(f"   • Target Platforms: {len(music_campaign_config['platform_focus'])}")
            
            return {
                'seo_analysis': seo_analysis,
                'keyword_research': music_keywords,
                'content_optimization': music_optimization,
                'campaign': music_campaign,
                'success_indicators': {
                    'seo_improvement_potential': seo_analysis.improvement_percentage,
                    'keyword_opportunities': len(top_keywords),
                    'optimization_score': music_optimization['improvement_metrics']['overall_score'],
                    'campaign_readiness': True
                }
            }
            
        except Exception as e:
            logger.error(f"Music industry SEO example failed: {str(e)}")
            raise

    async def video_content_seo_example(self) -> Dict[str, Any]:
        """        Professional video content SEO optimization example
        
        Covers optimization for:
        - YouTube videos and channels
        - TikTok short-form content
        - Educational and tutorial videos
        - Entertainment content
        - Video series and playlists
        """        print("🎬 Video Content SEO Optimization Example")
        print("=" * 50)
        
        video_content = {
            'id': 'video_music_production_tutorial_2025',
            'type': ContentType.VIDEO_CONTENT.value,
            'title': 'Complete Music Production Tutorial: From Idea to Final Mix',
            'description': '''
            Master the art of music production with this comprehensive tutorial covering every step 
            from initial concept to professional-quality final mix. This in-depth guide explores 
            modern production techniques, industry-standard software, and creative approaches used 
            by professional producers.
            
            What You'll Learn:
            - Song structure and arrangement principles
            - Recording techniques for various instruments
            - MIDI programming and virtual instruments
            - Mixing fundamentals and advanced techniques
            - Mastering basics for radio-ready sound
            - Industry tips and professional workflows
            
            Perfect for aspiring producers, musicians looking to enhance their skills, and anyone 
            interested in the technical and creative aspects of modern music production. No prior 
            experience required - we start with the basics and progress to advanced techniques.
            
            Includes downloadable project files, samples, and bonus content for hands-on learning.
            ''',
            'duration': '28:45',
            'video_quality': '4K',
            'upload_date': '2025-01-20',
            'category': 'Education',
            'tags': [
                'music production', 'tutorial', 'recording', 'mixing', 'mastering',
                'DAW', 'audio engineering', 'music technology', 'producer tips',
                'home studio', 'music software', 'beat making'
            ],
            'target_audience': 'musicians, producers, audio enthusiasts',
            'video_chapters': [
                {'title': 'Introduction & Setup', 'timestamp': '00:00'},
                {'title': 'Song Structure Planning', 'timestamp': '02:30'},
                {'title': 'Recording Techniques', 'timestamp': '07:15'},
                {'title': 'MIDI Programming', 'timestamp': '12:00'},
                {'title': 'Mixing Fundamentals', 'timestamp': '18:30'},
                {'title': 'Final Master & Export', 'timestamp': '25:00'}
            ],
            'platforms': ['youtube', 'vimeo', 'tiktok_series'],
            'url': 'https://example.com/complete-music-production-tutorial'
        }
        
        # Comprehensive video SEO analysis
        print("🔍 Analyzing video content SEO...")
        video_analysis = await self.seo_system.analyze_content(
            content=video_content,
            analysis_options={
                'depth': 'expert',
                'target_keywords': [
                    'music production tutorial', 'how to make music', 'recording tips',
                    'mixing tutorial', 'home studio setup', 'music producer guide'
                ],
                'platform_optimization': video_content['platforms'],
                'video_specific_seo': True,
                'thumbnail_optimization': True,
                'engagement_analysis': True
            }
        )
        
        print(f"✅ Video SEO Analysis:")
        print(f"   • Current Score: {video_analysis.current_score:.1f}/100")
        print(f"   • Video-specific Score: {video_analysis.content_quality_score:.1f}/100")
        print(f"   • Engagement Potential: {video_analysis.user_experience_score:.1f}/100")
        
        return {
            'seo_analysis': video_analysis,
            'video_optimization_recommendations': video_analysis.recommendations[:5],
            'platform_specific_tips': {
                'youtube': 'Optimize for search and suggested videos',
                'tiktok': 'Focus on trending hashtags and short-form engagement',
                'vimeo': 'Emphasize professional quality and portfolio presentation'
            }
        }

    async def ecommerce_product_seo_example(self) -> Dict[str, Any]:
        """        E-commerce product SEO optimization example
        
        Demonstrates optimization for:
        - Product pages and descriptions
        - Category pages
        - Product images and media
        - Customer reviews integration
        - Shopping feed optimization
        """        print("🛒 E-commerce Product SEO Example")
        print("=" * 45)
        
        product_content = {
            'id': 'product_wireless_headphones_pro',
            'type': ContentType.PRODUCT_PAGE.value,
            'title': 'WirelessPro Studio Headphones - Professional Grade Audio',
            'product_name': 'WirelessPro Studio',
            'brand': 'AudioTech',
            'category': 'Audio Equipment > Headphones > Wireless',
            'price': 299.99,
            'currency': 'USD',
            'description': '''
            Experience professional-grade audio with WirelessPro Studio Headphones, designed for 
            musicians, audio professionals, and serious music enthusiasts. These premium wireless 
            headphones deliver studio-quality sound with advanced noise cancellation and all-day comfort.
            
            Key Features:
            - Professional-grade 40mm drivers for exceptional sound clarity
            - Active noise cancellation with ambient sound control
            - 30-hour battery life with quick charge technology
            - Studio-quality wireless connectivity with aptX HD support
            - Comfortable over-ear design with memory foam padding
            - Built-in microphone for calls and voice commands
            - Foldable design for easy transport and storage
            
            Perfect for:
            • Music production and mixing
            • Critical listening and audio analysis
            • Travel and commuting
            • Gaming and entertainment
            • Professional audio work
            
            Includes premium carrying case, charging cable, and 3.5mm backup cable.
            2-year warranty with professional support.
            ''',
            'specifications': {
                'driver_size': '40mm',
                'frequency_response': '20Hz - 20kHz',
                'impedance': '32 ohms',
                'connectivity': 'Bluetooth 5.0, aptX HD',
                'battery_life': '30 hours',
                'weight': '280g',
                'colors': ['Black', 'Silver', 'Blue']
            },
            'features': [
                'Active Noise Cancellation',
                'Professional Audio Quality',
                '30-Hour Battery Life',
                'Quick Charge Technology',
                'Foldable Design',
                'Built-in Microphone'
            ],
            'target_keywords': [
                'wireless headphones', 'professional headphones', 'studio headphones',
                'noise cancelling headphones', 'music production headphones'
            ],
            'images': [
                'product_main.jpg', 'product_side.jpg', 'product_details.jpg',
                'lifestyle_studio.jpg', 'packaging.jpg'
            ],
            'url': 'https://example.com/wirelesspro-studio-headphones'
        }
        
        # E-commerce SEO analysis
        print("🔍 Analyzing product page SEO...")
        product_analysis = await self.seo_system.analyze_content(
            content=product_content,
            analysis_options={
                'depth': 'expert',
                'ecommerce_focus': True,
                'product_schema': True,
                'image_optimization': True,
                'local_seo': True,
                'shopping_feed_optimization': True
            }
        )
        
        print(f"✅ Product SEO Analysis:")
        print(f"   • Product Page Score: {product_analysis.current_score:.1f}/100")
        print(f"   • Schema Markup Score: {product_analysis.schema_markup_status.get('score', 0):.1f}/100")
        print(f"   • Commercial Intent Optimization: {product_analysis.content_quality_score:.1f}/100")
        
        return {
            'seo_analysis': product_analysis,
            'product_optimization': 'Comprehensive e-commerce SEO optimization completed',
            'conversion_optimization_tips': [
                'Optimize product title for search intent',
                'Implement rich snippets for better SERP visibility',
                'Optimize product images with descriptive alt text',
                'Create compelling meta descriptions with pricing info',
                'Implement customer review schema markup'
            ]
        }

    async def run_all_examples(self) -> Dict[str, Any]:
        """        Run all SEO optimization examples and return comprehensive results
        """        print("🚀 Running All SEO Agent Examples")
        print("=" * 60)
        
        await self.initialize()
        
        results = {}
        
        try:
            # Run music industry example
            print("
" + "="*20 + " MUSIC INDUSTRY " + "="*20)
            results['music_industry'] = await self.music_industry_seo_example()
            
            # Run video content example
            print("
" + "="*20 + " VIDEO CONTENT " + "="*21)
            results['video_content'] = await self.video_content_seo_example()
            
            # Run e-commerce example
            print("
" + "="*20 + " E-COMMERCE " + "="*23)
            results['ecommerce'] = await self.ecommerce_product_seo_example()
            
            print("
🎉 All Examples Completed Successfully!")
            print("
Next Steps:")
            print("1. Review the detailed optimization recommendations")
            print("2. Implement the suggested SEO improvements")
            print("3. Monitor performance metrics and adjust strategies")
            print("4. Scale successful optimizations across more content")
            print("5. Contact mlaiel@live.de for production licensing")
            
            return results
            
        except Exception as e:
            logger.error(f"Examples execution failed: {str(e)}")
            raise
        
        finally:
            if self.seo_system:
                await self.seo_system.shutdown()

# Convenience functions for direct execution
async def run_music_example():
    """Quick access to music industry SEO example"""    examples = SEOAgentExamples()
    await examples.initialize()
    try:
        return await examples.music_industry_seo_example()
    finally:
        await examples.seo_system.shutdown()

async def run_video_example():
    """Quick access to video content SEO example"""    examples = SEOAgentExamples()
    await examples.initialize()
    try:
        return await examples.video_content_seo_example()
    finally:
        await examples.seo_system.shutdown()

async def run_ecommerce_example():
    """Quick access to e-commerce SEO example"""    examples = SEOAgentExamples()
    await examples.initialize()
    try:
        return await examples.ecommerce_product_seo_example()
    finally:
        await examples.seo_system.shutdown()

# Main execution for standalone running
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SEO Agent Examples')
    parser.add_argument('--music', action='store_true', help='Run music industry example')
    parser.add_argument('--video', action='store_true', help='Run video content example')
    parser.add_argument('--ecommerce', action='store_true', help='Run e-commerce example')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    
    args = parser.parse_args()
    
    if args.music:
        asyncio.run(run_music_example())
    elif args.video:
        asyncio.run(run_video_example())
    elif args.ecommerce:
        asyncio.run(run_ecommerce_example())
    elif args.all:
        examples = SEOAgentExamples()
        asyncio.run(examples.run_all_examples())
    else:
        print("Use --all to run all examples, or specify --music, --video, or --ecommerce")

# Export main classes and functions
__all__ = [
    'SEOAgentExamples',
    'run_music_example',
    'run_video_example', 
    'run_ecommerce_example'
]

import asyncio
from datetime import datetime, timedelta
import json

# Import SEO Agent components
from seo_agent import (
    SEOSystem, SEOAgent, SEOAgentManager,
    KeywordAnalyzer, TrendAnalyzer, CompetitorAnalyzer,
    MetadataOptimizer, ContentStructureOptimizer, LinkBuilder,
    SEOMetricsCollector, SEOReportGenerator,
    ContentType, OptimizationType, ReportType, ReportFormat,
    ReportConfig
)

async def example_basic_content_analysis():
    """    Example 1: Basic SEO content analysis
    Demonstrates analyzing a blog post for SEO optimization opportunities
    """    print("🔍 Example 1: Basic SEO Content Analysis")
    print("=" * 50)
    
    # Initialize SEO Agent
    seo_agent = SEOAgent({
        'languages': ['en', 'de', 'fr'],
        'content_types': ['blog', 'music', 'video']
    })
    await seo_agent.initialize()
    
    # Sample blog content
    blog_content = {
        'content_type': ContentType.BLOG_POST,
        'title': 'Ultimate Guide to Music Production in 2025',
        'content': '''
        Music production has evolved significantly in recent years. With advances in digital audio workstations (DAWs), 
        producers can now create professional-quality tracks from their home studios. This guide covers essential 
        music production techniques including beat making, mixing, mastering, and sound design.
        
        Key areas we'll explore:
        - Setting up your home studio
        - Choosing the right DAW
        - Beat making fundamentals
        - Audio mixing techniques
        - Mastering your tracks
        - Sound design principles
        ''',
        'meta_description': 'Learn music production with this comprehensive 2025 guide covering beat making, mixing, and mastering.',
        'target_keywords': ['music production', 'beat making', 'audio mixing', 'home studio'],
        'url_slug': 'ultimate-music-production-guide-2025'
    }
    
    # Analyze content
    result = await seo_agent.process(blog_content)
    
    print(f"SEO Score: {result['seo_score']:.2f}/1.00")
    print(f"Content Type: {result['content_analysis']['content_type']}")
    print(f"Word Count: {result['content_analysis']['word_count']}")
    print(f"Reading Level: {result['content_analysis']['reading_level']}")
    
    print("\n🎯 Top Keywords Found:")
    for keyword in result['keyword_analysis']['top_keywords'][:5]:
        print(f"  • {keyword['keyword']} (density: {keyword['density']:.2f}%)")
    
    print("\n💡 Optimization Suggestions:")
    for suggestion in result['optimization_suggestions'][:3]:
        print(f"  • {suggestion['title']}: {suggestion['description']}")
    
    print("\n" + "=" * 50 + "\n")
    return result

async def example_music_track_optimization():
    """    Example 2: Music track SEO optimization
    Shows how to optimize music content for better discoverability
    """    print("🎵 Example 2: Music Track SEO Optimization")
    print("=" * 50)
    
    # Initialize complete SEO system
    seo_system = SEOSystem({
        'enable_metrics': True,
        'enable_reporting': True,
        'content_types': ['music', 'audio']
    })
    await seo_system.initialize()
    
    # Music track content
    music_track = {
        'content_type': ContentType.MUSIC_TRACK,
        'title': 'Midnight Vibes - Chill Lo-Fi Beat',
        'artist': 'BeatMaker Pro',
        'album': 'Nocturnal Sessions',
        'genre': 'lo-fi hip hop',
        'duration': '3:24',
        'description': 'A smooth lo-fi hip hop beat perfect for studying, relaxing, or late-night coding sessions.',
        'tags': ['lo-fi', 'chill', 'study music', 'hip hop', 'instrumental', 'relaxing'],
        'target_keywords': ['lo-fi beats', 'chill hip hop', 'study music', 'relaxing beats'],
        'mood': 'chill, relaxing, focused',
        'instruments': ['piano', 'drums', 'bass', 'vinyl crackle']
    }
    
    # Comprehensive analysis
    analysis_result = await seo_system.analyze_content_comprehensive(music_track)
    
    print(f"🎼 Track: {music_track['title']}")
    print(f"Artist: {music_track['artist']}")
    print(f"SEO Score: {analysis_result['seo_analysis']['seo_score']:.2f}/1.00")
    
    print("\n🔍 SEO Analysis Results:")
    print(f"  • Content Quality Score: {analysis_result['seo_analysis']['content_quality_score']:.2f}")
    print(f"  • Keyword Optimization: {analysis_result['seo_analysis']['keyword_optimization_score']:.2f}")
    print(f"  • Metadata Completeness: {analysis_result['seo_analysis']['metadata_score']:.2f}")
    
    # Optimize the content
    optimized_result = await seo_system.optimize_content_complete(
        music_track,
        target_keywords=['lo-fi beats', 'chill music', 'study playlist']
    )
    
    print("\n✨ Optimization Results:")
    print(f"  • Optimized Title: {optimized_result['optimized_content']['title']}")
    print(f"  • Enhanced Description: {optimized_result['optimized_content']['description'][:100]}...")
    print(f"  • SEO Tags: {', '.join(optimized_result['optimized_content']['seo_tags'][:5])}")
    
    print("\n📈 Performance Predictions:")
    for prediction in optimized_result['performance_predictions']['keyword_rankings']:
        print(f"  • '{prediction['keyword']}' - Expected ranking: #{prediction['predicted_position']}")
    
    print("\n" + "=" * 50 + "\n")
    return optimized_result

async def example_keyword_research_workflow():
    """    Example 3: Advanced keyword research workflow
    Demonstrates comprehensive keyword research and analysis
    """    print("🔬 Example 3: Advanced Keyword Research Workflow")
    print("=" * 50)
    
    # Initialize keyword research components
    keyword_analyzer = KeywordAnalyzer({
        'max_keywords': 50,
        'search_engines': ['google', 'youtube', 'spotify']
    })
    
    trend_analyzer = TrendAnalyzer({
        'trend_sources': ['google_trends', 'social_media', 'music_platforms']
    })
    
    competitor_analyzer = CompetitorAnalyzer({
        'max_competitors': 10,
        'analysis_depth': 'comprehensive'
    })
    
    await keyword_analyzer.initialize()
    await trend_analyzer.initialize()
    await competitor_analyzer.initialize()
    
    # Research keywords for a music blog
    seed_keyword = 'electronic music production'
    
    print(f"🔍 Researching keywords for: '{seed_keyword}'")
    
    # Step 1: Basic keyword research
    keyword_research = await keyword_analyzer.research_keywords(
        seed_keyword,
        content_type='blog',
        max_keywords=25
    )
    
    print(f"\n📊 Found {len(keyword_research['keywords'])} related keywords:")
    for kw in keyword_research['keywords'][:10]:
        print(f"  • {kw['keyword']} - Volume: {kw['search_volume']:,} - Difficulty: {kw['difficulty']:.1f}/10")
    
    # Step 2: Trend analysis
    top_keywords = [kw['keyword'] for kw in keyword_research['keywords'][:10]]
    trend_analysis = await trend_analyzer.analyze_keyword_trends(
        top_keywords,
        time_period=timedelta(days=90)
    )
    
    print(f"\n📈 Trend Analysis (90 days):")
    print(f"  • Overall trend: {trend_analysis['overall_trend']}")
    print(f"  • Trending up: {len(trend_analysis['trending_up'])} keywords")
    print(f"  • Trending down: {len(trend_analysis['trending_down'])} keywords")
    
    # Step 3: Competitor analysis
    competitor_analysis = await competitor_analyzer.analyze_competitors(
        keywords=[seed_keyword],
        max_competitors=5
    )
    
    print(f"\n🏆 Top Competitors:")
    for competitor in competitor_analysis['competitors'][:3]:
        print(f"  • {competitor['domain']} - Authority: {competitor['domain_authority']}")
        print(f"    Keywords: {len(competitor['ranking_keywords'])}")
    
    print(f"\n💎 Keyword Opportunities:")
    for opportunity in competitor_analysis['keyword_gaps'][:5]:
        print(f"  • '{opportunity['keyword']}' - Gap score: {opportunity['opportunity_score']:.1f}")
    
    print("\n" + "=" * 50 + "\n")
    return {
        'keyword_research': keyword_research,
        'trend_analysis': trend_analysis,
        'competitor_analysis': competitor_analysis
    }

async def example_seo_campaign_management():
    """    Example 4: Complete SEO campaign management
    Shows how to create, run, and monitor SEO campaigns
    """    print("🚀 Example 4: SEO Campaign Management")
    print("=" * 50)
    
    # Initialize SEO system with campaign management
    seo_system = SEOSystem({
        'enable_campaigns': True,
        'enable_metrics': True,
        'campaign_tracking': True
    })
    await seo_system.initialize()
    
    # Define campaign content
    campaign_content = [
        {
            'content_type': ContentType.BLOG_POST,
            'title': 'Best DAW Software for Music Production 2025',
            'content': 'Comprehensive review of digital audio workstations for music producers...',
            'target_keywords': ['best daw software', 'music production software', 'digital audio workstation']
        },
        {
            'content_type': ContentType.VIDEO,
            'title': 'FL Studio Tutorial: Making Your First Beat',
            'description': 'Step-by-step tutorial for creating beats in FL Studio...',
            'target_keywords': ['fl studio tutorial', 'beat making tutorial', 'music production tutorial']
        },
        {
            'content_type': ContentType.MUSIC_TRACK,
            'title': 'Sample Pack: Modern Trap Beats',
            'description': 'Collection of high-quality trap beats and samples...',
            'target_keywords': ['trap beats', 'sample pack', 'music samples']
        }
    ]
    
    # Create SEO campaign
    campaign_config = {
        'name': 'Music Production Content Marketing Campaign',
        'description': 'Comprehensive SEO campaign targeting music production enthusiasts',
        'content_type': 'mixed',
        'target_audience': 'music producers, beatmakers, audio engineers',
        'primary_keywords': ['music production', 'beat making', 'audio mixing', 'daw software'],
        'secondary_keywords': ['home studio', 'music software', 'audio equipment', 'mixing tips'],
        'content_items': campaign_content,
        'duration_days': 60,
        'optimization_level': 'aggressive',
        'tracking_metrics': ['rankings', 'traffic', 'conversions', 'engagement']
    }
    
    print(f"📋 Creating campaign: '{campaign_config['name']}'")
    
    # Create and start campaign
    campaign = await seo_system.campaign_manager.create_campaign(campaign_config)
    
    print(f"✅ Campaign created successfully!")
    print(f"  • Campaign ID: {campaign.id}")
    print(f"  • Content items: {len(campaign.content_items)}")
    print(f"  • Target keywords: {len(campaign.target_keywords)}")
    print(f"  • Duration: {campaign.duration_days} days")
    
    # Start campaign execution
    execution_result = await seo_system.campaign_manager.start_campaign(campaign.id)
    
    print(f"\n🚀 Campaign execution started:")
    print(f"  • Status: {execution_result['status']}")
    print(f"  • Execution ID: {execution_result['execution_id']}")
    print(f"  • Estimated completion: {execution_result['estimated_completion']}")
    
    # Get campaign performance
    performance = await seo_system.campaign_manager.get_campaign_performance(campaign.id)
    
    print(f"\n📊 Campaign Performance:")
    print(f"  • Progress: {performance['progress_percentage']:.1f}%")
    print(f"  • Content processed: {performance['content_processed']}/{performance['total_content']}")
    print(f"  • Average SEO improvement: +{performance['avg_seo_improvement']:.2f}")
    
    print("\n📈 Performance by Content Type:")
    for content_type, stats in performance['content_type_performance'].items():
        print(f"  • {content_type}: Avg score {stats['avg_score']:.2f} (+{stats['improvement']:.2f})")
    
    print("\n" + "=" * 50 + "\n")
    return campaign

async def example_content_optimization_workflow():
    """    Example 5: Advanced content optimization workflow
    Shows detailed optimization of different content types
    """    print("⚡ Example 5: Advanced Content Optimization Workflow")
    print("=" * 50)
    
    # Initialize optimization components
    metadata_optimizer = MetadataOptimizer({
        'optimization_level': 'aggressive',
        'include_schema': True
    })
    
    content_optimizer = ContentStructureOptimizer({
        'target_readability': 8.0,  # Grade level
        'keyword_density_target': 0.02  # 2%
    })
    
    link_builder = LinkBuilder({
        'internal_link_ratio': 0.15,  # 15% of content
        'external_authority_threshold': 70
    })
    
    await metadata_optimizer.initialize()
    await content_optimizer.initialize() 
    await link_builder.initialize()
    
    # Sample content for optimization
    content = {
        'title': 'Music Mixing Tips',
        'content': '''
        Mixing music is an art that requires both technical knowledge and creative intuition. 
        Professional mixing engineers spend years perfecting their craft. Here are essential 
        mixing techniques every producer should know.
        
        EQ is fundamental to good mixing. Use high-pass filters to remove unwanted low frequencies. 
        Compression helps control dynamics. Reverb adds space and depth to your mix.
        
        Always reference your mix on different speakers and headphones. Professional studios 
        use multiple monitoring systems to ensure translations.
        ''',
        'target_keywords': ['music mixing', 'audio mixing tips', 'mixing techniques', 'music production'],
        'content_type': 'blog',
        'author': 'Audio Engineer Pro',
        'publish_date': '2025-01-15'
    }
    
    print(f"🎯 Optimizing content: '{content['title']}'")
    
    # Step 1: Metadata optimization
    metadata_result = await metadata_optimizer.optimize_metadata(content)
    
    print(f"\n📋 Metadata Optimization:")
    print(f"  • Original title: {content['title']}")
    print(f"  • Optimized title: {metadata_result['title_tag']}")
    print(f"  • Meta description: {metadata_result['meta_description'][:80]}...")
    print(f"  • Focus keywords: {', '.join(metadata_result['keywords'][:3])}")
    
    # Step 2: Content structure optimization
    structure_result = await content_optimizer.optimize_structure(content)
    
    print(f"\n🏗️ Structure Optimization:")
    print(f"  • Reading level: {structure_result['readability_score']:.1f}")
    print(f"  • Keyword density: {structure_result['keyword_density']:.2f}%")
    print(f"  • Suggested headings: {len(structure_result['headings'])}")
    
    for heading in structure_result['headings'][:3]:
        print(f"    - {heading['level']}: {heading['text']}")
    
    # Step 3: Link building
    link_result = await link_builder.build_content_links(content)
    
    print(f"\n🔗 Link Building:")
    print(f"  • Internal links added: {len(link_result['internal_links'])}")
    print(f"  • External links added: {len(link_result['external_links'])}")
    
    print(f"\n  Internal links:")
    for link in link_result['internal_links'][:3]:
        print(f"    - {link['anchor_text']} → {link['url']}")
    
    print(f"\n  External links:")
    for link in link_result['external_links'][:2]:
        print(f"    - {link['anchor_text']} → {link['domain']} (Authority: {link['authority']})")
    
    print("\n" + "=" * 50 + "\n")
    
    return {
        'metadata': metadata_result,
        'structure': structure_result,
        'links': link_result
    }

async def example_metrics_and_reporting():
    """    Example 6: Metrics collection and automated reporting
    Demonstrates comprehensive metrics tracking and report generation
    """    print("📊 Example 6: Metrics Collection & Automated Reporting")
    print("=" * 50)
    
    # Initialize metrics and reporting system
    metrics_collector = SEOMetricsCollector({
        'retention_days': 90,
        'aggregation_intervals': ['1h', '1d', '1w'],
        'alert_thresholds': {
            'seo_score_drop': 0.1,
            'traffic_drop': 0.2,
            'ranking_drop': 5
        }
    })
    
    report_generator = SEOReportGenerator(metrics_collector, {
        'template_dir': 'templates',
        'output_dir': 'reports'
    })
    
    await metrics_collector.initialize()
    await report_generator.initialize()
    
    # Simulate collecting metrics over time
    print("📈 Collecting sample metrics...")
    
    # Simulate a week of data
    for day in range(7):
        for hour in range(0, 24, 4):  # Every 4 hours
            timestamp = datetime.utcnow() - timedelta(days=6-day, hours=23-hour)
            
            # Content metrics
            metrics_collector.record_metric(
                'content_seo_score',
                0.75 + (day * 0.02) + (hour * 0.001),  # Improving trend
                labels={'content_type': 'blog'},
                timestamp=timestamp
            )
            
            # Traffic metrics
            traffic = 1000 + (day * 100) + (hour * 10)
            metrics_collector.record_metric(
                'organic_traffic',
                traffic,
                labels={'source': 'google'},
                timestamp=timestamp
            )
            
            # Ranking metrics
            position = max(1, 15 - day)  # Improving rankings
            metrics_collector.record_metric(
                'keyword_ranking_position',
                position,
                labels={'keyword': 'music production', 'search_engine': 'google'},
                timestamp=timestamp
            )
    
    # Record campaign metrics
    campaign_data = {
        'campaign_id': 'music_campaign_2025',
        'optimization_score': 0.82,
        'roi_analysis': {'roi': 3.5, 'cost': 1000, 'revenue': 3500}
    }
    metrics_collector.record_campaign_metrics(campaign_data)
    
    # Get performance dashboard
    dashboard = metrics_collector.get_performance_dashboard()
    
    print(f"\n📊 Performance Dashboard:")
    print(f"  • Total content analyzed: {dashboard['overview']['total_content_analyzed']}")
    print(f"  • Average SEO score: {dashboard['overview']['avg_seo_score']:.2f}")
    print(f"  • Keywords tracked: {dashboard['overview']['total_keywords_tracked']}")
    print(f"  • Average load time: {dashboard['overview']['avg_page_load_time']:.2f}s")
    
    # Content metrics summary
    content_metrics = dashboard['content_metrics']['seo_score']
    print(f"\n📝 Content Performance (7 days):")
    print(f"  • Min SEO score: {content_metrics['min']:.2f}")
    print(f"  • Max SEO score: {content_metrics['max']:.2f}")
    print(f"  • Average: {content_metrics['mean']:.2f}")
    print(f"  • Trend: {content_metrics.get('trend', 'stable')}")
    
    # Generate comprehensive report
    print(f"\n📄 Generating comprehensive report...")
    
    report_config = ReportConfig(
        report_type=ReportType.COMPREHENSIVE,
        format=ReportFormat.HTML,
        time_period=timedelta(days=7),
        include_visualizations=True,
        include_recommendations=True,
        branding={
            'company_name': 'Music Production Studio',
            'copyright_holder': 'Fahed Mlaiel'
        }
    )
    
    report_result = await report_generator.generate_report(report_config)
    
    print(f"✅ Report generated successfully!")
    print(f"  • Report ID: {report_result['report_id']}")
    print(f"  • Format: {report_result['report']['format']}")
    print(f"  • Sections: {report_result['report']['metadata']['sections_count']}")
    print(f"  • Charts: {report_result['report']['metadata']['visualizations_count']}")
    
    # Show report preview
    print(f"\n📋 Report Preview:")
    metadata = report_result['report']['metadata']
    print(f"  • Report Type: {metadata['report_type']}")
    print(f"  • Time Period: {metadata['time_period']['duration']}")
    print(f"  • Generated: {metadata['generated_at']}")
    
    print("\n" + "=" * 50 + "\n")
    return report_result

async def example_competitive_analysis():
    """    Example 7: Competitive analysis and benchmarking
    Shows how to analyze competitors and identify opportunities
    """    print("🏆 Example 7: Competitive Analysis & Benchmarking")
    print("=" * 50)
    
    # Initialize competitor analyzer
    competitor_analyzer = CompetitorAnalyzer({
        'max_competitors': 10,
        'analysis_depth': 'deep',
        'track_changes': True
    })
    await competitor_analyzer.initialize()
    
    # Target keywords for analysis
    target_keywords = [
        'music production software',
        'beat making tutorial',
        'home recording studio',
        'audio mixing guide',
        'music production tips'
    ]
    
    print(f"🔍 Analyzing competitors for {len(target_keywords)} keywords...")
    
    # Perform competitive analysis
    competitor_analysis = await competitor_analyzer.analyze_competitors(
        keywords=target_keywords,
        max_competitors=8,
        include_content_analysis=True
    )
    
    print(f"\n🏆 Top Competitors Found: {len(competitor_analysis['competitors'])}")
    
    # Display competitor insights
    for i, competitor in enumerate(competitor_analysis['competitors'][:5], 1):
        print(f"\n#{i} {competitor['domain']}")
        print(f"  • Domain Authority: {competitor['domain_authority']}")
        print(f"  • Total Keywords: {len(competitor['ranking_keywords'])}")
        print(f"  • Avg Position: {competitor['avg_position']:.1f}")
        print(f"  • Organic Traffic: {competitor.get('organic_traffic', 'N/A')}")
        
        # Show top keywords for this competitor
        print(f"  • Top Keywords:")
        for kw in competitor['ranking_keywords'][:3]:
            print(f"    - '{kw['keyword']}' (#{kw['position']})")
    
    # Keyword gap analysis
    print(f"\n💎 Keyword Opportunities ({len(competitor_analysis['keyword_gaps'])} found):")
    for gap in competitor_analysis['keyword_gaps'][:8]:
        print(f"  • '{gap['keyword']}' - Opportunity Score: {gap['opportunity_score']:.1f}/10")
        print(f"    Avg competitor position: #{gap['competitor_avg_position']:.1f}")
        print(f"    Search volume: {gap.get('search_volume', 'N/A')}")
        print()
    
    # Content gap analysis
    if 'content_gaps' in competitor_analysis:
        print(f"📄 Content Gap Analysis:")
        for topic in competitor_analysis['content_gaps'][:5]:
            print(f"  • Topic: {topic['topic']}")
            print(f"    Coverage by competitors: {topic['competitor_coverage']}%")
            print(f"    Opportunity score: {topic['opportunity_score']:.1f}/10")
    
    print("\n" + "=" * 50 + "\n")
    return competitor_analysis

async def example_multilingual_seo():
    """    Example 8: Multi-language SEO optimization
    Demonstrates SEO for content in multiple languages
    """    print("🌍 Example 8: Multi-language SEO Optimization")
    print("=" * 50)
    
    # Initialize SEO system with multi-language support
    seo_system = SEOSystem({
        'languages': ['en', 'de', 'fr', 'es'],
        'auto_translate': True,
        'cultural_adaptation': True
    })
    await seo_system.initialize()
    
    # Original content in English
    original_content = {
        'content_type': ContentType.BLOG_POST,
        'language': 'en',
        'title': 'Electronic Music Production Guide',
        'content': '''
        Electronic music production has revolutionized the music industry. With digital audio workstations (DAWs) 
        becoming more accessible, anyone can start creating electronic music from their bedroom. This guide covers 
        essential techniques for producing electronic music, including synthesis, sampling, and arrangement.
        
        Key topics include:
        - Synthesizer programming
        - Drum programming and sampling
        - Audio effects and processing
        - Mixing electronic music
        - Mastering for digital distribution
        ''',
        'target_keywords': ['electronic music production', 'synthesizer programming', 'digital music creation'],
        'target_markets': ['US', 'UK', 'Germany', 'France']
    }
    
    print(f"🎵 Optimizing content for multiple languages:")
    print(f"Original: {original_content['title']} ({original_content['language']})")
    
    # Analyze and optimize for each target language
    multilingual_results = {}
    
    for language in ['en', 'de', 'fr']:
        print(f"\n🌐 Processing language: {language.upper()}")
        
        # Create localized content
        localized_content = original_content.copy()
        localized_content['language'] = language
        
        # Language-specific keyword research
        if language == 'de':
            localized_content['target_keywords'] = [
                'elektronische musik produktion', 
                'synthesizer programmierung', 
                'digitale musik erstellung'
            ]
        elif language == 'fr':
            localized_content['target_keywords'] = [
                'production musique électronique', 
                'programmation synthétiseur', 
                'création musicale numérique'
            ]
        
        # Comprehensive analysis
        analysis_result = await seo_system.analyze_content_comprehensive(localized_content)
        
        print(f"  • SEO Score: {analysis_result['seo_analysis']['seo_score']:.2f}")
        print(f"  • Keywords found: {len(analysis_result['keyword_research']['keywords'])}")
        print(f"  • Top keyword: '{analysis_result['keyword_research']['keywords'][0]['keyword']}'")
        
        # Store results
        multilingual_results[language] = analysis_result
    
    # Cross-language performance comparison
    print(f"\n📊 Cross-language Performance Comparison:")
    for lang, results in multilingual_results.items():
        score = results['seo_analysis']['seo_score']
        kw_count = len(results['keyword_research']['keywords'])
        print(f"  • {lang.upper()}: SEO Score {score:.2f} | {kw_count} keywords")
    
    # Generate multilingual campaign recommendations
    print(f"\n💡 Multilingual Campaign Recommendations:")
    print(f"  • Primary market: English (highest search volume)")
    print(f"  • Secondary market: German (good opportunity/competition ratio)")
    print(f"  • Tertiary market: French (emerging opportunity)")
    print(f"  • Recommended budget allocation: EN 50% | DE 30% | FR 20%")
    
    print("\n" + "=" * 50 + "\n")
    return multilingual_results

async def example_real_time_monitoring():
    """    Example 9: Real-time SEO monitoring and alerts
    Shows continuous monitoring and alert system
    """    print("⚡ Example 9: Real-time SEO Monitoring & Alerts")
    print("=" * 50)
    
    # Initialize monitoring system
    metrics_collector = SEOMetricsCollector({
        'real_time_monitoring': True,
        'alert_thresholds': {
            'seo_score_drop': 0.05,  # 5% drop triggers alert
            'ranking_position_drop': 3,  # 3 position drop triggers alert
            'traffic_drop': 0.15,  # 15% traffic drop triggers alert
            'page_load_time_increase': 0.5  # 0.5s increase triggers alert
        },
        'alert_channels': ['email', 'slack', 'webhook']
    })
    
    await metrics_collector.initialize()
    
    print("🔍 Starting real-time monitoring simulation...")
    print("Monitoring key SEO metrics with alert thresholds:")
    print("  • SEO Score drop: >5%")
    print("  • Ranking drop: >3 positions")
    print("  • Traffic drop: >15%")
    print("  • Load time increase: >0.5s")
    
    # Simulate monitoring over time with some issues
    monitoring_scenarios = [
        {
            'time': '09:00', 'seo_score': 0.85, 'ranking': 5, 'traffic': 1500, 'load_time': 2.1,
            'status': '✅ Normal', 'description': 'All metrics within normal range'
        },
        {
            'time': '09:15', 'seo_score': 0.84, 'ranking': 5, 'traffic': 1520, 'load_time': 2.0,
            'status': '✅ Normal', 'description': 'Slight improvement in load time'
        },
        {
            'time': '09:30', 'seo_score': 0.79, 'ranking': 8, 'traffic': 1450, 'load_time': 2.8,
            'status': '⚠️ ALERT', 'description': 'SEO score dropped 7%, ranking dropped 3 positions, load time increased'
        },
        {
            'time': '09:45', 'seo_score': 0.77, 'ranking': 12, 'traffic': 1200, 'load_time': 3.2,
            'status': '🚨 CRITICAL', 'description': 'Multiple critical thresholds exceeded'
        },
        {
            'time': '10:00', 'seo_score': 0.82, 'ranking': 7, 'traffic': 1400, 'load_time': 2.3,
            'status': '🔄 Recovery', 'description': 'Metrics recovering, but still monitoring'
        }
    ]
    
    print(f"\n⏰ Real-time Monitoring Log:")
    print("-" * 80)
    
    for scenario in monitoring_scenarios:
        # Record metrics
        timestamp = datetime.utcnow()
        
        metrics_collector.record_metric('content_seo_score', scenario['seo_score'], timestamp=timestamp)
        metrics_collector.record_metric('keyword_ranking_position', scenario['ranking'], 
                                       labels={'keyword': 'music production'}, timestamp=timestamp)
        metrics_collector.record_metric('organic_traffic', scenario['traffic'], timestamp=timestamp)
        metrics_collector.record_metric('page_load_time', scenario['load_time'], timestamp=timestamp)
        
        # Display monitoring update
        print(f"{scenario['time']} | {scenario['status']} | SEO: {scenario['seo_score']:.2f} | "
              f"Rank: #{scenario['ranking']} | Traffic: {scenario['traffic']} | "
              f"Load: {scenario['load_time']:.1f}s")
        print(f"         └─ {scenario['description']}")
        
        # Simulate alert if status is alert or critical
        if 'ALERT' in scenario['status'] or 'CRITICAL' in scenario['status']:
            print(f"         └─ 🔔 Alert sent via email, Slack, and webhook")
        
        print()
        
        # Small delay to simulate real-time monitoring
        await asyncio.sleep(0.1)
    
    # Show final dashboard with alerts
    dashboard = metrics_collector.get_performance_dashboard()
    alerts = dashboard.get('alerts', [])
    
    print(f"📊 Monitoring Summary:")
    print(f"  • Total alerts generated: {len(alerts)}")
    print(f"  • Current status: {'⚠️ Issues detected' if alerts else '✅ All systems normal'}")
    
    if alerts:
        print(f"\n🚨 Active Alerts:")
        for alert in alerts[-3:]:  # Show last 3 alerts
            print(f"  • {alert['type']}: {alert['message']}")
            print(f"    Severity: {alert['severity']} | Time: {alert['timestamp']}")
    
    print("\n" + "=" * 50 + "\n")
    return dashboard

async def run_all_examples():
    """    Run all SEO Agent examples to demonstrate complete functionality
    """    print("🚀 SEO Agent Complete Functionality Demonstration")
    print("=" * 70)
    print("Running comprehensive examples of all SEO Agent capabilities...")
    print("=" * 70 + "\n")
    
    try:
        # Run all examples
        examples = [
            example_basic_content_analysis,
            example_music_track_optimization,
            example_keyword_research_workflow,
            example_seo_campaign_management,
            example_content_optimization_workflow,
            example_metrics_and_reporting,
            example_competitive_analysis,
            example_multilingual_seo,
            example_real_time_monitoring
        ]
        
        results = []
        
        for i, example_func in enumerate(examples, 1):
            print(f"Running example {i}/{len(examples)}: {example_func.__name__}")
            result = await example_func()
            results.append(result)
            
            # Short pause between examples
            await asyncio.sleep(0.5)
        
        print("🎉 All examples completed successfully!")
        print("=" * 70)
        print("SEO Agent system demonstrates:")
        print("✅ Content analysis and optimization")
        print("✅ Advanced keyword research")
        print("✅ Campaign management")
        print("✅ Performance monitoring")
        print("✅ Automated reporting")
        print("✅ Competitive analysis")
        print("✅ Multi-language support")
        print("✅ Real-time monitoring")
        print("=" * 70)
        
        return results
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        raise

if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
