# SEO Automation Engine - Usage Examples

This document provides examples of how to use the SEO Automation Engine components.

## Quick Start Example

```python
from seo.optimization import (
    ContentSEOOptimizer, 
    KeywordGeneratorAI, 
    PlatformSEOAdapter,
    Platform,
    OptimizationLevel
)

# Initialize components
content_optimizer = ContentSEOOptimizer(OptimizationLevel.ADVANCED)
keyword_generator = KeywordGeneratorAI(language="en", region="US")
platform_adapter = PlatformSEOAdapter()

# Sample content
content = """
Digital marketing has evolved significantly in 2025. Businesses need to understand 
the importance of content marketing, social media engagement, and search engine 
optimization to succeed in today's competitive online landscape.
"""

# 1. Generate keywords
keywords_result = keyword_generator.generate_keywords(
    seed_keywords=["digital marketing", "content marketing"],
    content=content,
    industry="marketing",
    max_keywords=50
)

print(f"Generated {keywords_result.total_keywords} keywords")
primary_keywords = [kw.keyword for kw in keywords_result.primary_keywords]

# 2. Optimize content
optimization_result = content_optimizer.optimize_content(
    content=content,
    target_keywords=primary_keywords,
    platform_type="blog",
    language="en"
)

print(f"Content optimization score: {optimization_result.analysis.optimization_score}")

# 3. Adapt for platform
platform_result = platform_adapter.optimize_for_platform(
    content=optimization_result.optimized_content,
    platform=Platform.INSTAGRAM,
    keywords=primary_keywords,
    title="Digital Marketing Guide 2025"
)

print(f"Instagram optimization complete - SEO score: {platform_result.seo_score}")
print(f"Generated hashtags: {platform_result.hashtags[:5]}")
```

## Advanced Usage Examples

### Complete SEO Optimization Pipeline

```python
from seo.optimization import *

def complete_seo_optimization(content, title, url, target_keywords):
    """Complete SEO optimization pipeline"""
    
    # 1. Content optimization
    content_optimizer = ContentSEOOptimizer(OptimizationLevel.ADVANCED)
    content_result = content_optimizer.optimize_content(
        content=content,
        target_keywords=target_keywords,
        platform_type="blog"
    )
    
    # 2. Meta data optimization
    meta_optimizer = MetaOptimizer()
    meta_result = meta_optimizer.optimize_meta_data(
        content=content_result.optimized_content,
        keywords=target_keywords,
        title=title,
        url=url,
        content_type=ContentType.ARTICLE
    )
    
    # 3. Multi-platform adaptation
    platform_adapter = PlatformSEOAdapter()
    platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN]
    
    platform_results = platform_adapter.optimize_for_multiple_platforms(
        content=content_result.optimized_content,
        platforms=platforms,
        keywords=target_keywords,
        title=meta_result.optimized_title
    )
    
    return {
        'content': content_result,
        'meta': meta_result,
        'platforms': platform_results
    }

# Usage
results = complete_seo_optimization(
    content="Your content here...",
    title="Your title",
    url="https://example.com/page",
    target_keywords=["keyword1", "keyword2"]
)
```

### International SEO Setup

```python
from seo.optimization import MultilingualSEO, Language, Region, LocalizationLevel

def setup_international_seo(content, target_markets):
    """Setup international SEO for multiple markets"""
    
    multilingual_seo = MultilingualSEO()
    
    result = multilingual_seo.optimize_for_international_markets(
        content=content,
        title="Your International Title",
        description="Your description",
        keywords=["global", "business"],
        source_language=Language.ENGLISH,
        target_markets=target_markets,
        base_url="https://example.com",
        localization_level=LocalizationLevel.ADVANCED
    )
    
    # Generate hreflang HTML
    hreflang_html = multilingual_seo.generate_hreflang_html(result.hreflang_tags)
    
    return result, hreflang_html

# Usage
target_markets = [
    (Language.FRENCH, Region.FRANCE),
    (Language.GERMAN, Region.GERMANY),
    (Language.SPANISH, Region.SPAIN)
]

international_result, hreflang_tags = setup_international_seo(
    content="Your content...",
    target_markets=target_markets
)
```

### Competitive Analysis

```python
from seo.optimization import CompetitorIntelligence, AnalysisType

def analyze_competition(domain, competitors, keywords):
    """Perform comprehensive competitive analysis"""
    
    competitor_intel = CompetitorIntelligence(industry="marketing")
    
    result = competitor_intel.analyze_competitive_landscape(
        user_domain=domain,
        competitors=competitors,
        user_keywords=keywords,
        analysis_types=[
            AnalysisType.KEYWORD_GAP,
            AnalysisType.CONTENT_GAP,
            AnalysisType.CONTENT_STRATEGY
        ]
    )
    
    # Export results
    json_report = competitor_intel.export_competitive_analysis(result, format="json")
    
    return result, json_report

# Usage
competition_result, report = analyze_competition(
    domain="yoursite.com",
    competitors=["competitor1.com", "competitor2.com"],
    keywords=["your", "target", "keywords"]
)

print(f"Analysis score: {competition_result.analysis_score}")
print(f"Keyword gaps found: {len(competition_result.keyword_gaps)}")
```

### Performance Monitoring

```python
from seo.optimization import SEOPerformanceTracker, TimeRange

def monitor_seo_performance(domain, keywords):
    """Monitor SEO performance with alerts"""
    
    tracker = SEOPerformanceTracker(
        domain=domain,
        tracking_keywords=keywords
    )
    
    # Generate comprehensive report
    report = tracker.generate_performance_report(
        time_range=TimeRange.MONTH,
        include_competitive=True
    )
    
    # Check for critical alerts
    critical_alerts = [alert for alert in report.alerts if alert.level.value == "critical"]
    
    if critical_alerts:
        print(f"⚠️ {len(critical_alerts)} critical issues found!")
        for alert in critical_alerts:
            print(f"- {alert.message}")
    
    return report

# Usage
performance_report = monitor_seo_performance(
    domain="yoursite.com",
    keywords=["your", "tracking", "keywords"]
)

print(f"Overall SEO score: {performance_report.overall_score}/100")
```

## Integration with Existing Platform

The SEO Automation Engine integrates seamlessly with the existing Ainflue platform:

```python
# In your content creation workflow
from seo.optimization import ContentSEOOptimizer, PlatformSEOAdapter, HashtagIntelligence

def create_optimized_content(content_data):
    """Integrate SEO optimization into content creation"""
    
    # Extract content details
    content = content_data['content']
    platform = content_data['target_platform']
    keywords = content_data['keywords']
    
    # Apply SEO optimization
    content_optimizer = ContentSEOOptimizer()
    optimized = content_optimizer.optimize_content(
        content=content,
        target_keywords=keywords,
        platform_type=platform
    )
    
    # Generate hashtags
    hashtag_intel = HashtagIntelligence()
    hashtag_strategy = hashtag_intel.generate_hashtag_strategy(
        content=optimized.optimized_content,
        keywords=keywords,
        target_platforms=[Platform(platform)]
    )
    
    return {
        'optimized_content': optimized.optimized_content,
        'seo_score': optimized.analysis.optimization_score,
        'hashtags': [h.hashtag for h in hashtag_strategy.primary_hashtags],
        'recommendations': optimized.analysis.seo_recommendations
    }
```

## Export and Reporting

All components support comprehensive reporting:

```python
# Export keyword research
keyword_result = keyword_generator.generate_keywords(...)
json_export = keyword_generator.export_keywords(keyword_result, format="json")
csv_export = keyword_generator.export_keywords(keyword_result, format="csv")

# Export performance reports
performance_report = tracker.generate_performance_report(...)
html_report = tracker.export_performance_report(performance_report, format="html")

# Export competitive analysis
competitive_result = competitor_intel.analyze_competitive_landscape(...)
analysis_report = competitor_intel.export_competitive_analysis(competitive_result, format="json")
```

## Best Practices

1. **Start with keyword research** using KeywordGeneratorAI
2. **Optimize content** with ContentSEOOptimizer before publication
3. **Adapt for specific platforms** using PlatformSEOAdapter
4. **Monitor performance** regularly with SEOPerformanceTracker
5. **Analyze competition** monthly with CompetitorIntelligence
6. **Track trends** weekly with TrendingAnalyzer
7. **Optimize internationally** for global reach with MultilingualSEO

The SEO Automation Engine provides enterprise-grade SEO capabilities specifically designed for the Ainflue platform's content creation and optimization workflows.