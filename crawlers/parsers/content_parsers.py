"""
Content Parsers Module
======================

Specialized parsers for various content formats including HTML, JSON, XML, CSV, RSS, Atom.
Provides content extraction and structure analysis capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""

import csv
import json
import re
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from io import StringIO
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin, urlparse

import markdown
from bs4 import BeautifulSoup, Comment
import feedparser

from .exceptions import ContentExtractionError, UnsupportedFormatError, ValidationError
from .parser_config import ParserConfig


class BaseContentParser(ABC):
    """Abstract base class for content parsers"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
    
    @abstractmethod
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse content and extract structured data"""
        pass
    
    @abstractmethod
    def get_parser_type(self) -> str:
        """Get the type of content this parser handles"""
        pass
    
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
    
    def _normalize_url(self, url: str, base_url: Optional[str] = None) -> str:
        """Normalize relative URLs to absolute URLs"""
        if not url or url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            return url
        
        if base_url:
            return urljoin(base_url, url)
        
        return url


class HTMLContentParser(BaseContentParser):
    """Parser for HTML content with advanced extraction capabilities"""
    
    def get_parser_type(self) -> str:
        return "html_content"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse HTML content and extract structured information"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            soup = BeautifulSoup(content, 'html.parser')
            base_url = kwargs.get('base_url')
            
            # Extract main content
            main_content = await self._extract_main_content(soup)
            
            # Extract document structure
            structure = await self._analyze_document_structure(soup)
            
            # Extract links and media
            links = await self._extract_links(soup, base_url)
            media = await self._extract_media(soup, base_url)
            
            # Extract text statistics
            text_stats = await self._calculate_text_statistics(soup)
            
            # Extract semantic elements
            semantic_elements = await self._extract_semantic_elements(soup)
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'main_content': main_content,
                    'raw_text': soup.get_text(separator=' ', strip=True),
                    'title': self._extract_title(soup),
                    'headings': self._extract_headings(soup),
                    'paragraphs': self._extract_paragraphs(soup)
                },
                'structure': structure,
                'links': links,
                'media': media,
                'statistics': text_stats,
                'semantic': semantic_elements,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise ContentExtractionError(
                f"HTML content parsing failed: {str(e)}",
                extraction_method="html_parser",
                parser_type="HTMLContentParser"
            )
    
    async def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content using multiple heuristics"""
        content_candidates = []
        
        # Try semantic HTML5 elements first
        main_element = soup.find('main')
        if main_element:
            content_candidates.append(('main', main_element.get_text(separator=' ', strip=True)))
        
        article_element = soup.find('article')
        if article_element:
            content_candidates.append(('article', article_element.get_text(separator=' ', strip=True)))
        
        # Try common content containers
        content_selectors = [
            '.content', '.main-content', '.post-content', '.entry-content',
            '#content', '#main-content', '#post-content', '#entry-content',
            '.article-body', '.post-body', '.story-body'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                text = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                content_candidates.append((selector, text))
        
        # Use largest content block
        if content_candidates:
            return max(content_candidates, key=lambda x: len(x[1]))[1]
        
        # Fallback: extract content from body, excluding navigation and footer
        body = soup.find('body')
        if body:
            # Remove navigation, header, footer, sidebar
            for elem in body.find_all(['nav', 'header', 'footer', 'aside']):
                elem.decompose()
            
            # Remove common non-content elements
            for elem in body.find_all(class_=re.compile(r'(nav|menu|sidebar|footer|header)')):
                elem.decompose()
            
            return body.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)
    
    async def _analyze_document_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze HTML document structure"""
        structure = {
            'doctype': '',
            'html_lang': '',
            'head_elements': {},
            'body_structure': {},
            'semantic_elements': []
        }
        
        # Extract doctype
        if soup.contents and hasattr(soup.contents[0], 'string'):
            structure['doctype'] = str(soup.contents[0]).strip()
        
        # Extract HTML lang
        html_tag = soup.find('html')
        if html_tag:
            structure['html_lang'] = html_tag.get('lang', '')
        
        # Analyze head elements
        head = soup.find('head')
        if head:
            structure['head_elements'] = {
                'meta_count': len(head.find_all('meta')),
                'link_count': len(head.find_all('link')),
                'script_count': len(head.find_all('script')),
                'style_count': len(head.find_all('style'))
            }
        
        # Analyze body structure
        body = soup.find('body')
        if body:
            structure['body_structure'] = {
                'total_elements': len(body.find_all()),
                'div_count': len(body.find_all('div')),
                'span_count': len(body.find_all('span')),
                'p_count': len(body.find_all('p')),
                'img_count': len(body.find_all('img')),
                'a_count': len(body.find_all('a')),
                'table_count': len(body.find_all('table')),
                'form_count': len(body.find_all('form'))
            }
        
        # Find semantic HTML5 elements
        semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        for tag in semantic_tags:
            elements = soup.find_all(tag)
            if elements:
                structure['semantic_elements'].append({
                    'tag': tag,
                    'count': len(elements),
                    'has_content': any(elem.get_text(strip=True) for elem in elements)
                })
        
        return structure
    
    async def _extract_links(self, soup: BeautifulSoup, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract and categorize links"""
        links = {
            'internal': [],
            'external': [],
            'anchors': [],
            'mailto': [],
            'tel': [],
            'statistics': {}
        }
        
        base_domain = urlparse(base_url).netloc if base_url else None
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            text = self._clean_text(link.get_text())
            title = link.get('title', '')
            
            if not href:
                continue
            
            link_data = {
                'url': self._normalize_url(href, base_url),
                'text': text,
                'title': title,
                'rel': link.get('rel', []),
                'target': link.get('target', '')
            }
            
            # Categorize link
            if href.startswith('#'):
                links['anchors'].append(link_data)
            elif href.startswith('mailto:'):
                links['mailto'].append(link_data)
            elif href.startswith('tel:'):
                links['tel'].append(link_data)
            elif base_domain and urlparse(href).netloc == base_domain:
                links['internal'].append(link_data)
            elif href.startswith(('http://', 'https://')):
                links['external'].append(link_data)
            else:
                # Relative link, treat as internal
                links['internal'].append(link_data)
        
        # Calculate statistics
        links['statistics'] = {
            'total_links': len(soup.find_all('a', href=True)),
            'internal_count': len(links['internal']),
            'external_count': len(links['external']),
            'anchor_count': len(links['anchors']),
            'mailto_count': len(links['mailto']),
            'tel_count': len(links['tel']),
            'nofollow_count': len(soup.find_all('a', rel=re.compile(r'nofollow')))
        }
        
        return links
    
    async def _extract_media(self, soup: BeautifulSoup, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Extract media elements (images, videos, audio)"""
        media = {
            'images': [],
            'videos': [],
            'audio': [],
            'iframes': [],
            'statistics': {}
        }
        
        # Extract images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                media['images'].append({
                    'src': self._normalize_url(src, base_url),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                    'loading': img.get('loading', ''),
                    'srcset': img.get('srcset', '')
                })
        
        # Extract videos
        for video in soup.find_all('video'):
            video_data = {
                'src': '',
                'sources': [],
                'poster': video.get('poster', ''),
                'controls': video.has_attr('controls'),
                'autoplay': video.has_attr('autoplay'),
                'loop': video.has_attr('loop'),
                'muted': video.has_attr('muted')
            }
            
            # Get main source
            if video.get('src'):
                video_data['src'] = self._normalize_url(video.get('src'), base_url)
            
            # Get source elements
            for source in video.find_all('source'):
                if source.get('src'):
                    video_data['sources'].append({
                        'src': self._normalize_url(source.get('src'), base_url),
                        'type': source.get('type', ''),
                        'media': source.get('media', '')
                    })
            
            media['videos'].append(video_data)
        
        # Extract audio
        for audio in soup.find_all('audio'):
            audio_data = {
                'src': '',
                'sources': [],
                'controls': audio.has_attr('controls'),
                'autoplay': audio.has_attr('autoplay'),
                'loop': audio.has_attr('loop'),
                'muted': audio.has_attr('muted')
            }
            
            if audio.get('src'):
                audio_data['src'] = self._normalize_url(audio.get('src'), base_url)
            
            for source in audio.find_all('source'):
                if source.get('src'):
                    audio_data['sources'].append({
                        'src': self._normalize_url(source.get('src'), base_url),
                        'type': source.get('type', '')
                    })
            
            media['audio'].append(audio_data)
        
        # Extract iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src:
                media['iframes'].append({
                    'src': self._normalize_url(src, base_url),
                    'title': iframe.get('title', ''),
                    'width': iframe.get('width', ''),
                    'height': iframe.get('height', ''),
                    'loading': iframe.get('loading', ''),
                    'sandbox': iframe.get('sandbox', '')
                })
        
        # Calculate statistics
        media['statistics'] = {
            'total_images': len(media['images']),
            'total_videos': len(media['videos']),
            'total_audio': len(media['audio']),
            'total_iframes': len(media['iframes']),
            'images_with_alt': len([img for img in media['images'] if img['alt']]),
            'lazy_loaded_images': len([img for img in media['images'] if img['loading'] == 'lazy'])
        }
        
        return media
    
    async def _calculate_text_statistics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Calculate text-based statistics"""
        text = soup.get_text(separator=' ', strip=True)
        
        return {
            'character_count': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'paragraph_count': len(soup.find_all('p')),
            'heading_count': len(soup.find_all(re.compile(r'^h[1-6]$'))),
            'list_count': len(soup.find_all(['ul', 'ol'])),
            'list_item_count': len(soup.find_all('li')),
            'table_count': len(soup.find_all('table')),
            'form_count': len(soup.find_all('form'))
        }
    
    async def _extract_semantic_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract semantic HTML5 elements content"""
        semantic = {}
        
        # Extract header content
        header = soup.find('header')
        if header:
            semantic['header'] = self._clean_text(header.get_text())
        
        # Extract navigation
        nav = soup.find('nav')
        if nav:
            nav_links = [{'text': self._clean_text(a.get_text()), 'href': a.get('href', '')} 
                        for a in nav.find_all('a', href=True)]
            semantic['navigation'] = nav_links
        
        # Extract main content
        main = soup.find('main')
        if main:
            semantic['main'] = self._clean_text(main.get_text())
        
        # Extract articles
        articles = soup.find_all('article')
        if articles:
            semantic['articles'] = [self._clean_text(article.get_text()) for article in articles]
        
        # Extract sections
        sections = soup.find_all('section')
        if sections:
            semantic['sections'] = [self._clean_text(section.get_text()) for section in sections]
        
        # Extract aside content
        aside = soup.find('aside')
        if aside:
            semantic['aside'] = self._clean_text(aside.get_text())
        
        # Extract footer
        footer = soup.find('footer')
        if footer:
            semantic['footer'] = self._clean_text(footer.get_text())
        
        return semantic
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title"""
        title_tag = soup.find('title')
        return self._clean_text(title_tag.get_text()) if title_tag else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all headings with hierarchy"""
        headings = []
        
        for heading in soup.find_all(re.compile(r'^h[1-6]$')):
            headings.append({
                'level': int(heading.name[1]),
                'text': self._clean_text(heading.get_text()),
                'id': heading.get('id', ''),
                'class': heading.get('class', [])
            })
        
        return headings
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract all paragraph content"""
        paragraphs = []
        
        for p in soup.find_all('p'):
            text = self._clean_text(p.get_text())
            if text:  # Only include non-empty paragraphs
                paragraphs.append(text)
        
        return paragraphs


class MarkdownParser(BaseContentParser):
    """Parser for Markdown content"""
    
    def get_parser_type(self) -> str:
        return "markdown"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse Markdown content"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Convert Markdown to HTML
            md = markdown.Markdown(extensions=['meta', 'toc', 'tables', 'fenced_code'])
            html = md.convert(content)
            
            # Parse the generated HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract Markdown-specific metadata
            metadata = getattr(md, 'Meta', {})
            
            # Extract headings for TOC
            headings = []
            for heading in soup.find_all(re.compile(r'^h[1-6]$')):
                headings.append({
                    'level': int(heading.name[1]),
                    'text': self._clean_text(heading.get_text()),
                    'id': heading.get('id', '')
                })
            
            # Extract code blocks
            code_blocks = []
            for code in soup.find_all('code'):
                parent = code.parent
                if parent and parent.name == 'pre':
                    code_blocks.append({
                        'language': code.get('class', [''])[0].replace('language-', '') if code.get('class') else '',
                        'content': code.get_text()
                    })
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    'url': link.get('href'),
                    'text': self._clean_text(link.get_text()),
                    'title': link.get('title', '')
                })
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                images.append({
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
            
            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                table_data = {
                    'headers': [],
                    'rows': []
                }
                
                # Get headers
                header_row = table.find('thead')
                if header_row:
                    headers = header_row.find_all('th')
                    table_data['headers'] = [self._clean_text(th.get_text()) for th in headers]
                
                # Get rows
                tbody = table.find('tbody') or table
                for row in tbody.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    table_data['rows'].append([self._clean_text(cell.get_text()) for cell in cells])
                
                tables.append(table_data)
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'raw_markdown': content,
                    'html': html,
                    'text': soup.get_text(separator=' ', strip=True),
                    'metadata': metadata
                },
                'structure': {
                    'headings': headings,
                    'code_blocks': code_blocks,
                    'links': links,
                    'images': images,
                    'tables': tables
                },
                'statistics': {
                    'character_count': len(content),
                    'word_count': len(content.split()),
                    'line_count': len(content.splitlines()),
                    'heading_count': len(headings),
                    'code_block_count': len(code_blocks),
                    'link_count': len(links),
                    'image_count': len(images),
                    'table_count': len(tables)
                },
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise ContentExtractionError(
                f"Markdown parsing failed: {str(e)}",
                extraction_method="markdown_parser",
                parser_type="MarkdownParser"
            )


class JSONContentParser(BaseContentParser):
    """Parser for JSON content"""
    
    def get_parser_type(self) -> str:
        return "json"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse JSON content"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Parse JSON
            data = json.loads(content)
            
            # Analyze JSON structure
            structure_analysis = await self._analyze_json_structure(data)
            
            # Extract strings for text analysis
            text_content = await self._extract_text_from_json(data)
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'data': data,
                    'text_content': text_content,
                    'raw_json': content
                },
                'structure': structure_analysis,
                'statistics': {
                    'character_count': len(content),
                    'text_character_count': len(text_content),
                    'word_count': len(text_content.split()) if text_content else 0
                },
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except json.JSONDecodeError as e:
            raise ContentExtractionError(
                f"JSON parsing failed: {str(e)}",
                extraction_method="json_parser",
                parser_type="JSONContentParser"
            )
        except Exception as e:
            raise ContentExtractionError(
                f"JSON content analysis failed: {str(e)}",
                extraction_method="json_parser",
                parser_type="JSONContentParser"
            )
    
    async def _analyze_json_structure(self, data: Any, path: str = "$") -> Dict[str, Any]:
        """Analyze JSON structure recursively"""
        analysis = {
            'type': type(data).__name__,
            'path': path,
            'size': 0,
            'depth': 0,
            'children': {}
        }
        
        if isinstance(data, dict):
            analysis['size'] = len(data)
            analysis['keys'] = list(data.keys())
            max_depth = 0
            
            for key, value in data.items():
                child_analysis = await self._analyze_json_structure(value, f"{path}.{key}")
                analysis['children'][key] = child_analysis
                max_depth = max(max_depth, child_analysis['depth'])
            
            analysis['depth'] = max_depth + 1
            
        elif isinstance(data, list):
            analysis['size'] = len(data)
            max_depth = 0
            
            for i, item in enumerate(data):
                if i < 5:  # Analyze first 5 items to avoid excessive processing
                    child_analysis = await self._analyze_json_structure(item, f"{path}[{i}]")
                    analysis['children'][f'item_{i}'] = child_analysis
                    max_depth = max(max_depth, child_analysis['depth'])
            
            analysis['depth'] = max_depth + 1
            
        elif isinstance(data, str):
            analysis['size'] = len(data)
            analysis['depth'] = 0
            
        else:
            analysis['size'] = 1
            analysis['depth'] = 0
        
        return analysis
    
    async def _extract_text_from_json(self, data: Any) -> str:
        """Extract all text content from JSON recursively"""
        text_parts = []
        
        if isinstance(data, dict):
            for value in data.values():
                text_parts.append(await self._extract_text_from_json(value))
        elif isinstance(data, list):
            for item in data:
                text_parts.append(await self._extract_text_from_json(item))
        elif isinstance(data, str):
            text_parts.append(data)
        elif data is not None:
            text_parts.append(str(data))
        
        return ' '.join(filter(None, text_parts))


class XMLContentParser(BaseContentParser):
    """Parser for XML content"""
    
    def get_parser_type(self) -> str:
        return "xml"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse XML content"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Convert to structured format
            structured_data = await self._xml_to_dict(root)
            
            # Extract text content
            text_content = ''.join(root.itertext())
            
            # Analyze XML structure
            structure_analysis = await self._analyze_xml_structure(root)
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'data': structured_data,
                    'text_content': self._clean_text(text_content),
                    'raw_xml': content
                },
                'structure': structure_analysis,
                'statistics': {
                    'character_count': len(content),
                    'text_character_count': len(text_content),
                    'word_count': len(text_content.split()) if text_content else 0,
                    'element_count': len(list(root.iter()))
                },
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except ET.ParseError as e:
            raise ContentExtractionError(
                f"XML parsing failed: {str(e)}",
                extraction_method="xml_parser",
                parser_type="XMLContentParser"
            )
        except Exception as e:
            raise ContentExtractionError(
                f"XML content analysis failed: {str(e)}",
                extraction_method="xml_parser",
                parser_type="XMLContentParser"
            )
    
    async def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # Leaf node
                return element.text.strip()
            else:
                result['@text'] = element.text.strip()
        
        # Add child elements
        children = {}
        for child in element:
            child_data = await self._xml_to_dict(child)
            
            if child.tag in children:
                # Convert to list if multiple elements with same tag
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_data)
            else:
                children[child.tag] = child_data
        
        result.update(children)
        
        return result if result else None
    
    async def _analyze_xml_structure(self, root: ET.Element) -> Dict[str, Any]:
        """Analyze XML structure"""
        all_elements = list(root.iter())
        tag_counts = {}
        
        for element in all_elements:
            tag_counts[element.tag] = tag_counts.get(element.tag, 0) + 1
        
        return {
            'root_tag': root.tag,
            'total_elements': len(all_elements),
            'unique_tags': len(tag_counts),
            'tag_counts': tag_counts,
            'max_depth': await self._calculate_xml_depth(root),
            'has_attributes': any(elem.attrib for elem in all_elements),
            'has_namespaces': any(':' in elem.tag for elem in all_elements)
        }
    
    async def _calculate_xml_depth(self, element: ET.Element, current_depth: int = 0) -> int:
        """Calculate maximum depth of XML tree"""
        if not list(element):
            return current_depth
        
        return max(await self._calculate_xml_depth(child, current_depth + 1) for child in element)


class CSVParser(BaseContentParser):
    """Parser for CSV content"""
    
    def get_parser_type(self) -> str:
        return "csv"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse CSV content"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Detect CSV dialect
            dialect = csv.Sniffer().sniff(content[:1024])
            has_header = csv.Sniffer().has_header(content[:1024])
            
            # Parse CSV
            csv_reader = csv.reader(StringIO(content), dialect=dialect)
            rows = list(csv_reader)
            
            if not rows:
                raise ContentExtractionError("Empty CSV content", parser_type="CSVParser")
            
            # Process data
            headers = rows[0] if has_header else [f"Column_{i+1}" for i in range(len(rows[0]))]
            data_rows = rows[1:] if has_header else rows
            
            # Convert to list of dictionaries
            structured_data = []
            for row in data_rows:
                if len(row) == len(headers):
                    structured_data.append(dict(zip(headers, row)))
            
            # Analyze columns
            column_analysis = await self._analyze_csv_columns(structured_data, headers)
            
            # Extract all text content
            text_content = ' '.join([' '.join(row) for row in rows])
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'data': structured_data,
                    'headers': headers,
                    'raw_rows': rows,
                    'text_content': text_content
                },
                'structure': {
                    'has_header': has_header,
                    'column_count': len(headers),
                    'row_count': len(data_rows),
                    'delimiter': dialect.delimiter,
                    'quote_char': dialect.quotechar,
                    'column_analysis': column_analysis
                },
                'statistics': {
                    'character_count': len(content),
                    'word_count': len(text_content.split()),
                    'total_cells': len(headers) * len(data_rows),
                    'empty_cells': sum(1 for row in structured_data for value in row.values() if not value)
                },
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except csv.Error as e:
            raise ContentExtractionError(
                f"CSV parsing failed: {str(e)}",
                extraction_method="csv_parser",
                parser_type="CSVParser"
            )
        except Exception as e:
            raise ContentExtractionError(
                f"CSV content analysis failed: {str(e)}",
                extraction_method="csv_parser",
                parser_type="CSVParser"
            )
    
    async def _analyze_csv_columns(self, data: List[Dict[str, str]], headers: List[str]) -> Dict[str, Any]:
        """Analyze CSV columns for data types and patterns"""
        analysis = {}
        
        for header in headers:
            values = [row.get(header, '') for row in data if row.get(header, '')]
            
            column_info = {
                'non_empty_count': len(values),
                'unique_count': len(set(values)),
                'max_length': max(len(str(v)) for v in values) if values else 0,
                'min_length': min(len(str(v)) for v in values) if values else 0,
                'avg_length': sum(len(str(v)) for v in values) / len(values) if values else 0,
                'data_type': 'string'
            }
            
            # Try to detect data types
            if values:
                # Check if numeric
                numeric_count = sum(1 for v in values if str(v).replace('.', '').replace('-', '').isdigit())
                if numeric_count > len(values) * 0.8:
                    column_info['data_type'] = 'numeric'
                
                # Check if date-like
                date_patterns = [
                    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                    r'\d{2}-\d{2}-\d{4}'   # MM-DD-YYYY
                ]
                
                date_count = sum(1 for v in values 
                               if any(re.match(pattern, str(v)) for pattern in date_patterns))
                if date_count > len(values) * 0.8:
                    column_info['data_type'] = 'date'
                
                # Check if email-like
                email_count = sum(1 for v in values if '@' in str(v) and '.' in str(v))
                if email_count > len(values) * 0.8:
                    column_info['data_type'] = 'email'
                
                # Check if URL-like
                url_count = sum(1 for v in values if str(v).startswith(('http://', 'https://')))
                if url_count > len(values) * 0.8:
                    column_info['data_type'] = 'url'
            
            analysis[header] = column_info
        
        return analysis


class RSSParser(BaseContentParser):
    """Parser for RSS feeds"""
    
    def get_parser_type(self) -> str:
        return "rss"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse RSS feed content"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Parse RSS using feedparser
            feed = feedparser.parse(content)
            
            if feed.bozo:
                # Feed has errors but might be parseable
                pass
            
            # Extract feed information
            feed_info = {
                'title': feed.feed.get('title', ''),
                'description': feed.feed.get('description', ''),
                'link': feed.feed.get('link', ''),
                'language': feed.feed.get('language', ''),
                'updated': feed.feed.get('updated', ''),
                'generator': feed.feed.get('generator', ''),
                'image': feed.feed.get('image', {}),
                'author': feed.feed.get('author', ''),
                'rights': feed.feed.get('rights', '')
            }
            
            # Extract entries
            entries = []
            for entry in feed.entries:
                entry_data = {
                    'title': entry.get('title', ''),
                    'description': entry.get('description', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'updated': entry.get('updated', ''),
                    'author': entry.get('author', ''),
                    'id': entry.get('id', ''),
                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])],
                    'enclosures': [
                        {
                            'url': enc.get('href', ''),
                            'type': enc.get('type', ''),
                            'length': enc.get('length', '')
                        }
                        for enc in entry.get('enclosures', [])
                    ]
                }
                entries.append(entry_data)
            
            # Extract all text for analysis
            text_content = ' '.join([
                feed_info['title'],
                feed_info['description'],
                ' '.join([entry['title'] + ' ' + entry['description'] for entry in entries])
            ])
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'feed_info': feed_info,
                    'entries': entries,
                    'text_content': self._clean_text(text_content)
                },
                'structure': {
                    'feed_format': feed.version,
                    'entry_count': len(entries),
                    'has_images': bool(feed_info.get('image')),
                    'has_enclosures': any(entry['enclosures'] for entry in entries),
                    'languages': list(set(filter(None, [feed_info.get('language')]))),
                    'categories': list(set([tag for entry in entries for tag in entry['tags']]))
                },
                'statistics': {
                    'character_count': len(content),
                    'text_character_count': len(text_content),
                    'word_count': len(text_content.split()) if text_content else 0,
                    'average_entry_length': sum(len(entry['description']) for entry in entries) / len(entries) if entries else 0
                },
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise ContentExtractionError(
                f"RSS parsing failed: {str(e)}",
                extraction_method="rss_parser",
                parser_type="RSSParser"
            )


class AtomParser(BaseContentParser):
    """Parser for Atom feeds"""
    
    def get_parser_type(self) -> str:
        return "atom"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse Atom feed content"""
        # Atom feeds are handled by feedparser as well
        # This could be extended for Atom-specific features
        rss_parser = RSSParser(self.config)
        result = await rss_parser.parse(content, **kwargs)
        result['type'] = self.get_parser_type()
        return result


class SitemapParser(BaseContentParser):
    """Parser for XML sitemaps"""
    
    def get_parser_type(self) -> str:
        return "sitemap"
    
    async def parse(self, content: Union[str, bytes], **kwargs) -> Dict[str, Any]:
        """Parse XML sitemap content"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            root = ET.fromstring(content)
            
            # Handle namespaces
            namespaces = {
                'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'image': 'http://www.google.com/schemas/sitemap-image/1.1',
                'video': 'http://www.google.com/schemas/sitemap-video/1.1',
                'news': 'http://www.google.com/schemas/sitemap-news/0.9'
            }
            
            urls = []
            sitemaps = []
            
            # Check if this is a sitemap index
            sitemap_elements = root.findall('.//sitemap:sitemap', namespaces)
            if sitemap_elements:
                # This is a sitemap index
                for sitemap_elem in sitemap_elements:
                    loc = sitemap_elem.find('sitemap:loc', namespaces)
                    lastmod = sitemap_elem.find('sitemap:lastmod', namespaces)
                    
                    sitemap_data = {
                        'loc': loc.text if loc is not None else '',
                        'lastmod': lastmod.text if lastmod is not None else ''
                    }
                    sitemaps.append(sitemap_data)
            
            # Parse URL entries
            url_elements = root.findall('.//sitemap:url', namespaces)
            for url_elem in url_elements:
                loc = url_elem.find('sitemap:loc', namespaces)
                lastmod = url_elem.find('sitemap:lastmod', namespaces)
                changefreq = url_elem.find('sitemap:changefreq', namespaces)
                priority = url_elem.find('sitemap:priority', namespaces)
                
                url_data = {
                    'loc': loc.text if loc is not None else '',
                    'lastmod': lastmod.text if lastmod is not None else '',
                    'changefreq': changefreq.text if changefreq is not None else '',
                    'priority': priority.text if priority is not None else '',
                    'images': [],
                    'videos': [],
                    'news': []
                }
                
                # Parse image extensions
                for image_elem in url_elem.findall('image:image', namespaces):
                    image_loc = image_elem.find('image:loc', namespaces)
                    image_caption = image_elem.find('image:caption', namespaces)
                    image_title = image_elem.find('image:title', namespaces)
                    
                    if image_loc is not None:
                        url_data['images'].append({
                            'loc': image_loc.text,
                            'caption': image_caption.text if image_caption is not None else '',
                            'title': image_title.text if image_title is not None else ''
                        })
                
                # Parse video extensions
                for video_elem in url_elem.findall('video:video', namespaces):
                    video_title = video_elem.find('video:title', namespaces)
                    video_description = video_elem.find('video:description', namespaces)
                    video_thumbnail_loc = video_elem.find('video:thumbnail_loc', namespaces)
                    video_content_loc = video_elem.find('video:content_loc', namespaces)
                    
                    url_data['videos'].append({
                        'title': video_title.text if video_title is not None else '',
                        'description': video_description.text if video_description is not None else '',
                        'thumbnail_loc': video_thumbnail_loc.text if video_thumbnail_loc is not None else '',
                        'content_loc': video_content_loc.text if video_content_loc is not None else ''
                    })
                
                # Parse news extensions
                for news_elem in url_elem.findall('news:news', namespaces):
                    news_publication = news_elem.find('news:publication', namespaces)
                    news_title = news_elem.find('news:title', namespaces)
                    news_publication_date = news_elem.find('news:publication_date', namespaces)
                    
                    news_data = {
                        'title': news_title.text if news_title is not None else '',
                        'publication_date': news_publication_date.text if news_publication_date is not None else ''
                    }
                    
                    if news_publication is not None:
                        pub_name = news_publication.find('news:name', namespaces)
                        pub_language = news_publication.find('news:language', namespaces)
                        news_data['publication_name'] = pub_name.text if pub_name is not None else ''
                        news_data['publication_language'] = pub_language.text if pub_language is not None else ''
                    
                    url_data['news'].append(news_data)
                
                urls.append(url_data)
            
            return {
                'type': self.get_parser_type(),
                'content': {
                    'urls': urls,
                    'sitemaps': sitemaps,
                    'is_index': bool(sitemaps)
                },
                'structure': {
                    'url_count': len(urls),
                    'sitemap_count': len(sitemaps),
                    'has_images': any(url['images'] for url in urls),
                    'has_videos': any(url['videos'] for url in urls),
                    'has_news': any(url['news'] for url in urls),
                    'changefreq_values': list(set(url['changefreq'] for url in urls if url['changefreq'])),
                    'priority_range': {
                        'min': min([float(url['priority']) for url in urls if url['priority']], default=0),
                        'max': max([float(url['priority']) for url in urls if url['priority']], default=0)
                    }
                },
                'statistics': {
                    'character_count': len(content),
                    'total_images': sum(len(url['images']) for url in urls),
                    'total_videos': sum(len(url['videos']) for url in urls),
                    'total_news': sum(len(url['news']) for url in urls)
                },
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except ET.ParseError as e:
            raise ContentExtractionError(
                f"Sitemap XML parsing failed: {str(e)}",
                extraction_method="sitemap_parser",
                parser_type="SitemapParser"
            )
        except Exception as e:
            raise ContentExtractionError(
                f"Sitemap parsing failed: {str(e)}",
                extraction_method="sitemap_parser",
                parser_type="SitemapParser"
            )
