"""
SEO Analytics Crawler - Analyseur SEO et surveillance de positionnement
=====================================================================

Crawler spécialisé dans l'analyse SEO, le monitoring de positionnement
et la détection d'usage non autorisé via les moteurs de recherche.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, quote
import aiohttp
from bs4 import BeautifulSoup
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from ..ai.content_analysis import ContentAnalyzer
from ..security.fingerprint import ContentFingerprint
from ...utils.rate_limiter import RateLimiter
from ...utils.proxy_manager import ProxyManager


@dataclass
class SEOMetrics:
    """Métriques SEO d'un contenu"""
    url: str
    title: str
    meta_description: str
    keywords: List[str]
    h1_tags: List[str]
    h2_tags: List[str]
    image_count: int
    internal_links: int
    external_links: int
    page_load_time: float
    mobile_friendly: bool
    ssl_enabled: bool
    schema_markup: List[str]
    social_tags: Dict[str, str]
    word_count: int
    reading_time: int
    last_modified: Optional[datetime] = None


@dataclass
class SearchRanking:
    """Position dans les résultats de recherche"""
    query: str
    url: str
    position: int
    search_engine: str
    page_number: int
    snippet: str
    title: str
    featured_snippet: bool = False
    local_pack: bool = False
    knowledge_panel: bool = False
    timestamp: datetime = None


@dataclass
class CompetitorAnalysis:
    """Analyse de la concurrence"""
    competitor_url: str
    shared_keywords: List[str]
    ranking_comparison: Dict[str, Tuple[int, int]]  # keyword: (our_rank, their_rank)
    content_overlap: float
    backlink_comparison: Dict[str, int]
    traffic_estimate: int
    authority_score: float
    strengths: List[str]
    weaknesses: List[str]


class SEOAnalyticsCrawler:
    """
    Crawler avancé pour l'analyse SEO et la surveillance de positionnement
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le crawler SEO
        
        Args:
            config: Configuration du crawler
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Composants de base
        self.content_analyzer = ContentAnalyzer()
        self.fingerprint_engine = ContentFingerprint()
        self.rate_limiter = RateLimiter(
            max_requests=config.get('max_requests_per_minute', 30),
            window_seconds=60
        )
        self.proxy_manager = ProxyManager(config.get('proxy_config', {}))
        
        # Configuration Selenium
        self._setup_selenium_driver()
        
        # Données et cache
        self.monitored_urls: Set[str] = set()
        self.seo_metrics_cache: Dict[str, SEOMetrics] = {}
        self.ranking_history: Dict[str, List[SearchRanking]] = {}
        self.competitor_data: Dict[str, CompetitorAnalysis] = {}
        
        # Moteurs de recherche supportés
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'yahoo': 'https://search.yahoo.com/search?p={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}'
        }
        
        # User agents pour rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

    def _setup_selenium_driver(self) -> None:
        """Configure le driver Selenium pour JavaScript"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.selenium_driver = webdriver.Chrome(options=chrome_options)

    async def analyze_seo_metrics(self, url: str) -> Optional[SEOMetrics]:
        """
        Analyse complète des métriques SEO d'une page
        
        Args:
            url: URL à analyser
            
        Returns:
            Optional[SEOMetrics]: Métriques SEO extraites
        """



        try:
            # Vérification du cache
            if url in self.seo_metrics_cache:
                cached_metrics = self.seo_metrics_cache[url]
                # Utilise le cache si récent (< 24h)
                if datetime.now() - datetime.fromtimestamp(0) < timedelta(hours=24):
                    return cached_metrics
            
            await self.rate_limiter.acquire()
            
            # Récupération du contenu
            proxy = await self.proxy_manager.get_proxy()
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': np.random.choice(self.user_agents)}
                
                start_time = datetime.now()
                async with session.get(url, proxy=proxy, headers=headers) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    load_time = (datetime.now() - start_time).total_seconds()
            
            # Analyse du HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraction des métriques
            metrics = SEOMetrics(
                url=url,
                title=self._extract_title(soup),
                meta_description=self._extract_meta_description(soup),
                keywords=self._extract_keywords(soup),
                h1_tags=self._extract_h_tags(soup, 'h1'),
                h2_tags=self._extract_h_tags(soup, 'h2'),
                image_count=len(soup.find_all('img')),
                internal_links=self._count_internal_links(soup, url),
                external_links=self._count_external_links(soup, url),
                page_load_time=load_time,
                mobile_friendly=self._check_mobile_friendly(soup),
                ssl_enabled=url.startswith('https://'),
                schema_markup=self._extract_schema_markup(soup),
                social_tags=self._extract_social_tags(soup),
                word_count=self._count_words(soup),
                reading_time=self._calculate_reading_time(soup),
                last_modified=self._extract_last_modified(response.headers)
            )
            
            # Mise en cache
            self.seo_metrics_cache[url] = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse SEO de {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrait le titre de la page"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extrait la meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ''

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les mots-clés"""
        keywords = []
        
        # Meta keywords (obsolète mais parfois présent)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords.extend([kw.strip() for kw in meta_keywords.get('content', '').split(',')])
        
        # Analyse du contenu pour extraire les mots-clés principaux
        text_content = soup.get_text()
        # Implémentation simplifiée - utiliserait normalement du NLP
        words = re.findall(r'\b\w{4,}\b', text_content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 10 mots les plus fréquents
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords.extend([word for word, _ in top_words])
        
        return list(set(keywords))  # Déduplication

    def _extract_h_tags(self, soup: BeautifulSoup, tag_name: str) -> List[str]:
        """Extrait les balises H1/H2/etc."""
        tags = soup.find_all(tag_name)
        return [tag.get_text().strip() for tag in tags]

    def _count_internal_links(self, soup: BeautifulSoup, base_url: str) -> int:
        """Compte les liens internes"""
        base_domain = urlparse(base_url).netloc
        internal_count = 0
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/') or base_domain in href:
                internal_count += 1
        
        return internal_count

    def _count_external_links(self, soup: BeautifulSoup, base_url: str) -> int:
        """Compte les liens externes"""
        base_domain = urlparse(base_url).netloc
        external_count = 0
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and base_domain not in href:
                external_count += 1
        
        return external_count

    def _check_mobile_friendly(self, soup: BeautifulSoup) -> bool:
        """Vérifie la compatibilité mobile"""
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        return viewport_meta is not None

    def _extract_schema_markup(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les balises de données structurées"""
        schema_types = []
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if '@type' in data:
                    schema_types.append(data['@type'])
            except json.JSONDecodeError:
                continue
        
        # Microdata
        microdata_items = soup.find_all(attrs={'itemtype': True})
        for item in microdata_items:
            itemtype = item.get('itemtype', '')
            if itemtype.startswith('http://schema.org/'):
                schema_types.append(itemtype.split('/')[-1])
        
        return list(set(schema_types))

    def _extract_social_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrait les métadonnées sociales"""
        social_tags = {}
        
        # Open Graph
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            property_name = tag.get('property')
            content = tag.get('content')
            if property_name and content:
                social_tags[property_name] = content
        
        # Twitter Cards
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
        for tag in twitter_tags:
            name = tag.get('name')
            content = tag.get('content')
            if name and content:
                social_tags[name] = content
        
        return social_tags

    def _count_words(self, soup: BeautifulSoup) -> int:
        """Compte les mots dans le contenu"""
        # Suppression des scripts et styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def _calculate_reading_time(self, soup: BeautifulSoup) -> int:
        """Calcule le temps de lecture en minutes"""
        word_count = self._count_words(soup)
        # Moyenne de 200 mots par minute
        return max(1, word_count // 200)

    def _extract_last_modified(self, headers: Dict[str, str]) -> Optional[datetime]:
        """Extrait la date de dernière modification"""
        last_modified = headers.get('Last-Modified')
        if last_modified:
            try:
                return datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            except ValueError:
                pass
        return None

    async def track_search_rankings(
        self,
        target_urls: List[str],
        keywords: List[str],
        search_engines: List[str] = None
    ) -> Dict[str, List[SearchRanking]]:
        """
        Suit le positionnement dans les moteurs de recherche
        
        Args:
            target_urls: URLs à surveiller
            keywords: Mots-clés à suivre
            search_engines: Moteurs de recherche (par défaut: tous)
            
        Returns:
            Dict[str, List[SearchRanking]]: Résultats de positionnement
        """
        if search_engines is None:
            search_engines = list(self.search_engines.keys())
        
        all_rankings = {}
        
        for keyword in keywords:
            keyword_rankings = []
            
            for engine in search_engines:
                await self.rate_limiter.acquire()
                
                try:
                    rankings = await self._search_keyword_rankings(keyword, engine, target_urls)
                    keyword_rankings.extend(rankings)
                    
                    # Pause pour éviter la détection
                    await asyncio.sleep(np.random.uniform(2, 5))
                    
                except Exception as e:
                    self.logger.error(f"Erreur lors de la recherche '{keyword}' sur {engine}: {e}")
            
            all_rankings[keyword] = keyword_rankings
            
            # Sauvegarde dans l'historique
            if keyword not in self.ranking_history:
                self.ranking_history[keyword] = []
            self.ranking_history[keyword].extend(keyword_rankings)
        
        return all_rankings

    async def _search_keyword_rankings(
        self,
        keyword: str,
        search_engine: str,
        target_urls: List[str]
    ) -> List[SearchRanking]:
        """
        Recherche le positionnement pour un mot-clé spécifique
        
        Args:
            keyword: Mot-clé à rechercher
            search_engine: Moteur de recherche
            target_urls: URLs cibles à localiser
            
        Returns:
            List[SearchRanking]: Positions trouvées
        """
        rankings = []
        
        try:
            search_url = self.search_engines[search_engine].format(quote(keyword))
            
            # Utilisation de Selenium pour JavaScript et pagination
            self.selenium_driver.get(search_url)
            await asyncio.sleep(3)  # Attente du chargement
            
            # Parcours des pages de résultats
            for page in range(1, 4):  # 3 premières pages
                results = self._extract_search_results(self.selenium_driver.page_source)
                
                for position, result in enumerate(results, 1 + (page - 1) * 10):
                    result_url = result.get('url', '')
                    
                    # Vérification si l'URL correspond aux cibles
                    for target_url in target_urls:
                        if self._urls_match(result_url, target_url):
                            ranking = SearchRanking(
                                query=keyword,
                                url=result_url,
                                position=position,
                                search_engine=search_engine,
                                page_number=page,
                                snippet=result.get('snippet', ''),
                                title=result.get('title', ''),
                                featured_snippet=result.get('featured_snippet', False),
                                timestamp=datetime.now()
                            )
                            rankings.append(ranking)
                
                # Navigation vers la page suivante
                if page < 3:
                    next_button = self.selenium_driver.find_elements(By.CSS_SELECTOR, 'a[aria-label="Next"]')
                    if next_button:
                        next_button[0].click()
                        await asyncio.sleep(3)
                    else:
                        break
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de rankings: {e}")
        
        return rankings

    def _extract_search_results(self, page_source: str) -> List[Dict[str, Any]]:
        """
        Extrait les résultats de recherche depuis le HTML
        
        Args:
            page_source: Source HTML de la page
            
        Returns:
            List[Dict[str, Any]]: Résultats extraits
        """
        soup = BeautifulSoup(page_source, 'html.parser')
        results = []
        
        # Sélecteurs pour Google (à adapter pour autres moteurs)
        result_divs = soup.find_all('div', class_=re.compile(r'g\b'))
        
        for div in result_divs:
            try:
                # Extraction du lien
                link_tag = div.find('a')
                if not link_tag:
                    continue
                
                url = link_tag.get('href', '')
                if not url.startswith('http'):
                    continue
                
                # Extraction du titre
                title_tag = div.find('h3')
                title = title_tag.get_text() if title_tag else ''
                
                # Extraction du snippet
                snippet_div = div.find('div', class_=re.compile(r'VwiC3b'))
                snippet = snippet_div.get_text() if snippet_div else ''
                
                results.append({
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'featured_snippet': 'featured snippet' in div.get('class', [])
                })
                
            except Exception as e:
                self.logger.debug(f"Erreur extraction résultat: {e}")
                continue
        
        return results

    def _urls_match(self, url1: str, url2: str) -> bool:
        """
        Vérifie si deux URLs correspondent (domaine et chemin)
        
        Args:
            url1: Première URL
            url2: Deuxième URL
            
        Returns:
            bool: True si correspondance
        """



        try:
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)
            
            return (parsed1.netloc == parsed2.netloc and 
                    parsed1.path == parsed2.path)
        except Exception:
            return False

    async def analyze_competitors(
        self,
        target_url: str,
        competitor_urls: List[str],
        shared_keywords: List[str]
    ) -> Dict[str, CompetitorAnalysis]:
        """
        Analyse la concurrence pour les mots-clés partagés
        
        Args:
            target_url: URL à analyser
            competitor_urls: URLs des concurrents
            shared_keywords: Mots-clés communs
            
        Returns:
            Dict[str, CompetitorAnalysis]: Analyse par concurrent
        """
        competitor_analyses = {}
        
        # Analyse SEO de la cible
        target_metrics = await self.analyze_seo_metrics(target_url)
        if not target_metrics:
            return {}
        
        for competitor_url in competitor_urls:
            try:
                analysis = await self._analyze_single_competitor(
                    target_url, target_metrics, competitor_url, shared_keywords
                )
                if analysis:
                    competitor_analyses[competitor_url] = analysis
                    
            except Exception as e:
                self.logger.error(f"Erreur analyse concurrent {competitor_url}: {e}")
        
        return competitor_analyses

    async def _analyze_single_competitor(
        self,
        target_url: str,
        target_metrics: SEOMetrics,
        competitor_url: str,
        shared_keywords: List[str]
    ) -> Optional[CompetitorAnalysis]:
        """
        Analyse un concurrent spécifique
        
        Args:
            target_url: URL cible
            target_metrics: Métriques de la cible
            competitor_url: URL concurrent
            shared_keywords: Mots-clés partagés
            
        Returns:
            Optional[CompetitorAnalysis]: Analyse du concurrent
        """



        try:
            # Analyse SEO du concurrent
            competitor_metrics = await self.analyze_seo_metrics(competitor_url)
            if not competitor_metrics:
                return None
            
            # Comparaison des rankings
            ranking_comparison = await self._compare_rankings(
                target_url, competitor_url, shared_keywords
            )
            
            # Analyse du contenu
            content_overlap = await self._calculate_content_overlap(
                target_metrics, competitor_metrics
            )
            
            # Estimation du trafic et autorité
            traffic_estimate = await self._estimate_traffic(competitor_url)
            authority_score = await self._calculate_authority_score(competitor_metrics)
            
            # Identification des forces/faiblesses
            strengths, weaknesses = self._analyze_strengths_weaknesses(
                target_metrics, competitor_metrics
            )
            
            return CompetitorAnalysis(
                competitor_url=competitor_url,
                shared_keywords=shared_keywords,
                ranking_comparison=ranking_comparison,
                content_overlap=content_overlap,
                backlink_comparison={},  # Nécessiterait des outils tiers
                traffic_estimate=traffic_estimate,
                authority_score=authority_score,
                strengths=strengths,
                weaknesses=weaknesses
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse concurrent détaillé: {e}")
            return None

    async def _compare_rankings(
        self,
        target_url: str,
        competitor_url: str,
        keywords: List[str]
    ) -> Dict[str, Tuple[int, int]]:
        """
        Compare les rankings pour les mots-clés
        
        Args:
            target_url: URL cible
            competitor_url: URL concurrent
            keywords: Mots-clés à comparer
            
        Returns:
            Dict[str, Tuple[int, int]]: Comparaison des positions
        """
        comparison = {}
        
        for keyword in keywords:
            try:
                # Recherche des positions pour les deux URLs
                rankings = await self._search_keyword_rankings(
                    keyword, 'google', [target_url, competitor_url]
                )
                
                target_position = None
                competitor_position = None
                
                for ranking in rankings:
                    if self._urls_match(ranking.url, target_url):
                        target_position = ranking.position
                    elif self._urls_match(ranking.url, competitor_url):
                        competitor_position = ranking.position
                
                if target_position or competitor_position:
                    comparison[keyword] = (
                        target_position or 999,  # 999 = non trouvé
                        competitor_position or 999
                    )
                    
            except Exception as e:
                self.logger.error(f"Erreur comparaison ranking pour '{keyword}': {e}")
        
        return comparison

    async def _calculate_content_overlap(
        self,
        metrics1: SEOMetrics,
        metrics2: SEOMetrics
    ) -> float:
        """
        Calcule le chevauchement de contenu entre deux pages
        
        Args:
            metrics1: Métriques de la première page
            metrics2: Métriques de la deuxième page
            
        Returns:
            float: Score de chevauchement (0-1)
        """
        # Comparaison des mots-clés
        keywords1 = set(metrics1.keywords)
        keywords2 = set(metrics2.keywords)
        
        if not keywords1 and not keywords2:
            return 0.0
        
        common_keywords = keywords1 & keywords2
        total_keywords = keywords1 | keywords2
        
        keyword_overlap = len(common_keywords) / len(total_keywords) if total_keywords else 0
        
        # Comparaison des titres H1/H2
        h1_overlap = self._calculate_text_similarity(
            ' '.join(metrics1.h1_tags), ' '.join(metrics2.h1_tags)
        )
        
        h2_overlap = self._calculate_text_similarity(
            ' '.join(metrics1.h2_tags), ' '.join(metrics2.h2_tags)
        )
        
        # Score pondéré
        overlap_score = (keyword_overlap * 0.5) + (h1_overlap * 0.3) + (h2_overlap * 0.2)
        
        return min(1.0, overlap_score)

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité entre deux textes"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 0.0
        
        common_words = words1 & words2
        total_words = words1 | words2
        
        return len(common_words) / len(total_words) if total_words else 0.0

    async def _estimate_traffic(self, url: str) -> int:
        """
        Estime le trafic d'un site (méthode simplifiée)
        
        Args:
            url: URL à analyser
            
        Returns:
            int: Estimation du trafic mensuel
        """
        # Implémentation simplifiée basée sur les métriques SEO
        # En production, utiliserait des APIs comme SEMrush, Ahrefs, etc.
        
        try:
            metrics = await self.analyze_seo_metrics(url)
            if not metrics:
                return 0
            
            # Estimation basée sur plusieurs facteurs
            base_score = 1000  # Score de base
            
            # Facteurs positifs
            if metrics.ssl_enabled:
                base_score *= 1.2
            
            if metrics.mobile_friendly:
                base_score *= 1.3
            
            if metrics.schema_markup:
                base_score *= 1.1
            
            # Facteur basé sur le nombre de mots
            if metrics.word_count > 1000:
                base_score *= 1.5
            elif metrics.word_count > 500:
                base_score *= 1.2
            
            # Facteur basé sur les liens
            link_factor = min(2.0, (metrics.external_links + metrics.internal_links) / 50)
            base_score *= link_factor
            
            return int(base_score)
            
        except Exception as e:
            self.logger.error(f"Erreur estimation trafic: {e}")
            return 0

    async def _calculate_authority_score(self, metrics: SEOMetrics) -> float:
        """
        Calcule un score d'autorité basé sur les métriques SEO
        
        Args:
            metrics: Métriques SEO
            
        Returns:
            float: Score d'autorité (0-100)
        """
        score = 0.0
        
        # Facteurs techniques
        if metrics.ssl_enabled:
            score += 10
        if metrics.mobile_friendly:
            score += 10
        if metrics.page_load_time < 3.0:
            score += 15
        elif metrics.page_load_time < 5.0:
            score += 10
        
        # Facteurs de contenu
        if metrics.word_count > 1000:
            score += 15
        elif metrics.word_count > 500:
            score += 10
        
        if len(metrics.h1_tags) > 0:
            score += 5
        if len(metrics.h2_tags) > 2:
            score += 5
        
        # Facteurs de structure
        if metrics.meta_description:
            score += 5
        if len(metrics.keywords) > 5:
            score += 5
        
        # Facteurs de liens
        link_score = min(20, (metrics.external_links + metrics.internal_links) / 5)
        score += link_score
        
        # Schema markup
        if metrics.schema_markup:
            score += 10
        
        return min(100.0, score)

    def _analyze_strengths_weaknesses(
        self,
        target_metrics: SEOMetrics,
        competitor_metrics: SEOMetrics
    ) -> Tuple[List[str], List[str]]:
        """
        Identifie les forces et faiblesses du concurrent
        
        Args:
            target_metrics: Métriques de la cible
            competitor_metrics: Métriques du concurrent
            
        Returns:
            Tuple[List[str], List[str]]: Forces et faiblesses
        """
        strengths = []
        weaknesses = []
        
        # Comparaison des métriques
        if competitor_metrics.page_load_time < target_metrics.page_load_time:
            strengths.append("Vitesse de chargement supérieure")
        else:
            weaknesses.append("Vitesse de chargement inférieure")
        
        if competitor_metrics.word_count > target_metrics.word_count:
            strengths.append("Contenu plus riche")
        else:
            weaknesses.append("Contenu moins développé")
        
        if len(competitor_metrics.keywords) > len(target_metrics.keywords):
            strengths.append("Plus de mots-clés ciblés")
        else:
            weaknesses.append("Moins de mots-clés ciblés")
        
        if competitor_metrics.external_links > target_metrics.external_links:
            strengths.append("Plus de liens externes")
        else:
            weaknesses.append("Moins de liens externes")
        
        if len(competitor_metrics.schema_markup) > len(target_metrics.schema_markup):
            strengths.append("Meilleur balisage structuré")
        else:
            weaknesses.append("Balisage structuré insuffisant")
        
        return strengths, weaknesses

    async def monitor_seo_continuously(
        self,
        urls: List[str],
        keywords: List[str],
        competitors: List[str],
        interval_hours: int = 24
    ) -> None:
        """
        Surveillance SEO continue
        
        Args:
            urls: URLs à surveiller
            keywords: Mots-clés à suivre
            competitors: Concurrents à analyser
            interval_hours: Intervalle de surveillance
        """
        self.logger.info("Démarrage de la surveillance SEO continue")
        
        while True:
            try:
                # Analyse SEO des URLs
                for url in urls:
                    await self.analyze_seo_metrics(url)
                
                # Suivi des rankings
                await self.track_search_rankings(urls, keywords)
                
                # Analyse de la concurrence
                for url in urls:
                    competitor_analyses = await self.analyze_competitors(
                        url, competitors, keywords
                    )
                    self.competitor_data.update(competitor_analyses)
                
                # Génération de rapports
                await self._generate_seo_report()
                
                # Pause avant le prochain cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance SEO: {e}")
                await asyncio.sleep(300)  # Pause de 5 minutes en cas d'erreur

    async def _generate_seo_report(self) -> None:
        """Génère un rapport SEO"""



        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'monitored_urls': len(self.monitored_urls),
                'seo_metrics_count': len(self.seo_metrics_cache),
                'ranking_keywords': len(self.ranking_history),
                'competitors_analyzed': len(self.competitor_data),
                'recent_rankings': self._get_recent_rankings(),
                'top_performing_keywords': self._get_top_keywords(),
                'competitor_insights': self._get_competitor_insights()
            }
            
            # Sauvegarde du rapport
            report_file = f"/reports/seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Rapport SEO généré: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Erreur génération rapport SEO: {e}")

    def _get_recent_rankings(self) -> List[Dict[str, Any]]:
        """Récupère les rankings récents"""
        recent_rankings = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for keyword, rankings in self.ranking_history.items():
            for ranking in rankings:
                if ranking.timestamp and ranking.timestamp > cutoff_time:
                    recent_rankings.append({
                        'keyword': keyword,
                        'position': ranking.position,
                        'url': ranking.url,
                        'search_engine': ranking.search_engine,
                        'timestamp': ranking.timestamp.isoformat()
                    })
        
        return sorted(recent_rankings, key=lambda x: x['timestamp'], reverse=True)[:20]

    def _get_top_keywords(self) -> List[Dict[str, Any]]:
        """Récupère les mots-clés les plus performants"""
        keyword_performance = {}
        
        for keyword, rankings in self.ranking_history.items():
            if rankings:
                best_position = min(r.position for r in rankings)
                avg_position = sum(r.position for r in rankings) / len(rankings)
                
                keyword_performance[keyword] = {
                    'keyword': keyword,
                    'best_position': best_position,
                    'average_position': avg_position,
                    'tracking_count': len(rankings)
                }
        
        # Tri par meilleure position
        top_keywords = sorted(
            keyword_performance.values(),
            key=lambda x: x['best_position']
        )[:10]
        
        return top_keywords

    def _get_competitor_insights(self) -> List[Dict[str, Any]]:
        """Récupère les insights sur les concurrents"""
        insights = []
        
        for competitor_url, analysis in self.competitor_data.items():
            insights.append({
                'competitor_url': competitor_url,
                'authority_score': analysis.authority_score,
                'traffic_estimate': analysis.traffic_estimate,
                'content_overlap': analysis.content_overlap,
                'strengths_count': len(analysis.strengths),
                'weaknesses_count': len(analysis.weaknesses),
                'shared_keywords_count': len(analysis.shared_keywords)
            })
        
        return sorted(insights, key=lambda x: x['authority_score'], reverse=True)

    def get_seo_dashboard_data(self) -> Dict[str, Any]:
        """
        Retourne les données pour le dashboard SEO
        
        Returns:
            Dict[str, Any]: Données du dashboard
        """



        return {
            'overview': {
                'monitored_urls': len(self.monitored_urls),
                'tracked_keywords': len(self.ranking_history),
                'competitors_monitored': len(self.competitor_data),
                'last_update': datetime.now().isoformat()
            },
            'recent_rankings': self._get_recent_rankings()[:5],
            'top_keywords': self._get_top_keywords()[:5],
            'competitor_summary': self._get_competitor_insights()[:3],
            'alerts': self._get_seo_alerts()
        }

    def _get_seo_alerts(self) -> List[Dict[str, Any]]:
        """Génère des alertes SEO"""
        alerts = []
        
        # Alertes de chute de ranking
        for keyword, rankings in self.ranking_history.items():
            if len(rankings) >= 2:
                recent_ranking = rankings[-1]
                previous_ranking = rankings[-2]
                
                if recent_ranking.position > previous_ranking.position + 5:
                    alerts.append({
                        'type': 'ranking_drop',
                        'severity': 'high',
                        'message': f"Chute de ranking pour '{keyword}': {previous_ranking.position} → {recent_ranking.position}",
                        'keyword': keyword,
                        'timestamp': recent_ranking.timestamp.isoformat() if recent_ranking.timestamp else None
                    })
        
        # Alertes de problèmes techniques
        for url, metrics in self.seo_metrics_cache.items():
            if metrics.page_load_time > 5.0:
                alerts.append({
                    'type': 'performance_issue',
                    'severity': 'medium',
                    'message': f"Temps de chargement élevé pour {url}: {metrics.page_load_time:.1f}s",
                    'url': url,
                    'load_time': metrics.page_load_time
                })
            
            if not metrics.mobile_friendly:
                alerts.append({
                    'type': 'mobile_issue',
                    'severity': 'high',
                    'message': f"Page non-responsive détectée: {url}",
                    'url': url
                })
        
        return sorted(alerts, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['severity']], reverse=True)[:10]

    def __del__(self):
        """Nettoyage lors de la destruction"""



        try:
            if hasattr(self, 'selenium_driver'):
                self.selenium_driver.quit()
        except Exception:
            pass
