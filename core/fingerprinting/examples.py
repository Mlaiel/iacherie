"""IA Influencer Agent - Fingerprinting Module Examples
Comprehensive examples and usage patterns for the fingerprinting system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

from .fingerprint_manager import FingerprintManager, ContentType
from .fingerprint_analyzer import FingerprintAnalyzer
from .similarity_engine import SimilarityEngine
from .hash_generator import HashGenerator
from .index import get_fingerprinting_system, validate_fingerprinting_system

logger = logging.getLogger(__name__)


class FingerprintingExamples:
    """    Comprehensive examples for the fingerprinting system
    Demonstrates all major functionality and use cases
    """    
    def __init__(self):
        """Initialize examples with fingerprinting system"""        self.system = get_fingerprinting_system()
        self.manager = self.system['manager']
        self.analyzer = self.system['analyzer']
        self.similarity = self.system['similarity']
        self.hash_generator = self.system['hash_generator']
    
    async def example_1_basic_audio_fingerprinting(self):
        """        Example 1: Basic audio fingerprinting
        Demonstrates how to fingerprint a single audio file
        """        print("\n=== Example 1: Basic Audio Fingerprinting ===")
        
        # Sample audio file path (replace with actual path)
        audio_path = "sample_audio.mp3"
        
        try:
            # Create fingerprint
            result = await self.manager.create_fingerprint(audio_path)
            
            print(f"Content Type: {result.content_type}")
            print(f"File Size: {result.metadata.get('file_size', 'Unknown')}")
            print(f"Duration: {result.metadata.get('duration', 'Unknown')}")
            print(f"Methods Used: {list(result.fingerprints.keys())}")
            print(f"Processing Time: {result.processing_time:.2f}s")
            
            # Generate secure hash
            hash_result = self.hash_generator.generate_hash(
                result.fingerprints['chromaprint'], 
                algorithm='sha256'
            )
            print(f"Secure Hash: {hash_result.hash[:32]}...")
            
        except FileNotFoundError:
            print("Sample audio file not found. Please provide a valid audio file path.")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def example_2_video_fingerprinting_with_analysis(self):
        """        Example 2: Video fingerprinting with detailed analysis
        Shows advanced video processing and quality analysis
        """        print("\n=== Example 2: Video Fingerprinting with Analysis ===")
        
        video_path = "sample_video.mp4"
        
        try:
            # Create fingerprint with detailed analysis
            result = await self.manager.create_fingerprint(video_path)
            
            # Perform quality analysis
            analysis = await self.analyzer.analyze_fingerprint_quality(result)
            
            print(f"Video Information:")
            print(f"  Resolution: {result.metadata.get('resolution', 'Unknown')}")
            print(f"  FPS: {result.metadata.get('fps', 'Unknown')}")
            print(f"  Duration: {result.metadata.get('duration', 'Unknown')}")
            
            print(f"\nFingerprint Quality:")
            print(f"  Overall Score: {analysis.quality_score:.2f}")
            print(f"  Uniqueness: {analysis.uniqueness_score:.2f}")
            print(f"  Reliability: {analysis.reliability_score:.2f}")
            
            if analysis.issues:
                print(f"  Issues Found: {', '.join(analysis.issues)}")
            
            if analysis.recommendations:
                print(f"  Recommendations: {', '.join(analysis.recommendations)}")
                
        except FileNotFoundError:
            print("Sample video file not found. Please provide a valid video file path.")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def example_3_batch_image_processing(self):
        """        Example 3: Batch image processing
        Demonstrates processing multiple images efficiently
        """        print("\n=== Example 3: Batch Image Processing ===")
        
        # Sample image directory (replace with actual path)
        image_dir = "sample_images/"
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        try:
            # Find all image files
            image_files = []
            if os.path.exists(image_dir):
                for ext in image_extensions:
                    image_files.extend(Path(image_dir).glob(f"*{ext}"))
            
            if not image_files:
                print("No image files found. Creating demo with placeholder data...")
                # Demo with placeholder data
                results = []
                for i in range(3):
                    print(f"Processing demo image {i+1}/3...")
                
                return
            
            # Process images in batches
            batch_size = 5
            all_results = []
            
            for i in range(0, len(image_files), batch_size):
                batch = image_files[i:i+batch_size]
                print(f"Processing batch {i//batch_size + 1}: {len(batch)} images")
                
                # Process batch
                batch_results = await self.manager.process_batch([str(f) for f in batch])
                all_results.extend(batch_results)
                
                # Show progress
                for result in batch_results:
                    if result and hasattr(result, 'file_path'):
                        filename = Path(result.file_path).name
                        methods = list(result.fingerprints.keys()) if result.fingerprints else []
                        print(f"  ✓ {filename}: {', '.join(methods)}")
            
            print(f"\nBatch Processing Summary:")
            print(f"  Total Images: {len(image_files)}")
            print(f"  Successfully Processed: {len([r for r in all_results if r])}")
            print(f"  Failed: {len([r for r in all_results if not r])}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def example_4_similarity_search_and_clustering(self):
        """        Example 4: Similarity search and clustering
        Shows how to find similar content and create clusters
        """        print("\n=== Example 4: Similarity Search and Clustering ===")
        
        try:
            # Create sample fingerprints (in real scenario, these would come from actual files)
            sample_fingerprints = []
            
            # Generate some demo fingerprints
            for i in range(10):
                # Create demo fingerprint data
                fingerprint_data = f"demo_fingerprint_{i}"
                vector = self.similarity.convert_to_vector(fingerprint_data)
                
                sample_fingerprints.append({
                    'id': f"content_{i}",
                    'vector': vector,
                    'metadata': {'type': 'demo', 'index': i}
                })
            
            # Build similarity index
            if sample_fingerprints:
                vectors = [fp['vector'] for fp in sample_fingerprints]
                await self.similarity.build_index(vectors)
                print(f"Built similarity index with {len(vectors)} vectors")
            
            # Perform similarity search
            if sample_fingerprints:
                query_vector = sample_fingerprints[0]['vector']
                matches = await self.similarity.search_similar(query_vector, top_k=3)
                
                print(f"\nSimilarity Search Results:")
                for i, match in enumerate(matches):
                    print(f"  {i+1}. Similarity: {match.similarity:.3f}")
            
            # Perform clustering analysis
            fingerprint_results = []  # In real scenario, load actual fingerprint results
            
            if fingerprint_results:
                clusters = await self.analyzer.find_similar_clusters(fingerprint_results)
                
                print(f"\nClustering Analysis:")
                print(f"  Found {len(clusters)} clusters")
                
                for i, cluster in enumerate(clusters):
                    print(f"  Cluster {i+1}: {len(cluster.fingerprints)} items")
                    print(f"    Avg Similarity: {cluster.average_similarity:.3f}")
                    if cluster.representative_item:
                        print(f"    Representative: {cluster.representative_item}")
            else:
                print("\nNo fingerprint data available for clustering demo")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def example_5_security_and_hashing(self):
        """        Example 5: Security features and cryptographic hashing
        Demonstrates secure hash generation and verification
        """        print("\n=== Example 5: Security and Hashing ===")
        
        try:
            # Original data to hash
            original_data = "sensitive_fingerprint_data_12345"
            
            # Generate different types of hashes
            algorithms = ['sha256', 'sha3_256', 'blake2b']
            
            print("Hash Generation:")
            hashes = {}
            for algorithm in algorithms:
                hash_result = self.hash_generator.generate_hash(original_data, algorithm=algorithm)
                hashes[algorithm] = hash_result
                print(f"  {algorithm.upper()}: {hash_result.hash[:32]}...")
            
            # Generate salted hash
            salted_hash = self.hash_generator.generate_salted_hash(original_data)
            print(f"  Salted SHA-256: {salted_hash.hash[:32]}...")
            print(f"  Salt: {salted_hash.salt[:16]}...")
            
            # Generate HMAC
            secret_key = "super_secret_key_for_hmac"
            hmac_result = self.hash_generator.generate_hmac(original_data, secret_key)
            print(f"  HMAC: {hmac_result.hash[:32]}...")
            
            # Verify hashes
            print(f"\nHash Verification:")
            for algorithm, hash_result in hashes.items():
                is_valid = self.hash_generator.verify_hash(original_data, hash_result.hash, algorithm)
                print(f"  {algorithm.upper()}: {'✓ Valid' if is_valid else '✗ Invalid'}")
            
            # Verify salted hash
            is_salted_valid = self.hash_generator.verify_salted_hash(
                original_data, salted_hash.hash, salted_hash.salt
            )
            print(f"  Salted SHA-256: {'✓ Valid' if is_salted_valid else '✗ Invalid'}")
            
            # Verify HMAC
            is_hmac_valid = self.hash_generator.verify_hmac(
                original_data, hmac_result.hash, secret_key
            )
            print(f"  HMAC: {'✓ Valid' if is_hmac_valid else '✗ Invalid'}")
            
            # Generate Merkle tree (demo with multiple items)
            items = [f"item_{i}" for i in range(8)]
            merkle_root = self.hash_generator.generate_merkle_tree(items)
            print(f"\nMerkle Tree Root: {merkle_root[:32]}...")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    async def example_6_comprehensive_workflow(self):
        """        Example 6: Comprehensive workflow
        Complete example showing a full content protection workflow
        """        print("\n=== Example 6: Comprehensive Content Protection Workflow ===")
        
        try:
            # Step 1: System validation
            print("1. Validating system requirements...")
            requirements = validate_fingerprinting_system()
            
            all_valid = all(requirements.values())
            print(f"   System Ready: {'✓ Yes' if all_valid else '✗ No'}")
            
            if not all_valid:
                print("   Issues found:")
                for req, status in requirements.items():
                    if not status:
                        print(f"     - {req}: Not available")
            
            # Step 2: Content discovery and processing
            print("\n2. Content discovery and processing...")
            content_files = [
                "content/audio/song1.mp3",
                "content/video/clip1.mp4", 
                "content/images/photo1.jpg"
            ]
            
            fingerprint_database = {}
            
            for file_path in content_files:
                print(f"   Processing: {Path(file_path).name}")
                
                # In real scenario, check if file exists and process
                # For demo, create simulated result
                content_type = None
                if file_path.endswith(('.mp3', '.wav')):
                    content_type = ContentType.AUDIO
                elif file_path.endswith(('.mp4', '.avi')):
                    content_type = ContentType.VIDEO
                elif file_path.endswith(('.jpg', '.png')):
                    content_type = ContentType.IMAGE
                
                if content_type:
                    # Simulate fingerprint creation
                    fingerprint_id = f"fp_{hash(file_path) % 10000}"
                    fingerprint_database[fingerprint_id] = {
                        'file_path': file_path,
                        'content_type': content_type,
                        'fingerprints': {'demo': f"fingerprint_data_{fingerprint_id}"},
                        'created_at': 'demo_timestamp'
                    }
                    print(f"     ✓ Fingerprint created: {fingerprint_id}")
            
            # Step 3: Security and protection
            print(f"\n3. Applying security measures...")
            protected_fingerprints = {}
            
            for fp_id, fp_data in fingerprint_database.items():
                # Generate secure hash
                hash_result = self.hash_generator.generate_salted_hash(str(fp_data))
                protected_fingerprints[fp_id] = {
                    **fp_data,
                    'secure_hash': hash_result.hash,
                    'salt': hash_result.salt
                }
                print(f"   ✓ Protected: {fp_id}")
            
            # Step 4: Analysis and reporting
            print(f"\n4. Analysis and reporting...")
            print(f"   Total content items: {len(protected_fingerprints)}")
            print(f"   Audio items: {sum(1 for fp in protected_fingerprints.values() if fp['content_type'] == ContentType.AUDIO)}")
            print(f"   Video items: {sum(1 for fp in protected_fingerprints.values() if fp['content_type'] == ContentType.VIDEO)}")
            print(f"   Image items: {sum(1 for fp in protected_fingerprints.values() if fp['content_type'] == ContentType.IMAGE)}")
            
            # Step 5: Export protection report
            print(f"\n5. Generating protection report...")
            report = {
                'timestamp': 'demo_timestamp',
                'total_items': len(protected_fingerprints),
                'protection_level': 'enterprise',
                'hash_algorithm': 'salted_sha256',
                'fingerprint_methods': ['chromaprint', 'perceptual_hash', 'sift_features'],
                'security_features': ['salted_hashing', 'merkle_trees', 'hmac_verification']
            }
            
            print(f"   Report generated:")
            for key, value in report.items():
                print(f"     {key}: {value}")
            
            print(f"\n✓ Comprehensive workflow completed successfully!")
            
        except Exception as e:
            print(f"Error in comprehensive workflow: {str(e)}")
    
    async def run_all_examples(self):
        """Run all examples in sequence"""        print("=" * 60)
        print("IA INFLUENCER AGENT - FINGERPRINTING EXAMPLES")
        print("=" * 60)
        
        examples = [
            self.example_1_basic_audio_fingerprinting,
            self.example_2_video_fingerprinting_with_analysis,
            self.example_3_batch_image_processing,
            self.example_4_similarity_search_and_clustering,
            self.example_5_security_and_hashing,
            self.example_6_comprehensive_workflow
        ]
        
        for i, example in enumerate(examples, 1):
            try:
                await example()
                print(f"\n{'='*60}")
            except Exception as e:
                print(f"\nExample {i} failed: {str(e)}")
                print(f"{'='*60}")
        
        print("\nAll examples completed!")


async def main():
    """Main function to run examples"""    try:
        # Create examples instance
        examples = FingerprintingExamples()
        
        # Run all examples
        await examples.run_all_examples()
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())


# Quick demo functions for easy testing
async def quick_demo_audio():
    """Quick demo for audio fingerprinting"""    examples = FingerprintingExamples()
    await examples.example_1_basic_audio_fingerprinting()

async def quick_demo_security():
    """Quick demo for security features"""    examples = FingerprintingExamples()
    await examples.example_5_security_and_hashing()

async def quick_demo_workflow():
    """Quick demo for complete workflow"""    examples = FingerprintingExamples()
    await examples.example_6_comprehensive_workflow()


# Export for easy access
__all__ = [
    'FingerprintingExamples',
    'main',
    'quick_demo_audio',
    'quick_demo_security', 
    'quick_demo_workflow'
]
