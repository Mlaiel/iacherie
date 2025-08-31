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

"""SEO Optimizer Tests

Comprehensive tests for the SEOOptimizer class that handles
search engine optimization for content.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.seo_optimizer import (
    SEOOptimizer
)
from ai.content_generation.content_models import ContentType, Platform


class TestSEOOptimizer:
    """Test suite for SEOOptimizer"""    
    @pytest.fixture
    def optimizer(self):
        """Create an SEO optimizer instance"""        return SEOOptimizer()
    
    @pytest.fixture
    def sample_content(self):
        """Create sample content for SEO analysis"""        return """        # The Future of Artificial Intelligence in 2025
        
        Artificial intelligence (AI) is rapidly transforming industries across the globe. 
        From machine learning algorithms to natural language processing, AI technology 
        continues to evolve at an unprecedented pace.
        
        ## What is Artificial Intelligence?
        
        Artificial intelligence refers to the simulation of human intelligence in machines 
        that are programmed to think and learn like humans. These AI systems can perform 
        tasks that typically require human intelligence.
        
        ## Key AI Technologies
        
        - Machine Learning (ML)
        - Deep Learning
        - Natural Language Processing (NLP)
        - Computer Vision
        - Robotics
        
        The future of AI looks promising with continued advancements in these technologies.
        """    
    @pytest.fixture
    def target_keywords(self):
        """Create sample target keywords"""        return [
            "artificial intelligence",
            "AI technology",
            "machine learning",
            "deep learning",
            "AI future 2025"
        ]
    
    def test_optimizer_initialization(self, optimizer):
        """Test SEO optimizer initialization"""        assert optimizer is not None
        assert hasattr(optimizer, 'keyword_analyzer')
        assert hasattr(optimizer, 'content_analyzer')
        assert hasattr(optimizer, 'competitor_analyzer')
        assert hasattr(optimizer, 'technical_seo')
        assert hasattr(optimizer, 'optimization_cache')
    
    @pytest.mark.asyncio
    async def test_keyword_analysis(self, optimizer, target_keywords):
        """Test keyword analysis functionality"""        with patch.object(optimizer, '_analyze_keywords') as mock_analysis:
            mock_analysis.return_value = {
                "success": True,
                "keywords": [
                    {
                        "keyword": "artificial intelligence",
                        "search_volume": 165000,
                        "competition": "high",
                        "difficulty": 85,
                        "cpc": 2.45,
                        "trend": "increasing"
                    },
                    {
                        "keyword": "AI technology",
                        "search_volume": 89000,
                        "competition": "medium",
                        "difficulty": 72,
                        "cpc": 1.89,
                        "trend": "stable"
                    }
                ],
                "related_keywords": [
                    "machine learning algorithms",
                    "neural networks",
                    "AI applications"
                ]
            }
            
            result = await optimizer.analyze_keywords(
                keywords=target_keywords,
                language="en",
                location="US"
            )
            
            assert result["success"] is True
            assert len(result["keywords"]) == 2
            assert result["keywords"][0]["search_volume"] == 165000
    
    @pytest.mark.asyncio
    async def test_content_optimization(self, optimizer, sample_content, target_keywords):
        """Test content optimization for SEO"""        with patch.object(optimizer, '_optimize_content') as mock_optimize:
            mock_optimize.return_value = {
                "success": True,
                "optimized_content": sample_content + "\n\n## Conclusion\nAI technology will continue to shape our future.",
                "improvements": {
                    "keyword_density_improved": True,
                    "headings_optimized": True,
                    "meta_tags_added": True,
                    "internal_links_suggested": 3
                },
                "seo_score": {
                    "before": 65,
                    "after": 85,
                    "improvement": 20
                }
            }
            
            result = await optimizer.optimize_content(
                content=sample_content,
                target_keywords=target_keywords,
                content_type=ContentType.BLOG_POST,
                optimization_level="aggressive"
            )
            
            assert result["success"] is True
            assert result["seo_score"]["after"] == 85
            assert result["improvements"]["keyword_density_improved"] is True
    
    @pytest.mark.asyncio
    async def test_seo_score_calculation(self, optimizer, sample_content):
        """Test SEO score calculation"""        with patch.object(optimizer, '_calculate_seo_score') as mock_score:
            mock_score.return_value = {
                "overall_score": 78,
                "components": {
                    "keyword_optimization": 82,
                    "content_structure": 75,
                    "meta_tags": 85,
                    "readability": 88,
                    "technical_seo": 72,
                    "user_experience": 79
                },
                "recommendations": [
                    "Improve keyword density for target keywords",
                    "Add more internal links",
                    "Optimize meta description length"
                ]
            }
            
            result = await optimizer.calculate_seo_score(
                content=sample_content,
                target_keywords=["artificial intelligence", "AI technology"],
                url="https://example.com/ai-future"
            )
            
            assert result["overall_score"] == 78
            assert result["components"]["readability"] == 88
            assert len(result["recommendations"]) == 3
    
    @pytest.mark.asyncio
    async def test_competitor_analysis(self, optimizer):
        """Test competitor analysis functionality"""        competitor_urls = [
            "https://competitor1.com/ai-article",
            "https://competitor2.com/ai-guide",
            "https://competitor3.com/ai-trends"
        ]
        
        with patch.object(optimizer, '_analyze_competitors') as mock_competitors:
            mock_competitors.return_value = {
                "success": True,
                "competitors": [
                    {
                        "url": "https://competitor1.com/ai-article",
                        "seo_score": 88,
                        "keywords": ["artificial intelligence", "AI applications"],
                        "content_length": 2500,
                        "backlinks": 45,
                        "domain_authority": 72
                    },
                    {
                        "url": "https://competitor2.com/ai-guide",
                        "seo_score": 92,
                        "keywords": ["AI technology", "machine learning"],
                        "content_length": 3200,
                        "backlinks": 67,
                        "domain_authority": 85
                    }
                ],
                "opportunities": [
                    "Target long-tail keywords with lower competition",
                    "Create longer, more comprehensive content",
                    "Focus on technical AI terminology"
                ]
            }
            
            result = await optimizer.analyze_competitors(
                competitor_urls=competitor_urls,
                target_keywords=["artificial intelligence", "AI technology"],
                analysis_depth="comprehensive"
            )
            
            assert result["success"] is True
            assert len(result["competitors"]) == 2
            assert result["competitors"][1]["seo_score"] == 92
    
    @pytest.mark.asyncio
    async def test_meta_tag_optimization(self, optimizer, sample_content):
        """Test meta tag optimization"""        with patch.object(optimizer, '_optimize_meta_tags') as mock_meta:
            mock_meta.return_value = {
                "success": True,
                "meta_tags": {
                    "title": "The Future of Artificial Intelligence in 2025 | AI Technology Guide",
                    "description": "Discover how artificial intelligence and AI technology will transform industries in 2025. Learn about machine learning, deep learning, and the future of AI.",
                    "keywords": "artificial intelligence, AI technology, machine learning, deep learning, AI 2025",
                    "og:title": "The Future of AI Technology in 2025",
                    "og:description": "Complete guide to AI trends and technologies shaping our future",
                    "twitter:card": "summary_large_image"
                },
                "character_counts": {
                    "title": 68,
                    "description": 154,
                    "keywords": 78
                },
                "optimization_score": 92
            }
            
            result = await optimizer.optimize_meta_tags(
                content=sample_content,
                target_keywords=["artificial intelligence", "AI technology"],
                brand_name="TechGuide",
                max_title_length=70
            )
            
            assert result["success"] is True
            assert result["character_counts"]["title"] == 68
            assert result["optimization_score"] == 92
    
    @pytest.mark.asyncio
    async def test_internal_linking_suggestions(self, optimizer, sample_content):
        """Test internal linking suggestions"""        existing_pages = [
            {"url": "/machine-learning-guide", "title": "Machine Learning Complete Guide", "keywords": ["machine learning", "ML algorithms"]},
            {"url": "/deep-learning-basics", "title": "Deep Learning Fundamentals", "keywords": ["deep learning", "neural networks"]},
            {"url": "/ai-applications", "title": "AI Applications in Business", "keywords": ["AI applications", "business AI"]}
        ]
        
        with patch.object(optimizer, '_suggest_internal_links') as mock_links:
            mock_links.return_value = {
                "success": True,
                "suggested_links": [
                    {
                        "anchor_text": "machine learning algorithms",
                        "target_url": "/machine-learning-guide",
                        "relevance_score": 0.89,
                        "position": "paragraph 3"
                    },
                    {
                        "anchor_text": "deep learning",
                        "target_url": "/deep-learning-basics",
                        "relevance_score": 0.85,
                        "position": "paragraph 4"
                    }
                ],
                "link_density": 0.012,
                "seo_value": 15.2
            }
            
            result = await optimizer.suggest_internal_links(
                content=sample_content,
                existing_pages=existing_pages,
                max_links=5,
                min_relevance=0.8
            )
            
            assert result["success"] is True
            assert len(result["suggested_links"]) == 2
            assert result["suggested_links"][0]["relevance_score"] == 0.89
    
    @pytest.mark.asyncio
    async def test_readability_optimization(self, optimizer, sample_content):
        """Test content readability optimization"""        with patch.object(optimizer, '_optimize_readability') as mock_readability:
            mock_readability.return_value = {
                "success": True,
                "readability_scores": {
                    "flesch_kincaid": 8.5,
                    "gunning_fog": 9.2,
                    "coleman_liau": 7.8,
                    "automated_readability": 8.1
                },
                "improvements": {
                    "sentences_simplified": 3,
                    "complex_words_replaced": 7,
                    "passive_voice_reduced": 2,
                    "transition_words_added": 4
                },
                "optimized_content": sample_content.replace("unprecedented", "remarkable"),
                "grade_level": "8th grade"
            }
            
            result = await optimizer.optimize_readability(
                content=sample_content,
                target_grade_level=8,
                preserve_technical_terms=True
            )
            
            assert result["success"] is True
            assert result["readability_scores"]["flesch_kincaid"] == 8.5
            assert result["improvements"]["sentences_simplified"] == 3
    
    @pytest.mark.asyncio
    async def test_schema_markup_generation(self, optimizer, sample_content):
        """Test schema markup generation"""        article_info = {
            "title": "The Future of Artificial Intelligence in 2025",
            "author": "Fahed Mlaiel",
            "publish_date": "2025-01-15",
            "category": "Technology",
            "image": "https://example.com/ai-future.jpg"
        }
        
        with patch.object(optimizer, '_generate_schema') as mock_schema:
            mock_schema.return_value = {
                "success": True,
                "schema_types": ["Article", "TechArticle", "BlogPosting"],
                "json_ld": {
                    "@context": "https://schema.org",
                    "@type": "TechArticle",
                    "headline": "The Future of Artificial Intelligence in 2025",
                    "author": {"@type": "Person", "name": "Fahed Mlaiel"},
                    "datePublished": "2025-01-15",
                    "articleSection": "Technology"
                },
                "validation_score": 98
            }
            
            result = await optimizer.generate_schema_markup(
                content=sample_content,
                article_info=article_info,
                schema_types=["Article", "TechArticle"]
            )
            
            assert result["success"] is True
            assert result["validation_score"] == 98
            assert result["json_ld"]["@type"] == "TechArticle"
    
    @pytest.mark.asyncio
    async def test_featured_snippet_optimization(self, optimizer, sample_content):
        """Test featured snippet optimization"""        target_questions = [
            "What is artificial intelligence?",
            "How does AI work?",
            "What are the benefits of AI?"
        ]
        
        with patch.object(optimizer, '_optimize_for_snippets') as mock_snippets:
            mock_snippets.return_value = {
                "success": True,
                "snippet_opportunities": [
                    {
                        "question": "What is artificial intelligence?",
                        "answer_format": "definition",
                        "optimized_answer": "Artificial intelligence refers to the simulation of human intelligence in machines that are programmed to think and learn like humans.",
                        "snippet_probability": 0.78
                    }
                ],
                "structured_content": {
                    "definitions": 1,
                    "lists": 1,
                    "tables": 0,
                    "step_by_step": 0
                }
            }
            
            result = await optimizer.optimize_for_featured_snippets(
                content=sample_content,
                target_questions=target_questions,
                include_faq=True
            )
            
            assert result["success"] is True
            assert len(result["snippet_opportunities"]) == 1
            assert result["snippet_opportunities"][0]["snippet_probability"] == 0.78
    
    @pytest.mark.asyncio
    async def test_local_seo_optimization(self, optimizer):
        """Test local SEO optimization"""        business_info = {
            "name": "AI Tech Solutions",
            "address": "123 Tech Street, San Francisco, CA 94102",
            "phone": "+1-555-0123",
            "business_type": "Technology Consulting",
            "services": ["AI Consulting", "Machine Learning", "Data Science"]
        }
        
        with patch.object(optimizer, '_optimize_local_seo') as mock_local:
            mock_local.return_value = {
                "success": True,
                "local_keywords": [
                    "AI consulting San Francisco",
                    "machine learning experts California",
                    "data science consulting Bay Area"
                ],
                "citation_opportunities": [
                    "Google My Business",
                    "Yelp for Business",
                    "Yellow Pages"
                ],
                "nap_consistency": 95,
                "local_schema": {
                    "@type": "LocalBusiness",
                    "name": "AI Tech Solutions",
                    "address": {"@type": "PostalAddress"}
                }
            }
            
            result = await optimizer.optimize_local_seo(
                business_info=business_info,
                target_location="San Francisco",
                service_area=["San Francisco", "Oakland", "San Jose"]
            )
            
            assert result["success"] is True
            assert result["nap_consistency"] == 95
            assert len(result["local_keywords"]) == 3
    
    @pytest.mark.asyncio
    async def test_technical_seo_audit(self, optimizer):
        """Test technical SEO audit"""        url = "https://example.com/ai-article"
        
        with patch.object(optimizer, '_audit_technical_seo') as mock_audit:
            mock_audit.return_value = {
                "success": True,
                "audit_results": {
                    "page_speed": {
                        "mobile": 85,
                        "desktop": 92,
                        "core_web_vitals": "good"
                    },
                    "crawlability": {
                        "robots_txt": "valid",
                        "sitemap": "present",
                        "internal_links": 15
                    },
                    "mobile_friendliness": {
                        "responsive": True,
                        "mobile_score": 95
                    },
                    "security": {
                        "https": True,
                        "ssl_valid": True
                    }
                },
                "issues": [
                    "Meta description too long",
                    "Missing alt tags on 2 images"
                ],
                "recommendations": [
                    "Optimize image compression",
                    "Add structured data markup"
                ]
            }
            
            result = await optimizer.audit_technical_seo(
                url=url,
                include_performance=True,
                check_mobile=True
            )
            
            assert result["success"] is True
            assert result["audit_results"]["page_speed"]["mobile"] == 85
            assert len(result["issues"]) == 2
    
    @pytest.mark.asyncio
    async def test_content_gap_analysis(self, optimizer, target_keywords):
        """Test content gap analysis"""        competitor_urls = [
            "https://competitor1.com",
            "https://competitor2.com"
        ]
        
        with patch.object(optimizer, '_analyze_content_gaps') as mock_gaps:
            mock_gaps.return_value = {
                "success": True,
                "content_gaps": [
                    {
                        "topic": "AI ethics and responsibility",
                        "opportunity_score": 85,
                        "competition_level": "medium",
                        "suggested_keywords": ["AI ethics", "responsible AI", "AI governance"]
                    },
                    {
                        "topic": "AI implementation challenges",
                        "opportunity_score": 78,
                        "competition_level": "low",
                        "suggested_keywords": ["AI challenges", "AI implementation", "AI adoption"]
                    }
                ],
                "content_suggestions": [
                    "Create comprehensive guide on AI ethics",
                    "Develop case studies on AI implementation"
                ]
            }
            
            result = await optimizer.analyze_content_gaps(
                target_keywords=target_keywords,
                competitor_urls=competitor_urls,
                industry="technology"
            )
            
            assert result["success"] is True
            assert len(result["content_gaps"]) == 2
            assert result["content_gaps"][0]["opportunity_score"] == 85
    
    @pytest.mark.asyncio
    async def test_multilingual_seo(self, optimizer, sample_content):
        """Test multilingual SEO optimization"""        target_languages = ["es", "fr", "de"]
        
        with patch.object(optimizer, '_optimize_multilingual') as mock_multilingual:
            mock_multilingual.return_value = {
                "success": True,
                "language_optimizations": {
                    "es": {
                        "keywords": ["inteligencia artificial", "tecnología IA"],
                        "meta_title": "El Futuro de la Inteligencia Artificial en 2025",
                        "hreflang": "es-ES"
                    },
                    "fr": {
                        "keywords": ["intelligence artificielle", "technologie IA"],
                        "meta_title": "L'Avenir de l'Intelligence Artificielle en 2025",
                        "hreflang": "fr-FR"
                    }
                },
                "hreflang_tags": [
                    '<link rel="alternate" hreflang="es-ES" href="https://example.com/es/ai-future">',
                    '<link rel="alternate" hreflang="fr-FR" href="https://example.com/fr/ai-future">'
                ]
            }
            
            result = await optimizer.optimize_multilingual_seo(
                content=sample_content,
                target_languages=target_languages,
                base_url="https://example.com"
            )
            
            assert result["success"] is True
            assert len(result["language_optimizations"]) == 2
            assert "es" in result["language_optimizations"]
    
    @pytest.mark.asyncio
    async def test_seo_monitoring_and_tracking(self, optimizer):
        """Test SEO monitoring and tracking"""        tracking_keywords = ["artificial intelligence", "AI technology", "machine learning"]
        
        with patch.object(optimizer, '_track_seo_performance') as mock_tracking:
            mock_tracking.return_value = {
                "success": True,
                "tracking_data": {
                    "keywords": [
                        {
                            "keyword": "artificial intelligence",
                            "current_position": 8,
                            "previous_position": 12,
                            "change": 4,
                            "search_volume": 165000,
                            "click_through_rate": 0.15
                        }
                    ],
                    "organic_traffic": {
                        "current_month": 15420,
                        "previous_month": 12350,
                        "growth_rate": 0.25
                    },
                    "backlinks": {
                        "total": 156,
                        "new_this_month": 8,
                        "domain_authority": 72
                    }
                }
            }
            
            result = await optimizer.track_seo_performance(
                keywords=tracking_keywords,
                url="https://example.com",
                time_period="30_days"
            )
            
            assert result["success"] is True
            assert result["tracking_data"]["organic_traffic"]["growth_rate"] == 0.25
            assert result["tracking_data"]["keywords"][0]["change"] == 4


class TestKeywordAnalysis:
    """Test suite for KeywordAnalysis model"""    
    def test_keyword_analysis_creation(self):
        """Test keyword analysis creation"""        analysis = KeywordAnalysis(
            keyword="artificial intelligence",
            search_volume=165000,
            competition="high",
            difficulty=85,
            cpc=2.45,
            trend="increasing"
        )
        
        assert analysis.keyword == "artificial intelligence"
        assert analysis.search_volume == 165000
        assert analysis.competition == "high"
        assert analysis.difficulty == 85
        assert analysis.cpc == 2.45
        assert analysis.trend == "increasing"


class TestSEOScore:
    """Test suite for SEOScore model"""    
    def test_seo_score_creation(self):
        """Test SEO score creation"""        score = SEOScore(
            overall_score=78,
            keyword_optimization=82,
            content_structure=75,
            meta_tags=85,
            readability=88,
            technical_seo=72,
            user_experience=79
        )
        
        assert score.overall_score == 78
        assert score.keyword_optimization == 82
        assert score.readability == 88
    
    def test_seo_score_validation(self):
        """Test SEO score validation"""        # Test scores outside valid range
        with pytest.raises(Exception):  # Adjust based on actual validation
            SEOScore(
                overall_score=150,  # Too high
                keyword_optimization=50
            )


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
