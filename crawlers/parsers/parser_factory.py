"""Parser Factory Module
====================

Factory pattern implementation for creating and managing parser instances.
Provides centralized access to all parser types with configuration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""
import asyncio
from typing import Dict, Any, List, Optional, Union, Type
from enum import Enum

from .exceptions import ParserFactoryError, UnsupportedParserTypeError
from .parser_config import ParserConfig

# Import all parser modules
from .platform_parsers import (
    BasePlatformParser, YouTubeParser, InstagramParser, TikTokParser,
    TwitterParser, FacebookParser, LinkedInParser, SpotifyParser
)
from .media_parsers import (
    BaseMediaParser, AudioParser, VideoParser, ImageParser,
    TextParser, DocumentParser
)
from .metadata_parsers import (
    BaseMetadataParser, OpenGraphParser, TwitterCardParser,
    SchemaOrgParser, DublinCoreParser, JsonLdParser, MicrodataParser
)
from .content_parsers import (
    BaseContentParser, HTMLContentParser, MarkdownParser,
    JSONContentParser, XMLContentParser, CSVContentParser,
    RSSParser, AtomParser, SitemapParser
)
from .analytics_parsers import (
    BaseAnalyticsParser, GoogleAnalyticsParser, FacebookInsightsParser,
    TwitterAnalyticsParser, YouTubeAnalyticsParser, InstagramInsightsParser,
    TikTokAnalyticsParser, SpotifyAnalyticsParser
)
from .engagement_parsers import (
    BaseEngagementParser, YouTubeEngagementParser, InstagramEngagementParser,
    FacebookEngagementParser, TwitterEngagementParser, TikTokEngagementParser,
    LinkedInEngagementParser
)
from .revenue_parsers import (
    BaseRevenueParser, YouTubeRevenueParser, SpotifyRoyaltiesParser,
    PatreonRevenueParser, TwitchRevenueParser, PayPalRevenueParser,
    StripeRevenueParser
)
from .fingerprint_parsers import (
    BaseFingerprintParser, AudioFingerprintParser, VideoFingerprintParser,
    ImageFingerprintParser, TextFingerprintParser
)


class ParserType(Enum):
    """Enumeration of available parser types"""    
    # Platform parsers
    PLATFORM_YOUTUBE = "platform_youtube"
    PLATFORM_INSTAGRAM = "platform_instagram"
    PLATFORM_TIKTOK = "platform_tiktok"
    PLATFORM_TWITTER = "platform_twitter"
    PLATFORM_FACEBOOK = "platform_facebook"
    PLATFORM_LINKEDIN = "platform_linkedin"
    PLATFORM_SPOTIFY = "platform_spotify"
    
    # Media parsers
    MEDIA_AUDIO = "media_audio"
    MEDIA_VIDEO = "media_video"
    MEDIA_IMAGE = "media_image"
    MEDIA_TEXT = "media_text"
    MEDIA_DOCUMENT = "media_document"
    
    # Metadata parsers
    METADATA_OPENGRAPH = "metadata_opengraph"
    METADATA_TWITTER_CARD = "metadata_twitter_card"
    METADATA_SCHEMA_ORG = "metadata_schema_org"
    METADATA_DUBLIN_CORE = "metadata_dublin_core"
    METADATA_JSON_LD = "metadata_json_ld"
    METADATA_MICRODATA = "metadata_microdata"
    
    # Content parsers
    CONTENT_HTML = "content_html"
    CONTENT_MARKDOWN = "content_markdown"
    CONTENT_JSON = "content_json"
    CONTENT_XML = "content_xml"
    CONTENT_CSV = "content_csv"
    CONTENT_RSS = "content_rss"
    CONTENT_ATOM = "content_atom"
    CONTENT_SITEMAP = "content_sitemap"
    
    # Analytics parsers
    ANALYTICS_GOOGLE = "analytics_google"
    ANALYTICS_FACEBOOK = "analytics_facebook"
    ANALYTICS_TWITTER = "analytics_twitter"
    ANALYTICS_YOUTUBE = "analytics_youtube"
    ANALYTICS_INSTAGRAM = "analytics_instagram"
    ANALYTICS_TIKTOK = "analytics_tiktok"
    ANALYTICS_SPOTIFY = "analytics_spotify"
    
    # Engagement parsers
    ENGAGEMENT_YOUTUBE = "engagement_youtube"
    ENGAGEMENT_INSTAGRAM = "engagement_instagram"
    ENGAGEMENT_FACEBOOK = "engagement_facebook"
    ENGAGEMENT_TWITTER = "engagement_twitter"
    ENGAGEMENT_TIKTOK = "engagement_tiktok"
    ENGAGEMENT_LINKEDIN = "engagement_linkedin"
    
    # Revenue parsers
    REVENUE_YOUTUBE = "revenue_youtube"
    REVENUE_SPOTIFY = "revenue_spotify"
    REVENUE_PATREON = "revenue_patreon"
    REVENUE_TWITCH = "revenue_twitch"
    REVENUE_PAYPAL = "revenue_paypal"
    REVENUE_STRIPE = "revenue_stripe"
    
    # Fingerprint parsers
    FINGERPRINT_AUDIO = "fingerprint_audio"
    FINGERPRINT_VIDEO = "fingerprint_video"
    FINGERPRINT_IMAGE = "fingerprint_image"
    FINGERPRINT_TEXT = "fingerprint_text"


class ParserCategory(Enum):
    """Categories of parsers for organization"""    
    PLATFORM = "platform"
    MEDIA = "media"
    METADATA = "metadata"
    CONTENT = "content"
    ANALYTICS = "analytics"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    FINGERPRINT = "fingerprint"


class ParserFactory:
    """Factory class for creating parser instances"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self._parser_registry = self._build_parser_registry()
        self._parser_cache = {}
        self._category_mapping = self._build_category_mapping()
    
    def _build_parser_registry(self) -> Dict[ParserType, Type]:
        """Build registry of parser types to classes"""        return {
            # Platform parsers
            ParserType.PLATFORM_YOUTUBE: YouTubeParser,
            ParserType.PLATFORM_INSTAGRAM: InstagramParser,
            ParserType.PLATFORM_TIKTOK: TikTokParser,
            ParserType.PLATFORM_TWITTER: TwitterParser,
            ParserType.PLATFORM_FACEBOOK: FacebookParser,
            ParserType.PLATFORM_LINKEDIN: LinkedInParser,
            ParserType.PLATFORM_SPOTIFY: SpotifyParser,
            
            # Media parsers
            ParserType.MEDIA_AUDIO: AudioParser,
            ParserType.MEDIA_VIDEO: VideoParser,
            ParserType.MEDIA_IMAGE: ImageParser,
            ParserType.MEDIA_TEXT: TextParser,
            ParserType.MEDIA_DOCUMENT: DocumentParser,
            
            # Metadata parsers
            ParserType.METADATA_OPENGRAPH: OpenGraphParser,
            ParserType.METADATA_TWITTER_CARD: TwitterCardParser,
            ParserType.METADATA_SCHEMA_ORG: SchemaOrgParser,
            ParserType.METADATA_DUBLIN_CORE: DublinCoreParser,
            ParserType.METADATA_JSON_LD: JsonLdParser,
            ParserType.METADATA_MICRODATA: MicrodataParser,
            
            # Content parsers
            ParserType.CONTENT_HTML: HTMLContentParser,
            ParserType.CONTENT_MARKDOWN: MarkdownParser,
            ParserType.CONTENT_JSON: JSONContentParser,
            ParserType.CONTENT_XML: XMLContentParser,
            ParserType.CONTENT_CSV: CSVContentParser,
            ParserType.CONTENT_RSS: RSSParser,
            ParserType.CONTENT_ATOM: AtomParser,
            ParserType.CONTENT_SITEMAP: SitemapParser,
            
            # Analytics parsers
            ParserType.ANALYTICS_GOOGLE: GoogleAnalyticsParser,
            ParserType.ANALYTICS_FACEBOOK: FacebookInsightsParser,
            ParserType.ANALYTICS_TWITTER: TwitterAnalyticsParser,
            ParserType.ANALYTICS_YOUTUBE: YouTubeAnalyticsParser,
            ParserType.ANALYTICS_INSTAGRAM: InstagramInsightsParser,
            ParserType.ANALYTICS_TIKTOK: TikTokAnalyticsParser,
            ParserType.ANALYTICS_SPOTIFY: SpotifyAnalyticsParser,
            
            # Engagement parsers
            ParserType.ENGAGEMENT_YOUTUBE: YouTubeEngagementParser,
            ParserType.ENGAGEMENT_INSTAGRAM: InstagramEngagementParser,
            ParserType.ENGAGEMENT_FACEBOOK: FacebookEngagementParser,
            ParserType.ENGAGEMENT_TWITTER: TwitterEngagementParser,
            ParserType.ENGAGEMENT_TIKTOK: TikTokEngagementParser,
            ParserType.ENGAGEMENT_LINKEDIN: LinkedInEngagementParser,
            
            # Revenue parsers
            ParserType.REVENUE_YOUTUBE: YouTubeRevenueParser,
            ParserType.REVENUE_SPOTIFY: SpotifyRoyaltiesParser,
            ParserType.REVENUE_PATREON: PatreonRevenueParser,
            ParserType.REVENUE_TWITCH: TwitchRevenueParser,
            ParserType.REVENUE_PAYPAL: PayPalRevenueParser,
            ParserType.REVENUE_STRIPE: StripeRevenueParser,
            
            # Fingerprint parsers
            ParserType.FINGERPRINT_AUDIO: AudioFingerprintParser,
            ParserType.FINGERPRINT_VIDEO: VideoFingerprintParser,
            ParserType.FINGERPRINT_IMAGE: ImageFingerprintParser,
            ParserType.FINGERPRINT_TEXT: TextFingerprintParser,
        }
    
    def _build_category_mapping(self) -> Dict[ParserCategory, List[ParserType]]:
        """Build mapping of categories to parser types"""        return {
            ParserCategory.PLATFORM: [
                ParserType.PLATFORM_YOUTUBE, ParserType.PLATFORM_INSTAGRAM,
                ParserType.PLATFORM_TIKTOK, ParserType.PLATFORM_TWITTER,
                ParserType.PLATFORM_FACEBOOK, ParserType.PLATFORM_LINKEDIN,
                ParserType.PLATFORM_SPOTIFY
            ],
            ParserCategory.MEDIA: [
                ParserType.MEDIA_AUDIO, ParserType.MEDIA_VIDEO,
                ParserType.MEDIA_IMAGE, ParserType.MEDIA_TEXT,
                ParserType.MEDIA_DOCUMENT
            ],
            ParserCategory.METADATA: [
                ParserType.METADATA_OPENGRAPH, ParserType.METADATA_TWITTER_CARD,
                ParserType.METADATA_SCHEMA_ORG, ParserType.METADATA_DUBLIN_CORE,
                ParserType.METADATA_JSON_LD, ParserType.METADATA_MICRODATA
            ],
            ParserCategory.CONTENT: [
                ParserType.CONTENT_HTML, ParserType.CONTENT_MARKDOWN,
                ParserType.CONTENT_JSON, ParserType.CONTENT_XML,
                ParserType.CONTENT_CSV, ParserType.CONTENT_RSS,
                ParserType.CONTENT_ATOM, ParserType.CONTENT_SITEMAP
            ],
            ParserCategory.ANALYTICS: [
                ParserType.ANALYTICS_GOOGLE, ParserType.ANALYTICS_FACEBOOK,
                ParserType.ANALYTICS_TWITTER, ParserType.ANALYTICS_YOUTUBE,
                ParserType.ANALYTICS_INSTAGRAM, ParserType.ANALYTICS_TIKTOK,
                ParserType.ANALYTICS_SPOTIFY
            ],
            ParserCategory.ENGAGEMENT: [
                ParserType.ENGAGEMENT_YOUTUBE, ParserType.ENGAGEMENT_INSTAGRAM,
                ParserType.ENGAGEMENT_FACEBOOK, ParserType.ENGAGEMENT_TWITTER,
                ParserType.ENGAGEMENT_TIKTOK, ParserType.ENGAGEMENT_LINKEDIN
            ],
            ParserCategory.REVENUE: [
                ParserType.REVENUE_YOUTUBE, ParserType.REVENUE_SPOTIFY,
                ParserType.REVENUE_PATREON, ParserType.REVENUE_TWITCH,
                ParserType.REVENUE_PAYPAL, ParserType.REVENUE_STRIPE
            ],
            ParserCategory.FINGERPRINT: [
                ParserType.FINGERPRINT_AUDIO, ParserType.FINGERPRINT_VIDEO,
                ParserType.FINGERPRINT_IMAGE, ParserType.FINGERPRINT_TEXT
            ]
        }
    
    def create_parser(self, parser_type: Union[ParserType, str], use_cache: bool = True) -> Any:
        """Create a parser instance"""        try:
            # Convert string to ParserType if necessary
            if isinstance(parser_type, str):
                try:
                    parser_type = ParserType(parser_type)
                except ValueError:
                    raise UnsupportedParserTypeError(
                        f"Unknown parser type: {parser_type}",
                        parser_type=parser_type
                    )
            
            # Check cache
            if use_cache and parser_type in self._parser_cache:
                return self._parser_cache[parser_type]
            
            # Get parser class
            parser_class = self._parser_registry.get(parser_type)
            if not parser_class:
                raise UnsupportedParserTypeError(
                    f"Parser not found for type: {parser_type.value}",
                    parser_type=parser_type.value
                )
            
            # Create parser instance
            parser_instance = parser_class(self.config)
            
            # Cache if requested
            if use_cache:
                self._parser_cache[parser_type] = parser_instance
            
            return parser_instance
            
        except Exception as e:
            if isinstance(e, (UnsupportedParserTypeError, ParserFactoryError)):
                raise
            
            raise ParserFactoryError(
                f"Failed to create parser: {str(e)}",
                parser_type=parser_type.value if isinstance(parser_type, ParserType) else str(parser_type)
            )
    
    def create_parsers_by_category(self, category: Union[ParserCategory, str], use_cache: bool = True) -> Dict[ParserType, Any]:
        """Create all parsers in a category"""        try:
            # Convert string to ParserCategory if necessary
            if isinstance(category, str):
                try:
                    category = ParserCategory(category)
                except ValueError:
                    raise ParserFactoryError(
                        f"Unknown parser category: {category}",
                        category=category
                    )
            
            # Get parser types for category
            parser_types = self._category_mapping.get(category, [])
            
            # Create parsers
            parsers = {}
            for parser_type in parser_types:
                try:
                    parser = self.create_parser(parser_type, use_cache)
                    parsers[parser_type] = parser
                except Exception as e:
                    # Log error but continue with other parsers
                    continue
            
            return parsers
            
        except Exception as e:
            if isinstance(e, ParserFactoryError):
                raise
            
            raise ParserFactoryError(
                f"Failed to create parsers for category: {str(e)}",
                category=category.value if isinstance(category, ParserCategory) else str(category)
            )
    
    def get_available_parser_types(self) -> List[ParserType]:
        """Get list of available parser types"""        return list(self._parser_registry.keys())
    
    def get_parser_types_by_category(self, category: Union[ParserCategory, str]) -> List[ParserType]:
        """Get parser types for a specific category"""        if isinstance(category, str):
            try:
                category = ParserCategory(category)
            except ValueError:
                return []
        
        return self._category_mapping.get(category, [])
    
    def get_categories(self) -> List[ParserCategory]:
        """Get list of available parser categories"""        return list(self._category_mapping.keys())
    
    def is_parser_type_supported(self, parser_type: Union[ParserType, str]) -> bool:
        """Check if a parser type is supported"""        if isinstance(parser_type, str):
            try:
                parser_type = ParserType(parser_type)
            except ValueError:
                return False
        
        return parser_type in self._parser_registry
    
    def clear_cache(self):
        """Clear the parser cache"""        self._parser_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached parsers"""        return {
            'cached_parsers': len(self._parser_cache),
            'cached_types': [parser_type.value for parser_type in self._parser_cache.keys()],
            'total_available': len(self._parser_registry)
        }
    
    def auto_detect_parser_type(self, content_info: Dict[str, Any]) -> Optional[ParserType]:
        """Auto-detect parser type based on content information"""        try:
            # Check for URL patterns (platform detection)
            if 'url' in content_info:
                url = content_info['url'].lower()
                
                if 'youtube.com' in url or 'youtu.be' in url:
                    return ParserType.PLATFORM_YOUTUBE
                elif 'instagram.com' in url:
                    return ParserType.PLATFORM_INSTAGRAM
                elif 'tiktok.com' in url:
                    return ParserType.PLATFORM_TIKTOK
                elif 'twitter.com' in url or 'x.com' in url:
                    return ParserType.PLATFORM_TWITTER
                elif 'facebook.com' in url:
                    return ParserType.PLATFORM_FACEBOOK
                elif 'linkedin.com' in url:
                    return ParserType.PLATFORM_LINKEDIN
                elif 'spotify.com' in url:
                    return ParserType.PLATFORM_SPOTIFY
            
            # Check for file extensions (media detection)
            if 'file_extension' in content_info:
                ext = content_info['file_extension'].lower()
                
                audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
                video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
                image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
                text_exts = ['.txt', '.md', '.rst']
                document_exts = ['.pdf', '.doc', '.docx', '.rtf']
                
                if ext in audio_exts:
                    return ParserType.MEDIA_AUDIO
                elif ext in video_exts:
                    return ParserType.MEDIA_VIDEO
                elif ext in image_exts:
                    return ParserType.MEDIA_IMAGE
                elif ext in text_exts:
                    return ParserType.MEDIA_TEXT
                elif ext in document_exts:
                    return ParserType.MEDIA_DOCUMENT
            
            # Check for MIME types
            if 'mime_type' in content_info:
                mime = content_info['mime_type'].lower()
                
                if mime.startswith('audio/'):
                    return ParserType.MEDIA_AUDIO
                elif mime.startswith('video/'):
                    return ParserType.MEDIA_VIDEO
                elif mime.startswith('image/'):
                    return ParserType.MEDIA_IMAGE
                elif mime.startswith('text/'):
                    if 'html' in mime:
                        return ParserType.CONTENT_HTML
                    elif 'xml' in mime:
                        return ParserType.CONTENT_XML
                    elif 'csv' in mime:
                        return ParserType.CONTENT_CSV
                    else:
                        return ParserType.MEDIA_TEXT
            
            # Check for content type hints
            if 'content_type' in content_info:
                content_type = content_info['content_type'].lower()
                
                if content_type == 'rss':
                    return ParserType.CONTENT_RSS
                elif content_type == 'atom':
                    return ParserType.CONTENT_ATOM
                elif content_type == 'sitemap':
                    return ParserType.CONTENT_SITEMAP
                elif content_type == 'json':
                    return ParserType.CONTENT_JSON
                elif content_type == 'markdown':
                    return ParserType.CONTENT_MARKDOWN
            
            return None
            
        except Exception:
            return None
    
    def create_parser_pipeline(self, parser_types: List[Union[ParserType, str]], use_cache: bool = True) -> List[Any]:
        """Create a pipeline of parsers"""        try:
            pipeline = []
            
            for parser_type in parser_types:
                parser = self.create_parser(parser_type, use_cache)
                pipeline.append(parser)
            
            return pipeline
            
        except Exception as e:
            raise ParserFactoryError(
                f"Failed to create parser pipeline: {str(e)}",
                pipeline_types=[pt.value if isinstance(pt, ParserType) else str(pt) for pt in parser_types]
            )
    
    def get_parser_info(self, parser_type: Union[ParserType, str]) -> Dict[str, Any]:
        """Get information about a parser type"""        try:
            if isinstance(parser_type, str):
                parser_type = ParserType(parser_type)
            
            parser_class = self._parser_registry.get(parser_type)
            if not parser_class:
                return {}
            
            # Find category
            category = None
            for cat, types in self._category_mapping.items():
                if parser_type in types:
                    category = cat
                    break
            
            return {
                'parser_type': parser_type.value,
                'parser_class': parser_class.__name__,
                'category': category.value if category else None,
                'module': parser_class.__module__,
                'is_cached': parser_type in self._parser_cache,
                'supported': True
            }
            
        except Exception:
            return {
                'parser_type': str(parser_type),
                'supported': False
            }
