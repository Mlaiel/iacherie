"""IA Influencer Agent - Filters Demo & Validation
===============================================

Professional demonstration and validation of the content filtering system.
Showcases enterprise-grade capabilities and integration examples.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.
"""
import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

# Import our filtering system
from .index import (
    get_filter_engine,
    get_available_filter_types,
    create_filter,
    ContentItem,
    FilterType,
    FilterResult
)


class FilterSystemDemo:
    """Demonstration and validation of the filtering system."""    
    def __init__(self):
        """Initialize demo system."""        self.logger = logging.getLogger(__name__)
        self.engine = get_filter_engine()
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all filter capabilities."""        self.logger.info("🚀 Starting IA Influencer Agent Filters Demo")
        self.logger.info("=" * 60)
        
        # Show available filters
        await self._show_available_filters()
        
        # Demo different content types
        await self._demo_text_filtering()
        await self._demo_security_filtering()
        await self._demo_performance_monitoring()
        await self._demo_quality_assessment()
        await self._demo_duplicate_detection()
        
        # Show system statistics
        await self._show_system_stats()
        
        self.logger.info("✅ Demo completed successfully!")
    
    async def _show_available_filters(self):
        """Display all available filter types."""        self.logger.info("\n📋 Available Filter Types:")
        filter_types = get_available_filter_types()
        
        for filter_type in filter_types:
            self.logger.info(f"  • {filter_type.value.upper()}: {filter_type.name}")
    
    async def _demo_text_filtering(self):
        """Demonstrate text content filtering."""        self.logger.info("\n📝 TEXT FILTERING DEMO")
        self.logger.info("-" * 30)
        
        # Create sample text content
        sample_texts = [
            "This is a high-quality professional article about AI technology and innovation.",
            "spam spam buy now click here amazing offer!!!",
            "This text contains inappropriate content and toxic language.",
            "Une analyse professionnelle en français sur l'intelligence artificielle."
        ]
        
        for i, text in enumerate(sample_texts, 1):
            content = ContentItem(
                content_id=f"text_{i}",
                content_type="text",
                content_data=text,
                metadata={"source": "demo"}
            )
            
            result = await self.engine.filter_content(
                content, 
                filter_types=[FilterType.TEXT, FilterType.QUALITY],
                ai_validation=True
            )
            
            self.logger.info(f"Text {i}: {result.overall_result.name} (Score: {result.overall_score:.2f})")
    
    async def _demo_security_filtering(self):
        """Demonstrate security filtering capabilities."""        self.logger.info("\n🔒 SECURITY FILTERING DEMO")
        self.logger.info("-" * 30)
        
        # Create sample content for security testing
        suspicious_contents = [
            "http://phishing-site.com/login?steal=password",
            "Normal safe content without threats",
            "javascript:alert('xss attack')",
            "Professional business content for analysis"
        ]
        
        for i, content_data in enumerate(suspicious_contents, 1):
            content = ContentItem(
                content_id=f"security_{i}",
                content_type="text",
                content_data=content_data,
                metadata={"source": "security_test"}
            )
            
            result = await self.engine.filter_content(
                content,
                filter_types=[FilterType.SECURITY],
                strict_mode=True
            )
            
            security_result = result.filter_results.get(FilterType.SECURITY)
            if security_result:
                self.logger.info(f"Security Test {i}: {security_result.result.name} "
                               f"(Confidence: {security_result.confidence:.2f})")
    
    async def _demo_performance_monitoring(self):
        """Demonstrate performance monitoring."""        self.logger.info("\n⚡ PERFORMANCE MONITORING DEMO")
        self.logger.info("-" * 35)
        
        start_time = time.time()
        
        # Process multiple items to show performance
        tasks = []
        for i in range(10):
            content = ContentItem(
                content_id=f"perf_{i}",
                content_type="text",
                content_data=f"Performance test content item {i}",
                metadata={"batch": "performance_test"}
            )
            
            task = self.engine.filter_content(
                content,
                filter_types=[FilterType.PERFORMANCE, FilterType.QUALITY]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        passed_count = sum(1 for r in results if r.overall_result == FilterResult.PASSED)
        
        self.logger.info(f"Processed 10 items in {total_time:.2f}s")
        self.logger.info(f"Success rate: {passed_count}/10 ({passed_count*10}%)")
        self.logger.info(f"Average time per item: {total_time/10:.3f}s")
    
    async def _demo_quality_assessment(self):
        """Demonstrate quality assessment capabilities."""        self.logger.info("\n⭐ QUALITY ASSESSMENT DEMO")
        self.logger.info("-" * 30)
        
        quality_samples = [
            ("High quality professional content with detailed analysis", "high"),
            ("ok", "low"),
            ("Medium quality content with some good points but could be better", "medium"),
            ("Excellent comprehensive analysis with detailed insights and professional presentation", "excellent")
        ]
        
        for content_text, expected_quality in quality_samples:
            content = ContentItem(
                content_id=f"quality_{expected_quality}",
                content_type="text",
                content_data=content_text,
                metadata={"expected_quality": expected_quality}
            )
            
            result = await self.engine.filter_content(
                content,
                filter_types=[FilterType.QUALITY, FilterType.TEXT]
            )
            
            self.logger.info(f"Quality ({expected_quality}): Score {result.overall_score:.2f}")
    
    async def _demo_duplicate_detection(self):
        """Demonstrate duplicate content detection."""        self.logger.info("\n🔍 DUPLICATE DETECTION DEMO")
        self.logger.info("-" * 30)
        
        # Test with identical content
        original_content = "This is the original content for duplicate testing."
        
        for i in range(3):
            content = ContentItem(
                content_id=f"duplicate_test_{i}",
                content_type="text",
                content_data=original_content,  # Same content
                metadata={"test": "duplicate"}
            )
            
            result = await self.engine.filter_content(
                content,
                filter_types=[FilterType.DUPLICATE]
            )
            
            duplicate_result = result.filter_results.get(FilterType.DUPLICATE)
            if duplicate_result:
                is_duplicate = duplicate_result.metadata.get('is_duplicate', False)
                self.logger.info(f"Content {i+1}: {'DUPLICATE' if is_duplicate else 'UNIQUE'}")
    
    async def _show_system_stats(self):
        """Display system statistics."""        self.logger.info("\n📊 SYSTEM STATISTICS")
        self.logger.info("-" * 25)
        
        stats = self.engine.get_statistics()
        
        self.logger.info(f"Total processed: {stats['total_processed']}")
        self.logger.info(f"Total passed: {stats['total_passed']}")
        self.logger.info(f"Total failed: {stats['total_failed']}")
        self.logger.info(f"Average processing time: {stats['average_processing_time']:.3f}s")
        
        self.logger.info("\nFilter usage:")
        for filter_type, count in stats['filter_usage'].items():
            self.logger.info(f"  {filter_type}: {count} times")


async def run_demo():
    """Run the complete filtering system demonstration."""    demo = FilterSystemDemo()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    # Run demo if executed directly
    asyncio.run(run_demo())
