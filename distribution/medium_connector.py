"""
Medium Platform Connector
========================

Enterprise-grade Medium API connector for Ainflue Distribution Platform.
Supports article publishing, story management, publication integration, and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
import hashlib
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import markdown

logger = logging.getLogger(__name__)

class MediumPublishStatus(Enum):
    """Medium publish status options"""
    PUBLIC = "public"
    DRAFT = "draft"
    UNLISTED = "unlisted"

class MediumContentFormat(Enum):
    """Medium content format options"""
    MARKDOWN = "markdown"
    HTML = "html"

class MediumLicense(Enum):
    """Medium license options"""
    ALL_RIGHTS_RESERVED = "all-rights-reserved"
    CC_40_BY = "cc-40-by"
    CC_40_BY_SA = "cc-40-by-sa"
    CC_40_BY_ND = "cc-40-by-nd"
    CC_40_BY_NC = "cc-40-by-nc"
    CC_40_BY_NC_ND = "cc-40-by-nc-nd"
    CC_40_BY_NC_SA = "cc-40-by-nc-sa"
    CC_40_ZERO = "cc-40-zero"
    PUBLIC_DOMAIN = "public-domain"

@dataclass
class MediumArticle:
    """Medium article data structure"""
    title: str
    content: str
    content_format: str = "markdown"
    tags: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    publish_status: str = "public"
    license: str = "all-rights-reserved"
    notify_followers: bool = True

@dataclass
class MediumPublication:
    """Medium publication data structure"""
    id: str
    name: str
    description: str
    url: str
    image_url: Optional[str] = None

@dataclass
class MediumUser:
    """Medium user data structure"""
    id: str
    username: str
    name: str
    url: str
    image_url: Optional[str] = None

class MediumConnector:
    """
    Enterprise Medium API Connector
    
    Provides comprehensive integration with Medium platform for:
    - Article publishing and management
    - Publication integration
    - User profile management
    - Content analytics and insights
    - SEO optimization for articles
    """
    
    def __init__(self, access_token: str):
        """
        Initialize Medium connector
        
        Args:
            access_token: Medium API access token
        """
        self.access_token = access_token
        self.base_url = "https://api.medium.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_info: Optional[MediumUser] = None
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = datetime.now()
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Medium and get user info
        
        Returns:
            bool: Authentication success status
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                )
            
            # Get user information
            response = await self._make_request('GET', '/me')
            
            if response and 'data' in response:
                user_data = response['data']
                self.user_info = MediumUser(
                    id=user_data['id'],
                    username=user_data['username'],
                    name=user_data['name'],
                    url=user_data['url'],
                    image_url=user_data.get('imageUrl')
                )
                logger.info(f"Successfully authenticated with Medium for user: {self.user_info.username}")
                return True
            else:
                logger.error("Medium authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Medium authentication error: {str(e)}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make authenticated API request with rate limiting
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Optional[Dict]: API response data
        """
        # Check rate limits
        if self.rate_limit_remaining <= 0:
            if datetime.now() < self.rate_limit_reset:
                wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            async with self.session.request(method, url, **kwargs) as response:
                # Update rate limiting info
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 1000))
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
                
                if response.status == 200 or response.status == 201:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Medium rate limit exceeded")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Medium API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Medium API request error: {str(e)}")
            return None
    
    async def publish_article(self, article: MediumArticle, publication_id: Optional[str] = None) -> Optional[str]:
        """
        Publish an article to Medium
        
        Args:
            article: Article data
            publication_id: Optional publication ID to publish to
            
        Returns:
            Optional[str]: Article URL if successful
        """
        try:
            if not self.user_info:
                await self.authenticate()
            
            # Prepare article data
            article_data = {
                'title': article.title,
                'contentFormat': article.content_format,
                'content': article.content,
                'publishStatus': article.publish_status,
                'license': article.license,
                'notifyFollowers': article.notify_followers
            }
            
            if article.tags:
                article_data['tags'] = article.tags[:5]  # Medium allows max 5 tags
            
            if article.canonical_url:
                article_data['canonicalUrl'] = article.canonical_url
            
            # Determine endpoint based on publication
            if publication_id:
                endpoint = f'/publications/{publication_id}/posts'
            else:
                endpoint = f'/users/{self.user_info.id}/posts'
            
            response = await self._make_request(
                'POST',
                endpoint,
                json=article_data
            )
            
            if response and 'data' in response:
                article_url = response['data']['url']
                logger.info(f"Successfully published article: {article.title}")
                return article_url
            else:
                logger.error(f"Failed to publish article: {article.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error publishing article: {str(e)}")
            return None
    
    async def get_user_publications(self) -> List[MediumPublication]:
        """
        Get user's publications
        
        Returns:
            List[MediumPublication]: List of publications
        """
        try:
            if not self.user_info:
                await self.authenticate()
            
            response = await self._make_request(
                'GET',
                f'/users/{self.user_info.id}/publications'
            )
            
            publications = []
            if response and 'data' in response:
                for pub_data in response['data']:
                    publication = MediumPublication(
                        id=pub_data['id'],
                        name=pub_data['name'],
                        description=pub_data['description'],
                        url=pub_data['url'],
                        image_url=pub_data.get('imageUrl')
                    )
                    publications.append(publication)
                
                logger.info(f"Retrieved {len(publications)} publications")
            
            return publications
            
        except Exception as e:
            logger.error(f"Error retrieving publications: {str(e)}")
            return []
    
    async def get_publication_contributors(self, publication_id: str) -> List[Dict]:
        """
        Get contributors for a publication
        
        Args:
            publication_id: Publication ID
            
        Returns:
            List[Dict]: List of contributors
        """
        try:
            response = await self._make_request(
                'GET',
                f'/publications/{publication_id}/contributors'
            )
            
            if response and 'data' in response:
                logger.info(f"Retrieved contributors for publication: {publication_id}")
                return response['data']
            else:
                logger.error(f"Failed to retrieve contributors for publication: {publication_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving contributors: {str(e)}")
            return []
    
    async def upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload an image to Medium
        
        Args:
            image_path: Path to image file
            
        Returns:
            Optional[str]: Image URL if successful
        """
        try:
            import aiofiles
            
            async with aiofiles.open(image_path, 'rb') as f:
                image_data = await f.read()
            
            # Create form data for image upload
            data = aiohttp.FormData()
            data.add_field('image', image_data,
                          filename=image_path.split('/')[-1],
                          content_type='image/jpeg')
            
            response = await self._make_request(
                'POST',
                '/images',
                data=data
            )
            
            if response and 'data' in response:
                image_url = response['data']['url']
                logger.info(f"Successfully uploaded image: {image_path}")
                return image_url
            else:
                logger.error(f"Failed to upload image: {image_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return None
    
    def _optimize_content_for_medium(self, content: str, title: str) -> str:
        """
        Optimize content for Medium platform
        
        Args:
            content: Article content
            title: Article title
            
        Returns:
            str: Optimized content
        """
        # Add engaging subtitle
        optimized = f"# {title}\n\n"
        
        # Add reading time estimation
        word_count = len(content.split())
        read_time = max(1, word_count // 200)  # Average reading speed
        optimized += f"*{read_time} min read*\n\n"
        
        # Optimize paragraphs for readability
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Break long paragraphs
                if len(para) > 500:
                    sentences = para.split('. ')
                    mid_point = len(sentences) // 2
                    para = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
                
                optimized += para + '\n\n'
        
        return optimized
    
    def _generate_seo_tags(self, content: str, custom_tags: List[str] = None) -> List[str]:
        """
        Generate SEO-optimized tags for Medium article
        
        Args:
            content: Article content
            custom_tags: Custom tags to include
            
        Returns:
            List[str]: Optimized tags
        """
        tags = []
        
        # Add custom tags first
        if custom_tags:
            tags.extend(custom_tags[:3])  # Limit custom tags
        
        # Common high-engagement tags based on content analysis
        content_lower = content.lower()
        
        tag_keywords = {
            'technology': ['tech', 'software', 'programming', 'code', 'development'],
            'startup': ['startup', 'entrepreneur', 'business', 'company'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'productivity': ['productivity', 'efficiency', 'workflow', 'habits'],
            'marketing': ['marketing', 'growth', 'sales', 'strategy'],
            'design': ['design', 'ui', 'ux', 'interface'],
            'data': ['data', 'analytics', 'statistics', 'insights']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if tag not in tags:
                    tags.append(tag)
                    if len(tags) >= 5:  # Medium limit
                        break
        
        return tags[:5]
    
    async def create_optimized_article(self, title: str, content: str, 
                                     custom_tags: List[str] = None,
                                     publication_id: Optional[str] = None) -> Optional[str]:
        """
        Create and publish an SEO-optimized article
        
        Args:
            title: Article title
            content: Article content
            custom_tags: Custom tags
            publication_id: Optional publication ID
            
        Returns:
            Optional[str]: Article URL if successful
        """
        try:
            # Optimize content
            optimized_content = self._optimize_content_for_medium(content, title)
            
            # Generate SEO tags
            seo_tags = self._generate_seo_tags(content, custom_tags)
            
            # Create article
            article = MediumArticle(
                title=title,
                content=optimized_content,
                content_format="markdown",
                tags=seo_tags,
                publish_status="public",
                notify_followers=True
            )
            
            # Publish article
            return await self.publish_article(article, publication_id)
            
        except Exception as e:
            logger.error(f"Error creating optimized article: {str(e)}")
            return None
    
    async def schedule_article(self, article: MediumArticle, publish_time: datetime) -> Optional[str]:
        """
        Schedule an article for future publication
        Note: Medium doesn't support native scheduling, so this saves as draft
        
        Args:
            article: Article data
            publish_time: Scheduled publish time
            
        Returns:
            Optional[str]: Draft article ID if successful
        """
        try:
            # Save as draft for now
            draft_article = MediumArticle(
                title=f"[SCHEDULED: {publish_time.isoformat()}] {article.title}",
                content=article.content,
                content_format=article.content_format,
                tags=article.tags,
                publish_status="draft",
                canonical_url=article.canonical_url,
                license=article.license,
                notify_followers=False
            )
            
            return await self.publish_article(draft_article)
            
        except Exception as e:
            logger.error(f"Error scheduling article: {str(e)}")
            return None
    
    async def get_article_stats(self, article_id: str) -> Optional[Dict]:
        """
        Get article statistics (Note: Limited by Medium API)
        
        Args:
            article_id: Article ID
            
        Returns:
            Optional[Dict]: Article statistics
        """
        try:
            # Medium API has limited analytics access
            # This would need to be implemented with web scraping or partner access
            logger.warning("Medium API has limited analytics access")
            return {
                'views': None,
                'reads': None,
                'claps': None,
                'comments': None,
                'note': 'Limited analytics access through public API'
            }
            
        except Exception as e:
            logger.error(f"Error retrieving article stats: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

# Usage example
async def main():
    """Example usage of MediumConnector"""
    async with MediumConnector(
        access_token="your_medium_access_token"
    ) as medium:
        
        # Get user publications
        publications = await medium.get_user_publications()
        print(f"Found {len(publications)} publications")
        
        # Create optimized article
        article_url = await medium.create_optimized_article(
            title="The Future of AI in Content Creation",
            content="""
            Artificial Intelligence is revolutionizing how we create and distribute content.
            From automated writing to intelligent distribution strategies, AI is changing everything.
            
            In this article, we'll explore the latest trends and what they mean for creators.
            """,
            custom_tags=["AI", "Content Creation", "Technology"]
        )
        print(f"Article published: {article_url}")

if __name__ == "__main__":
    asyncio.run(main())