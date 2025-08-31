"""
SEO Optimizer - Advanced content optimization for search engines

Professional SEO optimization engine that enhances content for better
search engine visibility and ranking performance.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade

from .base_generator import ContentGenerationContext


class SEOOptimizer:
    """
    Advanced SEO optimizer that enhances content for search engine optimization.
    
    This optimizer provides:
    - Keyword density optimization
    - Meta description generation
    - Title optimization
    - Header structure optimization
    - Internal linking suggestions
    - Content readability analysis
    - Schema markup recommendations
    - SEO score calculation
    """
    
    def __init__(self):
        """Initialize the SEO optimizer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # SEO configuration
        self.target_keyword_density = 0.02  # 2%
        self.max_keyword_density = 0.05     # 5%
        self.min_content_length = 300       # 300 words minimum
        self.optimal_content_length = 1500  # 1500 words optimal
        
        # Initialize NLP components
        self._initialize_nlp()
        
        # SEO rules and weights
        self.seo_weights = {
            'keyword_density': 0.2,
            'content_length': 0.15,
            'readability': 0.15,
            'title_optimization': 0.15,
            'meta_description': 0.1,
            'header_structure': 0.1,
            'internal_links': 0.05,
            'external_links': 0.05,
            'image_alt_text': 0.05
        }
    
    def _initialize_nlp(self) -> None:
        """Initialize NLP components"""



        try:
            # Download required NLTK data
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
            
        except Exception as e:
            self.logger.warning(f"NLP initialization warning: {str(e)}")
            self.stop_words = set()
    
    async def optimize_content(
        self,
        content: Any,
        content_type: str,
        context: ContentGenerationContext
    ) -> Dict[str, Any]:
        """
        Optimize content for SEO.
        
        Args:
            content: Content to optimize (text, dict, etc.)
            content_type: Type of content (text, blog, social, etc.)
            context: Generation context with optimization requirements
            
        Returns:
            Optimized content with SEO enhancements
        """



        try:
            # Extract text content
            text_content = self._extract_text_content(content)
            
            # Get target keywords from context
            target_keywords = self._extract_target_keywords(context)
            
            # Perform SEO analysis
            seo_analysis = await self._analyze_seo(text_content, target_keywords)
            
            # Apply optimizations based on content type
            if content_type == 'blog':
                optimized_content = await self._optimize_blog_content(
                    text_content, target_keywords, seo_analysis, context
                )
            elif content_type in ['instagram_post', 'social']:
                optimized_content = await self._optimize_social_content(
                    text_content, target_keywords, seo_analysis, context
                )
            elif content_type == 'product':
                optimized_content = await self._optimize_product_content(
                    text_content, target_keywords, seo_analysis, context
                )
            else:
                optimized_content = await self._optimize_general_content(
                    text_content, target_keywords, seo_analysis, context
                )
            
            # Generate SEO metadata
            seo_metadata = await self._generate_seo_metadata(
                optimized_content, target_keywords, content_type
            )
            
            # Calculate final SEO score
            final_score = await self._calculate_seo_score(
                optimized_content, target_keywords, seo_metadata
            )
            
            return {
                'optimized_content': optimized_content,
                'seo_metadata': seo_metadata,
                'seo_analysis': seo_analysis,
                'seo_score': final_score,
                'recommendations': await self._generate_recommendations(seo_analysis),
                'target_keywords': target_keywords
            }
            
        except Exception as e:
            self.logger.error(f"SEO optimization failed: {str(e)}")
            return {
                'optimized_content': content,
                'seo_metadata': {},
                'seo_analysis': {},
                'seo_score': 0.0,
                'recommendations': [],
                'target_keywords': []
            }
    
    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from various content types"""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            if 'content' in content:
                return str(content['content'])
            elif 'text' in content:
                return str(content['text'])
            elif 'body' in content:
                return str(content['body'])
            else:
                # Concatenate all string values
                return ' '.join([str(v) for v in content.values() if isinstance(v, str)])
        else:
            return str(content)
    
    def _extract_target_keywords(self, context: ContentGenerationContext) -> List[str]:
        """Extract target keywords from context"""
        keywords = []
        
        # From metadata
        if context.metadata and 'keywords' in context.metadata:
            keywords.extend(context.metadata['keywords'])
        
        # From platform requirements
        if context.platform_requirements and 'keywords' in context.platform_requirements:
            keywords.extend(context.platform_requirements['keywords'])
        
        # From brand guidelines
        if context.brand_guidelines and 'keywords' in context.brand_guidelines:
            keywords.extend(context.brand_guidelines['keywords'])
        
        # Default keywords based on content type
        if not keywords:
            keywords = ['content', 'quality', 'professional']
        
        return list(set(keywords))  # Remove duplicates
    
    async def _analyze_seo(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis"""
        analysis = {}
        
        # Content length analysis
        word_count = len(content.split())
        analysis['word_count'] = word_count
        analysis['content_length_score'] = self._score_content_length(word_count)
        
        # Keyword analysis
        analysis['keyword_analysis'] = await self._analyze_keywords(content, keywords)
        
        # Readability analysis
        analysis['readability'] = await self._analyze_readability(content)
        
        # Structure analysis
        analysis['structure'] = await self._analyze_structure(content)
        
        # Link analysis
        analysis['links'] = await self._analyze_links(content)
        
        return analysis
    
    def _score_content_length(self, word_count: int) -> float:
        """Score content based on length"""
        if word_count < self.min_content_length:
            return word_count / self.min_content_length * 0.5
        elif word_count > self.optimal_content_length:
            # Diminishing returns after optimal length
            excess = word_count - self.optimal_content_length
            penalty = excess / 1000 * 0.1  # Small penalty for excessive length
            return max(0.8, 1.0 - penalty)
        else:
            # Linear score between min and optimal
            progress = (word_count - self.min_content_length) / (self.optimal_content_length - self.min_content_length)
            return 0.5 + (progress * 0.5)
    
    async def _analyze_keywords(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword usage and density"""
        content_lower = content.lower()
        total_words = len(content.split())
        
        keyword_analysis = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Count keyword occurrences
            count = content_lower.count(keyword_lower)
            density = count / total_words if total_words > 0 else 0
            
            # Score keyword density
            if density < self.target_keyword_density * 0.5:
                density_score = 0.3  # Too low
            elif density > self.max_keyword_density:
                density_score = 0.2  # Too high (keyword stuffing)
            elif self.target_keyword_density * 0.8 <= density <= self.target_keyword_density * 1.2:
                density_score = 1.0  # Optimal
            else:
                density_score = 0.7  # Acceptable
            
            keyword_analysis[keyword] = {
                'count': count,
                'density': density,
                'density_score': density_score,
                'positions': self._find_keyword_positions(content_lower, keyword_lower)
            }
        
        # Overall keyword score
        keyword_scores = [kw['density_score'] for kw in keyword_analysis.values()]
        overall_score = sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0
        
        keyword_analysis['overall_score'] = overall_score
        
        return keyword_analysis
    
    def _find_keyword_positions(self, content: str, keyword: str) -> List[int]:
        """Find positions of keyword in content"""
        positions = []
        start = 0
        
        while True:
            pos = content.find(keyword, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""



        try:
            # Flesch Reading Ease
            reading_ease = flesch_reading_ease(content)
            
            # Flesch-Kincaid Grade Level
            grade_level = flesch_kincaid_grade(content)
            
            # Sentence statistics
            sentences = content.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = len(content.split()) / sentence_count if sentence_count > 0 else 0
            
            # Score readability
            if 60 <= reading_ease <= 80:  # Good readability
                readability_score = 1.0
            elif 40 <= reading_ease < 60 or 80 < reading_ease <= 90:  # Acceptable
                readability_score = 0.8
            else:  # Poor readability
                readability_score = 0.5
            
            return {
                'flesch_reading_ease': reading_ease,
                'flesch_kincaid_grade': grade_level,
                'sentence_count': sentence_count,
                'avg_sentence_length': avg_sentence_length,
                'readability_score': readability_score
            }
            
        except Exception as e:
            self.logger.warning(f"Readability analysis failed: {str(e)}")
            return {
                'flesch_reading_ease': 50.0,
                'flesch_kincaid_grade': 10.0,
                'sentence_count': 0,
                'avg_sentence_length': 0,
                'readability_score': 0.5
            }
    
    async def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        # Count headers (markdown style)
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        # Paragraph analysis
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / paragraph_count if paragraph_count > 0 else 0
        
        # Structure score
        structure_score = 0.5  # Base score
        
        if h1_count >= 1:
            structure_score += 0.2
        if h2_count >= 2:
            structure_score += 0.2
        if paragraph_count >= 3:
            structure_score += 0.1
        
        structure_score = min(1.0, structure_score)
        
        return {
            'h1_count': h1_count,
            'h2_count': h2_count,
            'h3_count': h3_count,
            'paragraph_count': paragraph_count,
            'avg_paragraph_length': avg_paragraph_length,
            'structure_score': structure_score
        }
    
    async def _analyze_links(self, content: str) -> Dict[str, Any]:
        """Analyze links in content"""
        # Find markdown links
        markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]*)\)', content)
        
        # Find HTML links
        html_links = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>([^<]*)</a>', content)
        
        internal_links = []
        external_links = []
        
        # Classify links (simplified)
        for link_text, url in markdown_links + html_links:
            if url.startswith('http'):
                external_links.append((link_text, url))
            else:
                internal_links.append((link_text, url))
        
        # Link score
        link_score = 0.5  # Base score
        
        if len(internal_links) >= 2:
            link_score += 0.3
        if len(external_links) >= 1:
            link_score += 0.2
        
        link_score = min(1.0, link_score)
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'total_links': len(internal_links) + len(external_links),
            'link_score': link_score
        }
    
    async def _optimize_blog_content(
        self,
        content: str,
        keywords: List[str],
        analysis: Dict[str, Any],
        context: ContentGenerationContext
    ) -> str:
        """Optimize blog content for SEO"""
        optimized_content = content
        
        # Add title if missing
        if not re.match(r'^#\s+', content):
            title = await self._generate_seo_title(content, keywords)
            optimized_content = f"# {title}\n\n{optimized_content}"
        
        # Optimize keyword placement
        optimized_content = await self._optimize_keyword_placement(optimized_content, keywords)
        
        # Add meta description
        meta_description = await self._generate_meta_description(optimized_content, keywords)
        optimized_content = f"{optimized_content}\n\n<!-- Meta Description: {meta_description} -->"
        
        # Improve structure if needed
        if analysis['structure']['structure_score'] < 0.7:
            optimized_content = await self._improve_content_structure(optimized_content)
        
        return optimized_content
    
    async def _optimize_social_content(
        self,
        content: str,
        keywords: List[str],
        analysis: Dict[str, Any],
        context: ContentGenerationContext
    ) -> str:
        """Optimize social media content for SEO"""
        optimized_content = content
        
        # Add hashtags if not present
        if '#' not in content:
            hashtags = await self._generate_hashtags(keywords)
            optimized_content += f"\n\n{hashtags}"
        
        # Optimize for engagement
        if not re.search(r'[?!]', content):
            optimized_content += " What do you think?"
        
        return optimized_content
    
    async def _optimize_product_content(
        self,
        content: str,
        keywords: List[str],
        analysis: Dict[str, Any],
        context: ContentGenerationContext
    ) -> str:
        """Optimize product content for SEO"""
        optimized_content = content
        
        # Add product-specific keywords
        product_keywords = ['quality', 'best', 'premium', 'professional']
        for keyword in product_keywords:
            if keyword not in content.lower() and len(keywords) > 0:
                # Insert keyword naturally
                sentences = content.split('.')
                if len(sentences) > 1:
                    sentences[0] += f" with {keyword}"
                    optimized_content = '.'.join(sentences)
                break
        
        return optimized_content
    
    async def _optimize_general_content(
        self,
        content: str,
        keywords: List[str],
        analysis: Dict[str, Any],
        context: ContentGenerationContext
    ) -> str:
        """Optimize general content for SEO"""
        optimized_content = content
        
        # Basic keyword optimization
        optimized_content = await self._optimize_keyword_placement(optimized_content, keywords)
        
        return optimized_content
    
    async def _optimize_keyword_placement(self, content: str, keywords: List[str]) -> str:
        """Optimize keyword placement in content"""
        if not keywords:
            return content
        
        sentences = content.split('.')
        primary_keyword = keywords[0]
        
        # Ensure primary keyword appears in first paragraph
        if len(sentences) > 0 and primary_keyword.lower() not in sentences[0].lower():
            # Insert keyword naturally
            first_sentence = sentences[0].strip()
            if first_sentence:
                sentences[0] = f"{first_sentence} featuring {primary_keyword}"
        
        return '.'.join(sentences)
    
    async def _generate_seo_title(self, content: str, keywords: List[str]) -> str:
        """Generate SEO-optimized title"""
        # Extract first sentence or use primary keyword
        first_sentence = content.split('.')[0].strip()
        
        if keywords:
            primary_keyword = keywords[0]
            if primary_keyword.lower() not in first_sentence.lower():
                return f"{primary_keyword}: {first_sentence[:50]}..."
        
        return first_sentence[:60] + "..." if len(first_sentence) > 60 else first_sentence
    
    async def _generate_meta_description(self, content: str, keywords: List[str]) -> str:
        """Generate meta description"""
        # Take first 150 characters and ensure keyword inclusion
        description = content.replace('\n', ' ').strip()[:150]
        
        if keywords and keywords[0].lower() not in description.lower():
            description = f"{keywords[0]} - {description}"
        
        return description[:160] + "..." if len(description) > 160 else description
    
    async def _generate_hashtags(self, keywords: List[str]) -> str:
        """Generate hashtags from keywords"""
        hashtags = []
        
        for keyword in keywords[:5]:  # Max 5 hashtags
            # Convert to hashtag format
            hashtag = '#' + ''.join(word.capitalize() for word in keyword.split())
            hashtags.append(hashtag)
        
        # Add generic hashtags
        hashtags.extend(['#Content', '#Quality', '#Professional'])
        
        return ' '.join(hashtags[:8])  # Max 8 hashtags
    
    async def _improve_content_structure(self, content: str) -> str:
        """Improve content structure"""
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 3:
            return content
        
        # Add subheadings every few paragraphs
        improved_content = []
        for i, paragraph in enumerate(paragraphs):
            if i > 0 and i % 3 == 0:
                improved_content.append(f"## Section {i//3 + 1}")
            improved_content.append(paragraph)
        
        return '\n\n'.join(improved_content)
    
    async def _generate_seo_metadata(
        self,
        content: str,
        keywords: List[str],
        content_type: str
    ) -> Dict[str, str]:
        """Generate SEO metadata"""
        title = await self._generate_seo_title(content, keywords)
        description = await self._generate_meta_description(content, keywords)
        
        metadata = {
            'title': title,
            'description': description,
            'keywords': ', '.join(keywords),
            'og:type': 'article' if content_type == 'blog' else 'website',
            'og:title': title,
            'og:description': description
        }
        
        return metadata
    
    async def _calculate_seo_score(
        self,
        content: str,
        keywords: List[str],
        metadata: Dict[str, str]
    ) -> float:
        """Calculate overall SEO score"""
        # Reanalyze optimized content
        analysis = await self._analyze_seo(content, keywords)
        
        # Calculate weighted score
        score = 0.0
        
        # Keyword score
        keyword_score = analysis['keyword_analysis'].get('overall_score', 0.0)
        score += keyword_score * self.seo_weights['keyword_density']
        
        # Content length score
        content_length_score = analysis.get('content_length_score', 0.0)
        score += content_length_score * self.seo_weights['content_length']
        
        # Readability score
        readability_score = analysis['readability'].get('readability_score', 0.0)
        score += readability_score * self.seo_weights['readability']
        
        # Structure score
        structure_score = analysis['structure'].get('structure_score', 0.0)
        score += structure_score * self.seo_weights['header_structure']
        
        # Link score
        link_score = analysis['links'].get('link_score', 0.0)
        score += link_score * self.seo_weights['internal_links']
        
        # Title optimization (check if keywords in title)
        title_score = 1.0 if any(kw.lower() in metadata.get('title', '').lower() for kw in keywords) else 0.5
        score += title_score * self.seo_weights['title_optimization']
        
        # Meta description score
        meta_score = 1.0 if metadata.get('description') else 0.0
        score += meta_score * self.seo_weights['meta_description']
        
        return min(1.0, max(0.0, score))
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        # Content length recommendations
        word_count = analysis.get('word_count', 0)
        if word_count < self.min_content_length:
            recommendations.append(f"Increase content length to at least {self.min_content_length} words (currently {word_count})")
        
        # Keyword recommendations
        keyword_analysis = analysis.get('keyword_analysis', {})
        for keyword, kw_data in keyword_analysis.items():
            if isinstance(kw_data, dict) and kw_data.get('density_score', 0) < 0.5:
                recommendations.append(f"Improve keyword density for '{keyword}' (currently {kw_data.get('density', 0):.2%})")
        
        # Readability recommendations
        readability = analysis.get('readability', {})
        if readability.get('readability_score', 0) < 0.7:
            recommendations.append("Improve content readability by using shorter sentences and simpler words")
        
        # Structure recommendations
        structure = analysis.get('structure', {})
        if structure.get('h1_count', 0) == 0:
            recommendations.append("Add a main heading (H1) to your content")
        if structure.get('h2_count', 0) < 2:
            recommendations.append("Add more subheadings (H2) to improve content structure")
        
        # Link recommendations
        links = analysis.get('links', {})
        if links.get('total_links', 0) < 3:
            recommendations.append("Add more internal and external links to improve SEO")
        
        return recommendations
