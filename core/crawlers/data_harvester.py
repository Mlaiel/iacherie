"""Data Harvester - Collecteur de données multi-sources
====================================================

Système avancé de collecte et extraction de données
depuis diverses sources web et plateformes digitales.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import hashlib
import mimetypes
from urllib.parse import urlparse, urljoin
import re

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

try:
    from ...utils.proxy_manager import ProxyManager
    from ...utils.rate_limiter import RateLimiter
    from ...utils.data_validator import DataValidator
    from ...utils.data_transformer import DataTransformer
    from ..ai.content_analysis import ContentAnalyzer
except ImportError:
    # Fallback to local utils if imports fail
    from .data_collection_utils import (
        ProxyManager, RateLimiter, DataValidator, 
        DataTransformer, ContentAnalyzer
    )


class SourceType(Enum):
    """
Types de sources de données"""

    WEB_PAGE = "web_page"
    API = "api"
    RSS_FEED = "rss_feed"
    SOCIAL_MEDIA = "social_media"
    STREAMING = "streaming"
    MARKETPLACE = "marketplace"
    NEWS = "news"
    FORUM = "forum"
    BLOG = "blog"
    DATABASE = "database"


class DataFormat(Enum):
    """Formats de données"""

    HTML = "html"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    EXCEL = "excel"


class HarvestingStatus(Enum):
    """Statuts de collecte"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class HarvestingTarget:
    """Cible de collecte de données"""
    target_id: str
    source_url: str
    source_type: SourceType
    data_format: DataFormat
    extraction_rules: Dict[str, Any]
    scheduling: Dict[str, Any]
    output_config: Dict[str, Any]
    created_at: datetime
    last_harvested: Optional[datetime] = None
    status: HarvestingStatus = HarvestingStatus.PENDING
    success_count: int = 0
    failure_count: int = 0
    total_data_size: int = 0


@dataclass
class HarvestResult:
    """
Résultat de collecte"""
    target_id: str
    harvest_id: str
    status: HarvestingStatus
    data_collected: Dict[str, Any]
    metadata: Dict[str, Any]
    file_paths: List[str]
    processing_time: float
    errors: List[str]
    timestamp: datetime


@dataclass
class ExtractionRule:
    """
Règle d'extraction de données"""
    field_name: str
    selector_type: str  # css, xpath, regex, json_path
    selector: str
    data_type: str  # text, number, date, url, image
    is_required: bool = False
    default_value: Any = None
    validation_rules: List[str] = None
    transformation_rules: List[str] = None


class DataHarvester:
    """
    Collecteur de données multi-sources avancé
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le collecteur de données
        
        Args:
            config: Configuration du harvester
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Gestionnaires
        self.proxy_manager = ProxyManager(config.get('proxy_config', {}))
        self.rate_limiter = RateLimiter(
            max_requests=config.get('max_requests_per_minute', 60),
            window_seconds=60
        )
        self.data_validator = DataValidator()
        self.data_transformer = DataTransformer()
        self.content_analyzer = ContentAnalyzer()
        
        # Données de collecte
        self.harvesting_targets: Dict[str, HarvestingTarget] = {}
        self.harvest_results: Dict[str, HarvestResult] = {}
        self.extraction_templates: Dict[str, List[ExtractionRule]] = {}
        
        # Pool de threads pour traitement
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))
        
        # Configuration Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        
        # Session HTTP persistante
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Cache des données récupérées
        self.data_cache: Dict[str, Any] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        # Répertoires de sortie
        self.output_dirs = {
            'raw': config.get('raw_data_dir', '/tmp/harvester/raw'),
            'processed': config.get('processed_data_dir', '/tmp/harvester/processed'),
            'media': config.get('media_dir', '/tmp/harvester/media'),
            'exports': config.get('exports_dir', '/tmp/harvester/exports')
        }
        
        # Templates d'extraction prédéfinis
        self._initialize_extraction_templates()

    def _initialize_extraction_templates(self) -> None:
        """
Initialise les templates d'extraction prédéfinis"""
        
        # Template pour articles de blog
        self.extraction_templates['blog_article'] = [
            ExtractionRule('title', 'css', 'h1, .title, .post-title', 'text', True),
            ExtractionRule('content', 'css', '.content, .post-content, article', 'text', True),
            ExtractionRule('author', 'css', '.author, .byline, .post-author', 'text'),
            ExtractionRule('date', 'css', '.date, .publish-date, time', 'date'),
            ExtractionRule('tags', 'css', '.tags a, .tag', 'text'),
            ExtractionRule('images', 'css', 'img', 'image'),
            ExtractionRule('links', 'css', 'a[href]', 'url')
        ]
        
        # Template pour produits e-commerce
        self.extraction_templates['ecommerce_product'] = [
            ExtractionRule('name', 'css', '.product-name, .title, h1', 'text', True),
            ExtractionRule('price', 'css', '.price, .cost, .amount', 'number', True),
            ExtractionRule('description', 'css', '.description, .product-desc', 'text'),
            ExtractionRule('images', 'css', '.product-image img, .gallery img', 'image'),
            ExtractionRule('rating', 'css', '.rating, .stars', 'number'),
            ExtractionRule('reviews_count', 'css', '.reviews-count, .review-count', 'number'),
            ExtractionRule('availability', 'css', '.stock, .availability', 'text'),
            ExtractionRule('sku', 'css', '.sku, .product-id', 'text')
        ]
        
        # Template pour profils sociaux
        self.extraction_templates['social_profile'] = [
            ExtractionRule('username', 'css', '.username, .handle, .user-name', 'text', True),
            ExtractionRule('display_name', 'css', '.display-name, .full-name', 'text'),
            ExtractionRule('bio', 'css', '.bio, .description, .about', 'text'),
            ExtractionRule('follower_count', 'css', '.followers, .follower-count', 'number'),
            ExtractionRule('following_count', 'css', '.following, .following-count', 'number'),
            ExtractionRule('post_count', 'css', '.posts, .post-count', 'number'),
            ExtractionRule('profile_image', 'css', '.profile-image img, .avatar img', 'image'),
            ExtractionRule('verified', 'css', '.verified, .checkmark', 'text')
        ]
        
        # Template pour actualités
        self.extraction_templates['news_article'] = [
            ExtractionRule('headline', 'css', 'h1, .headline, .news-title', 'text', True),
            ExtractionRule('summary', 'css', '.summary, .lead, .excerpt', 'text'),
            ExtractionRule('content', 'css', '.article-content, .news-content', 'text', True),
            ExtractionRule('author', 'css', '.author, .byline, .journalist', 'text'),
            ExtractionRule('publication_date', 'css', '.date, .publish-date, time', 'date'),
            ExtractionRule('category', 'css', '.category, .section', 'text'),
            ExtractionRule('tags', 'css', '.tags a, .keywords', 'text'),
            ExtractionRule('source', 'css', '.source, .publication', 'text')
        ]

    async def add_harvesting_target(
        self,
        source_url: str,
        source_type: SourceType,
        data_format: DataFormat,
        extraction_rules: Dict[str, Any],
        scheduling: Dict[str, Any] = None,
        output_config: Dict[str, Any] = None
    ) -> str:
        """
        Ajoute une nouvelle cible de collecte
        
        Args:
            source_url: URL source
            source_type: Type de source
            data_format: Format des données
            extraction_rules: Règles d'extraction
            scheduling: Configuration de planification
            output_config: Configuration de sortie
            
        Returns:
            str: ID de la cible créée
        """
        try:
            target_id = self._generate_target_id(source_url)
            
            target = HarvestingTarget(
                target_id=target_id,
                source_url=source_url,
                source_type=source_type,
                data_format=data_format,
                extraction_rules=extraction_rules,
                scheduling=scheduling or {},
                output_config=output_config or {},
                created_at=datetime.now()
            )
            
            # Validation de la cible
            await self._validate_harvesting_target(target)
            
            # Sauvegarde
            self.harvesting_targets[target_id] = target
            
            self.logger.info(f"Cible de collecte ajoutée: {target_id}")
            return target_id
            
        except Exception as e:
            self.logger.error(f"Erreur ajout cible collecte: {e}")
            raise

    def _generate_target_id(self, source_url: str) -> str:
        """Génère un ID unique pour la cible"""
        url_hash = hashlib.md5(source_url.encode()).hexdigest()[:8]
        timestamp = int(datetime.now().timestamp())
        return f"TGT_{url_hash}_{timestamp}".upper()

    async def _validate_harvesting_target(self, target: HarvestingTarget) -> None:
        """Valide une cible de collecte"""
        # Validation URL
        parsed_url = urlparse(target.source_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"URL invalide: {target.source_url}")
        
        # Test de connectivité
        try:
            await self._test_url_accessibility(target.source_url)
        except Exception as e:
            self.logger.warning(f"Problème d'accessibilité URL {target.source_url}: {e}")

    async def _test_url_accessibility(self, url: str) -> bool:
        """Test l'accessibilité d'une URL"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.head(url, timeout=aiohttp.ClientTimeout(10)) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Test accessibilité échoué pour {url}: {e}")
            return False

    async def start_harvesting(self, target_id: str = None) -> None:
        """
        Démarre la collecte de données
        
        Args:
            target_id: ID de cible spécifique (optionnel)
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Démarrage pour cible spécifique ou toutes les cibles
            if target_id:
                if target_id in self.harvesting_targets:
                    await self._harvest_target(self.harvesting_targets[target_id])
                else:
                    raise ValueError(f"Cible non trouvée: {target_id}")
            else:
                # Collecte pour toutes les cibles actives
                tasks = []
                for target in self.harvesting_targets.values():
                    if target.status != HarvestingStatus.CANCELLED:
                        tasks.append(asyncio.create_task(self._harvest_target(target)))
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage collecte: {e}")
            raise

    async def _harvest_target(self, target: HarvestingTarget) -> HarvestResult:
        """
        Collecte les données d'une cible spécifique
        
        Args:
            target: Cible de collecte
            
        Returns:
            HarvestResult: Résultat de la collecte
        """
        start_time = datetime.now()
        harvest_id = self._generate_harvest_id(target.target_id)
        
        try:
            # Mise à jour du statut
            target.status = HarvestingStatus.RUNNING
            
            # Respect du rate limiting
            await self.rate_limiter.acquire()
            
            # Collecte selon le type de source
            if target.source_type == SourceType.WEB_PAGE:
                collected_data = await self._harvest_web_page(target)
            elif target.source_type == SourceType.API:
                collected_data = await self._harvest_api(target)
            elif target.source_type == SourceType.RSS_FEED:
                collected_data = await self._harvest_rss_feed(target)
            elif target.source_type == SourceType.SOCIAL_MEDIA:
                collected_data = await self._harvest_social_media(target)
            else:
                collected_data = await self._harvest_generic(target)
            
            # Traitement et validation des données
            processed_data = await self._process_collected_data(target, collected_data)
            
            # Sauvegarde des données
            file_paths = await self._save_harvested_data(target, processed_data, harvest_id)
            
            # Création du résultat
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = HarvestResult(
                target_id=target.target_id,
                harvest_id=harvest_id,
                status=HarvestingStatus.COMPLETED,
                data_collected=processed_data,
                metadata=self._generate_harvest_metadata(target, processed_data),
                file_paths=file_paths,
                processing_time=processing_time,
                errors=[],
                timestamp=datetime.now()
            )
            
            # Mise à jour de la cible
            target.status = HarvestingStatus.COMPLETED
            target.last_harvested = datetime.now()
            target.success_count += 1
            target.total_data_size += len(json.dumps(processed_data, default=str))
            
            # Sauvegarde du résultat
            self.harvest_results[harvest_id] = result
            
            self.logger.info(f"Collecte terminée pour {target.target_id} en {processing_time:.2f}s")
            return result
            
        except Exception as e:
            # Gestion d'erreur
            error_msg = str(e)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = HarvestResult(
                target_id=target.target_id,
                harvest_id=harvest_id,
                status=HarvestingStatus.FAILED,
                data_collected={},
                metadata={},
                file_paths=[],
                processing_time=processing_time,
                errors=[error_msg],
                timestamp=datetime.now()
            )
            
            # Mise à jour de la cible
            target.status = HarvestingStatus.FAILED
            target.failure_count += 1
            
            self.harvest_results[harvest_id] = result
            
            self.logger.error(f"Échec collecte pour {target.target_id}: {error_msg}")
            return result

    def _generate_harvest_id(self, target_id: str) -> str:
        """Génère un ID unique pour la collecte"""
        timestamp = int(datetime.now().timestamp())
        return f"HRV_{target_id}_{timestamp}".upper()

    async def _harvest_web_page(self, target: HarvestingTarget) -> Dict[str, Any]:
        """Collecte une page web"""
        try:
            # Récupération du contenu HTML
            html_content = await self._fetch_html_content(target.source_url)
            
            # Extraction des données selon les règles
            if 'template' in target.extraction_rules:
                # Utilisation d'un template prédéfini
                template_name = target.extraction_rules['template']
                if template_name in self.extraction_templates:
                    extracted_data = await self._extract_with_template(
                        html_content, self.extraction_templates[template_name]
                    )
                else:
                    raise ValueError(f"Template non trouvé: {template_name}")
            elif 'custom_rules' in target.extraction_rules:
                # Règles personnalisées
                rules = [
                    ExtractionRule(**rule) for rule in target.extraction_rules['custom_rules']
                ]
                extracted_data = await self._extract_with_template(html_content, rules)
            else:
                # Extraction générique
                extracted_data = await self._extract_generic_web_data(html_content)
            
            # Ajout de métadonnées
            extracted_data['_metadata'] = {
                'url': target.source_url,
                'extracted_at': datetime.now().isoformat(),
                'content_type': 'text/html',
                'content_length': len(html_content)
            }
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Erreur collecte page web {target.source_url}: {e}")
            raise

    async def _fetch_html_content(self, url: str) -> str:
        """Récupère le contenu HTML d'une URL"""
        try:
            # Tentative avec requête HTTP simple
            try:
                async with self.session.get(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    },
                    timeout=aiohttp.ClientTimeout(30)
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
            except (aiohttp.ClientError, asyncio.TimeoutError):
                # Fallback avec Selenium pour JavaScript
                return await self._fetch_with_selenium(url)
                
        except Exception as e:
            self.logger.error(f"Erreur récupération HTML {url}: {e}")
            raise

    async def _fetch_with_selenium(self, url: str) -> str:
        """Récupère le contenu avec Selenium (pour JavaScript)"""
        try:
            # Exécution dans le pool de threads
            loop = asyncio.get_event_loop()
            html_content = await loop.run_in_executor(
                self.executor,
                self._selenium_fetch,
                url
            )
            return html_content
            
        except Exception as e:
            self.logger.error(f"Erreur Selenium {url}: {e}")
            raise

    def _selenium_fetch(self, url: str) -> str:
        """Récupération Selenium synchrone"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Attente du chargement
            driver.implicitly_wait(10)
            
            # Gestion du lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            asyncio.sleep(2)
            
            html_content = driver.page_source
            return html_content
            
        finally:
            if driver:
                driver.quit()

    async def _extract_with_template(
        self,
        html_content: str,
        extraction_rules: List[ExtractionRule]
    ) -> Dict[str, Any]:
        """Extrait les données avec un template"""
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_data = {}
        
        for rule in extraction_rules:
            try:
                values = self._apply_extraction_rule(soup, rule)
                
                # Transformation des données
                if rule.transformation_rules:
                    values = self._apply_transformations(values, rule.transformation_rules)
                
                # Validation
                if rule.validation_rules:
                    values = self._apply_validations(values, rule.validation_rules)
                
                # Assignation
                if values or not rule.is_required:
                    extracted_data[rule.field_name] = values if len(values) != 1 else values[0]
                elif rule.default_value is not None:
                    extracted_data[rule.field_name] = rule.default_value
                elif rule.is_required:
                    self.logger.warning(f"Champ requis manquant: {rule.field_name}")
                
            except Exception as e:
                self.logger.error(f"Erreur extraction champ {rule.field_name}: {e}")
                if rule.is_required:
                    raise
        
        return extracted_data

    def _apply_extraction_rule(self, soup: BeautifulSoup, rule: ExtractionRule) -> List[Any]:
        """Applique une règle d'extraction"""
        values = []
        
        try:
            if rule.selector_type == 'css':
                elements = soup.select(rule.selector)
            elif rule.selector_type == 'xpath':
                # BeautifulSoup ne supporte pas XPath directement
                # Conversion CSS si possible ou utilisation lxml
                elements = soup.select(rule.selector)
            elif rule.selector_type == 'regex':
                pattern = re.compile(rule.selector)
                matches = pattern.findall(str(soup))
                return matches
            else:
                raise ValueError(f"Type de sélecteur non supporté: {rule.selector_type}")
            
            # Extraction des valeurs selon le type de données
            for element in elements:
                if rule.data_type == 'text':
                    value = element.get_text(strip=True)
                elif rule.data_type == 'url':
                    value = element.get('href') or element.get('src')
                elif rule.data_type == 'image':
                    value = element.get('src') or element.get('data-src')
                elif rule.data_type == 'number':
                    text = element.get_text(strip=True)
                    value = self._extract_number(text)
                elif rule.data_type == 'date':
                    text = element.get_text(strip=True)
                    value = self._parse_date(text)
                else:
                    value = element.get_text(strip=True)
                
                if value:
                    values.append(value)
            
            return values
            
        except Exception as e:
            self.logger.error(f"Erreur application règle {rule.field_name}: {e}")
            return []

    def _extract_number(self, text: str) -> Optional[float]:
        """Extrait un nombre d'un texte"""
        try:
            # Nettoyage du texte
            clean_text = re.sub(r'[^\d.,]', '', text)
            clean_text = clean_text.replace(',', '.')
            
            if clean_text:
                return float(clean_text)
        except:
            pass
        return None

    def _parse_date(self, text: str) -> Optional[str]:
        """
Parse une date depuis un texte"""
        try:
            from dateutil import parser
            parsed_date = parser.parse(text)
            return parsed_date.isoformat()
        except:
            return None

    def _apply_transformations(self, values: List[Any], transformations: List[str]) -> List[Any]:
        """
Applique des transformations aux valeurs"""
        for transformation in transformations:
            if transformation == 'lowercase':
                values = [str(v).lower() if v else v for v in values]
            elif transformation == 'uppercase':
                values = [str(v).upper() if v else v for v in values]
            elif transformation == 'strip':
                values = [str(v).strip() if v else v for v in values]
            elif transformation == 'unique':
                values = list(set(values))
        
        return values

    def _apply_validations(self, values: List[Any], validations: List[str]) -> List[Any]:
        """
Applique des validations aux valeurs"""
        validated_values = []
        
        for value in values:
            valid = True
            
            for validation in validations:
                if validation == 'not_empty' and not value:
                    valid = False
                    break
                elif validation == 'url' and not self._is_valid_url(str(value)):
                    valid = False
                    break
                elif validation == 'email' and not self._is_valid_email(str(value)):
                    valid = False
                    break
            
            if valid:
                validated_values.append(value)
        
        return validated_values

    def _is_valid_url(self, url: str) -> bool:
        """
Valide une URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _is_valid_email(self, email: str) -> bool:
        """
Valide un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    async def _extract_generic_web_data(self, html_content: str) -> Dict[str, Any]:
        """
Extraction générique de données web"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        data = {
            'title': '',
            'headings': [],
            'paragraphs': [],
            'links': [],
            'images': [],
            'meta_tags': {},
            'scripts': [],
            'forms': []
        }
        
        # Titre
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)
        
        # En-têtes
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            for heading in headings:
                data['headings'].append({
                    'level': level,
                    'text': heading.get_text(strip=True)
                })
        
        # Paragraphes
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                data['paragraphs'].append(text)
        
        # Liens
        links = soup.find_all('a', href=True)
        for link in links:
            data['links'].append({
                'url': link['href'],
                'text': link.get_text(strip=True)
            })
        
        # Images
        images = soup.find_all('img')
        for img in images:
            data['images'].append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                data['meta_tags'][name] = content
        
        return data

    async def _harvest_api(self, target: HarvestingTarget) -> Dict[str, Any]:
        """
Collecte depuis une API"""
        try:
            # Configuration de la requête
            method = target.extraction_rules.get('method', 'GET')
            headers = target.extraction_rules.get('headers', {})
            params = target.extraction_rules.get('params', {})
            data = target.extraction_rules.get('data', {})
            
            # Requête API
            async with self.session.request(
                method=method,
                url=target.source_url,
                headers=headers,
                params=params,
                json=data if method in ['POST', 'PUT'] else None,
                timeout=aiohttp.ClientTimeout(30)
            ) as response:
                
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'application/json' in content_type:
                        api_data = await response.json()
                    else:
                        api_data = {'raw_content': await response.text()}
                    
                    # Application de filtres si spécifiés
                    if 'filters' in target.extraction_rules:
                        api_data = self._apply_api_filters(api_data, target.extraction_rules['filters'])
                    
                    return api_data
                else:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                
        except Exception as e:
            self.logger.error(f"Erreur collecte API {target.source_url}: {e}")
            raise

    def _apply_api_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Applique des filtres aux données API"""
        filtered_data = data
        
        # Filtres de champs
        if 'fields' in filters:
            filtered_data = {
                field: data.get(field) for field in filters['fields']
                if field in data
            }
        
        # Filtres de valeurs
        if 'conditions' in filters:
            for condition in filters['conditions']:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field in filtered_data:
                    if operator == 'equals' and filtered_data[field] != value:
                        del filtered_data[field]
                    elif operator == 'contains' and value not in str(filtered_data[field]):
                        del filtered_data[field]
        
        return filtered_data

    async def _harvest_rss_feed(self, target: HarvestingTarget) -> Dict[str, Any]:
        """
Collecte depuis un flux RSS"""
        try:
            import feedparser
            
            # Récupération du flux RSS
            async with self.session.get(target.source_url) as response:
                rss_content = await response.text()
            
            # Parse du flux RSS
            feed = feedparser.parse(rss_content)
            
            # Extraction des données
            rss_data = {
                'feed_info': {
                    'title': feed.feed.get('title', ''),
                    'description': feed.feed.get('description', ''),
                    'link': feed.feed.get('link', ''),
                    'updated': feed.feed.get('updated', '')
                },
                'entries': []
            }
            
            # Limitation du nombre d'entrées si spécifié
            max_entries = target.extraction_rules.get('max_entries', len(feed.entries))
            
            for entry in feed.entries[:max_entries]:
                entry_data = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': entry.get('published', ''),
                    'updated': entry.get('updated', ''),
                    'author': entry.get('author', ''),
                    'tags': [tag.term for tag in entry.get('tags', [])]
                }
                rss_data['entries'].append(entry_data)
            
            return rss_data
            
        except Exception as e:
            self.logger.error(f"Erreur collecte RSS {target.source_url}: {e}")
            raise

    async def _harvest_social_media(self, target: HarvestingTarget) -> Dict[str, Any]:
        """Collecte depuis les réseaux sociaux"""
        # Délégation aux APIs spécialisées ou scraping
        platform = target.extraction_rules.get('platform', '')
        
        if platform == 'youtube':
            return await self._harvest_youtube(target)
        elif platform == 'twitter':
            return await self._harvest_twitter(target)
        elif platform == 'instagram':
            return await self._harvest_instagram(target)
        else:
            # Fallback générique
            return await self._harvest_web_page(target)

    async def _harvest_youtube(self, target: HarvestingTarget) -> Dict[str, Any]:
        """
Collecte YouTube spécialisée"""
        try:
            # Extraction de l'ID de la vidéo ou chaîne depuis l'URL
            url = target.source_url
            data = {
                'platform': 'youtube',
                'url': url,
                'extraction_type': 'basic_scraping'
            }
            
            # Récupération du contenu de la page
            html_content = await self._fetch_html_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraction des métadonnées de base
            data.update({
                'title': self._extract_youtube_title(soup),
                'description': self._extract_youtube_description(soup),
                'channel': self._extract_youtube_channel(soup),
                'views': self._extract_youtube_views(soup),
                'upload_date': self._extract_youtube_date(soup),
                'thumbnails': self._extract_youtube_thumbnails(soup)
            })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Erreur collecte YouTube {target.source_url}: {e}")
            # Fallback vers collecte web générique
            return await self._harvest_web_page(target)

    async def _harvest_twitter(self, target: HarvestingTarget) -> Dict[str, Any]:
        """Collecte Twitter spécialisée"""
        try:
            url = target.source_url
            data = {
                'platform': 'twitter',
                'url': url,
                'extraction_type': 'basic_scraping'
            }
            
            # Récupération du contenu de la page
            html_content = await self._fetch_html_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraction des métadonnées de base
            data.update({
                'username': self._extract_twitter_username(soup),
                'tweet_text': self._extract_twitter_text(soup),
                'tweet_date': self._extract_twitter_date(soup),
                'retweets': self._extract_twitter_retweets(soup),
                'likes': self._extract_twitter_likes(soup),
                'media': self._extract_twitter_media(soup)
            })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Erreur collecte Twitter {target.source_url}: {e}")
            # Fallback vers collecte web générique
            return await self._harvest_web_page(target)

    async def _harvest_instagram(self, target: HarvestingTarget) -> Dict[str, Any]:
        """Collecte Instagram spécialisée"""
        try:
            url = target.source_url
            data = {
                'platform': 'instagram',
                'url': url,
                'extraction_type': 'basic_scraping'
            }
            
            # Récupération du contenu de la page
            html_content = await self._fetch_html_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraction des métadonnées de base
            data.update({
                'username': self._extract_instagram_username(soup),
                'caption': self._extract_instagram_caption(soup),
                'post_date': self._extract_instagram_date(soup),
                'likes': self._extract_instagram_likes(soup),
                'comments': self._extract_instagram_comments(soup),
                'media_urls': self._extract_instagram_media(soup)
            })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Erreur collecte Instagram {target.source_url}: {e}")
            # Fallback vers collecte web générique
            return await self._harvest_web_page(target)

    async def _harvest_generic(self, target: HarvestingTarget) -> Dict[str, Any]:
        """Collecte générique"""
        # Tentative de collecte générique basée sur le format
        if target.data_format == DataFormat.JSON:
            return await self._harvest_api(target)
        elif target.data_format == DataFormat.XML:
            return await self._harvest_rss_feed(target)
        else:
            return await self._harvest_web_page(target)

    async def _process_collected_data(
        self,
        target: HarvestingTarget,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Traite et valide les données collectées"""
        try:
            # Nettoyage des données
            cleaned_data = self._clean_data(raw_data)
            
            # Enrichissement avec analyse de contenu
            if target.extraction_rules.get('enable_content_analysis', False):
                enriched_data = await self._enrich_with_content_analysis(cleaned_data)
            else:
                enriched_data = cleaned_data
            
            # Validation finale
            validated_data = self.data_validator.validate(
                enriched_data,
                target.extraction_rules.get('validation_schema', {})
            )
            
            return validated_data
            
        except Exception as e:
            self.logger.error(f"Erreur traitement données: {e}")
            return raw_data

    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie les données"""
        cleaned = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Nettoyage des chaînes
                cleaned_value = value.strip()
                cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
                cleaned[key] = cleaned_value
            elif isinstance(value, list):
                # Nettoyage des listes
                cleaned[key] = [self._clean_data({'item': item})['item'] if isinstance(item, dict) else item for item in value]
            elif isinstance(value, dict):
                # Nettoyage récursif
                cleaned[key] = self._clean_data(value)
            else:
                cleaned[key] = value
        
        return cleaned

    async def _enrich_with_content_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
Enrichit avec analyse de contenu IA"""
        enriched = data.copy()
        
        # Analyse des textes
        text_fields = ['content', 'description', 'title', 'summary']
        for field in text_fields:
            if field in data and isinstance(data[field], str):
                try:
                    analysis = await self.content_analyzer.analyze_text(data[field])
                    enriched[f'{field}_analysis'] = analysis
                except Exception as e:
                    self.logger.error(f"Erreur analyse {field}: {e}")
        
        # Analyse des images
        if 'images' in data:
            for i, image in enumerate(data['images']):
                if isinstance(image, dict) and 'src' in image:
                    try:
                        image_analysis = await self.content_analyzer.analyze_image(image['src'])
                        enriched['images'][i]['analysis'] = image_analysis
                    except Exception as e:
                        self.logger.error(f"Erreur analyse image {i}: {e}")
        
        return enriched

    async def _save_harvested_data(
        self,
        target: HarvestingTarget,
        data: Dict[str, Any],
        harvest_id: str
    ) -> List[str]:
        """Sauvegarde les données collectées"""
        file_paths = []
        
        try:
            # Création des répertoires
            for dir_path in self.output_dirs.values():
                await self._ensure_directory_exists(dir_path)
            
            # Sauvegarde JSON brute
            json_path = f"{self.output_dirs['raw']}/{harvest_id}.json"
            await self._save_json_file(json_path, data)
            file_paths.append(json_path)
            
            # Sauvegarde CSV si structuré
            if self._is_tabular_data(data):
                csv_path = f"{self.output_dirs['processed']}/{harvest_id}.csv"
                await self._save_csv_file(csv_path, data)
                file_paths.append(csv_path)
            
            # Sauvegarde médias si présents
            media_paths = await self._save_media_files(target, data, harvest_id)
            file_paths.extend(media_paths)
            
            # Export personnalisé si configuré
            if target.output_config.get('custom_export'):
                custom_path = await self._save_custom_export(target, data, harvest_id)
                file_paths.append(custom_path)
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde données: {e}")
            return []

    async def _ensure_directory_exists(self, directory: str) -> None:
        """Assure l'existence d'un répertoire"""
        import os
        os.makedirs(directory, exist_ok=True)

    async def _save_json_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """
Sauvegarde un fichier JSON"""
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    def _is_tabular_data(self, data: Dict[str, Any]) -> bool:
        """
Vérifie si les données sont tabulaires"""
        # Vérification simple : présence d'une liste d'objets similaires
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                if all(isinstance(item, dict) for item in value):
                    return True
        return False

    async def _save_csv_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """
Sauvegarde un fichier CSV"""
        try:
            # Recherche de données tabulaires
            tabular_data = None
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    if all(isinstance(item, dict) for item in value):
                        tabular_data = value
                        break
            
            if tabular_data:
                df = pd.DataFrame(tabular_data)
                df.to_csv(file_path, index=False, encoding='utf-8')
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde CSV: {e}")

    async def _save_media_files(
        self,
        target: HarvestingTarget,
        data: Dict[str, Any],
        harvest_id: str
    ) -> List[str]:
        """Sauvegarde les fichiers média"""
        media_paths = []
        
        try:
            # Extraction des URLs de médias
            media_urls = self._extract_media_urls(data)
            
            for i, url in enumerate(media_urls):
                try:
                    # Téléchargement du média
                    file_path = await self._download_media_file(url, harvest_id, i)
                    if file_path:
                        media_paths.append(file_path)
                        
                except Exception as e:
                    self.logger.error(f"Erreur téléchargement média {url}: {e}")
            
            return media_paths
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde médias: {e}")
            return []

    def _extract_media_urls(self, data: Dict[str, Any]) -> List[str]:
        """Extrait les URLs de médias des données"""
        urls = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['src', 'url', 'href'] and isinstance(value, str):
                        if self._is_media_url(value):
                            urls.append(value)
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(data)
        return list(set(urls))

    def _is_media_url(self, url: str) -> bool:
        """
Vérifie si une URL pointe vers un média"""
        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov', '.mp3', '.wav']
        return any(url.lower().endswith(ext) for ext in media_extensions)

    async def _download_media_file(self, url: str, harvest_id: str, index: int) -> Optional[str]:
        """
Télécharge un fichier média"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    # Détermination de l'extension
                    content_type = response.headers.get('content-type', '')
                    extension = mimetypes.guess_extension(content_type) or '.bin'
                    
                    # Nom du fichier
                    filename = f"{harvest_id}_media_{index}{extension}"
                    file_path = f"{self.output_dirs['media']}/{filename}"
                    
                    # Sauvegarde
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    return file_path
                    
        except Exception as e:
            self.logger.error(f"Erreur téléchargement {url}: {e}")
        
        return None

    async def _save_custom_export(
        self,
        target: HarvestingTarget,
        data: Dict[str, Any],
        harvest_id: str
    ) -> str:
        """Sauvegarde avec export personnalisé"""
        export_format = target.output_config.get('export_format', 'json')
        filename = f"{harvest_id}_export.{export_format}"
        file_path = f"{self.output_dirs['exports']}/{filename}"
        
        if export_format == 'xml':
            await self._save_xml_file(file_path, data)
        elif export_format == 'excel':
            await self._save_excel_file(file_path, data)
        else:
            await self._save_json_file(file_path, data)
        
        return file_path

    async def _save_xml_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """Sauvegarde XML"""
        try:
            import xml.etree.ElementTree as ET
            
            def dict_to_xml(obj, parent=None):
                if parent is None:
                    root = ET.Element('data')
                    dict_to_xml(obj, root)
                    return root
                
                for key, value in obj.items():
                    element = ET.SubElement(parent, str(key))
                    if isinstance(value, dict):
                        dict_to_xml(value, element)
                    elif isinstance(value, list):
                        for item in value:
                            item_elem = ET.SubElement(element, 'item')
                            if isinstance(item, dict):
                                dict_to_xml(item, item_elem)
                            else:
                                item_elem.text = str(item)
                    else:
                        element.text = str(value)
            
            root = dict_to_xml(data)
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde XML: {e}")

    async def _save_excel_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """Sauvegarde Excel"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Chaque liste d'objets devient une feuille
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        if all(isinstance(item, dict) for item in value):
                            df = pd.DataFrame(value)
                            sheet_name = key[:31]  # Limite Excel
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Feuille générale si pas de données tabulaires
                if not any(isinstance(v, list) for v in data.values()):
                    df = pd.DataFrame([data])
                    df.to_excel(writer, sheet_name='Summary', index=False)
                    
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde Excel: {e}")

    def _generate_harvest_metadata(
        self,
        target: HarvestingTarget,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère les métadonnées de collecte"""
        return {
            'target_id': target.target_id,
            'source_url': target.source_url,
            'source_type': target.source_type.value,
            'data_format': target.data_format.value,
            'harvest_timestamp': datetime.now().isoformat(),
            'data_size': len(json.dumps(data, default=str)),
            'fields_count': len(data),
            'has_media': bool(self._extract_media_urls(data)),
            'extraction_rules_used': list(target.extraction_rules.keys())
        }

    def get_harvesting_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de collecte
        
        Returns:
            Dict[str, Any]: Statut global
        """
        total_targets = len(self.harvesting_targets)
        completed_harvests = len([r for r in self.harvest_results.values() if r.status == HarvestingStatus.COMPLETED])
        failed_harvests = len([r for r in self.harvest_results.values() if r.status == HarvestingStatus.FAILED])
        
        return {
            'total_targets': total_targets,
            'completed_harvests': completed_harvests,
            'failed_harvests': failed_harvests,
            'success_rate': (completed_harvests / max(completed_harvests + failed_harvests, 1)) * 100,
            'targets_by_status': {
                status.value: len([t for t in self.harvesting_targets.values() if t.status == status])
                for status in HarvestingStatus
            },
            'recent_results': [
                {
                    'harvest_id': result.harvest_id,
                    'target_id': result.target_id,
                    'status': result.status.value,
                    'processing_time': result.processing_time,
                    'timestamp': result.timestamp.isoformat()
                }
                for result in sorted(self.harvest_results.values(), key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }

    async def stop_harvesting(self) -> None:
        """
Arrête toutes les collectes"""
        for target in self.harvesting_targets.values():
            if target.status == HarvestingStatus.RUNNING:
                target.status = HarvestingStatus.CANCELLED
        
        if self.session:
            await self.session.close()
        
        self.logger.info("Collecte de données arrêtée")

    # Helper methods for social media data extraction
    def _extract_youtube_title(self, soup: BeautifulSoup) -> str:
        """Extrait le titre d'une vidéo YouTube"""
        try:
            # Recherche dans les métadonnées
            title_tag = soup.find('meta', property='og:title')
            if title_tag:
                return title_tag.get('content', '')
            
            # Recherche dans le titre de la page
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text(strip=True)
                
            return ""
        except Exception:
            return ""
    
    def _extract_youtube_description(self, soup: BeautifulSoup) -> str:
        """Extrait la description d'une vidéo YouTube"""
        try:
            desc_tag = soup.find('meta', property='og:description')
            if desc_tag:
                return desc_tag.get('content', '')
            return ""
        except Exception:
            return ""
    
    def _extract_youtube_channel(self, soup: BeautifulSoup) -> str:
        """Extrait le nom de la chaîne YouTube"""
        try:
            channel_tag = soup.find('meta', {'name': 'author'})
            if channel_tag:
                return channel_tag.get('content', '')
            return ""
        except Exception:
            return ""
    
    def _extract_youtube_views(self, soup: BeautifulSoup) -> str:
        """Extrait le nombre de vues YouTube"""
        try:
            # Recherche de patterns de vues dans le HTML
            for script in soup.find_all('script'):
                if script.string and 'viewCount' in script.string:
                    # Simple extraction pattern, would need more sophisticated parsing
                    return "N/A"
            return "N/A"
        except Exception:
            return "N/A"
    
    def _extract_youtube_date(self, soup: BeautifulSoup) -> str:
        """Extrait la date de publication YouTube"""
        try:
            date_tag = soup.find('meta', {'itemprop': 'datePublished'})
            if date_tag:
                return date_tag.get('content', '')
            return ""
        except Exception:
            return ""
    
    def _extract_youtube_thumbnails(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les URLs des miniatures YouTube"""
        try:
            thumbnails = []
            thumb_tag = soup.find('meta', property='og:image')
            if thumb_tag:
                thumbnails.append(thumb_tag.get('content', ''))
            return thumbnails
        except Exception:
            return []
    
    def _extract_twitter_username(self, soup: BeautifulSoup) -> str:
        """
Extrait le nom d'utilisateur Twitter"""
        try:
            # Recherche dans les métadonnées Twitter
            username_tag = soup.find('meta', {'name': 'twitter:creator'})
            if username_tag:
                return username_tag.get('content', '').replace('@', '')
            return ""
        except Exception:
            return ""
    
    def _extract_twitter_text(self, soup: BeautifulSoup) -> str:
        """Extrait le texte du tweet"""
        try:
            desc_tag = soup.find('meta', property='og:description')
            if desc_tag:
                return desc_tag.get('content', '')
            return ""
        except Exception:
            return ""
    
    def _extract_twitter_date(self, soup: BeautifulSoup) -> str:
        """Extrait la date du tweet"""
        try:
            # Recherche dans les métadonnées structurées
            date_tag = soup.find('meta', {'name': 'twitter:label1'})
            if date_tag and 'time' in date_tag.get('content', '').lower():
                value_tag = soup.find('meta', {'name': 'twitter:data1'})
                if value_tag:
                    return value_tag.get('content', '')
            return ""
        except Exception:
            return ""
    
    def _extract_twitter_retweets(self, soup: BeautifulSoup) -> str:
        """Extrait le nombre de retweets"""
        try:
            # Pattern générique pour les métriques Twitter
            return "N/A"
        except Exception:
            return "N/A"
    
    def _extract_twitter_likes(self, soup: BeautifulSoup) -> str:
        """Extrait le nombre de likes"""
        try:
            return "N/A"
        except Exception:
            return "N/A"
    
    def _extract_twitter_media(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les URLs des médias Twitter"""
        try:
            media = []
            img_tag = soup.find('meta', property='og:image')
            if img_tag:
                media.append(img_tag.get('content', ''))
            return media
        except Exception:
            return []
    
    def _extract_instagram_username(self, soup: BeautifulSoup) -> str:
        """
Extrait le nom d'utilisateur Instagram"""
        try:
            # Recherche dans les métadonnées
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text()
                if '@' in title_text:
                    return title_text.split('@')[1].split()[0]
            return ""
        except Exception:
            return ""
    
    def _extract_instagram_caption(self, soup: BeautifulSoup) -> str:
        """Extrait la légende Instagram"""
        try:
            desc_tag = soup.find('meta', property='og:description')
            if desc_tag:
                return desc_tag.get('content', '')
            return ""
        except Exception:
            return ""
    
    def _extract_instagram_date(self, soup: BeautifulSoup) -> str:
        """Extrait la date de publication Instagram"""
        try:
            # Instagram utilise des structures complexes, extraction basique
            return ""
        except Exception:
            return ""
    
    def _extract_instagram_likes(self, soup: BeautifulSoup) -> str:
        """Extrait le nombre de likes Instagram"""
        try:
            return "N/A"
        except Exception:
            return "N/A"
    
    def _extract_instagram_comments(self, soup: BeautifulSoup) -> str:
        """Extrait le nombre de commentaires Instagram"""
        try:
            return "N/A"
        except Exception:
            return "N/A"
    
    def _extract_instagram_media(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les URLs des médias Instagram"""
        try:
            media = []
            img_tag = soup.find('meta', property='og:image')
            if img_tag:
                media.append(img_tag.get('content', ''))
            return media
        except Exception:
            return []

    async def __aenter__(self):
        """
Gestionnaire de contexte async"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Nettoyage async"""
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
