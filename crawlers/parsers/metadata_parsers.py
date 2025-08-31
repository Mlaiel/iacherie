"""Metadata Parsers Module
=======================

Specialized parsers for extracting metadata from various structured formats.
Handles Open Graph, Twitter Cards, Schema.org, Dublin Core, and other metadata standards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment

from .exceptions import MetadataParsingError, ValidationError
from .parser_config import ParserConfig


class BaseMetadataParser(ABC):
    """Abstract base class for metadata parsers"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
    
    @abstractmethod
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse metadata from HTML content"""
        pass
    
    @abstractmethod
    def get_parser_type(self) -> str:
        """Get the type of metadata this parser handles"""
        pass
    
    def _normalize_url(self, url: str, base_url: Optional[str] = None) -> str:
        """Normalize relative URLs to absolute URLs"""
        if not url:
            return url
        
        if url.startswith(('http://', 'https://')):
            return url
        
        if base_url:
            return urljoin(base_url, url)
        
        return url
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML entities
        import html
        text = html.unescape(text)
        
        return text


class OpenGraphParser(BaseMetadataParser):
    """Parser for Open Graph metadata"""
    
    def get_parser_type(self) -> str:
        return "open_graph"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse Open Graph metadata from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            og_data = {}
            
            # Find all Open Graph meta tags
            og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
            
            for tag in og_tags:
                property_name = tag.get('property', '')
                content = tag.get('content', '')
                
                if property_name and content:
                    # Remove 'og:' prefix
                    key = property_name[3:]
                    
                    # Handle special cases
                    if key in ['image', 'audio', 'video', 'url']:
                        content = self._normalize_url(content, base_url)
                    
                    # Handle array properties (image, video, audio can have multiple values)
                    if key in ['image', 'video', 'audio']:
                        if key not in og_data:
                            og_data[key] = []
                        if isinstance(og_data[key], list):
                            og_data[key].append(content)
                        else:
                            og_data[key] = [og_data[key], content]
                    else:
                        og_data[key] = self._clean_text(content)
            
            # Parse structured Open Graph data
            structured_data = self._parse_structured_og_data(og_data)
            
            return {
                'type': self.get_parser_type(),
                'data': og_data,
                'structured': structured_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"Open Graph parsing failed: {str(e)}",
                metadata_type="open_graph",
                parser_type="OpenGraphParser"
            )
    
    def _parse_structured_og_data(self, og_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Open Graph data into structured format"""
        structured = {
            'basic': {},
            'optional': {},
            'image': {},
            'video': {},
            'audio': {},
            'article': {},
            'book': {},
            'profile': {},
            'website': {}
        }
        
        # Basic required properties
        basic_props = ['title', 'type', 'image', 'url']
        for prop in basic_props:
            if prop in og_data:
                structured['basic'][prop] = og_data[prop]
        
        # Optional properties
        optional_props = ['description', 'determiner', 'locale', 'site_name']
        for prop in optional_props:
            if prop in og_data:
                structured['optional'][prop] = og_data[prop]
        
        # Image properties
        image_props = ['image:secure_url', 'image:type', 'image:width', 'image:height', 'image:alt']
        for prop in image_props:
            key = prop.replace('image:', '')
            if prop in og_data:
                structured['image'][key] = og_data[prop]
        
        # Video properties
        video_props = ['video:secure_url', 'video:type', 'video:width', 'video:height']
        for prop in video_props:
            key = prop.replace('video:', '')
            if prop in og_data:
                structured['video'][key] = og_data[prop]
        
        # Audio properties
        audio_props = ['audio:secure_url', 'audio:type']
        for prop in audio_props:
            key = prop.replace('audio:', '')
            if prop in og_data:
                structured['audio'][key] = og_data[prop]
        
        # Article properties
        article_props = [
            'article:published_time', 'article:modified_time', 'article:expiration_time',
            'article:author', 'article:section', 'article:tag'
        ]
        for prop in article_props:
            key = prop.replace('article:', '')
            if prop in og_data:
                structured['article'][key] = og_data[prop]
        
        # Book properties
        book_props = ['book:author', 'book:isbn', 'book:release_date', 'book:tag']
        for prop in book_props:
            key = prop.replace('book:', '')
            if prop in og_data:
                structured['book'][key] = og_data[prop]
        
        # Profile properties
        profile_props = ['profile:first_name', 'profile:last_name', 'profile:username', 'profile:gender']
        for prop in profile_props:
            key = prop.replace('profile:', '')
            if prop in og_data:
                structured['profile'][key] = og_data[prop]
        
        return structured


class TwitterCardParser(BaseMetadataParser):
    """Parser for Twitter Card metadata"""
    
    def get_parser_type(self) -> str:
        return "twitter_card"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse Twitter Card metadata from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            twitter_data = {}
            
            # Find all Twitter meta tags
            twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
            
            for tag in twitter_tags:
                name = tag.get('name', '')
                content = tag.get('content', '')
                
                if name and content:
                    # Remove 'twitter:' prefix
                    key = name[8:]
                    
                    # Handle URLs
                    if key in ['image', 'player', 'url']:
                        content = self._normalize_url(content, base_url)
                    
                    twitter_data[key] = self._clean_text(content)
            
            # Validate Twitter Card data
            card_type = twitter_data.get('card', '')
            validation_result = self._validate_twitter_card(twitter_data, card_type)
            
            return {
                'type': self.get_parser_type(),
                'data': twitter_data,
                'card_type': card_type,
                'validation': validation_result,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"Twitter Card parsing failed: {str(e)}",
                metadata_type="twitter_card",
                parser_type="TwitterCardParser"
            )
    
    def _validate_twitter_card(self, data: Dict[str, Any], card_type: str) -> Dict[str, Any]:
        """Validate Twitter Card data based on card type"""
        validation = {
            'is_valid': True,
            'missing_required': [],
            'missing_recommended': [],
            'errors': []
        }
        
        # Required fields for all cards
        required_fields = ['card']
        recommended_fields = ['site', 'creator']
        
        # Card type specific requirements
        if card_type == 'summary':
            required_fields.extend(['title', 'description'])
            recommended_fields.extend(['image'])
        elif card_type == 'summary_large_image':
            required_fields.extend(['title', 'description', 'image'])
        elif card_type == 'app':
            required_fields.extend(['app:name:iphone', 'app:id:iphone'])
        elif card_type == 'player':
            required_fields.extend(['title', 'description', 'player', 'player:width', 'player:height'])
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                validation['missing_required'].append(field)
                validation['is_valid'] = False
        
        # Check recommended fields
        for field in recommended_fields:
            if field not in data or not data[field]:
                validation['missing_recommended'].append(field)
        
        # Additional validations
        if 'image' in data:
            # Image should be absolute URL
            if not data['image'].startswith(('http://', 'https://')):
                validation['errors'].append('Image URL should be absolute')
        
        return validation


class SchemaOrgParser(BaseMetadataParser):
    """Parser for Schema.org structured data"""
    
    def get_parser_type(self) -> str:
        return "schema_org"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse Schema.org structured data from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            schema_data = {
                'json_ld': [],
                'microdata': [],
                'rdfa': []
            }
            
            # Parse JSON-LD
            schema_data['json_ld'] = await self._parse_json_ld(soup)
            
            # Parse Microdata
            schema_data['microdata'] = await self._parse_microdata(soup)
            
            # Parse RDFa
            schema_data['rdfa'] = await self._parse_rdfa(soup)
            
            return {
                'type': self.get_parser_type(),
                'data': schema_data,
                'total_items': len(schema_data['json_ld']) + len(schema_data['microdata']) + len(schema_data['rdfa']),
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"Schema.org parsing failed: {str(e)}",
                metadata_type="schema_org",
                parser_type="SchemaOrgParser"
            )
    
    async def _parse_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse JSON-LD structured data"""
        json_ld_data = []
        
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    
                    # Handle single object or array of objects
                    if isinstance(data, list):
                        json_ld_data.extend(data)
                    else:
                        json_ld_data.append(data)
                        
            except json.JSONDecodeError as e:
                # Log error but continue processing other scripts
                continue
        
        return json_ld_data
    
    async def _parse_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse Microdata structured data"""
        microdata_items = []
        
        # Find all elements with itemscope
        items = soup.find_all(attrs={'itemscope': True})
        
        for item in items:
            item_data = {
                'type': item.get('itemtype', ''),
                'properties': {}
            }
            
            # Find all properties within this item
            props = item.find_all(attrs={'itemprop': True})
            
            for prop in props:
                prop_name = prop.get('itemprop')
                
                # Get property value based on element type
                if prop.name in ['meta']:
                    prop_value = prop.get('content', '')
                elif prop.name in ['a', 'link']:
                    prop_value = prop.get('href', '')
                elif prop.name in ['img', 'audio', 'video', 'source']:
                    prop_value = prop.get('src', '')
                elif prop.name in ['time']:
                    prop_value = prop.get('datetime', prop.get_text(strip=True))
                else:
                    prop_value = prop.get_text(strip=True)
                
                # Handle multiple values for same property
                if prop_name in item_data['properties']:
                    if not isinstance(item_data['properties'][prop_name], list):
                        item_data['properties'][prop_name] = [item_data['properties'][prop_name]]
                    item_data['properties'][prop_name].append(prop_value)
                else:
                    item_data['properties'][prop_name] = prop_value
            
            if item_data['properties']:  # Only add if has properties
                microdata_items.append(item_data)
        
        return microdata_items
    
    async def _parse_rdfa(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse RDFa structured data"""
        rdfa_items = []
        
        # Find elements with RDFa attributes
        elements = soup.find_all(attrs={'typeof': True})
        
        for element in elements:
            item_data = {
                'type': element.get('typeof', ''),
                'about': element.get('about', ''),
                'properties': {}
            }
            
            # Find properties with 'property' attribute
            props = element.find_all(attrs={'property': True})
            
            for prop in props:
                prop_name = prop.get('property')
                
                # Get property value
                if prop.get('content'):
                    prop_value = prop.get('content')
                elif prop.get('href'):
                    prop_value = prop.get('href')
                elif prop.get('src'):
                    prop_value = prop.get('src')
                else:
                    prop_value = prop.get_text(strip=True)
                
                item_data['properties'][prop_name] = prop_value
            
            if item_data['properties']:  # Only add if has properties
                rdfa_items.append(item_data)
        
        return rdfa_items


class DublinCoreParser(BaseMetadataParser):
    """Parser for Dublin Core metadata"""
    
    def get_parser_type(self) -> str:
        return "dublin_core"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse Dublin Core metadata from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            dc_data = {}
            
            # Dublin Core elements
            dc_elements = [
                'title', 'creator', 'subject', 'description', 'publisher',
                'contributor', 'date', 'type', 'format', 'identifier',
                'source', 'language', 'relation', 'coverage', 'rights'
            ]
            
            # Find Dublin Core meta tags
            for element in dc_elements:
                # Try different naming conventions
                selectors = [
                    f'meta[name="dc.{element}"]',
                    f'meta[name="DC.{element}"]',
                    f'meta[name="dcterms.{element}"]',
                    f'meta[name="DCTERMS.{element}"]'
                ]
                
                for selector in selectors:
                    tags = soup.select(selector)
                    if tags:
                        values = [self._clean_text(tag.get('content', '')) for tag in tags if tag.get('content')]
                        if values:
                            if len(values) == 1:
                                dc_data[element] = values[0]
                            else:
                                dc_data[element] = values
                        break
            
            return {
                'type': self.get_parser_type(),
                'data': dc_data,
                'elements_found': len(dc_data),
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"Dublin Core parsing failed: {str(e)}",
                metadata_type="dublin_core",
                parser_type="DublinCoreParser"
            )


class MetaTagParser(BaseMetadataParser):
    """Parser for standard HTML meta tags"""
    
    def get_parser_type(self) -> str:
        return "meta_tags"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse standard meta tags from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            meta_data = {
                'basic': {},
                'seo': {},
                'viewport': {},
                'robots': {},
                'other': {}
            }
            
            # Parse title
            title_tag = soup.find('title')
            if title_tag:
                meta_data['basic']['title'] = self._clean_text(title_tag.get_text())
            
            # Parse meta tags
            meta_tags = soup.find_all('meta')
            
            for tag in meta_tags:
                name = tag.get('name', '').lower()
                content = tag.get('content', '')
                http_equiv = tag.get('http-equiv', '').lower()
                
                if not content:
                    continue
                
                content = self._clean_text(content)
                
                # Categorize meta tags
                if name in ['description', 'keywords', 'author']:
                    meta_data['seo'][name] = content
                elif name == 'viewport':
                    meta_data['viewport'] = self._parse_viewport(content)
                elif name == 'robots':
                    meta_data['robots'] = self._parse_robots(content)
                elif name in ['generator', 'application-name', 'theme-color']:
                    meta_data['basic'][name] = content
                elif http_equiv:
                    meta_data['other'][f'http-equiv-{http_equiv}'] = content
                elif name:
                    meta_data['other'][name] = content
            
            return {
                'type': self.get_parser_type(),
                'data': meta_data,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"Meta tag parsing failed: {str(e)}",
                metadata_type="meta_tags",
                parser_type="MetaTagParser"
            )
    
    def _parse_viewport(self, content: str) -> Dict[str, str]:
        """Parse viewport meta tag content"""
        viewport = {}
        
        parts = [part.strip() for part in content.split(',')]
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                viewport[key.strip()] = value.strip()
            else:
                viewport[part] = True
        
        return viewport
    
    def _parse_robots(self, content: str) -> Dict[str, bool]:
        """Parse robots meta tag content"""
        robots = {}
        
        directives = [directive.strip().lower() for directive in content.split(',')]
        
        for directive in directives:
            if directive in ['index', 'noindex', 'follow', 'nofollow', 
                           'archive', 'noarchive', 'snippet', 'nosnippet',
                           'translate', 'notranslate', 'imageindex', 'noimageindex']:
                robots[directive] = True
            elif directive.startswith('max-snippet:'):
                robots['max_snippet'] = directive.split(':')[1]
            elif directive.startswith('max-image-preview:'):
                robots['max_image_preview'] = directive.split(':')[1]
            elif directive.startswith('max-video-preview:'):
                robots['max_video_preview'] = directive.split(':')[1]
        
        return robots


class JsonLdParser(BaseMetadataParser):
    """Specialized parser for JSON-LD structured data"""
    
    def get_parser_type(self) -> str:
        return "json_ld"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse JSON-LD structured data with detailed analysis"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            json_ld_data = []
            schemas_found = {}
            
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script_idx, script in enumerate(scripts):
                try:
                    if script.string:
                        data = json.loads(script.string)
                        
                        # Handle single object or array
                        items = data if isinstance(data, list) else [data]
                        
                        for item in items:
                            # Analyze schema type
                            schema_type = self._extract_schema_type(item)
                            if schema_type:
                                schemas_found[schema_type] = schemas_found.get(schema_type, 0) + 1
                            
                            # Process URLs
                            processed_item = self._process_json_ld_urls(item, base_url)
                            
                            json_ld_data.append({
                                'script_index': script_idx,
                                'schema_type': schema_type,
                                'data': processed_item
                            })
                            
                except json.JSONDecodeError as e:
                    json_ld_data.append({
                        'script_index': script_idx,
                        'error': f"JSON parsing error: {str(e)}",
                        'raw_content': script.string[:200] + '...' if len(script.string) > 200 else script.string
                    })
            
            return {
                'type': self.get_parser_type(),
                'data': json_ld_data,
                'schemas_found': schemas_found,
                'total_scripts': len(scripts),
                'valid_scripts': len([item for item in json_ld_data if 'error' not in item]),
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"JSON-LD parsing failed: {str(e)}",
                metadata_type="json_ld",
                parser_type="JsonLdParser"
            )
    
    def _extract_schema_type(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract schema type from JSON-LD data"""
        if '@type' in data:
            schema_type = data['@type']
            if isinstance(schema_type, list):
                return schema_type[0] if schema_type else None
            return schema_type
        
        # Check for nested types
        for value in data.values():
            if isinstance(value, dict) and '@type' in value:
                return self._extract_schema_type(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and '@type' in item:
                        return self._extract_schema_type(item)
        
        return None
    
    def _process_json_ld_urls(self, data: Any, base_url: Optional[str]) -> Any:
        """Process URLs in JSON-LD data to make them absolute"""
        if isinstance(data, dict):
            processed = {}
            for key, value in data.items():
                if key in ['url', 'image', '@id'] and isinstance(value, str):
                    processed[key] = self._normalize_url(value, base_url)
                else:
                    processed[key] = self._process_json_ld_urls(value, base_url)
            return processed
        elif isinstance(data, list):
            return [self._process_json_ld_urls(item, base_url) for item in data]
        else:
            return data


class MicrodataParser(BaseMetadataParser):
    """Specialized parser for HTML Microdata"""
    
    def get_parser_type(self) -> str:
        return "microdata"
    
    async def parse(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse Microdata with detailed analysis"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all top-level items (itemscope without itemprop)
            top_level_items = soup.find_all(attrs={'itemscope': True, 'itemprop': False})
            
            # Also find items that have itemscope but are not nested
            all_itemscope = soup.find_all(attrs={'itemscope': True})
            for item in all_itemscope:
                # Check if this item is not nested within another itemscope
                parent_with_itemscope = item.find_parent(attrs={'itemscope': True})
                if not parent_with_itemscope:
                    top_level_items.append(item)
            
            # Remove duplicates
            top_level_items = list(set(top_level_items))
            
            microdata_items = []
            schemas_found = {}
            
            for item in top_level_items:
                parsed_item = await self._parse_microdata_item(item, base_url)
                
                if parsed_item:
                    microdata_items.append(parsed_item)
                    
                    # Count schema types
                    item_type = parsed_item.get('itemtype', '')
                    if item_type:
                        # Extract schema name from URL
                        schema_name = item_type.split('/')[-1] if '/' in item_type else item_type
                        schemas_found[schema_name] = schemas_found.get(schema_name, 0) + 1
            
            return {
                'type': self.get_parser_type(),
                'data': microdata_items,
                'schemas_found': schemas_found,
                'total_items': len(microdata_items),
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise MetadataParsingError(
                f"Microdata parsing failed: {str(e)}",
                metadata_type="microdata",
                parser_type="MicrodataParser"
            )
    
    async def _parse_microdata_item(self, item_element, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Parse individual microdata item"""
        item_data = {
            'itemtype': item_element.get('itemtype', ''),
            'itemid': item_element.get('itemid', ''),
            'properties': {},
            'nested_items': []
        }
        
        # Find all properties within this item
        properties = item_element.find_all(attrs={'itemprop': True})
        
        for prop in properties:
            # Skip if this property belongs to a nested item
            parent_itemscope = prop.find_parent(attrs={'itemscope': True})
            if parent_itemscope and parent_itemscope != item_element:
                continue
            
            prop_name = prop.get('itemprop')
            
            # Check if this property is itself an item
            if prop.get('itemscope'):
                nested_item = await self._parse_microdata_item(prop, base_url)
                item_data['nested_items'].append({
                    'property': prop_name,
                    'item': nested_item
                })
                continue
            
            # Get property value
            prop_value = self._extract_property_value(prop, base_url)
            
            # Handle multiple values for same property
            if prop_name in item_data['properties']:
                if not isinstance(item_data['properties'][prop_name], list):
                    item_data['properties'][prop_name] = [item_data['properties'][prop_name]]
                item_data['properties'][prop_name].append(prop_value)
            else:
                item_data['properties'][prop_name] = prop_value
        
        return item_data
    
    def _extract_property_value(self, element, base_url: Optional[str] = None) -> str:
        """Extract property value from element based on type"""
        # Value extraction based on element type and attributes
        if element.get('content'):
            return element.get('content')
        elif element.name in ['a', 'area', 'link']:
            url = element.get('href', '')
            return self._normalize_url(url, base_url)
        elif element.name in ['img', 'audio', 'embed', 'iframe', 'source', 'track', 'video']:
            url = element.get('src', '')
            return self._normalize_url(url, base_url)
        elif element.name == 'object':
            url = element.get('data', '')
            return self._normalize_url(url, base_url)
        elif element.name == 'meta':
            return element.get('content', '')
        elif element.name == 'time':
            return element.get('datetime', element.get_text(strip=True))
        else:
            return self._clean_text(element.get_text())
