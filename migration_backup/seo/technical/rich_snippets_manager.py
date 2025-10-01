"""Rich Snippets Manager
Advanced rich snippets and SERP feature optimization for IA Chéries creator economy platform.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Technical SEO Expert: Advanced Technical Optimization
SERP Features Specialist: Rich Snippets & Featured Snippets
Schema.org Expert: Structured Data Implementation
ML Engineer: SERP Intelligence & Optimization
"""

import asyncio
import json
import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import hashlib
import base64


class SERPFeatureType(Enum):
    """Types of SERP features to optimize for."""
    FEATURED_SNIPPET = "featured_snippet"
    KNOWLEDGE_PANEL = "knowledge_panel"
    VIDEO_SNIPPET = "video_snippet"
    AUDIO_SNIPPET = "audio_snippet"
    IMAGE_PACK = "image_pack"
    CAROUSEL = "carousel"
    FAQ_SNIPPET = "faq_snippet"
    HOW_TO_SNIPPET = "how_to_snippet"
    RECIPE_SNIPPET = "recipe_snippet"
    REVIEW_SNIPPET = "review_snippet"
    EVENT_SNIPPET = "event_snippet"
    PRODUCT_SNIPPET = "product_snippet"
    PERSON_SNIPPET = "person_snippet"
    ORGANIZATION_SNIPPET = "organization_snippet"


class SchemaType(Enum):
    """Schema.org types for rich snippets."""
    PERSON = "Person"
    ORGANIZATION = "Organization"
    CREATIVE_WORK = "CreativeWork"
    VIDEO_OBJECT = "VideoObject"
    AUDIO_OBJECT = "AudioObject"
    IMAGE_OBJECT = "ImageObject"
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    REVIEW = "Review"
    RATING = "Rating"
    EVENT = "Event"
    FAQ_PAGE = "FAQPage"
    HOW_TO = "HowTo"
    RECIPE = "Recipe"
    PRODUCT = "Product"
    OFFER = "Offer"
    BREADCRUMB_LIST = "BreadcrumbList"
    WEBSITE = "Website"
    WEB_PAGE = "WebPage"


@dataclass
class RichSnippetOpportunity:
    """Rich snippet optimization opportunity."""
    feature_type: SERPFeatureType
    schema_type: SchemaType
    target_url: str
    title: str
    description: str
    priority: str  # high, medium, low
    difficulty: str  # easy, medium, hard
    estimated_traffic_lift: float  # percentage
    required_content_changes: List[str] = field(default_factory=list)
    required_schema_markup: Dict[str, Any] = field(default_factory=dict)
    competing_snippets: List[str] = field(default_factory=list)
    optimization_steps: List[str] = field(default_factory=list)


@dataclass
class SERPAnalysisResult:
    """SERP analysis results."""
    query: str
    serp_features: List[SERPFeatureType]
    featured_snippet_content: Optional[str] = None
    featured_snippet_url: Optional[str] = None
    knowledge_panel_present: bool = False
    video_carousel_present: bool = False
    image_pack_present: bool = False
    related_questions: List[str] = field(default_factory=list)
    competitor_snippets: List[Dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: List[RichSnippetOpportunity] = field(default_factory=list)


@dataclass
class RichSnippetPerformance:
    """Rich snippet performance metrics."""
    url: str
    feature_type: SERPFeatureType
    query: str
    position: Optional[int] = None
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    stability_score: float = 0.0  # How consistently it appears
    traffic_contribution: float = 0.0


class FeaturedSnippetOptimizer:
    """Optimize content for featured snippets."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.featured_snippet_patterns = {
            'definition': {
                'pattern': r'^(.+?) (?:is|are|means?) (.+?)\.?$',
                'format': 'paragraph',
                'length_range': (40, 150)
            },
            'list': {
                'pattern': r'(?:steps?|ways?|methods?|types?|kinds?)',
                'format': 'list',
                'length_range': (30, 80)
            },
            'table': {
                'pattern': r'(?:comparison|vs|versus|differences?)',
                'format': 'table',
                'length_range': (20, 60)
            },
            'how_to': {
                'pattern': r'^how to (.+?)$',
                'format': 'ordered_list',
                'length_range': (25, 100)
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.FeaturedSnippetOptimizer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def optimize_for_featured_snippet(self, content: str, target_query: str) -> Dict[str, Any]:
        """Optimize content for featured snippet capture."""
        self.logger.info(f"Optimizing content for featured snippet: '{target_query}'")
        
        optimization = {
            'target_query': target_query,
            'current_content': content,
            'optimized_content': '',
            'snippet_type': 'paragraph',
            'optimization_score': 0,
            'recommendations': [],
            'schema_markup': {},
            'content_structure': {}
        }
        
        # Analyze query intent
        query_analysis = await self._analyze_query_intent(target_query)
        optimization['query_intent'] = query_analysis
        
        # Determine optimal snippet format
        optimal_format = await self._determine_optimal_format(target_query, content)
        optimization['snippet_type'] = optimal_format
        
        # Generate optimized content
        optimized_content = await self._generate_optimized_content(content, target_query, optimal_format)
        optimization['optimized_content'] = optimized_content
        
        # Generate schema markup
        schema_markup = await self._generate_snippet_schema(target_query, optimized_content, optimal_format)
        optimization['schema_markup'] = schema_markup
        
        # Content structure recommendations
        structure_recommendations = await self._generate_structure_recommendations(target_query, optimal_format)
        optimization['content_structure'] = structure_recommendations
        
        # Calculate optimization score
        optimization_score = await self._calculate_snippet_optimization_score(optimization)
        optimization['optimization_score'] = optimization_score
        
        # Generate recommendations
        recommendations = await self._generate_snippet_recommendations(optimization)
        optimization['recommendations'] = recommendations
        
        return optimization
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query intent for snippet optimization."""
        query_lower = query.lower()
        
        intent_analysis = {
            'intent_type': 'informational',
            'answer_format': 'paragraph',
            'question_type': 'what',
            'keywords': [],
            'entities': []
        }
        
        # Identify question type
        if query_lower.startswith('what'):
            intent_analysis['question_type'] = 'what'
            intent_analysis['answer_format'] = 'definition'
        elif query_lower.startswith('how'):
            intent_analysis['question_type'] = 'how'
            intent_analysis['answer_format'] = 'step_by_step'
        elif query_lower.startswith('why'):
            intent_analysis['question_type'] = 'why'
            intent_analysis['answer_format'] = 'explanation'
        elif query_lower.startswith('when'):
            intent_analysis['question_type'] = 'when'
            intent_analysis['answer_format'] = 'temporal'
        elif query_lower.startswith('where'):
            intent_analysis['question_type'] = 'where'
            intent_analysis['answer_format'] = 'location'
        elif query_lower.startswith('who'):
            intent_analysis['question_type'] = 'who'
            intent_analysis['answer_format'] = 'person_info'
        
        # Extract keywords
        stop_words = {'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in query_lower.split() if word not in stop_words and len(word) > 2]
        intent_analysis['keywords'] = keywords
        
        return intent_analysis
    
    async def _determine_optimal_format(self, query: str, content: str) -> str:
        """Determine optimal format for featured snippet."""
        query_lower = query.lower()
        
        # Check for list indicators
        list_indicators = ['steps', 'ways', 'methods', 'types', 'kinds', 'list', 'examples']
        if any(indicator in query_lower for indicator in list_indicators):
            return 'list'
        
        # Check for table indicators
        table_indicators = ['comparison', 'vs', 'versus', 'difference', 'compare']
        if any(indicator in query_lower for indicator in table_indicators):
            return 'table'
        
        # Check for how-to indicators
        if query_lower.startswith('how to'):
            return 'ordered_list'
        
        # Check content structure
        if '<ol>' in content or '</ol>' in content:
            return 'ordered_list'
        elif '<ul>' in content or '</ul>' in content:
            return 'list'
        elif '<table>' in content or '</table>' in content:
            return 'table'
        
        # Default to paragraph
        return 'paragraph'
    
    async def _generate_optimized_content(self, content: str, query: str, format_type: str) -> str:
        """Generate optimized content for featured snippet."""
        if format_type == 'paragraph':
            return await self._optimize_paragraph_content(content, query)
        elif format_type == 'list':
            return await self._optimize_list_content(content, query)
        elif format_type == 'ordered_list':
            return await self._optimize_ordered_list_content(content, query)
        elif format_type == 'table':
            return await self._optimize_table_content(content, query)
        else:
            return content
    
    async def _optimize_paragraph_content(self, content: str, query: str) -> str:
        """Optimize paragraph content for featured snippet."""
        # Extract main concepts from query
        query_words = query.lower().split()
        
        # Find the best answer paragraph in content
        soup = BeautifulSoup(content, 'html.parser')
        paragraphs = soup.find_all('p')
        
        best_paragraph = ""
        best_score = 0
        
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) < 40 or len(text) > 300:
                continue
            
            # Score based on query word presence
            score = sum(1 for word in query_words if word in text.lower())
            if score > best_score and len(text) >= 40:
                best_score = score
                best_paragraph = text
        
        if not best_paragraph:
            best_paragraph = content[:200] + "..." if len(content) > 200 else content
        
        # Ensure optimal length (40-160 characters for best snippet performance)
        if len(best_paragraph) > 160:
            # Find a good breaking point
            sentences = best_paragraph.split('.')
            optimized = ""
            for sentence in sentences:
                if len(optimized + sentence) <= 160:
                    optimized += sentence + "."
                else:
                    break
            best_paragraph = optimized.strip()
        
        return best_paragraph
    
    async def _optimize_list_content(self, content: str, query: str) -> str:
        """Optimize list content for featured snippet."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for existing lists
        lists = soup.find_all(['ul', 'ol'])
        if lists:
            list_items = lists[0].find_all('li')
            if list_items and len(list_items) <= 8:  # Optimal list length for snippets
                return str(lists[0])
        
        # Create a list from paragraph content
        paragraphs = soup.find_all('p')
        list_items = []
        
        for p in paragraphs:
            text = p.get_text().strip()
            # Look for list-like patterns
            if re.match(r'^\d+\.?\s+', text) or text.startswith('•') or text.startswith('-'):
                clean_text = re.sub(r'^\d+\.?\s+|^[•\-]\s+', '', text)
                if 10 <= len(clean_text) <= 80:
                    list_items.append(clean_text)
        
        if list_items:
            list_html = "<ul>\n"
            for item in list_items[:8]:  # Limit to 8 items
                list_html += f"  <li>{item}</li>\n"
            list_html += "</ul>"
            return list_html
        
        return content
    
    async def _optimize_ordered_list_content(self, content: str, query: str) -> str:
        """Optimize ordered list content for how-to snippets."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for existing ordered lists
        ordered_lists = soup.find_all('ol')
        if ordered_lists:
            return str(ordered_lists[0])
        
        # Create ordered list from step-like content
        paragraphs = soup.find_all('p')
        steps = []
        
        for p in paragraphs:
            text = p.get_text().strip()
            # Look for step patterns
            if re.match(r'^(?:step\s+)?\d+[:.\s]', text.lower()) or 'first' in text.lower() or 'then' in text.lower():
                clean_text = re.sub(r'^(?:step\s+)?\d+[:.\s]\s*', '', text, flags=re.IGNORECASE)
                if 15 <= len(clean_text) <= 100:
                    steps.append(clean_text)
        
        if steps:
            list_html = "<ol>\n"
            for step in steps[:8]:  # Limit to 8 steps
                list_html += f"  <li>{step}</li>\n"
            list_html += "</ol>"
            return list_html
        
        return content
    
    async def _optimize_table_content(self, content: str, query: str) -> str:
        """Optimize table content for comparison snippets."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for existing tables
        tables = soup.find_all('table')
        if tables:
            return str(tables[0])
        
        # Try to create a simple comparison table from content
        # This is a simplified implementation
        return content
    
    async def _generate_snippet_schema(self, query: str, content: str, format_type: str) -> Dict[str, Any]:
        """Generate schema markup for snippet optimization."""
        if format_type == 'ordered_list' and query.lower().startswith('how to'):
            return await self._generate_how_to_schema(query, content)
        elif 'faq' in query.lower() or '?' in query:
            return await self._generate_faq_schema(query, content)
        else:
            return await self._generate_article_schema(query, content)
    
    async def _generate_how_to_schema(self, query: str, content: str) -> Dict[str, Any]:
        """Generate HowTo schema markup."""
        soup = BeautifulSoup(content, 'html.parser')
        steps = []
        
        if '<ol>' in content:
            list_items = soup.find_all('li')
            for i, li in enumerate(list_items, 1):
                steps.append({
                    "@type": "HowToStep",
                    "position": i,
                    "name": f"Step {i}",
                    "text": li.get_text().strip()
                })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": query.title(),
            "description": f"Learn {query.lower()} with this step-by-step guide",
            "step": steps
        }
        
        return schema
    
    async def _generate_faq_schema(self, query: str, content: str) -> Dict[str, Any]:
        """Generate FAQ schema markup."""
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": query,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": content[:500]  # Limit answer length
                }
            }]
        }
        
        return schema
    
    async def _generate_article_schema(self, query: str, content: str) -> Dict[str, Any]:
        """Generate Article schema markup."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": query.title(),
            "articleBody": content[:1000],  # Limit content length
            "author": {
                "@type": "Organization",
                "name": "IA Chéries"
            },
            "publisher": {
                "@type": "Organization",
                "name": "IA Chéries",
                "url": "https://ainflue.com"
            },
            "datePublished": datetime.now(timezone.utc).isoformat(),
            "dateModified": datetime.now(timezone.utc).isoformat()
        }
        
        return schema
    
    async def _generate_structure_recommendations(self, query: str, format_type: str) -> Dict[str, Any]:
        """Generate content structure recommendations."""
        recommendations = {
            'heading_structure': [],
            'content_organization': [],
            'markup_requirements': []
        }
        
        if format_type == 'paragraph':
            recommendations['content_organization'] = [
                'Lead with a direct answer to the question',
                'Keep the answer concise (40-160 characters)',
                'Use clear, simple language',
                'Include the target keyword in the first sentence'
            ]
        
        elif format_type == 'list':
            recommendations['content_organization'] = [
                'Use numbered or bulleted lists',
                'Keep list items concise (10-80 characters each)',
                'Limit to 8 items maximum',
                'Use parallel structure for all items'
            ]
        
        elif format_type == 'ordered_list':
            recommendations['content_organization'] = [
                'Use numbered steps',
                'Start each step with an action verb',
                'Keep steps concise but complete',
                'Limit to 8 steps maximum'
            ]
            recommendations['markup_requirements'] = [
                'Use <ol> and <li> tags',
                'Consider adding HowTo schema markup',
                'Include step numbers in the text'
            ]
        
        return recommendations
    
    async def _calculate_snippet_optimization_score(self, optimization: Dict[str, Any]) -> float:
        """Calculate optimization score for snippet potential."""
        score = 50.0
        
        content = optimization.get('optimized_content', '')
        format_type = optimization.get('snippet_type', 'paragraph')
        
        # Content length score
        if format_type == 'paragraph':
            if 40 <= len(content) <= 160:
                score += 20
            elif 30 <= len(content) <= 200:
                score += 10
        
        # Format appropriateness
        query = optimization.get('target_query', '').lower()
        if format_type == 'ordered_list' and query.startswith('how to'):
            score += 25
        elif format_type == 'list' and any(word in query for word in ['steps', 'ways', 'types']):
            score += 25
        elif format_type == 'paragraph' and query.startswith('what'):
            score += 25
        
        # Schema markup bonus
        if optimization.get('schema_markup'):
            score += 15
        
        return min(100.0, score)
    
    async def _generate_snippet_recommendations(self, optimization: Dict[str, Any]) -> List[str]:
        """Generate recommendations for snippet optimization."""
        recommendations = []
        
        score = optimization.get('optimization_score', 0)
        if score < 70:
            recommendations.append('Content needs significant optimization for featured snippet capture')
        
        format_type = optimization.get('snippet_type')
        if format_type == 'paragraph':
            recommendations.extend([
                'Lead with a direct, concise answer',
                'Use the target keyword in the first sentence',
                'Keep answer between 40-160 characters for optimal snippet length'
            ])
        elif format_type == 'list':
            recommendations.extend([
                'Structure content as a clear bulleted or numbered list',
                'Keep list items concise and scannable',
                'Use parallel structure across all list items'
            ])
        elif format_type == 'ordered_list':
            recommendations.extend([
                'Create clear step-by-step instructions',
                'Start each step with an action verb',
                'Consider adding HowTo schema markup'
            ])
        
        return recommendations


class KnowledgePanelOptimizer:
    """Optimize for Knowledge Panel appearances."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.KnowledgePanelOptimizer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def optimize_for_knowledge_panel(self, entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entity for Knowledge Panel appearance."""
        self.logger.info(f"Optimizing {entity_type} for Knowledge Panel")
        
        optimization = {
            'entity_type': entity_type,
            'current_data': entity_data,
            'optimized_schema': {},
            'optimization_score': 0,
            'missing_properties': [],
            'recommendations': []
        }
        
        if entity_type == 'person':
            optimization.update(await self._optimize_person_entity(entity_data))
        elif entity_type == 'organization':
            optimization.update(await self._optimize_organization_entity(entity_data))
        elif entity_type == 'creative_work':
            optimization.update(await self._optimize_creative_work_entity(entity_data))
        
        return optimization
    
    async def _optimize_person_entity(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize person entity for Knowledge Panel."""
        required_properties = [
            'name', 'description', 'url', 'image', 'jobTitle', 
            'worksFor', 'birthDate', 'nationality', 'knowsAbout'
        ]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": person_data.get('name', ''),
            "description": person_data.get('description', ''),
            "url": person_data.get('url', ''),
            "image": person_data.get('image', ''),
            "jobTitle": person_data.get('job_title', ''),
            "nationality": person_data.get('nationality', ''),
            "birthDate": person_data.get('birth_date', ''),
            "knowsAbout": person_data.get('expertise', [])
        }
        
        # Add social media profiles
        if 'social_profiles' in person_data:
            schema['sameAs'] = person_data['social_profiles']
        
        # Add organization affiliation
        if 'organization' in person_data:
            schema['worksFor'] = {
                "@type": "Organization",
                "name": person_data['organization']
            }
        
        missing_properties = [prop for prop in required_properties if not person_data.get(prop.replace('_', ''))]
        
        recommendations = []
        if missing_properties:
            recommendations.append(f"Add missing properties: {', '.join(missing_properties)}")
        
        if not person_data.get('social_profiles'):
            recommendations.append('Add social media profile links to increase entity authority')
        
        if not person_data.get('image'):
            recommendations.append('Add high-quality profile image for Knowledge Panel display')
        
        score = ((len(required_properties) - len(missing_properties)) / len(required_properties)) * 100
        
        return {
            'optimized_schema': schema,
            'optimization_score': score,
            'missing_properties': missing_properties,
            'recommendations': recommendations
        }
    
    async def _optimize_organization_entity(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize organization entity for Knowledge Panel."""
        required_properties = [
            'name', 'description', 'url', 'logo', 'address', 
            'telephone', 'email', 'foundingDate', 'founder'
        ]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": org_data.get('name', ''),
            "description": org_data.get('description', ''),
            "url": org_data.get('url', ''),
            "logo": org_data.get('logo', ''),
            "telephone": org_data.get('telephone', ''),
            "email": org_data.get('email', ''),
            "foundingDate": org_data.get('founding_date', '')
        }
        
        # Add address
        if 'address' in org_data:
            schema['address'] = {
                "@type": "PostalAddress",
                "streetAddress": org_data['address'].get('street', ''),
                "addressLocality": org_data['address'].get('city', ''),
                "addressRegion": org_data['address'].get('state', ''),
                "postalCode": org_data['address'].get('zip', ''),
                "addressCountry": org_data['address'].get('country', '')
            }
        
        # Add founder
        if 'founder' in org_data:
            schema['founder'] = {
                "@type": "Person",
                "name": org_data['founder']
            }
        
        missing_properties = [prop for prop in required_properties if not org_data.get(prop.replace('_', ''))]
        
        recommendations = []
        if missing_properties:
            recommendations.append(f"Add missing properties: {', '.join(missing_properties)}")
        
        if not org_data.get('logo'):
            recommendations.append('Add high-quality logo for Knowledge Panel display')
        
        if not org_data.get('address'):
            recommendations.append('Add complete business address for local Knowledge Panel features')
        
        score = ((len(required_properties) - len(missing_properties)) / len(required_properties)) * 100
        
        return {
            'optimized_schema': schema,
            'optimization_score': score,
            'missing_properties': missing_properties,
            'recommendations': recommendations
        }
    
    async def _optimize_creative_work_entity(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize creative work entity for Knowledge Panel."""
        required_properties = [
            'name', 'description', 'creator', 'dateCreated', 
            'genre', 'keywords', 'thumbnail_url'
        ]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": work_data.get('name', ''),
            "description": work_data.get('description', ''),
            "dateCreated": work_data.get('date_created', ''),
            "genre": work_data.get('genre', ''),
            "keywords": work_data.get('keywords', []),
            "thumbnailUrl": work_data.get('thumbnail_url', '')
        }
        
        # Add creator
        if 'creator' in work_data:
            schema['creator'] = {
                "@type": "Person",
                "name": work_data['creator']
            }
        
        missing_properties = [prop for prop in required_properties if not work_data.get(prop.replace('_', ''))]
        
        recommendations = []
        if missing_properties:
            recommendations.append(f"Add missing properties: {', '.join(missing_properties)}")
        
        score = ((len(required_properties) - len(missing_properties)) / len(required_properties)) * 100
        
        return {
            'optimized_schema': schema,
            'optimization_score': score,
            'missing_properties': missing_properties,
            'recommendations': recommendations
        }


class VideoSnippetOptimizer:
    """Optimize video content for video snippets and carousels."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.VideoSnippetOptimizer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def optimize_video_for_snippets(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize video content for snippet appearance."""
        self.logger.info(f"Optimizing video {video_data.get('title', 'Unknown')} for snippets")
        
        optimization = {
            'video_data': video_data,
            'optimized_schema': {},
            'thumbnail_optimization': {},
            'title_optimization': {},
            'description_optimization': {},
            'chapters_optimization': {},
            'optimization_score': 0,
            'recommendations': []
        }
        
        # Generate optimized VideoObject schema
        schema = await self._generate_video_schema(video_data)
        optimization['optimized_schema'] = schema
        
        # Optimize title for snippets
        title_opt = await self._optimize_video_title(video_data.get('title', ''))
        optimization['title_optimization'] = title_opt
        
        # Optimize description
        desc_opt = await self._optimize_video_description(video_data.get('description', ''))
        optimization['description_optimization'] = desc_opt
        
        # Optimize thumbnail
        thumbnail_opt = await self._optimize_video_thumbnail(video_data)
        optimization['thumbnail_optimization'] = thumbnail_opt
        
        # Optimize chapters if available
        if 'chapters' in video_data:
            chapters_opt = await self._optimize_video_chapters(video_data['chapters'])
            optimization['chapters_optimization'] = chapters_opt
        
        # Calculate optimization score
        score = await self._calculate_video_optimization_score(optimization)
        optimization['optimization_score'] = score
        
        # Generate recommendations
        recommendations = await self._generate_video_recommendations(optimization)
        optimization['recommendations'] = recommendations
        
        return optimization
    
    async def _generate_video_schema(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate VideoObject schema markup."""
        schema = {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": video_data.get('title', ''),
            "description": video_data.get('description', ''),
            "thumbnailUrl": video_data.get('thumbnail_url', ''),
            "uploadDate": video_data.get('upload_date', datetime.now(timezone.utc).isoformat()),
            "duration": f"PT{video_data.get('duration', 0)}S" if video_data.get('duration') else None,
            "contentUrl": video_data.get('url', ''),
            "embedUrl": video_data.get('embed_url', ''),
            "width": video_data.get('width', 1920),
            "height": video_data.get('height', 1080)
        }
        
        # Add creator information
        if 'creator' in video_data:
            schema['creator'] = {
                "@type": "Person",
                "name": video_data['creator']
            }
        
        # Add interaction statistics
        if 'view_count' in video_data:
            schema['interactionStatistic'] = {
                "@type": "InteractionCounter",
                "interactionType": "https://schema.org/WatchAction",
                "userInteractionCount": video_data['view_count']
            }
        
        # Add rating if available
        if 'rating' in video_data and 'rating_count' in video_data:
            schema['aggregateRating'] = {
                "@type": "AggregateRating",
                "ratingValue": video_data['rating'],
                "ratingCount": video_data['rating_count'],
                "bestRating": 5
            }
        
        return schema
    
    async def _optimize_video_title(self, title: str) -> Dict[str, Any]:
        """Optimize video title for snippet capture."""
        optimization = {
            'original_title': title,
            'optimized_title': title,
            'issues': [],
            'improvements': []
        }
        
        if len(title) > 60:
            optimization['issues'].append('Title too long for optimal snippet display')
            optimization['optimized_title'] = title[:57] + "..."
        
        if len(title) < 10:
            optimization['issues'].append('Title too short for effective snippet capture')
        
        # Check for keyword positioning
        if not title or title[0].islower():
            optimization['improvements'].append('Start title with capital letter for better presentation')
        
        # Check for numbers (often perform well in snippets)
        if not re.search(r'\d+', title):
            optimization['improvements'].append('Consider adding numbers or specific quantities to title')
        
        return optimization
    
    async def _optimize_video_description(self, description: str) -> Dict[str, Any]:
        """Optimize video description for snippet capture."""
        optimization = {
            'original_description': description,
            'optimized_description': description,
            'issues': [],
            'improvements': []
        }
        
        if len(description) < 100:
            optimization['issues'].append('Description too short for comprehensive snippet optimization')
        
        if len(description) > 5000:
            optimization['issues'].append('Description very long - key information may be buried')
        
        # Check for timestamp inclusion
        if not re.search(r'\d+:\d+', description):
            optimization['improvements'].append('Add timestamps to description for chapter navigation')
        
        # Check for key takeaways section
        if 'takeaway' not in description.lower() and 'summary' not in description.lower():
            optimization['improvements'].append('Add key takeaways or summary section for snippet extraction')
        
        return optimization
    
    async def _optimize_video_thumbnail(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize video thumbnail for snippet display."""
        optimization = {
            'current_thumbnail': video_data.get('thumbnail_url', ''),
            'recommendations': []
        }
        
        if not video_data.get('thumbnail_url'):
            optimization['recommendations'].append('Add custom thumbnail for better snippet visibility')
        
        # Check thumbnail requirements for snippets
        optimization['recommendations'].extend([
            'Use high-resolution thumbnail (minimum 1280x720)',
            'Ensure thumbnail accurately represents video content',
            'Use clear, readable text overlay if applicable',
            'Maintain consistent branding across thumbnails'
        ])
        
        return optimization
    
    async def _optimize_video_chapters(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize video chapters for snippet enhancement."""
        optimization = {
            'chapter_count': len(chapters),
            'optimized_chapters': [],
            'recommendations': []
        }
        
        for chapter in chapters:
            optimized_chapter = {
                'title': chapter.get('title', ''),
                'start_time': chapter.get('start_time', 0),
                'description': chapter.get('description', '')
            }
            
            # Optimize chapter title
            if len(chapter.get('title', '')) < 5:
                optimization['recommendations'].append(f"Improve chapter title: '{chapter.get('title', '')}'")
            
            optimization['optimized_chapters'].append(optimized_chapter)
        
        if len(chapters) < 3:
            optimization['recommendations'].append('Add more chapter markers for better navigation and snippet opportunities')
        
        return optimization
    
    async def _calculate_video_optimization_score(self, optimization: Dict[str, Any]) -> float:
        """Calculate video optimization score for snippets."""
        score = 50.0
        
        # Schema markup completeness
        schema = optimization.get('optimized_schema', {})
        required_fields = ['name', 'description', 'thumbnailUrl', 'duration', 'uploadDate']
        present_fields = [field for field in required_fields if schema.get(field)]
        score += (len(present_fields) / len(required_fields)) * 30
        
        # Title optimization
        title_issues = len(optimization.get('title_optimization', {}).get('issues', []))
        if title_issues == 0:
            score += 10
        
        # Description optimization
        desc_issues = len(optimization.get('description_optimization', {}).get('issues', []))
        if desc_issues == 0:
            score += 10
        
        return min(100.0, score)
    
    async def _generate_video_recommendations(self, optimization: Dict[str, Any]) -> List[str]:
        """Generate video optimization recommendations."""
        recommendations = []
        
        # Collect all recommendations from sub-optimizations
        for key in ['title_optimization', 'description_optimization', 'thumbnail_optimization', 'chapters_optimization']:
            if key in optimization:
                recommendations.extend(optimization[key].get('recommendations', []))
                recommendations.extend(optimization[key].get('improvements', []))
        
        # Add general video snippet recommendations
        recommendations.extend([
            'Ensure video loads quickly for better snippet performance',
            'Use clear audio for accessibility and transcript generation',
            'Create engaging opening that summarizes video content',
            'Include relevant keywords in video filename'
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations


class RichSnippetsManager:
    """Main manager for rich snippets optimization across IA Chéries platform."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize optimizers
        self.featured_snippet_optimizer = FeaturedSnippetOptimizer()
        self.knowledge_panel_optimizer = KnowledgePanelOptimizer()
        self.video_snippet_optimizer = VideoSnippetOptimizer()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_serp_opportunities(self, target_queries: List[str]) -> List[RichSnippetOpportunity]:
        """Analyze SERP for rich snippet opportunities."""
        self.logger.info(f"Analyzing {len(target_queries)} queries for rich snippet opportunities")
        
        opportunities = []
        
        for query in target_queries:
            # Simulate SERP analysis (in production, would use real SERP API)
            serp_analysis = await self._analyze_serp_features(query)
            query_opportunities = await self._identify_opportunities_from_serp(query, serp_analysis)
            opportunities.extend(query_opportunities)
        
        # Sort by priority and potential impact
        opportunities.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x.priority],
            x.estimated_traffic_lift
        ), reverse=True)
        
        return opportunities
    
    async def _analyze_serp_features(self, query: str) -> SERPAnalysisResult:
        """Analyze SERP features for a query."""
        # Mock SERP analysis - in production, would use real SERP data
        analysis = SERPAnalysisResult(
            query=query,
            serp_features=[],
            related_questions=[
                f"What is {query}?",
                f"How to {query}?",
                f"Why {query}?",
                f"Best {query}?"
            ]
        )
        
        # Determine likely SERP features based on query intent
        query_lower = query.lower()
        
        if query_lower.startswith('how to'):
            analysis.serp_features.append(SERPFeatureType.FEATURED_SNIPPET)
            analysis.serp_features.append(SERPFeatureType.HOW_TO_SNIPPET)
        
        if query_lower.startswith('what is'):
            analysis.serp_features.append(SERPFeatureType.FEATURED_SNIPPET)
            analysis.serp_features.append(SERPFeatureType.KNOWLEDGE_PANEL)
        
        if 'video' in query_lower or 'tutorial' in query_lower:
            analysis.serp_features.append(SERPFeatureType.VIDEO_SNIPPET)
            analysis.serp_features.append(SERPFeatureType.CAROUSEL)
        
        return analysis
    
    async def _identify_opportunities_from_serp(self, query: str, serp_analysis: SERPAnalysisResult) -> List[RichSnippetOpportunity]:
        """Identify optimization opportunities from SERP analysis."""
        opportunities = []
        
        for feature_type in serp_analysis.serp_features:
            opportunity = await self._create_opportunity_for_feature(query, feature_type, serp_analysis)
            if opportunity:
                opportunities.append(opportunity)
        
        return opportunities
    
    async def _create_opportunity_for_feature(self, query: str, feature_type: SERPFeatureType, 
                                           serp_analysis: SERPAnalysisResult) -> Optional[RichSnippetOpportunity]:
        """Create optimization opportunity for specific SERP feature."""
        base_url = f"/content/{query.replace(' ', '-').lower()}"
        
        if feature_type == SERPFeatureType.FEATURED_SNIPPET:
            return RichSnippetOpportunity(
                feature_type=feature_type,
                schema_type=SchemaType.ARTICLE,
                target_url=base_url,
                title=f"Featured Snippet for '{query}'",
                description=f"Optimize content to capture featured snippet for {query}",
                priority='high',
                difficulty='medium',
                estimated_traffic_lift=35.0,
                required_content_changes=[
                    'Create direct answer in first paragraph',
                    'Optimize content length (40-160 characters)',
                    'Use target keyword in first sentence'
                ],
                optimization_steps=[
                    'Analyze current featured snippet holder',
                    'Create superior content answer',
                    'Implement structured content format',
                    'Add relevant schema markup'
                ]
            )
        
        elif feature_type == SERPFeatureType.VIDEO_SNIPPET:
            return RichSnippetOpportunity(
                feature_type=feature_type,
                schema_type=SchemaType.VIDEO_OBJECT,
                target_url=base_url + "/video",
                title=f"Video Snippet for '{query}'",
                description=f"Create video content optimized for video snippets",
                priority='high',
                difficulty='hard',
                estimated_traffic_lift=45.0,
                required_content_changes=[
                    'Create high-quality video content',
                    'Optimize video title and description',
                    'Add custom thumbnail',
                    'Include video transcript'
                ],
                optimization_steps=[
                    'Research video snippet competition',
                    'Create engaging video content',
                    'Implement VideoObject schema',
                    'Submit video sitemap'
                ]
            )
        
        elif feature_type == SERPFeatureType.KNOWLEDGE_PANEL:
            return RichSnippetOpportunity(
                feature_type=feature_type,
                schema_type=SchemaType.PERSON,
                target_url=base_url + "/entity",
                title=f"Knowledge Panel for '{query}'",
                description=f"Establish entity authority for knowledge panel appearance",
                priority='medium',
                difficulty='hard',
                estimated_traffic_lift=25.0,
                required_content_changes=[
                    'Create comprehensive entity page',
                    'Add structured data markup',
                    'Build entity citations and mentions',
                    'Establish social media presence'
                ],
                optimization_steps=[
                    'Audit current entity presence',
                    'Implement comprehensive schema markup',
                    'Build authoritative backlinks',
                    'Monitor entity tracking'
                ]
            )
        
        return None
    
    async def optimize_content_for_snippets(self, content_data: Dict[str, Any], 
                                          target_features: List[SERPFeatureType]) -> Dict[str, Any]:
        """Optimize content for multiple rich snippet features."""
        self.logger.info(f"Optimizing content for {len(target_features)} SERP features")
        
        optimization_results = {
            'content_data': content_data,
            'target_features': [feature.value for feature in target_features],
            'optimizations': {},
            'combined_schema': {},
            'overall_score': 0,
            'recommendations': []
        }
        
        feature_optimizations = []
        
        for feature_type in target_features:
            if feature_type == SERPFeatureType.FEATURED_SNIPPET:
                opt = await self.featured_snippet_optimizer.optimize_for_featured_snippet(
                    content_data.get('content', ''),
                    content_data.get('target_query', '')
                )
                optimization_results['optimizations']['featured_snippet'] = opt
                feature_optimizations.append(opt.get('optimization_score', 0))
            
            elif feature_type in [SERPFeatureType.VIDEO_SNIPPET, SERPFeatureType.CAROUSEL]:
                if 'video_data' in content_data:
                    opt = await self.video_snippet_optimizer.optimize_video_for_snippets(
                        content_data['video_data']
                    )
                    optimization_results['optimizations']['video_snippet'] = opt
                    feature_optimizations.append(opt.get('optimization_score', 0))
            
            elif feature_type == SERPFeatureType.KNOWLEDGE_PANEL:
                if 'entity_data' in content_data:
                    opt = await self.knowledge_panel_optimizer.optimize_for_knowledge_panel(
                        content_data.get('entity_type', 'person'),
                        content_data['entity_data']
                    )
                    optimization_results['optimizations']['knowledge_panel'] = opt
                    feature_optimizations.append(opt.get('optimization_score', 0))
        
        # Calculate overall score
        if feature_optimizations:
            optimization_results['overall_score'] = sum(feature_optimizations) / len(feature_optimizations)
        
        # Combine schema markups
        combined_schema = await self._combine_schema_markups(optimization_results['optimizations'])
        optimization_results['combined_schema'] = combined_schema
        
        # Generate combined recommendations
        all_recommendations = []
        for opt in optimization_results['optimizations'].values():
            all_recommendations.extend(opt.get('recommendations', []))
        
        optimization_results['recommendations'] = list(set(all_recommendations))[:10]
        
        return optimization_results
    
    async def _combine_schema_markups(self, optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple schema markups into a comprehensive structure."""
        combined_schema = {
            "@context": "https://schema.org",
            "@graph": []
        }
        
        for opt_type, opt_data in optimizations.items():
            schema = opt_data.get('schema_markup') or opt_data.get('optimized_schema')
            if schema and '@type' in schema:
                combined_schema["@graph"].append(schema)
        
        return combined_schema if combined_schema["@graph"] else {}
    
    async def generate_rich_snippets_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate comprehensive rich snippets report."""
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rich Snippets Optimization Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                .score {{ font-size: 48px; font-weight: bold; color: #28a745; }}
                .feature-card {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 5px solid #007bff; }}
                .recommendations {{ background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .schema-code {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }}
                .legal {{ font-size: 10px; color: #666; margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Rich Snippets Optimization Report</h1>
                <div class="score">{analysis_results.get('overall_score', 0):.1f}/100</div>
                <p>Overall Rich Snippets Optimization Score</p>
            </div>
        """
        
        # Add optimizations section
        optimizations = analysis_results.get('optimizations', {})
        if optimizations:
            report += "<h2>🎨 SERP Feature Optimizations</h2>"
            
            for feature_name, opt_data in optimizations.items():
                score = opt_data.get('optimization_score', 0)
                report += f"""
                <div class="feature-card">
                    <h3>{feature_name.replace('_', ' ').title()}</h3>
                    <p><strong>Optimization Score:</strong> {score:.1f}/100</p>
                    <p><strong>Recommendations:</strong></p>
                    <ul>
                """
                
                for rec in opt_data.get('recommendations', [])[:5]:
                    report += f"<li>{rec}</li>"
                
                report += "</ul></div>"
        
        # Add combined recommendations
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            report += """
            <h2>💡 Priority Recommendations</h2>
            <div class="recommendations">
                <ul>
            """
            
            for rec in recommendations[:10]:
                report += f"<li>{rec}</li>"
            
            report += "</ul></div>"
        
        # Add schema markup
        combined_schema = analysis_results.get('combined_schema', {})
        if combined_schema:
            report += f"""
            <h2>🔧 Combined Schema Markup</h2>
            <div class="schema-code">{json.dumps(combined_schema, indent=2)}</div>
            """
        
        report += f"""
            <div class="legal">
                <p>© 2025 Fahed Mlaiel (mlaiel@live.de) - Rich Snippets Manager</p>
                <p>SERP optimization report generated by IA Chéries Rich Snippets Manager</p>
                <p>📧 For enterprise SERP optimization consulting: mlaiel@live.de</p>
            </div>
        </body>
        </html>
        """
        
        return report


# Usage Example
async def main():
    """Example usage of Rich Snippets Manager."""
    
    # Initialize rich snippets manager
    rich_snippets_manager = RichSnippetsManager()
    
    try:
        # Example content data
        content_data = {
            'content': 'This is a comprehensive guide about creator economy and how creators can optimize their content for better visibility.',
            'target_query': 'how to optimize creator content',
            'video_data': {
                'title': 'Complete Guide to Creator Content Optimization',
                'description': 'Learn step-by-step how to optimize your creator content for maximum visibility and engagement.',
                'thumbnail_url': '/thumbnails/optimization-guide.jpg',
                'duration': 600,
                'url': '/videos/creator-optimization-guide',
                'creator': 'IA Chéries Expert'
            },
            'entity_data': {
                'name': 'Creator Economy Expert',
                'description': 'Leading expert in creator economy optimization and digital content strategy',
                'job_title': 'Creator Economy Consultant',
                'expertise': ['Content Creation', 'SEO', 'Digital Marketing']
            },
            'entity_type': 'person'
        }
        
        target_features = [
            SERPFeatureType.FEATURED_SNIPPET,
            SERPFeatureType.VIDEO_SNIPPET,
            SERPFeatureType.KNOWLEDGE_PANEL
        ]
        
        print(f"\n=== Rich Snippets Optimization ===")
        
        # Optimize content for rich snippets
        results = await rich_snippets_manager.optimize_content_for_snippets(content_data, target_features)
        
        print(f"Overall Optimization Score: {results['overall_score']:.1f}/100")
        print(f"Target Features: {', '.join(results['target_features'])}")
        print(f"Optimizations Completed: {len(results['optimizations'])}")
        
        # Show top recommendations
        if results['recommendations']:
            print("\n=== Top Rich Snippets Recommendations ===")
            for i, rec in enumerate(results['recommendations'][:5], 1):
                print(f"{i}. {rec}")
        
        # Generate report
        report_html = await rich_snippets_manager.generate_rich_snippets_report(results)
        print("\n=== Rich Snippets Report Generated ===")
        
        # Analyze SERP opportunities
        target_queries = ['how to optimize creator content', 'what is creator economy', 'video content creation tips']
        opportunities = await rich_snippets_manager.analyze_serp_opportunities(target_queries)
        
        print(f"\n=== SERP Opportunities Found: {len(opportunities)} ===")
        for opp in opportunities[:3]:
            print(f"- {opp.title} (Priority: {opp.priority}, Traffic Lift: {opp.estimated_traffic_lift}%)")
        
    except Exception as e:
        print(f"Error during rich snippets optimization: {e}")


if __name__ == "__main__":
    asyncio.run(main())