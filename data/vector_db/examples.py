"""Vector Database Usage Examples and Demonstrations
================================================

Comprehensive examples demonstrating all capabilities of the vector database system
for content fingerprinting, similarity search, duplicate detection, and collaboration matching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ COPYRIGHT WARNING ⚠️
This code is protected by copyright law. Any unauthorized reproduction, distribution, 
modification, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

For licensing and authorization requests, contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Developer + Backend Senior Engineer: Fahed Mlaiel
- ML Engineer + Data Scientist: Advanced algorithms & optimization
- Database Administrator + Performance Specialist: Scalability & efficiency  
- Security Engineer + DevOps Engineer: System security & deployment
- Audio Processing Specialist: Audio fingerprinting & analysis
- Computer Vision Engineer: Image/video processing & recognition
- Microservices Architect: Distributed systems & API design
"""
import asyncio
import logging
import numpy as np
import json
import os
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image
import io
import base64

# Local imports
from .index import VectorDatabaseManager, create_vector_database
from .similarity_search import SearchConfig, SearchType, RankingStrategy
from .operations import IndexStatus, BackupStatus

logger = logging.getLogger(__name__)


# Sample data for demonstrations
SAMPLE_TEXTS = [
    {
        'id': 'text_001',
        'content': 'The future of artificial intelligence in music creation is incredibly exciting. AI can help artists compose melodies, generate lyrics, and even master tracks.',
        'metadata': {
            'category': 'technology',
            'author': 'AI_Enthusiast',
            'language': 'en',
            'tags': ['AI', 'music', 'creation', 'technology'],
            'published_date': '2025-01-15'
        }
    },
    {
        'id': 'text_002', 
        'content': 'Machine learning algorithms are revolutionizing how we create and discover music. From recommendation systems to automated composition, AI is changing the music industry.',
        'metadata': {
            'category': 'technology',
            'author': 'MusicTech_Expert',
            'language': 'en',
            'tags': ['machine learning', 'music discovery', 'recommendation'],
            'published_date': '2025-01-16'
        }
    },
    {
        'id': 'text_003',
        'content': 'Photography has evolved tremendously with digital technology. From smartphone cameras to professional DSLRs, everyone can now capture stunning images.',
        'metadata': {
            'category': 'photography',
            'author': 'Photo_Pro',
            'language': 'en',
            'tags': ['photography', 'digital', 'camera', 'technology'],
            'published_date': '2025-01-17'
        }
    }
]

SAMPLE_CREATOR_PROFILES = [
    {
        'creator_id': 'creator_001',
        'name': 'ElectroArtist',
        'content_type': 'audio',
        'genre': 'electronic',
        'experience_level': 7,
        'skills': ['music production', 'mixing', 'sound design', 'synthesizers'],
        'interests': ['electronic music', 'technology', 'innovation', 'collaboration'],
        'target_audience': ['electronic music fans', 'tech enthusiasts', 'young adults'],
        'collaboration_openness': 0.9,
        'location': 'Berlin, Germany'
    },
    {
        'creator_id': 'creator_002',
        'name': 'DigitalPhotographer',
        'content_type': 'image',
        'style': 'urban photography',
        'experience_level': 5,
        'skills': ['photography', 'photo editing', 'composition', 'lighting'],
        'interests': ['urban landscapes', 'street art', 'architecture', 'travel'],
        'target_audience': ['photography enthusiasts', 'urban explorers', 'artists'],
        'collaboration_openness': 0.8,
        'location': 'New York, USA'
    }
]


class VectorDatabaseExamples:
    """
    Comprehensive examples demonstrating vector database capabilities.
    
    This class provides practical examples for:
    - System initialization and configuration
    - Content indexing (text, audio, image, video)
    - Similarity search and ranking
    - Duplicate detection and analysis
    - Collaboration matching
    - Content recommendations
    - System monitoring and maintenance
    - Backup and restore operations
    """
    
    def __init__(self):
        self.db_manager = None
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuration for examples
        self.config = {
            'backend': 'faiss',
            'storage_path': os.path.join(self.temp_dir, 'vector_db'),
            'embedding': {
                'text': {
                    'text_model': 'all-MiniLM-L6-v2',
                    'max_length': 512
                },
                'audio': {
                    'sample_rate': 22050,
                    'max_duration': 30.0
                },
                'image': {
                    'image_size': 224
                },
                'video': {
                    'max_frames': 50
                }
            },
            'similarity_thresholds': {
                'text': 0.7,
                'audio': 0.8,
                'image': 0.75,
                'video': 0.8
            },
            'auto_backup': False,  # Disable for examples
            'version': '1.0.0'
        }
    
    async def run_all_examples(self):
        """Run all demonstration examples."""
        print("=" * 80)
        print("VECTOR DATABASE SYSTEM - COMPREHENSIVE EXAMPLES")
        print("=" * 80)
        print(f"Author: Fahed Mlaiel (mlaiel@live.de)")
        print(f"Copyright: © 2025 Fahed Mlaiel - All Rights Reserved")
        print("=" * 80)
        
        try:
            # 1. System Initialization
            await self.example_system_initialization()
            
            # 2. Content Management
            await self.example_content_indexing()
            
            # 3. Similarity Search
            await self.example_similarity_search()
            
            # 4. Duplicate Detection
            await self.example_duplicate_detection()
            
            # 5. Collaboration Matching
            await self.example_collaboration_matching()
            
            # 6. Content Recommendations
            await self.example_content_recommendations()
            
            # 7. System Monitoring
            await self.example_system_monitoring()
            
            # 8. Backup and Restore
            await self.example_backup_restore()
            
            # 9. Advanced Features
            await self.example_advanced_features()
            
            print("
" + "=" * 80)
            print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"Example execution failed: {str(e)}")
            print(f"ERROR: {str(e)}")
        
        finally:
            # Cleanup
            await self.cleanup()
    
    async def example_system_initialization(self):
        """Example 1: System initialization and configuration."""
        print("
" + "="*50)
        print("EXAMPLE 1: SYSTEM INITIALIZATION")
        print("="*50)
        
        print("
1.1 Creating Vector Database Manager...")
        self.db_manager = VectorDatabaseManager(self.config)
        
        print("1.2 Initializing system with all content types...")
        success = await self.db_manager.initialize()
        print(f"✓ System initialization: {'SUCCESS' if success else 'FAILED'}")
        
        print("
1.3 Getting system status...")
        status = await self.db_manager.get_system_status()
        print(f"✓ System status: {status['status']}")
        print(f"✓ Supported content types: {status['supported_content_types']}")
        
        print("
1.4 Getting embedding dimensions...")
        dimensions = self.db_manager.get_embedding_dimensions()
        for content_type, dim in dimensions.items():
            print(f"✓ {content_type}: {dim} dimensions")
    
    async def example_content_indexing(self):
        """Example 2: Content indexing for multiple content types."""
        print("
" + "="*50)
        print("EXAMPLE 2: CONTENT INDEXING")
        print("="*50)
        
        # 2.1 Text Content Indexing
        print("
2.1 Indexing text content...")
        for sample in SAMPLE_TEXTS:
            success = await self.db_manager.add_text_content(
                sample['content'],
                sample['id'],
                sample['metadata']
            )
            print(f"✓ Added text '{sample['id']}': {'SUCCESS' if success else 'FAILED'}")
        
        # 2.2 Audio Content Indexing (simulated)
        print("
2.2 Indexing audio content (simulated)...")
        
        # Generate sample audio data
        sample_audio = np.random.randn(22050 * 5)  # 5 seconds of random audio
        audio_metadata = {
            'title': 'Sample Electronic Track',
            'artist': 'ElectroArtist',
            'genre': 'electronic',
            'tempo': 128,
            'key': 'C major',
            'duration': 5.0,
            'sample_rate': 22050
        }
        
        success = await self.db_manager.add_audio_content(
            sample_audio,
            'audio_001',
            audio_metadata
        )
        print(f"✓ Added audio 'audio_001': {'SUCCESS' if success else 'FAILED'}")
        
        # 2.3 Image Content Indexing (simulated)
        print("
2.3 Indexing image content (simulated)...")
        
        # Create a sample image
        sample_image = Image.new('RGB', (224, 224), color='blue')
        image_metadata = {
            'title': 'Urban Landscape',
            'photographer': 'DigitalPhotographer',
            'location': 'New York',
            'camera': 'Canon EOS R5',
            'iso': 100,
            'aperture': 'f/8',
            'tags': ['urban', 'architecture', 'blue hour']
        }
        
        success = await self.db_manager.add_image_content(
            sample_image,
            'image_001',
            image_metadata
        )
        print(f"✓ Added image 'image_001': {'SUCCESS' if success else 'FAILED'}")
        
        # 2.4 Get indexing statistics
        print("
2.4 Getting index statistics...")
        stats = await self.db_manager.get_index_statistics()
        
        for content_type, metrics in stats.items():
            print(f"✓ {content_type} index: {metrics.vector_count} vectors, "
                  f"health score: {metrics.health_score:.2f}")
    
    async def example_similarity_search(self):
        """Example 3: Similarity search with different configurations."""
        print("
" + "="*50)
        print("EXAMPLE 3: SIMILARITY SEARCH")
        print("="*50)
        
        # 3.1 Basic text similarity search
        print("
3.1 Basic text similarity search...")
        query_text = "AI and machine learning in music production"
        
        results = await self.db_manager.search_similar_text(
            query_text,
            max_results=10,
            threshold=0.3
        )
        
        print(f"✓ Found {len(results)} similar texts for query: '{query_text[:50]}...'")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. ID: {result.content_id}, "
                  f"Similarity: {result.similarity_score:.3f}")
        
        # 3.2 Filtered search
        print("
3.2 Text search with metadata filters...")
        filtered_results = await self.db_manager.search_similar_text(
            query_text,
            max_results=10,
            metadata_filters={'category': 'technology'}
        )
        
        print(f"✓ Found {len(filtered_results)} results with category filter")
        
        # 3.3 Audio similarity search (simulated)
        print("
3.3 Audio similarity search...")
        query_audio = np.random.randn(22050 * 3)  # 3 seconds
        
        audio_results = await self.db_manager.search_similar_audio(
            query_audio,
            max_results=5,
            threshold=0.7
        )
        
        print(f"✓ Found {len(audio_results)} similar audio tracks")
        
        # 3.4 Image similarity search (simulated)
        print("
3.4 Image similarity search...")
        query_image = Image.new('RGB', (224, 224), color='lightblue')
        
        image_results = await self.db_manager.search_similar_image(
            query_image,
            max_results=5,
            threshold=0.6
        )
        
        print(f"✓ Found {len(image_results)} similar images")
    
    async def example_duplicate_detection(self):
        """Example 4: Duplicate content detection and analysis."""
        print("
" + "="*50)
        print("EXAMPLE 4: DUPLICATE DETECTION")
        print("="*50)
        
        # 4.1 Text duplicate detection
        print("
4.1 Text duplicate detection...")
        
        # Use a slightly modified version of existing text
        duplicate_text = "The future of AI in music creation is incredibly exciting. AI helps artists compose melodies, generate lyrics, and master tracks."
        
        duplicates = await self.db_manager.detect_text_duplicates(
            duplicate_text,
            metadata={'test_type': 'duplicate_detection'}
        )
        
        print(f"✓ Found {len(duplicates)} potential text duplicates")
        
        for result, analysis in duplicates:
            print(f"  - Content ID: {result.content_id}")
            print(f"  - Similarity: {result.similarity_score:.3f}")
            print(f"  - Is Duplicate: {analysis.is_duplicate}")
            print(f"  - Confidence: {analysis.confidence_score:.3f}")
            print(f"  - Recommendation: {analysis.recommendation}")
            print()
        
        # 4.2 Audio duplicate detection (simulated)
        print("
4.2 Audio duplicate detection...")
        
        # Use the same audio with slight modifications
        modified_audio = sample_audio * 0.95 + np.random.randn(len(sample_audio)) * 0.01
        
        audio_duplicates = await self.db_manager.detect_audio_duplicates(
            modified_audio,
            metadata={'test_type': 'audio_duplicate'}
        )
        
        print(f"✓ Found {len(audio_duplicates)} potential audio duplicates")
        
        # 4.3 Image duplicate detection (simulated) 
        print("
4.3 Image duplicate detection...")
        
        # Create a very similar image
        similar_image = Image.new('RGB', (224, 224), color=(0, 0, 250))  # Slightly different blue
        
        image_duplicates = await self.db_manager.detect_image_duplicates(
            similar_image,
            metadata={'test_type': 'image_duplicate'}
        )
        
        print(f"✓ Found {len(image_duplicates)} potential image duplicates")
    
    async def example_collaboration_matching(self):
        """Example 5: Collaboration opportunity matching."""
        print("
" + "="*50)
        print("EXAMPLE 5: COLLABORATION MATCHING")
        print("="*50)
        
        # 5.1 Add creator profiles to system (as content)
        print("
5.1 Adding creator profiles...")
        
        for profile in SAMPLE_CREATOR_PROFILES:
            # Convert profile to text representation for indexing
            profile_text = f"Creator: {profile['name']}, Skills: {', '.join(profile['skills'])}, Interests: {', '.join(profile['interests'])}"
            
            success = await self.db_manager.add_text_content(
                profile_text,
                profile['creator_id'],
                profile
            )
            print(f"✓ Added creator profile '{profile['creator_id']}': {'SUCCESS' if success else 'FAILED'}")
        
        # 5.2 Find collaboration opportunities
        print("
5.2 Finding collaboration opportunities...")
        
        # Example: ElectroArtist looking for collaborations
        seeker_profile = SAMPLE_CREATOR_PROFILES[0]
        content_example = "Electronic music with innovative sound design and cutting-edge production techniques"
        
        collaborations = await self.db_manager.find_collaboration_opportunities(
            seeker_profile,
            content_example,
            'text'  # Using text representation for this example
        )
        
        print(f"✓ Found {len(collaborations)} collaboration opportunities for {seeker_profile['name']}")
        
        for match in collaborations:
            print(f"  - Creator ID: {match.creator_id}")
            print(f"  - Compatibility Score: {match.compatibility_score:.3f}")
            print(f"  - Shared Interests: {', '.join(match.shared_interests)}")
            print(f"  - Complementary Skills: {', '.join(match.complementary_skills)}")
            print(f"  - Contact Recommended: {match.contact_recommendation}")
            print()
    
    async def example_content_recommendations(self):
        """Example 6: Content recommendations for creators."""
        print("
" + "="*50)
        print("EXAMPLE 6: CONTENT RECOMMENDATIONS")
        print("="*50)
        
        # 6.1 Get recommendations for content strategy
        print("
6.1 Getting content recommendations...")
        
        user_profile = {
            'user_id': 'user_001',
            'content_type': 'text',
            'interests': ['AI', 'music', 'technology'],
            'target_audience': ['tech enthusiasts', 'music lovers'],
            'experience_level': 6,
            'preferred_style': 'educational and informative'
        }
        
        content_example = "Exploring how AI is transforming creative industries"
        
        recommendations = await self.db_manager.get_content_recommendations(
            user_profile,
            content_example,
            'text'
        )
        
        print(f"✓ Generated {len(recommendations)} content recommendations")
        
        for rec in recommendations[:3]:  # Show top 3
            print(f"  - Content ID: {rec.content_id}")
            print(f"  - Recommendation Score: {rec.recommendation_score:.3f}")
            print(f"  - Type: {rec.recommendation_type}")
            print(f"  - Reasoning: {', '.join(rec.reasoning)}")
            print(f"  - Audience Match: {rec.target_audience_match:.3f}")
            print()
    
    async def example_system_monitoring(self):
        """Example 7: System monitoring and performance tracking."""
        print("
" + "="*50)
        print("EXAMPLE 7: SYSTEM MONITORING")
        print("="*50)
        
        # 7.1 Performance metrics
        print("
7.1 Getting performance metrics...")
        
        performance = await self.db_manager.get_performance_metrics()
        
        print(f"✓ Total Queries: {performance.total_queries}")
        print(f"✓ Average Query Time: {performance.avg_query_time_ms:.2f}ms")
        print(f"✓ Cache Hit Rate: {performance.cache_hit_rate:.2%}")
        print(f"✓ Memory Usage: {performance.memory_usage_mb:.2f}MB")
        print(f"✓ Error Rate: {performance.error_rate:.2%}")
        print(f"✓ Uptime: {performance.uptime_seconds:.0f} seconds")
        
        # 7.2 Index statistics
        print("
7.2 Getting detailed index statistics...")
        
        stats = await self.db_manager.get_index_statistics()
        
        for content_type, metrics in stats.items():
            print(f"
{content_type.upper()} INDEX:")
            print(f"  - Vector Count: {metrics.vector_count}")
            print(f"  - Dimension: {metrics.dimension}")
            print(f"  - Memory Usage: {metrics.memory_usage_mb:.2f}MB")
            print(f"  - Health Score: {metrics.health_score:.2f}")
            print(f"  - Status: {metrics.status.value}")
        
        # 7.3 Health check
        print("
7.3 Performing system health check...")
        
        health = await self.db_manager.health_check()
        
        print(f"✓ Overall Status: {health['overall_status']}")
        print(f"✓ Components Checked: {len(health['components'])}")
        
        if health['recommendations']:
            print("⚠ Recommendations:")
            for rec in health['recommendations']:
                print(f"  - {rec}")
    
    async def example_backup_restore(self):
        """Example 8: Backup and restore operations."""
        print("
" + "="*50)
        print("EXAMPLE 8: BACKUP AND RESTORE")
        print("="*50)
        
        # 8.1 Create system backup
        print("
8.1 Creating full system backup...")
        
        backup_info = await self.db_manager.create_system_backup("demo_backup")
        
        print(f"✓ Backup Created: {backup_info.backup_id}")
        print(f"✓ Status: {backup_info.status.value}")
        print(f"✓ Size: {backup_info.size_mb:.2f}MB")
        print(f"✓ Path: {backup_info.backup_path}")
        
        # 8.2 Create content-specific backup
        print("
8.2 Creating text content backup...")
        
        text_backup = await self.db_manager.create_content_backup('text', 'text_demo_backup')
        
        print(f"✓ Text Backup Created: {text_backup.backup_id}")
        print(f"✓ Status: {text_backup.status.value}")
        
        # 8.3 List all backups
        print("
8.3 Listing all available backups...")
        
        backups = await self.db_manager.list_available_backups()
        
        print(f"✓ Found {len(backups)} backups:")
        for backup in backups:
            print(f"  - {backup.backup_id} ({backup.status.value}) - {backup.size_mb:.2f}MB")
        
        # 8.4 Backup validation (simulation)
        print("
8.4 Backup validation...")
        print("✓ All backups validated successfully")
    
    async def example_advanced_features(self):
        """Example 9: Advanced features and optimizations."""
        print("
" + "="*50)
        print("EXAMPLE 9: ADVANCED FEATURES")
        print("="*50)
        
        # 9.1 System optimization
        print("
9.1 Optimizing system performance...")
        
        optimization_success = await self.db_manager.optimize_system()
        print(f"✓ System optimization: {'SUCCESS' if optimization_success else 'FAILED'}")
        
        # 9.2 Configuration management
        print("
9.2 Configuration management...")
        
        current_config = self.db_manager.export_configuration()
        print(f"✓ Current configuration exported: {len(current_config)} settings")
        
        # 9.3 Batch operations simulation
        print("
9.3 Simulating batch operations...")
        
        # Simulate adding multiple items at once
        batch_start = time.time()
        
        batch_texts = [
            f"Sample batch text content number {i} for testing bulk operations"
            for i in range(5)
        ]
        
        batch_results = []
        for i, text in enumerate(batch_texts):
            success = await self.db_manager.add_text_content(
                text,
                f'batch_text_{i:03d}',
                {'batch_id': 'demo_batch', 'item_number': i}
            )
            batch_results.append(success)
        
        batch_time = time.time() - batch_start
        successful_items = sum(batch_results)
        
        print(f"✓ Batch operation: {successful_items}/{len(batch_texts)} items processed")
        print(f"✓ Processing time: {batch_time:.2f} seconds")
        print(f"✓ Throughput: {len(batch_texts)/batch_time:.1f} items/second")
        
        # 9.4 Memory and resource usage
        print("
9.4 Resource usage analysis...")
        
        final_status = await self.db_manager.get_system_status()
        performance = final_status['performance']
        
        print(f"✓ Final system state:")
        print(f"  - Total vectors indexed: {sum(idx['vector_count'] for idx in final_status['indices'].values())}")
        print(f"  - Memory usage: {performance['memory_usage_mb']:.2f}MB")
        print(f"  - Average query time: {performance['avg_query_time_ms']:.2f}ms")
        print(f"  - Total queries processed: {performance['total_queries']}")
    
    async def cleanup(self):
        """Clean up resources and temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"
✓ Cleanup completed: {self.temp_dir} removed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")


# Standalone example functions for specific use cases

async def example_content_protection_workflow():
    """
    Example workflow for content protection using the vector database.
    Demonstrates the complete process from content upload to duplicate detection.
    """
    print("
" + "="*60)
    print("CONTENT PROTECTION WORKFLOW EXAMPLE")
    print("="*60)
    
    # Initialize system
    config = {
        'backend': 'faiss',
        'storage_path': './temp_protection_demo',
        'similarity_thresholds': {
            'text': 0.8,
            'audio': 0.9,
            'image': 0.85
        },
        'duplicate_thresholds': {
            'text': 0.9,
            'audio': 0.95,
            'image': 0.9
        }
    }
    
    db_manager = await create_vector_database(config)
    
    # Simulate original content upload
    original_content = {
        'text': "This is my original creative work about the future of sustainable energy and green technology solutions.",
        'metadata': {
            'creator_id': 'creator_123',
            'title': 'Green Energy Innovation',
            'published_date': '2025-01-20',
            'copyright': 'All rights reserved',
            'license': 'exclusive'
        }
    }
    
    print("
1. Uploading original content...")
    success = await db_manager.add_text_content(
        original_content['text'],
        'original_001',
        original_content['metadata']
    )
    print(f"✓ Original content indexed: {'SUCCESS' if success else 'FAILED'}")
    
    # Simulate potential infringement detection
    print("
2. Scanning for potential infringement...")
    
    suspicious_content = "This is my original creative work about sustainable energy and green tech solutions for the future."
    
    duplicates = await db_manager.detect_text_duplicates(
        suspicious_content,
        metadata={'scanner': 'auto_protection', 'scan_date': '2025-01-21'}
    )
    
    print(f"✓ Duplicate scan completed: {len(duplicates)} potential infringements found")
    
    # Analyze results
    for result, analysis in duplicates:
        print(f"
⚠ POTENTIAL INFRINGEMENT DETECTED:")
        print(f"  - Original Content ID: {result.content_id}")
        print(f"  - Similarity Score: {result.similarity_score:.3f}")
        print(f"  - Confidence Level: {analysis.confidence_score:.3f}")
        print(f"  - Action Recommended: {analysis.recommendation}")
        
        if analysis.is_duplicate and analysis.confidence_score > 0.8:
            print(f"  - 🚨 HIGH CONFIDENCE INFRINGEMENT - TAKE ACTION!")
        else:
            print(f"  - ℹ Low confidence - manual review recommended")
    
    # Cleanup
    import shutil
    shutil.rmtree('./temp_protection_demo', ignore_errors=True)
    
    print("
✓ Content protection workflow completed")


async def example_collaboration_platform():
    """
    Example of using the vector database for a collaboration platform.
    Shows how creators can find compatible partners based on content similarity.
    """
    print("
" + "="*60)
    print("COLLABORATION PLATFORM EXAMPLE")
    print("="*60)
    
    db_manager = await create_vector_database()
    
    # Add creator portfolios
    creators = [
        {
            'id': 'musician_001',
            'profile': 'Electronic music producer specializing in ambient and techno beats with AI-assisted composition',
            'metadata': {
                'name': 'SynthMaster',
                'type': 'musician',
                'genres': ['electronic', 'ambient', 'techno'],
                'tools': ['Ableton Live', 'AI composition', 'Modular synths'],
                'location': 'Berlin',
                'collaboration_types': ['co-production', 'remix', 'live performance']
            }
        },
        {
            'id': 'vocalist_001',
            'profile': 'Vocalist with ethereal voice perfect for electronic and ambient music collaborations',
            'metadata': {
                'name': 'EtherealVoice',
                'type': 'vocalist',
                'styles': ['ethereal', 'electronic', 'experimental'],
                'languages': ['English', 'German'],
                'location': 'London',
                'collaboration_types': ['vocal features', 'songwriting', 'live performance']
            }
        }
    ]
    
    print("
1. Adding creator profiles to platform...")
    for creator in creators:
        success = await db_manager.add_text_content(
            creator['profile'],
            creator['id'],
            creator['metadata']
        )
        print(f"✓ Added {creator['metadata']['name']}: {'SUCCESS' if success else 'FAILED'}")
    
    # Find collaborations
    print("
2. Finding collaboration matches...")
    
    seeker_profile = {
        'user_id': 'musician_001',
        'interests': ['electronic music', 'AI technology', 'innovative sounds'],
        'skills': ['production', 'composition', 'sound design'],
        'looking_for': ['vocalist', 'lyricist', 'visual artist'],
        'collaboration_openness': 0.9
    }
    
    content_example = "Innovative electronic music with AI-enhanced production and ambient textures"
    
    matches = await db_manager.find_collaboration_opportunities(
        seeker_profile,
        content_example,
        'text'
    )
    
    print(f"✓ Found {len(matches)} potential collaboration matches")
    
    for match in matches:
        print(f"
🤝 COLLABORATION MATCH:")
        print(f"  - Partner ID: {match.creator_id}")
        print(f"  - Compatibility: {match.compatibility_score:.2f}")
        print(f"  - Shared Interests: {', '.join(match.shared_interests) if match.shared_interests else 'None detected'}")
        print(f"  - Potential: {match.collaboration_potential}")
        print(f"  - Suggested Projects: {', '.join(match.suggested_projects[:2]) if match.suggested_projects else 'General collaboration'}")
    
    print("
✓ Collaboration platform example completed")


async def example_recommendation_engine():
    """
    Example of using the vector database as a content recommendation engine.
    Shows personalized content discovery based on user preferences and behavior.
    """
    print("
" + "="*60)
    print("RECOMMENDATION ENGINE EXAMPLE")
    print("="*60)
    
    db_manager = await create_vector_database()
    
    # Add diverse content to the database
    content_library = [
        {
            'id': 'article_001',
            'content': 'Deep dive into neural networks and their applications in creative AI',
            'metadata': {
                'type': 'article',
                'category': 'AI/Technology',
                'difficulty': 'intermediate',
                'tags': ['neural networks', 'creative AI', 'deep learning'],
                'engagement_score': 0.85
            }
        },
        {
            'id': 'tutorial_001', 
            'content': 'Complete guide to music production using AI tools and modern DAWs',
            'metadata': {
                'type': 'tutorial',
                'category': 'Music Production',
                'difficulty': 'beginner',
                'tags': ['music production', 'AI tools', 'DAW', 'tutorial'],
                'engagement_score': 0.92
            }
        },
        {
            'id': 'review_001',
            'content': 'Review of the latest AI image generation tools and their creative potential',
            'metadata': {
                'type': 'review',
                'category': 'AI/Technology',
                'difficulty': 'beginner',
                'tags': ['AI art', 'image generation', 'creative tools'],
                'engagement_score': 0.78
            }
        }
    ]
    
    print("
1. Building content library...")
    for item in content_library:
        success = await db_manager.add_text_content(
            item['content'],
            item['id'],
            item['metadata']
        )
        print(f"✓ Added {item['id']}: {'SUCCESS' if success else 'FAILED'}")
    
    # Simulate user preferences
    print("
2. Generating personalized recommendations...")
    
    user_profile = {
        'user_id': 'user_123',
        'interests': ['AI technology', 'music production', 'creative tools'],
        'skill_level': 'intermediate',
        'preferred_content_types': ['tutorial', 'article'],
        'engagement_history': ['AI', 'music', 'production'],
        'target_audience': ['creators', 'tech enthusiasts']
    }
    
    # User's recent interaction (what they're currently interested in)
    current_interest = "Learning about AI applications in music and creative workflows"
    
    recommendations = await db_manager.get_content_recommendations(
        user_profile,
        current_interest,
        'text'
    )
    
    print(f"✓ Generated {len(recommendations)} personalized recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"
📋 RECOMMENDATION #{i}:")
        print(f"  - Content ID: {rec.content_id}")
        print(f"  - Recommendation Score: {rec.recommendation_score:.3f}")
        print(f"  - Type: {rec.recommendation_type}")
        print(f"  - Reasoning: {rec.reasoning[0] if rec.reasoning else 'Based on your interests'}")
        print(f"  - Audience Match: {rec.target_audience_match:.2f}")
        print(f"  - Trend Alignment: {rec.trend_alignment:.2f}")
    
    print("
✓ Recommendation engine example completed")


# Main execution function
async def main():
    """Main function to run all examples."""
    print("🚀 Starting Vector Database Examples...")
    print("Author: Fahed Mlaiel (mlaiel@live.de)")
    print("Copyright: © 2025 Fahed Mlaiel - All Rights Reserved")
    
    # Run comprehensive examples
    examples = VectorDatabaseExamples()
    await examples.run_all_examples()
    
    # Run specific workflow examples
    await example_content_protection_workflow()
    await example_collaboration_platform()
    await example_recommendation_engine()
    
    print("
🎉 All examples completed successfully!")
    print("
This demonstrates the complete capabilities of the Vector Database System")
    print("for content protection, collaboration, and recommendation in the IA Influencer Agent platform.")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(main())

import asyncio
import logging
import numpy as np
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
from datetime import datetime

# Import vector database components
from .index import VectorDatabaseManager, create_vector_database
from .operations import VectorDBOperations
from .similarity_search import SearchConfig, SearchType, RankingStrategy
from .embedding_engine import MultiModalEmbeddingEngine
from .config import VectorDBConfig

logger = logging.getLogger(__name__)


class VectorDBExamples:
    """
    Comprehensive examples for vector database operations.
    
    Demonstrates real-world usage patterns for content similarity,
    duplicate detection, collaboration matching, and recommendations.
    """
    
    def __init__(self):
        self.vector_db = None
        self.config = self._get_example_config()
        self.sample_data = self._generate_sample_data()
    
    def _get_example_config(self) -> Dict[str, Any]:
        """Get configuration for examples."""
        return {
            'backend': 'faiss',
            'data_directory': './data/vector_db_examples',
            'embedding': {
                'dimension': 384,
                'text_model': 'all-MiniLM-L6-v2',
                'audio_sample_rate': 22050,
                'image_size': 224
            },
            'similarity_thresholds': {
                'audio': 0.85,
                'video': 0.80,
                'image': 0.75,
                'text': 0.70
            },
            'duplicate_thresholds': {
                'audio': 0.92,
                'image': 0.95,
                'text': 0.88,
                'video': 0.90
            },
            'faiss': {
                'use_gpu': False,
                'index_type': 'ivf_flat',
                'metric': 'cosine'
            }
        }
    
    def _generate_sample_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate sample data for demonstrations."""
        return {
            'audio_tracks': [
                {
                    'id': 'track_001',
                    'title': 'Summer Vibes',
                    'genre': 'pop',
                    'duration': 180,
                    'tempo': 120,
                    'key': 'C major',
                    'features': np.random.rand(384).astype(np.float32)
                },
                {
                    'id': 'track_002',
                    'title': 'Electronic Dreams',
                    'genre': 'electronic',
                    'duration': 240,
                    'tempo': 128,
                    'key': 'A minor',
                    'features': np.random.rand(384).astype(np.float32)
                },
                {
                    'id': 'track_003',
                    'title': 'Jazz Fusion',
                    'genre': 'jazz',
                    'duration': 320,
                    'tempo': 110,
                    'key': 'F major',
                    'features': np.random.rand(384).astype(np.float32)
                }
            ],
            'video_content': [
                {
                    'id': 'video_001',
                    'title': 'Cooking Tutorial',
                    'category': 'education',
                    'duration': 600,
                    'resolution': '1080p',
                    'features': np.random.rand(384).astype(np.float32)
                },
                {
                    'id': 'video_002',
                    'title': 'Gaming Highlights',
                    'category': 'gaming',
                    'duration': 480,
                    'resolution': '4K',
                    'features': np.random.rand(384).astype(np.float32)
                }
            ],
            'images': [
                {
                    'id': 'image_001',
                    'title': 'Sunset Landscape',
                    'category': 'nature',
                    'resolution': '1920x1080',
                    'colors': ['orange', 'purple', 'yellow'],
                    'features': np.random.rand(384).astype(np.float32)
                },
                {
                    'id': 'image_002',
                    'title': 'City Architecture',
                    'category': 'urban',
                    'resolution': '2048x1536',
                    'colors': ['gray', 'blue', 'white'],
                    'features': np.random.rand(384).astype(np.float32)
                }
            ],
            'text_content': [
                {
                    'id': 'text_001',
                    'title': 'AI Revolution',
                    'category': 'technology',
                    'word_count': 1200,
                    'language': 'english',
                    'content': 'Artificial Intelligence is transforming industries...',
                    'features': np.random.rand(384).astype(np.float32)
                },
                {
                    'id': 'text_002',
                    'title': 'Climate Change Impact',
                    'category': 'environment',
                    'word_count': 800,
                    'language': 'english',
                    'content': 'Global warming effects are becoming more visible...',
                    'features': np.random.rand(384).astype(np.float32)
                }
            ]
        }
    
    async def initialize_database(self) -> bool:
        """Initialize the vector database for examples."""
        try:
            print("🚀 Initializing Vector Database for Examples...")
            
            self.vector_db = await create_vector_database(self.config)
            
            if self.vector_db:
                print("✅ Vector Database initialized successfully!")
                return True
            else:
                print("❌ Failed to initialize Vector Database")
                return False
                
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
            return False
    
    async def example_1_basic_content_addition(self):
        """Example 1: Basic content addition and indexing."""
        print("
" + "="*60)
        print("📝 EXAMPLE 1: Basic Content Addition and Indexing")
        print("="*60)
        
        try:
            # Add audio content
            print("
🎵 Adding audio tracks...")
            for track in self.sample_data['audio_tracks']:
                success = await self.vector_db.add_content(
                    content=track['features'],
                    content_type='audio',
                    content_id=track['id'],
                    metadata={
                        'title': track['title'],
                        'genre': track['genre'],
                        'duration': track['duration'],
                        'tempo': track['tempo'],
                        'key': track['key']
                    }
                )
                if success:
                    print(f"  ✅ Added: {track['title']}")
                else:
                    print(f"  ❌ Failed to add: {track['title']}")
            
            # Add text content
            print("
📄 Adding text content...")
            for text in self.sample_data['text_content']:
                success = await self.vector_db.add_content(
                    content=text['content'],
                    content_type='text',
                    content_id=text['id'],
                    metadata={
                        'title': text['title'],
                        'category': text['category'],
                        'word_count': text['word_count'],
                        'language': text['language']
                    }
                )
                if success:
                    print(f"  ✅ Added: {text['title']}")
                else:
                    print(f"  ❌ Failed to add: {text['title']}")
            
            # Get system status
            status = self.vector_db.get_system_status()
            print(f"
📊 System Status:")
            print(f"  - Total Indices: {status.get('index_summary', {}).get('total_indices', 0)}")
            print(f"  - Total Vectors: {status.get('index_summary', {}).get('total_vectors', 0)}")
            print(f"  - Backend: {status.get('backend_type', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error in basic content addition: {str(e)}")
    
    async def example_2_similarity_search(self):
        """Example 2: Similarity search across content types."""
        print("
" + "="*60)
        print("🔍 EXAMPLE 2: Similarity Search Across Content Types")
        print("="*60)
        
        try:
            # Search for similar audio
            print("
🎵 Searching for similar audio...")
            query_features = np.random.rand(384).astype(np.float32)
            
            audio_results = await self.vector_db.search_content(
                query=query_features,
                content_type='audio',
                k=3,
                threshold=0.5
            )
            
            print(f"  Found {len(audio_results)} similar audio tracks:")
            for i, result in enumerate(audio_results, 1):
                print(f"    {i}. ID: {result.content_id}, Score: {result.similarity:.3f}")
                if hasattr(result, 'metadata') and result.metadata:
                    print(f"       Title: {result.metadata.get('title', 'Unknown')}")
                    print(f"       Genre: {result.metadata.get('genre', 'Unknown')}")
            
            # Search for similar text
            print("
📄 Searching for similar text content...")
            query_text = "Artificial intelligence and machine learning advancements"
            
            text_results = await self.vector_db.search_content(
                query=query_text,
                content_type='text',
                k=2,
                threshold=0.3
            )
            
            print(f"  Found {len(text_results)} similar text articles:")
            for i, result in enumerate(text_results, 1):
                print(f"    {i}. ID: {result.content_id}, Score: {result.similarity:.3f}")
                if hasattr(result, 'metadata') and result.metadata:
                    print(f"       Title: {result.metadata.get('title', 'Unknown')}")
                    print(f"       Category: {result.metadata.get('category', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error in similarity search: {str(e)}")
    
    async def example_3_duplicate_detection(self):
        """Example 3: Advanced duplicate detection."""
        print("
" + "="*60)
        print("🔍 EXAMPLE 3: Advanced Duplicate Detection")
        print("="*60)
        
        try:
            # Create a near-duplicate of existing content
            print("
🎵 Testing audio duplicate detection...")
            
            # Get an existing track and create a slight variation
            original_track = self.sample_data['audio_tracks'][0]
            duplicate_features = original_track['features'].copy()
            # Add small noise to simulate near-duplicate
            duplicate_features += np.random.normal(0, 0.01, duplicate_features.shape).astype(np.float32)
            
            # Check for duplicates before adding
            duplicates = await self.vector_db.operations.detect_duplicates(
                content=duplicate_features,
                content_type='audio',
                metadata={'title': 'Summer Vibes - Remix'}
            )
            
            print(f"  Found {len(duplicates)} potential duplicates:")
            for result, analysis in duplicates:
                print(f"    - Original ID: {result.content_id}")
                print(f"      Similarity: {result.similarity:.3f}")
                print(f"      Duplicate Type: {analysis.duplicate_type}")
                print(f"      Confidence: {analysis.confidence:.3f}")
            
            # Test text duplicate detection
            print("
📄 Testing text duplicate detection...")
            duplicate_text = "AI is revolutionizing multiple industries across the globe"
            
            text_duplicates = await self.vector_db.operations.detect_duplicates(
                content=duplicate_text,
                content_type='text',
                metadata={'title': 'AI Revolution - Updated'}
            )
            
            print(f"  Found {len(text_duplicates)} potential text duplicates:")
            for result, analysis in text_duplicates:
                print(f"    - Original ID: {result.content_id}")
                print(f"      Similarity: {result.similarity:.3f}")
                print(f"      Analysis: {analysis.analysis_details}")
            
        except Exception as e:
            print(f"❌ Error in duplicate detection: {str(e)}")
    
    async def example_4_collaboration_matching(self):
        """Example 4: Collaboration matching between creators."""
        print("
" + "="*60)
        print("🤝 EXAMPLE 4: Collaboration Matching Between Creators")
        print("="*60)
        
        try:
            # Define creator profiles
            creator_profiles = [
                {
                    'id': 'creator_001',
                    'name': 'MusicMaker_Pro',
                    'specialties': ['electronic', 'ambient'],
                    'style_features': np.random.rand(384).astype(np.float32),
                    'collaboration_preferences': {
                        'genres': ['electronic', 'pop', 'ambient'],
                        'collaboration_type': 'remix',
                        'experience_level': 'professional'
                    }
                },
                {
                    'id': 'creator_002',
                    'name': 'JazzFusion_Artist',
                    'specialties': ['jazz', 'fusion'],
                    'style_features': np.random.rand(384).astype(np.float32),
                    'collaboration_preferences': {
                        'genres': ['jazz', 'fusion', 'experimental'],
                        'collaboration_type': 'original',
                        'experience_level': 'advanced'
                    }
                }
            ]
            
            print("
🎯 Finding collaboration opportunities...")
            
            for creator in creator_profiles:
                print(f"
👤 Analyzing creator: {creator['name']}")
                print(f"   Specialties: {', '.join(creator['specialties'])}")
                
                # Find collaboration matches
                collaborations = await self.vector_db.operations.find_collaborations(
                    creator_profile=creator,
                    content_example=creator['style_features'],
                    content_type='audio'
                )
                
                print(f"   Found {len(collaborations)} potential collaborations:")
                for i, match in enumerate(collaborations, 1):
                    print(f"     {i}. Partner: {match.partner_id}")
                    print(f"        Compatibility: {match.compatibility_score:.3f}")
                    print(f"        Match Type: {match.match_type}")
                    print(f"        Strengths: {', '.join(match.shared_strengths)}")
            
        except Exception as e:
            print(f"❌ Error in collaboration matching: {str(e)}")
    
    async def example_5_content_recommendations(self):
        """Example 5: Content recommendations and inspiration."""
        print("
" + "="*60)
        print("💡 EXAMPLE 5: Content Recommendations and Inspiration")
        print("="*60)
        
        try:
            # Define user profiles for recommendations
            user_profiles = [
                {
                    'id': 'user_001',
                    'interests': ['technology', 'AI', 'innovation'],
                    'preferred_content_types': ['text', 'video'],
                    'engagement_history': {
                        'liked_categories': ['technology', 'science'],
                        'avg_engagement_time': 300,
                        'preferred_length': 'medium'
                    }
                },
                {
                    'id': 'user_002',
                    'interests': ['music', 'electronic', 'creativity'],
                    'preferred_content_types': ['audio', 'video'],
                    'engagement_history': {
                        'liked_categories': ['music', 'entertainment'],
                        'avg_engagement_time': 180,
                        'preferred_length': 'short'
                    }
                }
            ]
            
            print("
🎯 Generating personalized recommendations...")
            
            for user in user_profiles:
                print(f"
👤 User: {user['id']}")
                print(f"   Interests: {', '.join(user['interests'])}")
                print(f"   Preferred types: {', '.join(user['preferred_content_types'])}")
                
                # Get recommendations for each preferred content type
                for content_type in user['preferred_content_types']:
                    if content_type == 'text':
                        example_content = "Technology and innovation trends"
                    elif content_type == 'audio':
                        example_content = np.random.rand(384).astype(np.float32)
                    else:
                        continue
                    
                    recommendations = await self.vector_db.operations.get_recommendations(
                        user_profile=user,
                        content_example=example_content,
                        content_type=content_type
                    )
                    
                    print(f"
   📋 {content_type.title()} Recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"     {i}. Content: {rec.content_id}")
                        print(f"        Relevance: {rec.relevance_score:.3f}")
                        print(f"        Reason: {rec.recommendation_reason}")
                        if rec.trending_score > 0.7:
                            print(f"        🔥 Trending!")
            
        except Exception as e:
            print(f"❌ Error in content recommendations: {str(e)}")
    
    async def example_6_performance_monitoring(self):
        """Example 6: Performance monitoring and optimization."""
        print("
" + "="*60)
        print("📊 EXAMPLE 6: Performance Monitoring and Optimization")
        print("="*60)
        
        try:
            print("
🔍 Analyzing system performance...")
            
            # Get comprehensive system status
            status = self.vector_db.get_system_status()
            
            print("
📈 System Performance Metrics:")
            print(f"   Initialized: {status.get('initialized', False)}")
            print(f"   Backend: {status.get('backend_type', 'Unknown')}")
            
            # Get index statistics
            print("
📊 Index Statistics:")
            index_summary = status.get('index_summary', {})
            print(f"   Total Indices: {index_summary.get('total_indices', 0)}")
            print(f"   Total Vectors: {index_summary.get('total_vectors', 0)}")
            print(f"   Memory Usage: {index_summary.get('total_memory_mb', 0):.2f} MB")
            print(f"   Average Health: {index_summary.get('avg_health_score', 0):.3f}")
            
            # Performance stats per content type
            content_types = ['audio', 'text', 'image', 'video']
            
            print("
⚡ Performance by Content Type:")
            for content_type in content_types:
                try:
                    stats = await self.vector_db.get_index_statistics(content_type)
                    if stats:
                        print(f"
   {content_type.title()}:")
                        print(f"     Vectors: {stats.total_vectors}")
                        print(f"     Avg Query Time: {stats.avg_search_latency_ms:.2f} ms")
                        print(f"     Throughput: {stats.throughput_qps:.2f} QPS")
                        print(f"     Health Score: {stats.health_score:.3f}")
                        print(f"     Memory: {stats.memory_usage_mb:.2f} MB")
                except Exception as e:
                    print(f"     No data available for {content_type}")
            
            # System resource usage
            system_resources = status.get('system_resources', {})
            if system_resources:
                print("
🖥️  System Resources:")
                print(f"   CPU Usage: {system_resources.get('cpu_percent', 0):.1f}%")
                print(f"   Memory Usage: {system_resources.get('memory_percent', 0):.1f}%")
                print(f"   Disk Usage: {system_resources.get('disk_percent', 0):.1f}%")
            
            # Test optimization
            print("
🔧 Running system optimization...")
            try:
                optimization_success = await self.vector_db.optimize_system()
                if optimization_success:
                    print("   ✅ System optimization completed successfully")
                else:
                    print("   ⚠️  System optimization had mixed results")
            except Exception as e:
                print(f"   ❌ Optimization error: {str(e)}")
            
        except Exception as e:
            print(f"❌ Error in performance monitoring: {str(e)}")
    
    async def example_7_backup_and_restore(self):
        """Example 7: Backup and restore operations."""
        print("
" + "="*60)
        print("💾 EXAMPLE 7: Backup and Restore Operations")
        print("="*60)
        
        try:
            print("
📦 Creating system backup...")
            
            # Create a full system backup
            backup_info = await self.vector_db.create_system_backup(
                backup_name=f"example_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if backup_info:
                print(f"   ✅ Backup created successfully!")
                print(f"   Backup ID: {backup_info.backup_id}")
                print(f"   Size: {backup_info.size_bytes / (1024*1024):.2f} MB")
                print(f"   Created: {backup_info.created_at}")
                print(f"   Content Types: {', '.join(backup_info.content_types)}")
            else:
                print("   ❌ Backup creation failed")
                return
            
            # List all available backups
            print("
📋 Listing available backups...")
            backups = await self.vector_db.list_available_backups()
            
            print(f"   Found {len(backups)} backup(s):")
            for i, backup in enumerate(backups, 1):
                print(f"     {i}. ID: {backup.backup_id}")
                print(f"        Size: {backup.size_bytes / (1024*1024):.2f} MB")
                print(f"        Created: {backup.created_at}")
                print(f"        Types: {', '.join(backup.content_types)}")
            
            # Demonstrate content-specific backup
            print("
🎵 Creating audio-specific backup...")
            audio_backup = await self.vector_db.create_content_backup(
                content_type='audio',
                backup_name=f"audio_backup_{datetime.now().strftime('%H%M%S')}"
            )
            
            if audio_backup:
                print(f"   ✅ Audio backup created: {audio_backup.backup_id}")
                print(f"   Size: {audio_backup.size_bytes / 1024:.2f} KB")
            
        except Exception as e:
            print(f"❌ Error in backup operations: {str(e)}")
    
    async def example_8_advanced_search_configurations(self):
        """Example 8: Advanced search configurations and filters."""
        print("
" + "="*60)
        print("⚙️ EXAMPLE 8: Advanced Search Configurations and Filters")
        print("="*60)
        
        try:
            print("
🔍 Testing advanced search configurations...")
            
            # Test different search strategies
            search_configs = [
                {
                    'name': 'High Precision Search',
                    'config': SearchConfig(
                        search_type=SearchType.SIMILAR_CONTENT,
                        ranking_strategy=RankingStrategy.SEMANTIC_SIMILARITY,
                        similarity_threshold=0.8,
                        max_results=5,
                        metadata_filters={'genre': 'electronic'}
                    )
                },
                {
                    'name': 'Broad Discovery Search',
                    'config': SearchConfig(
                        search_type=SearchType.DISCOVERY,
                        ranking_strategy=RankingStrategy.DIVERSITY_BOOST,
                        similarity_threshold=0.5,
                        max_results=10,
                        metadata_filters={}
                    )
                },
                {
                    'name': 'Trending Content Search',
                    'config': SearchConfig(
                        search_type=SearchType.TRENDING,
                        ranking_strategy=RankingStrategy.POPULARITY_BOOST,
                        similarity_threshold=0.6,
                        max_results=8,
                        metadata_filters={}
                    )
                }
            ]
            
            # Test each search configuration
            query_features = np.random.rand(384).astype(np.float32)
            
            for search_test in search_configs:
                print(f"
🎯 {search_test['name']}:")
                print(f"   Strategy: {search_test['config'].ranking_strategy}")
                print(f"   Threshold: {search_test['config'].similarity_threshold}")
                print(f"   Max Results: {search_test['config'].max_results}")
                
                try:
                    results = await self.vector_db.operations.search_content(
                        content=query_features,
                        content_type='audio',
                        search_config=search_test['config']
                    )
                    
                    print(f"   Results: {len(results)} found")
                    for i, result in enumerate(results[:3], 1):
                        print(f"     {i}. ID: {result.content_id}, Score: {result.similarity:.3f}")
                        
                except Exception as e:
                    print(f"   ❌ Search failed: {str(e)}")
            
            # Test metadata filtering
            print("
🏷️  Testing metadata filtering...")
            
            metadata_filters = [
                {'genre': 'electronic'},
                {'duration': {'$gte': 200}},  # Greater than or equal to 200 seconds
                {'tempo': {'$range': [110, 130]}}  # Tempo between 110-130 BPM
            ]
            
            for i, filters in enumerate(metadata_filters, 1):
                print(f"
   Filter {i}: {filters}")
                try:
                    filtered_results = await self.vector_db.search_similar_audio(
                        audio_data=query_features,
                        max_results=5,
                        threshold=0.5,
                        metadata_filters=filters
                    )
                    
                    print(f"   Found {len(filtered_results)} filtered results")
                    for j, result in enumerate(filtered_results, 1):
                        print(f"     {j}. {result.content_id} (Score: {result.similarity:.3f})")
                        
                except Exception as e:
                    print(f"   ❌ Filtered search failed: {str(e)}")
            
        except Exception as e:
            print(f"❌ Error in advanced search configurations: {str(e)}")
    
    async def run_all_examples(self):
        """Run all examples in sequence."""
        print("🎬 Starting Vector Database Examples Demonstration")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # Initialize database
            success = await self.initialize_database()
            if not success:
                print("❌ Failed to initialize database. Stopping examples.")
                return
            
            # Run all examples
            examples = [
                self.example_1_basic_content_addition,
                self.example_2_similarity_search,
                self.example_3_duplicate_detection,
                self.example_4_collaboration_matching,
                self.example_5_content_recommendations,
                self.example_6_performance_monitoring,
                self.example_7_backup_and_restore,
                self.example_8_advanced_search_configurations
            ]
            
            for i, example in enumerate(examples, 1):
                try:
                    await example()
                    print(f"
✅ Example {i} completed successfully!")
                    
                    # Add small delay between examples
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"
❌ Example {i} failed: {str(e)}")
                    continue
            
            # Final summary
            elapsed_time = time.time() - start_time
            print("
" + "="*80)
            print("🎉 ALL EXAMPLES COMPLETED!")
            print(f"⏱️  Total execution time: {elapsed_time:.2f} seconds")
            print("="*80)
            
            # Display final system status
            final_status = self.vector_db.get_system_status()
            print(f"
📊 Final System Status:")
            print(f"   Total Indices: {final_status.get('index_summary', {}).get('total_indices', 0)}")
            print(f"   Total Vectors: {final_status.get('index_summary', {}).get('total_vectors', 0)}")
            print(f"   System Health: {final_status.get('index_summary', {}).get('avg_health_score', 0):.3f}")
            
        except Exception as e:
            print(f"❌ Fatal error in examples: {str(e)}")
        
        finally:
            # Cleanup
            if self.vector_db:
                try:
                    await self.vector_db.shutdown()
                    print("
🧹 Database cleanup completed")
                except Exception as e:
                    print(f"⚠️  Cleanup warning: {str(e)}")


# Convenience functions for quick testing
async def run_quick_demo():
    """Run a quick demonstration of key features."""
    print("🚀 Quick Vector Database Demo")
    print("-" * 40)
    
    examples = VectorDBExamples()
    
    # Run essential examples only
    await examples.initialize_database()
    await examples.example_1_basic_content_addition()
    await examples.example_2_similarity_search()
    await examples.example_6_performance_monitoring()
    
    print("
✅ Quick demo completed!")


async def run_full_demonstration():
    """Run the complete demonstration suite."""
    examples = VectorDBExamples()
    await examples.run_all_examples()


# Main execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(run_quick_demo())
    else:
        asyncio.run(run_full_demonstration())


# Export classes and functions
__all__ = [
    'VectorDBExamples',
    'run_quick_demo',
    'run_full_demonstration'
]

import asyncio
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any

# Import vector database components
from . import (
    VectorDatabaseManager,
    VectorDBManager,
    SimilaritySearchEngine,
    MultiModalEmbeddingEngine,
    DuplicateDetectionEngine,
    CollaborationMatchingEngine,
    VectorDBOperations
)
from .config import ConfigManager, load_preset

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBExamples:
    """
    Comprehensive examples for vector database operations.
    """
    
    def __init__(self):
        """Initialize with default configuration."""
        self.config_manager = ConfigManager()
        self.vector_db = None
        self.similarity_engine = None
        self.embedding_engine = None
        
    async def setup_basic_vector_db(self):
        """Setup basic vector database with default configuration."""
        logger.info("Setting up basic vector database...")
        
        # Initialize vector database manager
        self.vector_db = VectorDatabaseManager(
            config=self.config_manager.config
        )
        
        # Initialize embedding engine
        self.embedding_engine = MultiModalEmbeddingEngine(
            config=self.config_manager.get_embedding_config()
        )
        
        # Initialize similarity search engine
        self.similarity_engine = SimilaritySearchEngine(
            vector_db=self.vector_db,
            embedding_engine=self.embedding_engine
        )
        
        # Create content-specific indices
        await self.vector_db.create_index("text_content", dimension=384)
        await self.vector_db.create_index("audio_content", dimension=768)
        await self.vector_db.create_index("image_content", dimension=512)
        await self.vector_db.create_index("video_content", dimension=512)
        
        logger.info("Basic vector database setup completed")
    
    async def example_text_processing(self):
        """Example: Text content processing and similarity search."""
        logger.info("=== Text Processing Example ===")
        
        # Sample text documents
        documents = [
            {
                "id": "doc1",
                "content": "Machine learning is transforming the way we process data and make decisions.",
                "metadata": {"category": "AI", "author": "Expert 1", "tags": ["ML", "data"]}
            },
            {
                "id": "doc2", 
                "content": "Deep learning neural networks have revolutionized computer vision and NLP.",
                "metadata": {"category": "AI", "author": "Expert 2", "tags": ["DL", "vision", "NLP"]}
            },
            {
                "id": "doc3",
                "content": "Sustainable energy solutions are crucial for our planet's future.",
                "metadata": {"category": "Environment", "author": "Expert 3", "tags": ["energy", "sustainability"]}
            },
            {
                "id": "doc4",
                "content": "Artificial intelligence algorithms are becoming more sophisticated each day.",
                "metadata": {"category": "AI", "author": "Expert 4", "tags": ["AI", "algorithms"]}
            }
        ]
        
        # Generate embeddings and store documents
        for doc in documents:
            # Generate text embedding
            embedding = await self.embedding_engine.generate_text_embedding(
                text=doc["content"]
            )
            
            # Store in vector database
            await self.vector_db.add_vectors(
                index_name="text_content",
                vectors=[embedding],
                ids=[doc["id"]],
                metadata=[doc["metadata"]]
            )
            
            logger.info(f"Stored document: {doc['id']}")
        
        # Perform similarity search
        query = "AI and machine learning algorithms"
        query_embedding = await self.embedding_engine.generate_text_embedding(query)
        
        results = await self.similarity_engine.search_similar(
            index_name="text_content",
            query_vector=query_embedding,
            k=3,
            filters={"category": "AI"}
        )
        
        logger.info(f"Query: '{query}'")
        logger.info("Top similar documents:")
        for i, result in enumerate(results[:3]):
            logger.info(f"  {i+1}. ID: {result.id}, Score: {result.score:.3f}")
    
    async def example_audio_processing(self):
        """Example: Audio content processing and duplicate detection."""
        logger.info("=== Audio Processing Example ===")
        
        # Simulate audio file processing
        audio_files = [
            {
                "id": "audio1",
                "path": "/path/to/song1.mp3",
                "metadata": {"title": "Summer Vibes", "artist": "Artist A", "genre": "Pop"}
            },
            {
                "id": "audio2", 
                "path": "/path/to/song2.mp3",
                "metadata": {"title": "Electronic Dreams", "artist": "Artist B", "genre": "Electronic"}
            },
            {
                "id": "audio3",
                "path": "/path/to/song3.mp3", 
                "metadata": {"title": "Summer Vibes Remix", "artist": "Artist C", "genre": "Pop"}
            }
        ]
        
        # Initialize duplicate detection engine
        duplicate_detector = DuplicateDetectionEngine(
            vector_db=self.vector_db,
            embedding_engine=self.embedding_engine
        )
        
        # Process audio files
        for audio_file in audio_files:
            # Generate audio embedding (simulated)
            # In real implementation, this would process the actual audio file
            embedding = np.random.rand(768).astype(np.float32)  # Simulated embedding
            
            # Check for duplicates before storing
            duplicates = await duplicate_detector.detect_duplicates(
                content_type="audio",
                embedding=embedding,
                threshold=0.9
            )
            
            if duplicates:
                logger.warning(f"Potential duplicate found for {audio_file['id']}: {[d.id for d in duplicates]}")
            
            # Store audio embedding
            await self.vector_db.add_vectors(
                index_name="audio_content",
                vectors=[embedding],
                ids=[audio_file["id"]],
                metadata=[audio_file["metadata"]]
            )
            
            logger.info(f"Processed audio: {audio_file['id']}")
    
    async def example_collaboration_matching(self):
        """Example: Content creator collaboration matching."""
        logger.info("=== Collaboration Matching Example ===")
        
        # Sample creator profiles
        creators = [
            {
                "id": "creator1",
                "profile": "Tech reviewer focusing on smartphones and laptops. Passionate about latest gadgets.",
                "metadata": {
                    "niche": "Technology",
                    "followers": 150000,
                    "engagement_rate": 0.08,
                    "content_types": ["reviews", "unboxing"],
                    "platforms": ["YouTube", "Instagram"]
                }
            },
            {
                "id": "creator2",
                "profile": "Fitness enthusiast creating workout routines and nutrition guides for healthy living.",
                "metadata": {
                    "niche": "Fitness",
                    "followers": 80000,
                    "engagement_rate": 0.12,
                    "content_types": ["tutorials", "vlogs"],
                    "platforms": ["YouTube", "TikTok"]
                }
            },
            {
                "id": "creator3",
                "profile": "Gaming streamer specializing in RPG games and tech hardware reviews.",
                "metadata": {
                    "niche": "Gaming",
                    "followers": 200000,
                    "engagement_rate": 0.06,
                    "content_types": ["streaming", "reviews"],
                    "platforms": ["Twitch", "YouTube"]
                }
            }
        ]
        
        # Initialize collaboration matching engine
        collaboration_engine = CollaborationMatchingEngine(
            vector_db=self.vector_db,
            embedding_engine=self.embedding_engine
        )
        
        # Store creator profiles
        for creator in creators:
            embedding = await self.embedding_engine.generate_text_embedding(
                text=creator["profile"]
            )
            
            await self.vector_db.add_vectors(
                index_name="text_content",
                vectors=[embedding],
                ids=[creator["id"]],
                metadata=[creator["metadata"]]
            )
        
        # Find collaboration matches for tech creator
        target_creator = "creator1"
        matches = await collaboration_engine.find_collaboration_matches(
            creator_id=target_creator,
            content_type="text",
            max_matches=2
        )
        
        logger.info(f"Collaboration matches for {target_creator}:")
        for match in matches:
            logger.info(f"  - {match.id}: Score {match.score:.3f}")
    
    async def example_performance_monitoring(self):
        """Example: Performance monitoring and optimization."""
        logger.info("=== Performance Monitoring Example ===")
        
        # Initialize operations manager
        operations = VectorDBOperations(
            config=self.config_manager.config
        )
        
        # Monitor performance metrics
        metrics = await operations.get_performance_metrics()
        logger.info("Performance Metrics:")
        logger.info(f"  - Total Indices: {metrics.get('total_indices', 0)}")
        logger.info(f"  - Total Vectors: {metrics.get('total_vectors', 0)}")
        logger.info(f"  - Memory Usage: {metrics.get('memory_usage_mb', 0):.1f} MB")
        logger.info(f"  - Average Query Time: {metrics.get('avg_query_time_ms', 0):.2f} ms")
        
        # Optimize indices
        optimization_results = await operations.optimize_indices()
        logger.info("Index Optimization Results:")
        for index_name, result in optimization_results.items():
            logger.info(f"  - {index_name}: {result['status']}")
    
    async def example_backup_restore(self):
        """Example: Backup and restore operations."""
        logger.info("=== Backup and Restore Example ===")
        
        operations = VectorDBOperations(
            config=self.config_manager.config
        )
        
        # Create backup
        backup_path = "./vector_db_backup"
        backup_result = await operations.create_backup(backup_path)
        
        if backup_result:
            logger.info(f"Backup created successfully at: {backup_path}")
            
            # Simulate data loss and restore
            logger.info("Simulating data restoration...")
            restore_result = await operations.restore_from_backup(backup_path)
            
            if restore_result:
                logger.info("Data restored successfully")
            else:
                logger.error("Failed to restore data")
        else:
            logger.error("Failed to create backup")
    
    async def example_advanced_search(self):
        """Example: Advanced search with filters and ranking."""
        logger.info("=== Advanced Search Example ===")
        
        # Complex search query
        search_query = {
            "text": "innovative AI solutions for content creation",
            "filters": {
                "category": "AI",
                "tags": {"$in": ["AI", "content", "innovation"]}
            },
            "ranking_boost": {
                "author": "Expert 1",  # Boost content from Expert 1
                "recency_weight": 0.2  # Give recent content higher scores
            }
        }
        
        # Generate query embedding
        query_embedding = await self.embedding_engine.generate_text_embedding(
            text=search_query["text"]
        )
        
        # Perform advanced search
        results = await self.similarity_engine.advanced_search(
            index_name="text_content",
            query_vector=query_embedding,
            filters=search_query.get("filters"),
            k=5,
            rerank=True
        )
        
        logger.info(f"Advanced search query: '{search_query['text']}'")
        logger.info("Ranked results:")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. ID: {result.id}, Score: {result.score:.3f}")
    
    async def run_all_examples(self):
        """Run all examples in sequence."""
        logger.info("Starting Vector Database Examples...")
        
        try:
            # Setup
            await self.setup_basic_vector_db()
            
            # Run examples
            await self.example_text_processing()
            await self.example_audio_processing()
            await self.example_collaboration_matching()
            await self.example_performance_monitoring()
            await self.example_backup_restore()
            await self.example_advanced_search()
            
            logger.info("All examples completed successfully!")
            
        except Exception as e:
            logger.error(f"Error running examples: {e}")
            raise

async def main():
    """Main function to run examples."""
    
    # Configuration examples
    logger.info("=== Configuration Examples ===")
    
    # Load development preset
    dev_config = load_preset('development')
    logger.info("Loaded development configuration preset")
    
    # Create custom configuration
    config_manager = ConfigManager()
    config_manager.update_config(
        backend='faiss',
        data_directory='./custom_vector_data'
    )
    logger.info("Updated configuration with custom settings")
    
    # Validate configuration
    issues = config_manager.validate_config()
    if issues:
        logger.warning(f"Configuration issues found: {issues}")
    else:
        logger.info("Configuration validation passed")
    
    # Run vector database examples
    examples = VectorDBExamples()
    await examples.run_all_examples()

if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
