"""Schema Markup Generator
Automated generation of schema.org structured data for enhanced SEO.

Features:
- Comprehensive schema type support
- Business-specific schema optimization
- Multi-format output (JSON-LD, Microdata, RDFa)
- Validation and error checking
- Creator-focused schema types

Author: Fahed Mlaiel (mlaiel@live.de)
Technical SEO + Structured Data expertise applied
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import uuid

logger = logging.getLogger(__name__)

class SchemaType(Enum):
    """Supported schema.org types."""
    PERSON = "Person"
    ORGANIZATION = "Organization"
    LOCAL_BUSINESS = "LocalBusiness"
    PRODUCT = "Product"
    SERVICE = "Service"
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    NEWS_ARTICLE = "NewsArticle"
    VIDEO_OBJECT = "VideoObject"
    AUDIO_OBJECT = "AudioObject"
    MUSIC_RECORDING = "MusicRecording"
    MUSIC_ALBUM = "MusicAlbum"
    MUSIC_PLAYLIST = "MusicPlaylist"
    PODCAST_EPISODE = "PodcastEpisode"
    PODCAST_SERIES = "PodcastSeries"
    EVENT = "Event"
    REVIEW = "Review"
    RATING = "Rating"
    CREATIVE_WORK = "CreativeWork"
    WEBSITE = "WebSite"
    WEB_PAGE = "WebPage"
    BREADCRUMB_LIST = "BreadcrumbList"
    FAQ_PAGE = "FAQPage"
    HOW_TO = "HowTo"
    RECIPE = "Recipe"
    COURSE = "Course"
    LEARNING_RESOURCE = "LearningResource"

class OutputFormat(Enum):
    """Schema markup output formats."""
    JSON_LD = "json-ld"
    MICRODATA = "microdata"
    RDFA = "rdfa"

@dataclass
class SchemaProperty:
    """Schema property definition."""
    name: str
    value: Any
    required: bool = False
    schema_type: Optional[str] = None

@dataclass
class SchemaValidationResult:
    """Schema validation result."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: float = 0.0

@dataclass
class SchemaGenerationConfig:
    """Configuration for schema generation."""
    primary_type: SchemaType
    output_format: OutputFormat = OutputFormat.JSON_LD
    include_context: bool = True
    validate_output: bool = True
    business_type: str = "general"
    language: str = "en"
    region: str = "US"
    currency: str = "USD"

class SchemaMarkupGenerator:
    """Advanced schema markup generation engine."""
    
    def __init__(self):
        """Initialize the Schema Markup Generator."""
        self.schema_context = "https://schema.org"
        self.property_mappings = self._load_property_mappings()
        self.validation_rules = self._load_validation_rules()
        self.business_schemas = self._load_business_specific_schemas()
        
    def _load_property_mappings(self) -> Dict[SchemaType, Dict[str, Any]]:
        """Load property mappings for each schema type."""
        return {
            SchemaType.PERSON: {
                "required": ["name"],
                "recommended": ["url", "image", "jobTitle", "worksFor", "sameAs"],
                "optional": ["description", "birthDate", "nationality", "knows", "alumniOf"]
            },
            SchemaType.ORGANIZATION: {
                "required": ["name"],
                "recommended": ["url", "logo", "contactPoint", "address", "sameAs"],
                "optional": ["description", "foundingDate", "founder", "employee", "member"]
            },
            SchemaType.LOCAL_BUSINESS: {
                "required": ["name", "address"],
                "recommended": ["telephone", "url", "openingHours", "priceRange"],
                "optional": ["description", "image", "review", "aggregateRating", "paymentAccepted"]
            },
            SchemaType.PRODUCT: {
                "required": ["name"],
                "recommended": ["image", "description", "brand", "offers"],
                "optional": ["sku", "gtin", "review", "aggregateRating", "category"]
            },
            SchemaType.ARTICLE: {
                "required": ["headline", "author", "datePublished"],
                "recommended": ["image", "publisher", "dateModified"],
                "optional": ["wordCount", "keywords", "articleSection", "articleBody"]
            },
            SchemaType.BLOG_POSTING: {
                "required": ["headline", "author", "datePublished"],
                "recommended": ["image", "publisher", "dateModified", "mainEntityOfPage"],
                "optional": ["wordCount", "keywords", "blogPost", "comment"]
            },
            SchemaType.VIDEO_OBJECT: {
                "required": ["name", "description", "thumbnailUrl", "uploadDate"],
                "recommended": ["duration", "contentUrl", "embedUrl", "publisher"],
                "optional": ["transcript", "caption", "genre", "director", "actor"]
            },
            SchemaType.AUDIO_OBJECT: {
                "required": ["name", "description", "contentUrl"],
                "recommended": ["duration", "encodingFormat", "publisher"],
                "optional": ["transcript", "genre", "creator", "isPartOf"]
            },
            SchemaType.MUSIC_RECORDING: {
                "required": ["name", "byArtist"],
                "recommended": ["duration", "inAlbum", "genre", "datePublished"],
                "optional": ["isrcCode", "recordingOf", "producer", "recordLabel"]
            },
            SchemaType.MUSIC_ALBUM: {
                "required": ["name", "byArtist"],
                "recommended": ["numTracks", "datePublished", "genre"],
                "optional": ["albumProductionType", "albumReleaseType", "recordLabel"]
            },
            SchemaType.PODCAST_EPISODE: {
                "required": ["name", "description", "url"],
                "recommended": ["duration", "partOfSeries", "episodeNumber", "datePublished"],
                "optional": ["transcript", "timeRequired", "associatedMedia"]
            },
            SchemaType.EVENT: {
                "required": ["name", "startDate"],
                "recommended": ["location", "description", "organizer"],
                "optional": ["endDate", "offers", "performer", "attendee", "doorTime"]
            },
            SchemaType.REVIEW: {
                "required": ["reviewBody", "author", "itemReviewed"],
                "recommended": ["reviewRating", "datePublished"],
                "optional": ["publisher", "positiveNotes", "negativeNotes"]
            },
            SchemaType.FAQ_PAGE: {
                "required": ["mainEntity"],
                "recommended": ["name", "description"],
                "optional": ["breadcrumb", "lastReviewed", "author"]
            },
            SchemaType.HOW_TO: {
                "required": ["name", "step"],
                "recommended": ["description", "image", "totalTime"],
                "optional": ["tool", "supply", "yield", "estimatedCost"]
            },
            SchemaType.COURSE: {
                "required": ["name", "description", "provider"],
                "recommended": ["courseCode", "numberOfCredits", "timeRequired"],
                "optional": ["coursePrerequisites", "educationalCredentialAwarded", "offers"]
            }
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for schema properties."""
        return {
            "url_fields": ["url", "sameAs", "logo", "image", "contentUrl", "embedUrl"],
            "date_fields": ["datePublished", "dateModified", "startDate", "endDate", "birthDate"],
            "email_fields": ["email"],
            "phone_fields": ["telephone", "faxNumber"],
            "required_for_rich_results": {
                SchemaType.ARTICLE: ["headline", "image", "datePublished", "author"],
                SchemaType.PRODUCT: ["name", "image", "offers"],
                SchemaType.EVENT: ["name", "startDate", "location"],
                SchemaType.LOCAL_BUSINESS: ["name", "address", "telephone"]
            }
        }
    
    def _load_business_specific_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load business-specific schema configurations."""
        return {
            "musician": {
                "primary_schemas": [SchemaType.PERSON, SchemaType.MUSIC_RECORDING, SchemaType.MUSIC_ALBUM],
                "properties": {
                    "jobTitle": "Musician",
                    "@type": ["Person", "MusicGroup"],
                    "genre": "music_genre",
                    "recordLabel": "record_label"
                }
            },
            "podcaster": {
                "primary_schemas": [SchemaType.PERSON, SchemaType.PODCAST_SERIES, SchemaType.PODCAST_EPISODE],
                "properties": {
                    "jobTitle": "Podcaster",
                    "creator": "person_reference",
                    "partOfSeries": "podcast_series"
                }
            },
            "blogger": {
                "primary_schemas": [SchemaType.PERSON, SchemaType.BLOG_POSTING, SchemaType.WEBSITE],
                "properties": {
                    "jobTitle": "Blogger",
                    "author": "person_reference",
                    "publisher": "organization_reference"
                }
            },
            "photographer": {
                "primary_schemas": [SchemaType.PERSON, SchemaType.CREATIVE_WORK, SchemaType.PRODUCT],
                "properties": {
                    "jobTitle": "Photographer",
                    "creator": "person_reference",
                    "artform": "Photography"
                }
            },
            "video_creator": {
                "primary_schemas": [SchemaType.PERSON, SchemaType.VIDEO_OBJECT, SchemaType.CREATIVE_WORK],
                "properties": {
                    "jobTitle": "Content Creator",
                    "creator": "person_reference",
                    "director": "person_reference"
                }
            },
            "local_business": {
                "primary_schemas": [SchemaType.LOCAL_BUSINESS, SchemaType.ORGANIZATION],
                "properties": {
                    "priceRange": "$$",
                    "paymentAccepted": ["Cash", "Credit Card"],
                    "openingHours": "business_hours"
                }
            },
            "ecommerce": {
                "primary_schemas": [SchemaType.PRODUCT, SchemaType.ORGANIZATION, SchemaType.REVIEW],
                "properties": {
                    "brand": "brand_reference",
                    "offers": "offer_object",
                    "aggregateRating": "rating_object"
                }
            }
        }
    
    async def generate_schema(
        self,
        data: Dict[str, Any],
        config: SchemaGenerationConfig
    ) -> Dict[str, Any]:
        """Generate schema markup from provided data.
        
        Args:
            data: Input data for schema generation
            config: Generation configuration
            
        Returns:
            Generated schema markup
        """
        try:
            # Create base schema structure
            schema = self._create_base_schema(config)
            
            # Add properties based on schema type
            schema = await self._populate_schema_properties(schema, data, config)
            
            # Add business-specific enhancements
            schema = self._enhance_for_business_type(schema, config.business_type)
            
            # Add SEO enhancements
            schema = self._add_seo_enhancements(schema, data, config)
            
            # Validate schema if requested
            if config.validate_output:
                validation = await self._validate_schema(schema, config)
                if not validation.is_valid:
                    logger.warning(f"Schema validation issues: {validation.errors}")
            
            # Format output
            return self._format_output(schema, config.output_format)
            
        except Exception as e:
            logger.error(f"Error generating schema: {e}")
            raise
    
    def _create_base_schema(self, config: SchemaGenerationConfig) -> Dict[str, Any]:
        """Create base schema structure."""
        try:
            schema = {}
            
            if config.include_context:
                schema["@context"] = self.schema_context
            
            schema["@type"] = config.primary_type.value
            
            # Add unique identifier
            schema["@id"] = f"#{config.primary_type.value.lower()}-{uuid.uuid4().hex[:8]}"
            
            return schema
            
        except Exception as e:
            logger.error(f"Error creating base schema: {e}")
            return {}
    
    async def _populate_schema_properties(
        self,
        schema: Dict[str, Any],
        data: Dict[str, Any],
        config: SchemaGenerationConfig
    ) -> Dict[str, Any]:
        """Populate schema with properties from data."""
        try:
            schema_type = config.primary_type
            property_config = self.property_mappings.get(schema_type, {})
            
            # Add required properties
            for prop in property_config.get("required", []):
                if prop in data:
                    schema[prop] = self._format_property_value(prop, data[prop], config)
                else:
                    logger.warning(f"Required property '{prop}' missing for {schema_type.value}")
            
            # Add recommended properties
            for prop in property_config.get("recommended", []):
                if prop in data:
                    schema[prop] = self._format_property_value(prop, data[prop], config)
            
            # Add optional properties
            for prop in property_config.get("optional", []):
                if prop in data:
                    schema[prop] = self._format_property_value(prop, data[prop], config)
            
            # Add custom properties from data
            for key, value in data.items():
                if key not in schema and key.startswith("schema_"):
                    # Remove schema_ prefix for actual schema property
                    actual_key = key[7:]
                    schema[actual_key] = self._format_property_value(actual_key, value, config)
            
            return schema
            
        except Exception as e:
            logger.error(f"Error populating schema properties: {e}")
            return schema
    
    def _format_property_value(
        self,
        property_name: str,
        value: Any,
        config: SchemaGenerationConfig
    ) -> Any:
        """Format property value according to schema.org specifications."""
        try:
            validation_rules = self.validation_rules
            
            # URL fields
            if property_name in validation_rules["url_fields"]:
                if isinstance(value, str) and not value.startswith(('http://', 'https://')):
                    return f"https://{value}"
                return value
            
            # Date fields
            if property_name in validation_rules["date_fields"]:
                if isinstance(value, str):
                    # Try to parse and format as ISO 8601
                    try:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return dt.isoformat()
                    except:
                        return value
                elif isinstance(value, datetime):
                    return value.isoformat()
                return value
            
            # Array values
            if isinstance(value, list):
                return [self._format_property_value(property_name, item, config) for item in value]
            
            # Object values
            if isinstance(value, dict):
                if "@type" in value:
                    # Already a schema object
                    return value
                else:
                    # Convert to appropriate schema object
                    return self._convert_to_schema_object(property_name, value, config)
            
            # String values
            if isinstance(value, str):
                # Clean and format string
                return value.strip()
            
            return value
            
        except Exception as e:
            logger.error(f"Error formatting property value: {e}")
            return value
    
    def _convert_to_schema_object(
        self,
        property_name: str,
        value: Dict[str, Any],
        config: SchemaGenerationConfig
    ) -> Dict[str, Any]:
        """Convert data to appropriate schema object."""
        try:
            # Common object type mappings
            object_mappings = {
                "author": "Person",
                "publisher": "Organization",
                "creator": "Person",
                "organizer": "Organization",
                "location": "Place",
                "address": "PostalAddress",
                "contactPoint": "ContactPoint",
                "offers": "Offer",
                "review": "Review",
                "rating": "Rating",
                "aggregateRating": "AggregateRating",
                "geo": "GeoCoordinates",
                "openingHours": "OpeningHoursSpecification",
                "image": "ImageObject",
                "video": "VideoObject",
                "audio": "AudioObject"
            }
            
            schema_type = object_mappings.get(property_name, "Thing")
            
            schema_object = {
                "@type": schema_type,
                **value
            }
            
            return schema_object
            
        except Exception as e:
            logger.error(f"Error converting to schema object: {e}")
            return value
    
    def _enhance_for_business_type(
        self,
        schema: Dict[str, Any],
        business_type: str
    ) -> Dict[str, Any]:
        """Enhance schema for specific business types."""
        try:
            business_config = self.business_schemas.get(business_type.lower(), {})
            
            if not business_config:
                return schema
            
            # Add business-specific properties
            for prop, value in business_config.get("properties", {}).items():
                if prop not in schema:
                    schema[prop] = value
            
            # Add multiple types if specified
            if "@type" in business_config.get("properties", {}):
                schema["@type"] = business_config["properties"]["@type"]
            
            return schema
            
        except Exception as e:
            logger.error(f"Error enhancing for business type: {e}")
            return schema
    
    def _add_seo_enhancements(
        self,
        schema: Dict[str, Any],
        data: Dict[str, Any],
        config: SchemaGenerationConfig
    ) -> Dict[str, Any]:
        """Add SEO-specific enhancements to schema."""
        try:
            # Add breadcrumb if available
            if "breadcrumb" in data:
                schema["breadcrumb"] = self._create_breadcrumb_schema(data["breadcrumb"])
            
            # Add FAQ if available
            if "faq" in data:
                schema["mainEntity"] = self._create_faq_schema(data["faq"])
            
            # Add structured data for rich results
            schema = self._optimize_for_rich_results(schema, config)
            
            # Add social media links
            if "social_links" in data:
                schema["sameAs"] = data["social_links"]
            
            # Add performance metrics
            if "metrics" in data:
                schema = self._add_performance_metrics(schema, data["metrics"])
            
            return schema
            
        except Exception as e:
            logger.error(f"Error adding SEO enhancements: {e}")
            return schema
    
    def _create_breadcrumb_schema(self, breadcrumb_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create breadcrumb schema."""
        try:
            breadcrumb_list = {
                "@type": "BreadcrumbList",
                "itemListElement": []
            }
            
            for i, item in enumerate(breadcrumb_data):
                list_item = {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": item.get("name", ""),
                    "item": item.get("url", "")
                }
                breadcrumb_list["itemListElement"].append(list_item)
            
            return breadcrumb_list
            
        except Exception as e:
            logger.error(f"Error creating breadcrumb schema: {e}")
            return {}
    
    def _create_faq_schema(self, faq_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Create FAQ schema."""
        try:
            faq_items = []
            
            for item in faq_data:
                faq_item = {
                    "@type": "Question",
                    "name": item.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.get("answer", "")
                    }
                }
                faq_items.append(faq_item)
            
            return faq_items
            
        except Exception as e:
            logger.error(f"Error creating FAQ schema: {e}")
            return []
    
    def _optimize_for_rich_results(
        self,
        schema: Dict[str, Any],
        config: SchemaGenerationConfig
    ) -> Dict[str, Any]:
        """Optimize schema for Google rich results."""
        try:
            schema_type = config.primary_type
            required_for_rich = self.validation_rules.get("required_for_rich_results", {})
            
            if schema_type in required_for_rich:
                required_props = required_for_rich[schema_type]
                
                # Check and add missing required properties for rich results
                for prop in required_props:
                    if prop not in schema:
                        # Add default values for missing required properties
                        default_value = self._get_default_value_for_property(prop, schema_type)
                        if default_value:
                            schema[prop] = default_value
                            logger.info(f"Added default value for required property: {prop}")
            
            # Add structured data specific optimizations
            if schema_type == SchemaType.ARTICLE:
                # Ensure proper article structure
                if "mainEntityOfPage" not in schema:
                    schema["mainEntityOfPage"] = {
                        "@type": "WebPage",
                        "@id": schema.get("url", "#webpage")
                    }
            
            elif schema_type == SchemaType.PRODUCT:
                # Ensure proper product structure
                if "offers" in schema and isinstance(schema["offers"], dict):
                    # Ensure offer has required properties
                    offer = schema["offers"]
                    if "@type" not in offer:
                        offer["@type"] = "Offer"
                    if "availability" not in offer:
                        offer["availability"] = "https://schema.org/InStock"
                    if "priceValidUntil" not in offer and "price" in offer:
                        # Set price valid until one year from now
                        valid_until = datetime.now() + timedelta(days=365)
                        offer["priceValidUntil"] = valid_until.strftime("%Y-%m-%d")
            
            elif schema_type == SchemaType.LOCAL_BUSINESS:
                # Ensure proper local business structure
                if "address" in schema and isinstance(schema["address"], dict):
                    address = schema["address"]
                    if "@type" not in address:
                        address["@type"] = "PostalAddress"
            
            return schema
            
        except Exception as e:
            logger.error(f"Error optimizing for rich results: {e}")
            return schema
    
    def _get_default_value_for_property(
        self,
        property_name: str,
        schema_type: SchemaType
    ) -> Optional[Any]:
        """Get default value for a property to ensure rich results compliance."""
        defaults = {
            "image": "https://example.com/default-image.jpg",
            "author": {
                "@type": "Person",
                "name": "Author Name"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Publisher Name",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://example.com/logo.jpg"
                }
            },
            "datePublished": datetime.now().isoformat(),
            "headline": "Default Headline",
            "description": "Default description",
            "name": "Default Name"
        }
        
        return defaults.get(property_name)
    
    def _add_performance_metrics(
        self,
        schema: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add performance metrics to schema."""
        try:
            # Add Core Web Vitals if available
            if "core_web_vitals" in metrics:
                schema["performanceMetrics"] = {
                    "@type": "PerformanceMetrics",
                    "coreWebVitals": metrics["core_web_vitals"]
                }
            
            # Add engagement metrics
            if "engagement" in metrics:
                schema["interactionStatistic"] = {
                    "@type": "InteractionCounter",
                    "userInteractionCount": metrics["engagement"].get("total_interactions", 0)
                }
            
            return schema
            
        except Exception as e:
            logger.error(f"Error adding performance metrics: {e}")
            return schema
    
    async def _validate_schema(
        self,
        schema: Dict[str, Any],
        config: SchemaGenerationConfig
    ) -> SchemaValidationResult:
        """Validate generated schema."""
        try:
            errors = []
            warnings = []
            score = 1.0
            
            # Check required properties
            schema_type = config.primary_type
            property_config = self.property_mappings.get(schema_type, {})
            
            for required_prop in property_config.get("required", []):
                if required_prop not in schema:
                    errors.append(f"Missing required property: {required_prop}")
                    score -= 0.2
            
            # Check recommended properties
            for recommended_prop in property_config.get("recommended", []):
                if recommended_prop not in schema:
                    warnings.append(f"Missing recommended property: {recommended_prop}")
                    score -= 0.1
            
            # Validate URLs
            for field in self.validation_rules["url_fields"]:
                if field in schema:
                    url = schema[field]
                    if isinstance(url, str) and not self._is_valid_url(url):
                        errors.append(f"Invalid URL in field '{field}': {url}")
                        score -= 0.15
            
            # Validate dates
            for field in self.validation_rules["date_fields"]:
                if field in schema:
                    date_value = schema[field]
                    if isinstance(date_value, str) and not self._is_valid_date(date_value):
                        errors.append(f"Invalid date format in field '{field}': {date_value}")
                        score -= 0.1
            
            # Check for rich results compliance
            rich_required = self.validation_rules.get("required_for_rich_results", {}).get(schema_type, [])
            for rich_prop in rich_required:
                if rich_prop not in schema:
                    warnings.append(f"Missing property for rich results: {rich_prop}")
                    score -= 0.05
            
            score = max(score, 0.0)
            is_valid = len(errors) == 0
            
            return SchemaValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return SchemaValidationResult(is_valid=False, errors=[str(e)])
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def _is_valid_date(self, date_string: str) -> bool:
        """Validate date format."""
        try:
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def _format_output(
        self,
        schema: Dict[str, Any],
        output_format: OutputFormat
    ) -> Dict[str, Any]:
        """Format schema output according to specified format."""
        try:
            if output_format == OutputFormat.JSON_LD:
                return schema
            
            elif output_format == OutputFormat.MICRODATA:
                return self._convert_to_microdata(schema)
            
            elif output_format == OutputFormat.RDFA:
                return self._convert_to_rdfa(schema)
            
            else:
                return schema
                
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
            return schema
    
    def _convert_to_microdata(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON-LD schema to Microdata format."""
        try:
            # Simplified conversion for demonstration
            # In production, this would be more comprehensive
            microdata = {
                "format": "microdata",
                "itemscope": True,
                "itemtype": f"https://schema.org/{schema.get('@type', 'Thing')}",
                "properties": {}
            }
            
            for key, value in schema.items():
                if not key.startswith('@'):
                    microdata["properties"][key] = {
                        "itemprop": key,
                        "content": value
                    }
            
            return microdata
            
        except Exception as e:
            logger.error(f"Error converting to microdata: {e}")
            return schema
    
    def _convert_to_rdfa(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON-LD schema to RDFa format."""
        try:
            # Simplified conversion for demonstration
            # In production, this would be more comprehensive
            rdfa = {
                "format": "rdfa",
                "typeof": schema.get('@type', 'Thing'),
                "vocab": "https://schema.org/",
                "properties": {}
            }
            
            for key, value in schema.items():
                if not key.startswith('@'):
                    rdfa["properties"][key] = {
                        "property": key,
                        "content": value
                    }
            
            return rdfa
            
        except Exception as e:
            logger.error(f"Error converting to RDFa: {e}")
            return schema

    async def generate_multiple_schemas(
        self,
        data_list: List[Dict[str, Any]],
        configs: List[SchemaGenerationConfig]
    ) -> List[Dict[str, Any]]:
        """Generate multiple schemas in batch."""
        try:
            tasks = [
                self.generate_schema(data, config)
                for data, config in zip(data_list, configs)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error generating schema {i}: {result}")
                    valid_results.append({})
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch schema generation: {e}")
            return [{}] * len(data_list)

    def generate_schema_for_creator(
        self,
        creator_data: Dict[str, Any],
        creator_type: str = "general"
    ) -> Dict[str, Any]:
        """Generate optimized schema for content creators."""
        try:
            # Creator type specific configurations
            creator_configs = {
                "musician": SchemaGenerationConfig(
                    primary_type=SchemaType.PERSON,
                    business_type="musician"
                ),
                "podcaster": SchemaGenerationConfig(
                    primary_type=SchemaType.PERSON,
                    business_type="podcaster"
                ),
                "blogger": SchemaGenerationConfig(
                    primary_type=SchemaType.PERSON,
                    business_type="blogger"
                ),
                "photographer": SchemaGenerationConfig(
                    primary_type=SchemaType.PERSON,
                    business_type="photographer"
                ),
                "video_creator": SchemaGenerationConfig(
                    primary_type=SchemaType.PERSON,
                    business_type="video_creator"
                )
            }
            
            config = creator_configs.get(creator_type, SchemaGenerationConfig(
                primary_type=SchemaType.PERSON,
                business_type="general"
            ))
            
            # Add creator-specific enhancements
            enhanced_data = creator_data.copy()
            
            # Add social proof if available
            if "followers" in creator_data:
                enhanced_data["interactionStatistic"] = {
                    "@type": "InteractionCounter",
                    "interactionType": "https://schema.org/FollowAction",
                    "userInteractionCount": creator_data["followers"]
                }
            
            # Add content creation info
            if "content_count" in creator_data:
                enhanced_data["numberOfItems"] = creator_data["content_count"]
            
            return asyncio.run(self.generate_schema(enhanced_data, config))
            
        except Exception as e:
            logger.error(f"Error generating creator schema: {e}")
            return {}

    def generate_content_schema(
        self,
        content_data: Dict[str, Any],
        content_type: str = "article"
    ) -> Dict[str, Any]:
        """Generate optimized schema for content."""
        try:
            # Content type specific configurations
            content_configs = {
                "article": SchemaType.ARTICLE,
                "blog_post": SchemaType.BLOG_POSTING,
                "video": SchemaType.VIDEO_OBJECT,
                "audio": SchemaType.AUDIO_OBJECT,
                "music": SchemaType.MUSIC_RECORDING,
                "podcast": SchemaType.PODCAST_EPISODE,
                "product": SchemaType.PRODUCT,
                "event": SchemaType.EVENT,
                "review": SchemaType.REVIEW,
                "faq": SchemaType.FAQ_PAGE,
                "how_to": SchemaType.HOW_TO,
                "course": SchemaType.COURSE
            }
            
            schema_type = content_configs.get(content_type, SchemaType.ARTICLE)
            
            config = SchemaGenerationConfig(
                primary_type=schema_type,
                business_type="content"
            )
            
            return asyncio.run(self.generate_schema(content_data, config))
            
        except Exception as e:
            logger.error(f"Error generating content schema: {e}")
            return {}