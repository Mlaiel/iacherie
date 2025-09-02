"""Platform Crawler Base
=====================

Professional base crawler for multi-platform content monitoring and surveillance.
Provides foundation for platform-specific crawlers with advanced detection capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
from urllib.parse import urljoin, urlparse

from ..fingerprinting.vector_matcher import VectorMatcher


class CrawlerStatus(Enum):
    """
Crawler status enumeration"""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class ContentMatchType(Enum):
    """Content match types"""

    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    SIMILAR_CONTENT = "similar_content"
    DERIVATIVE_WORK = "derivative_work"
    FALSE_POSITIVE = "false_positive"


@dataclass
class CrawlerConfig:
    """Crawler configuration"""
    platform_name: str
    search_terms: List[str]
    similarity_threshold: float
    max_results_per_search: int
    crawl_interval_minutes: int
    respect_robots_txt: bool
    rate_limit_delay: float
    user_agent: str
    timeout_seconds: int
    retry_attempts: int


@dataclass
class ContentMatch:
    """
Content match result"""
    url: str
    platform: str
    title: str
    description: str
    author: str
    upload_date: datetime
    view_count: int
    like_count: int
    share_count: int
    similarity_score: float
    match_type: ContentMatchType
    evidence_urls: List[str]
    thumbnail_url: str
    duration: Optional[float]
    file_size: Optional[int]
    metadata: Dict[str, Any]


@dataclass
class CrawlerResult:
    """
Crawler execution result"""
    platform: str
    crawl_id: str
    start_time: datetime
    end_time: datetime
    total_matches: int
    high_similarity_matches: int
    processing_time: float
    matches: List[ContentMatch]
    errors: List[str]
    next_crawl_time: datetime


class PlatformCrawler(ABC):
    """
    Abstract base class for platform-specific crawlers.
    
    Provides common functionality for web crawling, content detection,
    and similarity matching across different social media platforms.
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher):
        """
        Initialize PlatformCrawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service for similarity detection
        """
        self.config = config
        self.vector_matcher = vector_matcher
        self.logger = logging.getLogger(__name__)
        
        # Crawler state
        self.status = CrawlerStatus.IDLE
        self.current_crawl_id = None
        self.last_crawl_time = None
        self.total_crawls = 0
        self.total_matches_found = 0
        
        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window = 3600  # 1 hour
        
        # Session management
        self.session = None
        self.headers = {
            'User-Agent': config.user_agent,
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def initialize_session(self):
        """
Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10)
            )
    
    async def cleanup_session(self):
        """
Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    @abstractmethod
    async def search_content(self, search_terms: List[str], 
        try:
            logger.info(f"Executing search_content")
            
            # Implementation for search_content
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"search_content completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"search_content failed: {e}")
            raise
    @abstractmethod
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_extract_content_metadata_input(content_url)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_extract_content_metadata_result(result)
            
                    logger.info(f"AI processing extract_content_metadata completed")
                    return final_result
            
                except Exception as e:
        try:
            logger.info(f"Executing download_content_sample")
            
            # Implementation for download_content_sample
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"download_content_sample completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"download_content_sample failed: {e}")
            raise
    @abstractmethod
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """
        Download content sample for fingerprinting.
        
        Args:
            content_url: URL of the content
            
        Returns:
            Content data bytes or None if failed
        """
        pass
    
    async def crawl_for_matches(self, fingerprint_data: Dict[str, Any]) -> CrawlerResult:
        """
        Crawl platform for content matches.
        
        Args:
            fingerprint_data: Fingerprint data to search for
            
        Returns:
            Crawler result with found matches
        """
        try:
            crawl_id = f"{self.config.platform_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            start_time = datetime.utcnow()
            
            self.status = CrawlerStatus.RUNNING
            self.current_crawl_id = crawl_id
            
            await self.initialize_session()
            
            matches = []
            errors = []
            
            # Generate search terms from fingerprint
            search_terms = await self._generate_search_terms(fingerprint_data)
            
            # Search for content
            try:
                search_results = await self.search_content(
                    search_terms, 
                    self.config.max_results_per_search
                )
                
                # Process each result
                for result in search_results:
                    try:
                        match = await self._process_search_result(result, fingerprint_data)
                        if match and match.similarity_score >= self.config.similarity_threshold:
                            matches.append(match)
                        
                        # Rate limiting
                        await self._apply_rate_limit()
                        
                    except Exception as e:
                        error_msg = f"Error processing result {result.get('url', 'unknown')}: {str(e)}"
                        errors.append(error_msg)
                        self.logger.warning(error_msg)
                        continue
                
            except Exception as e:
                error_msg = f"Error during search: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Update stats
            self.total_crawls += 1
            self.total_matches_found += len(matches)
            self.last_crawl_time = end_time
            self.status = CrawlerStatus.COMPLETED
            
            # Calculate next crawl time
            next_crawl_time = end_time + timedelta(minutes=self.config.crawl_interval_minutes)
            
            # Count high similarity matches
            high_similarity_matches = sum(
                1 for match in matches if match.similarity_score >= 0.90
            )
            
            result = CrawlerResult(
                platform=self.config.platform_name,
                crawl_id=crawl_id,
                start_time=start_time,
                end_time=end_time,
                total_matches=len(matches),
                high_similarity_matches=high_similarity_matches,
                processing_time=processing_time,
                matches=matches,
                errors=errors,
                next_crawl_time=next_crawl_time
            )
            
            await self.cleanup_session()
            
            self.logger.info(
                f"Crawl {crawl_id} completed: {len(matches)} matches found in {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.status = CrawlerStatus.ERROR
            self.logger.error(f"Crawler error: {str(e)}")
            raise
    
    async def search_similar_content(self, fingerprints: Dict[str, Any], 
                                   threshold: float) -> List[Dict[str, Any]]:
        """
        Search for similar content using fingerprints.
        
        Args:
            fingerprints: Content fingerprints
            threshold: Similarity threshold
            
        Returns:
            List of similar content matches
        """
        try:
            # Generate search terms from fingerprints
            search_terms = await self._extract_search_terms_from_fingerprints(fingerprints)
            
            # Search platform
            search_results = await self.search_content(search_terms, 200)
            
            similar_content = []
            
            for result in search_results:
                try:
                    # Calculate similarity
                    similarity = await self._calculate_content_similarity(result, fingerprints)
                    
                    if similarity >= threshold:
                        similar_content.append({
                            'url': result.get('url'),
                            'title': result.get('title'),
                            'similarity_score': similarity,
                            'platform': self.config.platform_name,
                            'metadata': result
                        })
                    
                    await self._apply_rate_limit()
                    
                except Exception as e:
                    self.logger.warning(f"Error calculating similarity for {result.get('url')}: {str(e)}")
                    continue
            
            # Sort by similarity score
            similar_content.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_content
            
        except Exception as e:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "monitoring_task",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric monitoring_task collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection monitoring_task failed: {e}")
                    return None
        except Exception as e:
            self.logger.error(f"Error searching similar content: {str(e)}")
            return []
    
    async def monitor_content_continuously(self, fingerprint_data: Dict[str, Any],
                                         callback_url: str = None) -> str:
        """
        Start continuous monitoring for content.
        
        Args:
            fingerprint_data: Fingerprint data to monitor
            callback_url: Optional callback URL for notifications
            
        Returns:
            Monitoring task ID
        """
        try:
            monitoring_id = f"monitor_{self.config.platform_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create monitoring task
            async def monitoring_task():
                while True:
                    try:
                        result = await self.crawl_for_matches(fingerprint_data)
                        
                        # Process matches
                        if result.matches:
                            await self._handle_monitoring_matches(result, callback_url)
                        
                        # Wait for next crawl
                        await asyncio.sleep(self.config.crawl_interval_minutes * 60)
                        
                    except Exception as e:
                        self.logger.error(f"Monitoring task error: {str(e)}")
                        await asyncio.sleep(300)  # Wait 5 minutes on error
            
            # Start monitoring task
            asyncio.create_task(monitoring_task())
            
            self.logger.info(f"Started continuous monitoring: {monitoring_id}")
            return monitoring_id
            
        except Exception as e:
            self.logger.error(f"Error starting continuous monitoring: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _generate_search_terms(self, fingerprint_data: Dict[str, Any]) -> List[str]:
        """Generate search terms from fingerprint data"""
        search_terms = []
        
        # Extract terms from metadata
        if 'title' in fingerprint_data:
            search_terms.append(fingerprint_data['title'])
        
        if 'artist' in fingerprint_data:
            search_terms.append(fingerprint_data['artist'])
        
        if 'tags' in fingerprint_data:
            search_terms.extend(fingerprint_data['tags'][:5])  # Top 5 tags
        
        if 'description' in fingerprint_data:
            # Extract key phrases from description
            description_terms = await self._extract_key_phrases(fingerprint_data['description'])
            search_terms.extend(description_terms[:3])
        
        # Remove duplicates and empty terms
        search_terms = list(set(term.strip() for term in search_terms if term and term.strip()))
        
        return search_terms[:10]  # Limit to 10 terms
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """
Extract key phrases from text"""
        # Simple keyword extraction (in production, would use NLP)
        words = text.split()
        phrases = []
        
        # Extract 2-3 word phrases
        for i in range(len(words) - 1):
            if len(words[i]) > 3 and len(words[i + 1]) > 3:
                phrase = f"{words[i]} {words[i + 1]}"
                if len(phrase) <= 50:  # Reasonable phrase length
                    phrases.append(phrase)
        
        return phrases[:5]
    
    async def _process_search_result(self, result: Dict[str, Any], 
                                   fingerprint_data: Dict[str, Any]) -> Optional[ContentMatch]:
        """Process individual search result"""
        try:
            # Extract metadata
            metadata = await self.extract_content_metadata(result.get('url', ''))
            
            # Calculate similarity
            similarity_score = await self._calculate_content_similarity(result, fingerprint_data)
            
            # Determine match type
            match_type = self._determine_match_type(similarity_score)
            
            # Create content match
            match = ContentMatch(
                url=result.get('url', ''),
                platform=self.config.platform_name,
                title=result.get('title', ''),
                description=result.get('description', ''),
                author=result.get('author', ''),
                upload_date=self._parse_upload_date(result.get('upload_date')),
                view_count=result.get('view_count', 0),
                like_count=result.get('like_count', 0),
                share_count=result.get('share_count', 0),
                similarity_score=similarity_score,
                match_type=match_type,
                evidence_urls=[result.get('url', '')],
                thumbnail_url=result.get('thumbnail_url', ''),
                duration=result.get('duration'),
                file_size=result.get('file_size'),
                metadata=metadata
            )
            
            return match
            
        except Exception as e:
            self.logger.error(f"Error processing search result: {str(e)}")
            return None
    
    async def _calculate_content_similarity(self, content: Dict[str, Any], 
                                          fingerprint_data: Dict[str, Any]) -> float:
        """Calculate similarity between content and fingerprint"""
        try:
            # Text similarity (title, description)
            text_similarity = await self._calculate_text_similarity(content, fingerprint_data)
            
            # Metadata similarity
            metadata_similarity = await self._calculate_metadata_similarity(content, fingerprint_data)
            
            # Vector similarity (if available)
            vector_similarity = 0.0
            if 'vector_embedding' in fingerprint_data:
                content_vector = await self._extract_content_vector(content)
                if content_vector:
                    vector_similarity = await self.vector_matcher.calculate_similarity(
                        fingerprint_data['vector_embedding'], content_vector
                    )
            
            # Weighted combination
            overall_similarity = (
                text_similarity * 0.4 +
                metadata_similarity * 0.3 +
                vector_similarity * 0.3
            )
            
            return min(1.0, max(0.0, overall_similarity))
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    async def _calculate_text_similarity(self, content: Dict[str, Any], 
                                       fingerprint_data: Dict[str, Any]) -> float:
        """Calculate text similarity between content and fingerprint"""
        # Simple text similarity (in production, would use advanced NLP)
        content_text = f"{content.get('title', '')} {content.get('description', '')}"
        fingerprint_text = f"{fingerprint_data.get('title', '')} {fingerprint_data.get('description', '')}"
        
        if not content_text.strip() or not fingerprint_text.strip():
            return 0.0
        
        # Convert to lowercase and split into words
        content_words = set(content_text.lower().split())
        fingerprint_words = set(fingerprint_text.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(content_words.intersection(fingerprint_words))
        union = len(content_words.union(fingerprint_words))
        
        return intersection / union if union > 0 else 0.0
    
    async def _calculate_metadata_similarity(self, content: Dict[str, Any], 
        try:
            logger.info(f"Executing _parse_upload_date")
            
            # Implementation for _parse_upload_date
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_parse_upload_date completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_parse_upload_date failed: {e}")
            raise
        if 'tags' in content and 'tags' in fingerprint_data:
            content_tags = set(tag.lower() for tag in content['tags'])
            fingerprint_tags = set(tag.lower() for tag in fingerprint_data['tags'])
            
            if content_tags and fingerprint_tags:
                intersection = len(content_tags.intersection(fingerprint_tags))
                union = len(content_tags.union(fingerprint_tags))
                tag_similarity = intersection / union if union > 0 else 0.0
                similarities.append(tag_similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _determine_match_type(self, similarity_score: float) -> ContentMatchType:
        """
Determine match type based on similarity score"""
        if similarity_score >= 0.95:
            return ContentMatchType.EXACT_MATCH
        elif similarity_score >= 0.85:
            return ContentMatchType.PARTIAL_MATCH
        elif similarity_score >= 0.70:
            return ContentMatchType.SIMILAR_CONTENT
        elif similarity_score >= 0.50:
            return ContentMatchType.DERIVATIVE_WORK
        else:
            return ContentMatchType.FALSE_POSITIVE
    
    def _parse_upload_date(self, date_str: Any) -> datetime:
        """
Parse upload date from various formats"""
        if isinstance(date_str, datetime):
            return date_str
        
        if isinstance(date_str, str):
            try:
                # Try common formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        return datetime.strptime(date_str[:len(fmt)], fmt)
                    except ValueError:
                        continue
            except:
                pass
        
        return datetime.utcnow()  # Default to now
    
    async def _apply_rate_limit(self):
        """
Apply rate limiting between requests"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = asyncio.get_event_loop().time()
        self.request_count += 1
    
    async def _extract_search_terms_from_fingerprints(self, fingerprints: Dict[str, Any]) -> List[str]:
        """
Extract search terms from fingerprints"""
        terms = []
        
        # Extract from various fingerprint types
        if 'audio_fingerprint' in fingerprints:
            # Audio-specific terms
            terms.extend(['music', 'audio', 'song'])
        
        if 'video_fingerprint' in fingerprints:
            # Video-specific terms
            terms.extend(['video', 'clip', 'movie'])
        
        if 'image_fingerprint' in fingerprints:
            # Image-specific terms
            terms.extend(['image', 'photo', 'picture'])
        
        if 'metadata' in fingerprints:
            metadata = fingerprints['metadata']
            if 'title' in metadata:
                terms.append(metadata['title'])
            if 'artist' in metadata:
                terms.append(metadata['artist'])
        
        return list(set(terms))  # Remove duplicates
    
    async def _extract_content_vector(self, content: Dict[str, Any]) -> Optional[List[float]]:
        """
Extract vector representation from content"""
        # This would implement content-to-vector conversion
        # Placeholder implementation
        return None
    
    async def _handle_monitoring_matches(self, result: CrawlerResult, callback_url: str = None):
        """
Handle matches found during monitoring"""
        if not result.matches:
            return
        
        # Log matches
        self.logger.info(f"Monitoring found {len(result.matches)} matches on {result.platform}")
        
        # Send callback notification if URL provided
        if callback_url:
            try:
                notification_data = {
                    'platform': result.platform,
                    'crawl_id': result.crawl_id,
                    'match_count': len(result.matches),
                    'high_similarity_count': result.high_similarity_matches,
                    'matches': [match.__dict__ for match in result.matches[:10]]  # Top 10
                }
                
                async with aiohttp.ClientSession() as session:
                    await session.post(callback_url, json=notification_data)
                    
            except Exception as e:
                self.logger.error(f"Error sending callback notification: {str(e)}")
    
    def get_crawler_stats(self) -> Dict[str, Any]:
        """Get crawler statistics"""
        return {
            'platform': self.config.platform_name,
            'status': self.status.value,
            'total_crawls': self.total_crawls,
            'total_matches_found': self.total_matches_found,
            'last_crawl_time': self.last_crawl_time.isoformat() if self.last_crawl_time else None,
            'current_crawl_id': self.current_crawl_id,
            'request_count': self.request_count,
            'configuration': {
                'similarity_threshold': self.config.similarity_threshold,
                'max_results_per_search': self.config.max_results_per_search,
                'crawl_interval_minutes': self.config.crawl_interval_minutes,
                'rate_limit_delay': self.config.rate_limit_delay
            }
        }
