"""Social Media Tracker - Surveillance avancée des réseaux sociaux
==============================================================

Tracker spécialisé pour la surveillance automatisée des plateformes
de réseaux sociaux et détection de violations de contenu.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from bs4 import BeautifulSoup
import tweepy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import instaloader
import yt_dlp

from ..ai.content_analysis import ContentAnalyzer
from ..security.fingerprint import ContentFingerprint
from ...utils.rate_limiter import RateLimiter
from ...utils.proxy_manager import ProxyManager
from ...utils.captcha_solver import CaptchaSolver


class SocialPlatform(Enum):
    """Plateformes de réseaux sociaux supportées"""    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"


@dataclass
class SocialContent:
    """Contenu détecté sur réseau social"""    platform: SocialPlatform
    content_id: str
    url: str
    title: str
    description: str
    author: str
    author_id: str
    upload_date: datetime
    view_count: int
    like_count: int
    share_count: int
    comment_count: int
    content_type: str  # 'video', 'audio', 'image', 'text'
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class ViolationDetection:
    """Détection de violation sur réseau social"""    original_content: SocialContent
    violating_content: SocialContent
    similarity_score: float
    violation_confidence: float
    detection_method: str
    detected_at: datetime
    evidence_collected: bool = False
    takedown_initiated: bool = False


class SocialMediaTracker:
    """    Tracker avancé pour surveillance des réseaux sociaux
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialise le tracker de réseaux sociaux
        
        Args:
            config: Configuration du tracker
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des composants
        self.content_analyzer = ContentAnalyzer()
        self.fingerprint_engine = ContentFingerprint()
        self.rate_limiter = RateLimiter(
            max_requests=config.get('max_requests_per_minute', 30),
            window_seconds=60
        )
        self.proxy_manager = ProxyManager(config.get('proxy_config', {}))
        self.captcha_solver = CaptchaSolver(config.get('captcha_config', {}))
        
        # Cache et données
        self.tracked_content: Dict[str, SocialContent] = {}
        self.detected_violations: List[ViolationDetection] = []
        self.platform_cookies: Dict[SocialPlatform, Dict[str, str]] = {}
        
        # Configuration des APIs
        self._initialize_platform_apis()
        
        # Patterns de reconnaissance
        self.platform_patterns = {
            SocialPlatform.YOUTUBE: [
                r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
                r'https?://youtu\.be/([a-zA-Z0-9_-]+)'
            ],
            SocialPlatform.TIKTOK: [
                r'https?://(?:www\.)?tiktok\.com/@([^/]+)/video/(\d+)',
                r'https?://vm\.tiktok\.com/([a-zA-Z0-9]+)'
            ],
            SocialPlatform.INSTAGRAM: [
                r'https?://(?:www\.)?instagram\.com/p/([a-zA-Z0-9_-]+)',
                r'https?://(?:www\.)?instagram\.com/reel/([a-zA-Z0-9_-]+)'
            ],
            SocialPlatform.TWITTER: [
                r'https?://(?:www\.)?twitter\.com/([^/]+)/status/(\d+)',
                r'https?://(?:www\.)?x\.com/([^/]+)/status/(\d+)'
            ]
        }

    def _initialize_platform_apis(self) -> None:
        """        Initialise les APIs des plateformes
        """        try:
            # Twitter API
            if self.config.get('twitter_api_key'):
                self.twitter_api = tweepy.Client(
                    bearer_token=self.config['twitter_bearer_token'],
                    consumer_key=self.config['twitter_api_key'],
                    consumer_secret=self.config['twitter_api_secret'],
                    access_token=self.config['twitter_access_token'],
                    access_token_secret=self.config['twitter_access_secret']
                )
            
            # Instagram Loader
            self.instagram_loader = instaloader.Instaloader()
            
            # Configuration Selenium pour les plateformes nécessitant du scraping
            self._setup_selenium_driver()
            
            self.logger.info("APIs des plateformes initialisées")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation des APIs: {e}")

    def _setup_selenium_driver(self) -> None:
        """        Configure le driver Selenium
        """        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.selenium_driver = webdriver.Chrome(options=chrome_options)

    async def track_content_across_platforms(
        self, 
        original_content: SocialContent,
        search_keywords: List[str]
    ) -> List[ViolationDetection]:
        """        Traque le contenu à travers toutes les plateformes
        
        Args:
            original_content: Contenu original à protéger
            search_keywords: Mots-clés de recherche
            
        Returns:
            List[ViolationDetection]: Violations détectées
        """        violations = []
        
        # Enregistrement du contenu original
        self.tracked_content[original_content.content_id] = original_content
        
        # Recherche sur chaque plateforme
        platforms_to_search = [
            SocialPlatform.YOUTUBE,
            SocialPlatform.TIKTOK,
            SocialPlatform.INSTAGRAM,
            SocialPlatform.TWITTER,
            SocialPlatform.FACEBOOK
        ]
        
        tasks = []
        for platform in platforms_to_search:
            if platform != original_content.platform:  # Éviter la plateforme d'origine
                task = asyncio.create_task(
                    self._search_platform_for_content(
                        platform, original_content, search_keywords
                    )
                )
                tasks.append(task)
        
        # Exécution parallèle des recherches
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyse des résultats
        for result in platform_results:
            if isinstance(result, list):
                violations.extend(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Erreur lors de la recherche: {result}")
        
        # Sauvegarde des violations détectées
        self.detected_violations.extend(violations)
        
        return violations

    async def _search_platform_for_content(
        self,
        platform: SocialPlatform,
        original_content: SocialContent,
        search_keywords: List[str]
    ) -> List[ViolationDetection]:
        """        Recherche du contenu sur une plateforme spécifique
        
        Args:
            platform: Plateforme à rechercher
            original_content: Contenu original
            search_keywords: Mots-clés de recherche
            
        Returns:
            List[ViolationDetection]: Violations trouvées
        """        violations = []
        
        try:
            await self.rate_limiter.acquire()
            
            # Recherche selon la plateforme
            found_contents = []
            
            if platform == SocialPlatform.YOUTUBE:
                found_contents = await self._search_youtube(search_keywords)
            elif platform == SocialPlatform.TIKTOK:
                found_contents = await self._search_tiktok(search_keywords)
            elif platform == SocialPlatform.INSTAGRAM:
                found_contents = await self._search_instagram(search_keywords)
            elif platform == SocialPlatform.TWITTER:
                found_contents = await self._search_twitter(search_keywords)
            elif platform == SocialPlatform.FACEBOOK:
                found_contents = await self._search_facebook(search_keywords)
            
            # Analyse de similarité pour chaque contenu trouvé
            for found_content in found_contents:
                violation = await self._analyze_potential_violation(
                    original_content, found_content
                )
                
                if violation:
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche sur {platform.value}: {e}")
            return []

    async def _search_youtube(self, keywords: List[str]) -> List[SocialContent]:
        """        Recherche sur YouTube
        
        Args:
            keywords: Mots-clés de recherche
            
        Returns:
            List[SocialContent]: Contenus trouvés
        """        contents = []
        
        try:
            for keyword in keywords:
                search_query = f"https://www.youtube.com/results?search_query={keyword}"
                
                # Utilisation de yt-dlp pour l'extraction
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'default_search': 'ytsearch10:'
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    search_results = ydl.extract_info(keyword, download=False)
                    
                    if 'entries' in search_results:
                        for entry in search_results['entries']:
                            content = await self._extract_youtube_content(entry)
                            if content:
                                contents.append(content)
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Erreur recherche YouTube: {e}")
            return []

    async def _extract_youtube_content(self, entry: Dict[str, Any]) -> Optional[SocialContent]:
        """        Extrait les informations d'un contenu YouTube
        
        Args:
            entry: Entrée YouTube
            
        Returns:
            Optional[SocialContent]: Contenu extrait
        """        try:
            return SocialContent(
                platform=SocialPlatform.YOUTUBE,
                content_id=entry.get('id', ''),
                url=f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                title=entry.get('title', ''),
                description=entry.get('description', ''),
                author=entry.get('uploader', ''),
                author_id=entry.get('uploader_id', ''),
                upload_date=datetime.fromtimestamp(entry.get('timestamp', 0)) if entry.get('timestamp') else datetime.now(),
                view_count=entry.get('view_count', 0),
                like_count=entry.get('like_count', 0),
                share_count=0,  # Non disponible
                comment_count=entry.get('comment_count', 0),
                content_type='video',
                thumbnail_url=entry.get('thumbnail', ''),
                duration=entry.get('duration', 0),
                tags=entry.get('tags', []),
                metadata=entry
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction YouTube: {e}")
            return None

    async def _search_tiktok(self, keywords: List[str]) -> List[SocialContent]:
        """        Recherche sur TikTok
        
        Args:
            keywords: Mots-clés de recherche
            
        Returns:
            List[SocialContent]: Contenus trouvés
        """        contents = []
        
        try:
            for keyword in keywords:
                # Recherche via scraping web (TikTok n'a pas d'API publique)
                search_url = f"https://www.tiktok.com/search?q={keyword}"
                
                proxy = await self.proxy_manager.get_proxy()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        search_url,
                        proxy=proxy,
                        headers=self._get_tiktok_headers()
                    ) as response:
                        if response.status == 200:
                            html = await response.text()
                            parsed_contents = await self._parse_tiktok_search_results(html)
                            contents.extend(parsed_contents)
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Erreur recherche TikTok: {e}")
            return []

    async def _parse_tiktok_search_results(self, html: str) -> List[SocialContent]:
        """        Parse les résultats de recherche TikTok
        
        Args:
            html: HTML de la page de résultats
            
        Returns:
            List[SocialContent]: Contenus parsés
        """        contents = []
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Extraction des données JSON embarquées
            script_tags = soup.find_all('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    # Parse les données TikTok spécifiques
                    # (Structure complexe, nécessite adaptation)
                    pass
                except json.JSONDecodeError:
                    continue
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Erreur parsing TikTok: {e}")
            return []

    async def _search_instagram(self, keywords: List[str]) -> List[SocialContent]:
        """        Recherche sur Instagram
        
        Args:
            keywords: Mots-clés de recherche
            
        Returns:
            List[SocialContent]: Contenus trouvés
        """        contents = []
        
        try:
            for keyword in keywords:
                # Utilisation d'Instaloader pour la recherche
                posts = instaloader.Hashtag.from_name(
                    self.instagram_loader.context, keyword
                ).get_posts()
                
                count = 0
                for post in posts:
                    if count >= 20:  # Limite pour éviter le rate limiting
                        break
                    
                    content = await self._extract_instagram_content(post)
                    if content:
                        contents.append(content)
                    
                    count += 1
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Erreur recherche Instagram: {e}")
            return []

    async def _extract_instagram_content(self, post) -> Optional[SocialContent]:
        """        Extrait les informations d'un post Instagram
        
        Args:
            post: Post Instagram
            
        Returns:
            Optional[SocialContent]: Contenu extrait
        """        try:
            return SocialContent(
                platform=SocialPlatform.INSTAGRAM,
                content_id=post.shortcode,
                url=f"https://www.instagram.com/p/{post.shortcode}/",
                title=post.caption or '',
                description=post.caption or '',
                author=post.owner_username,
                author_id=str(post.owner_id),
                upload_date=post.date,
                view_count=post.video_view_count if post.is_video else 0,
                like_count=post.likes,
                share_count=0,  # Non disponible
                comment_count=post.comments,
                content_type='video' if post.is_video else 'image',
                thumbnail_url=post.url,
                duration=post.video_duration if post.is_video else None,
                tags=post.caption_hashtags,
                metadata={
                    'is_video': post.is_video,
                    'media_count': post.mediacount,
                    'tagged_users': post.tagged_users
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction Instagram: {e}")
            return None

    async def _search_twitter(self, keywords: List[str]) -> List[SocialContent]:
        """        Recherche sur Twitter
        
        Args:
            keywords: Mots-clés de recherche
            
        Returns:
            List[SocialContent]: Contenus trouvés
        """        contents = []
        
        try:
            if not hasattr(self, 'twitter_api'):
                return contents
            
            for keyword in keywords:
                # Recherche via l'API Twitter v2
                tweets = tweepy.Paginator(
                    self.twitter_api.search_recent_tweets,
                    query=keyword,
                    max_results=20,
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'attachments']
                ).flatten(limit=100)
                
                for tweet in tweets:
                    content = await self._extract_twitter_content(tweet)
                    if content:
                        contents.append(content)
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Erreur recherche Twitter: {e}")
            return []

    async def _extract_twitter_content(self, tweet) -> Optional[SocialContent]:
        """        Extrait les informations d'un tweet
        
        Args:
            tweet: Tweet
            
        Returns:
            Optional[SocialContent]: Contenu extrait
        """        try:
            metrics = tweet.public_metrics
            
            return SocialContent(
                platform=SocialPlatform.TWITTER,
                content_id=str(tweet.id),
                url=f"https://twitter.com/user/status/{tweet.id}",
                title=tweet.text[:100] + '...' if len(tweet.text) > 100 else tweet.text,
                description=tweet.text,
                author='',  # Nécessite une requête supplémentaire pour l'username
                author_id=str(tweet.author_id),
                upload_date=tweet.created_at,
                view_count=0,  # Non disponible
                like_count=metrics.get('like_count', 0),
                share_count=metrics.get('retweet_count', 0),
                comment_count=metrics.get('reply_count', 0),
                content_type='text',
                thumbnail_url=None,
                duration=None,
                tags=[],
                metadata={
                    'has_media': bool(tweet.attachments),
                    'lang': getattr(tweet, 'lang', 'en')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction Twitter: {e}")
            return None

    async def _search_facebook(self, keywords: List[str]) -> List[SocialContent]:
        """        Recherche sur Facebook (via scraping)
        
        Args:
            keywords: Mots-clés de recherche
            
        Returns:
            List[SocialContent]: Contenus trouvés
        """        contents = []
        
        try:
            # Facebook nécessite du scraping avancé avec gestion des cookies
            for keyword in keywords:
                search_url = f"https://www.facebook.com/search/posts/?q={keyword}"
                
                # Utilisation de Selenium pour le JavaScript
                self.selenium_driver.get(search_url)
                await asyncio.sleep(3)  # Attente du chargement
                
                # Extraction des posts
                posts = self.selenium_driver.find_elements(By.CSS_SELECTOR, '[data-pagelet="FeedUnit"]')
                
                for post in posts[:10]:  # Limite pour éviter les blocages
                    content = await self._extract_facebook_content(post)
                    if content:
                        contents.append(content)
            
            return contents
            
        except Exception as e:
            self.logger.error(f"Erreur recherche Facebook: {e}")
            return []

    async def _extract_facebook_content(self, post_element) -> Optional[SocialContent]:
        """        Extrait les informations d'un post Facebook
        
        Args:
            post_element: Élément DOM du post
            
        Returns:
            Optional[SocialContent]: Contenu extrait
        """        try:
            # Extraction basique des informations visibles
            text_elements = post_element.find_elements(By.CSS_SELECTOR, '[data-ad-preview="message"]')
            text = text_elements[0].text if text_elements else ''
            
            # Construction d'un objet SocialContent minimal
            return SocialContent(
                platform=SocialPlatform.FACEBOOK,
                content_id=f"fb_{hash(text)}",  # ID approximatif
                url="",  # URL complexe à extraire
                title=text[:100] + '...' if len(text) > 100 else text,
                description=text,
                author="",  # Nécessite extraction supplémentaire
                author_id="",
                upload_date=datetime.now(),  # Date approximative
                view_count=0,
                like_count=0,
                share_count=0,
                comment_count=0,
                content_type='text',
                thumbnail_url=None,
                duration=None,
                tags=[],
                metadata={'platform_specific': True}
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction Facebook: {e}")
            return None

    async def _analyze_potential_violation(
        self,
        original_content: SocialContent,
        found_content: SocialContent
    ) -> Optional[ViolationDetection]:
        """        Analyse une violation potentielle
        
        Args:
            original_content: Contenu original
            found_content: Contenu trouvé
            
        Returns:
            Optional[ViolationDetection]: Violation détectée
        """        try:
            # Comparaison de contenu basée sur le type
            similarity_score = 0.0
            detection_method = ""
            
            if original_content.content_type == found_content.content_type:
                if original_content.content_type == 'video':
                    similarity_score = await self._compare_videos(
                        original_content.url, found_content.url
                    )
                    detection_method = "video_fingerprint_analysis"
                
                elif original_content.content_type == 'image':
                    similarity_score = await self._compare_images(
                        original_content.thumbnail_url, found_content.thumbnail_url
                    )
                    detection_method = "image_perceptual_hash"
                
                elif original_content.content_type == 'audio':
                    similarity_score = await self._compare_audio(
                        original_content.url, found_content.url
                    )
                    detection_method = "audio_fingerprint_analysis"
                
                else:  # text
                    similarity_score = await self._compare_text(
                        original_content.description, found_content.description
                    )
                    detection_method = "text_similarity_analysis"
            
            # Comparaison des métadonnées
            metadata_similarity = self._compare_metadata(original_content, found_content)
            
            # Score final pondéré
            final_score = (similarity_score * 0.7) + (metadata_similarity * 0.3)
            
            # Seuil de détection
            violation_threshold = self.config.get('violation_threshold', 0.75)
            
            if final_score >= violation_threshold:
                confidence = self._calculate_violation_confidence(
                    similarity_score, metadata_similarity, original_content, found_content
                )
                
                return ViolationDetection(
                    original_content=original_content,
                    violating_content=found_content,
                    similarity_score=similarity_score,
                    violation_confidence=confidence,
                    detection_method=detection_method,
                    detected_at=datetime.now()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de violation: {e}")
            return None

    async def _compare_videos(self, url1: str, url2: str) -> float:
        """Compare deux vidéos"""        return await self.content_analyzer.compare_video_content(url1, url2)

    async def _compare_images(self, url1: str, url2: str) -> float:
        """Compare deux images"""        return await self.content_analyzer.compare_image_content(url1, url2)

    async def _compare_audio(self, url1: str, url2: str) -> float:
        """Compare deux audios"""        return await self.content_analyzer.compare_audio_content(url1, url2)

    async def _compare_text(self, text1: str, text2: str) -> float:
        """Compare deux textes"""        return await self.content_analyzer.compare_text_similarity(text1, text2)

    def _compare_metadata(self, content1: SocialContent, content2: SocialContent) -> float:
        """        Compare les métadonnées de deux contenus
        
        Args:
            content1: Premier contenu
            content2: Deuxième contenu
            
        Returns:
            float: Score de similarité des métadonnées
        """        score = 0.0
        factors = 0
        
        # Comparaison des titres
        if content1.title and content2.title:
            title_similarity = self._calculate_text_similarity(content1.title, content2.title)
            score += title_similarity
            factors += 1
        
        # Comparaison des descriptions
        if content1.description and content2.description:
            desc_similarity = self._calculate_text_similarity(content1.description, content2.description)
            score += desc_similarity
            factors += 1
        
        # Comparaison des tags
        if content1.tags and content2.tags:
            common_tags = set(content1.tags) & set(content2.tags)
            total_tags = set(content1.tags) | set(content2.tags)
            tag_similarity = len(common_tags) / len(total_tags) if total_tags else 0
            score += tag_similarity
            factors += 1
        
        # Comparaison de la durée (pour vidéos/audio)
        if content1.duration and content2.duration:
            duration_diff = abs(content1.duration - content2.duration)
            max_duration = max(content1.duration, content2.duration)
            duration_similarity = 1.0 - (duration_diff / max_duration) if max_duration > 0 else 1.0
            score += duration_similarity
            factors += 1
        
        return score / factors if factors > 0 else 0.0

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """        Calcule la similarité entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            float: Score de similarité
        """        # Implémentation simple basée sur les mots communs
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        common_words = words1 & words2
        total_words = words1 | words2
        
        return len(common_words) / len(total_words) if total_words else 0.0

    def _calculate_violation_confidence(
        self,
        similarity_score: float,
        metadata_similarity: float,
        original: SocialContent,
        suspect: SocialContent
    ) -> float:
        """        Calcule le niveau de confiance de la violation
        
        Args:
            similarity_score: Score de similarité du contenu
            metadata_similarity: Similarité des métadonnées
            original: Contenu original
            suspect: Contenu suspect
            
        Returns:
            float: Niveau de confiance
        """        confidence = similarity_score
        
        # Boost de confiance si même plateforme et auteur différent
        if original.platform == suspect.platform and original.author_id != suspect.author_id:
            confidence += 0.1
        
        # Boost si métadonnées très similaires
        if metadata_similarity > 0.8:
            confidence += 0.05
        
        # Boost si publié récemment après l'original
        if suspect.upload_date > original.upload_date:
            confidence += 0.05
        
        return min(1.0, confidence)

    def _get_tiktok_headers(self) -> Dict[str, str]:
        """Génère des headers pour TikTok"""        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    async def monitor_platforms_continuously(
        self, 
        tracked_contents: List[SocialContent],
        monitoring_interval: int = 3600
    ) -> None:
        """        Surveillance continue des plateformes
        
        Args:
            tracked_contents: Contenus à surveiller
            monitoring_interval: Intervalle de surveillance en secondes
        """        self.logger.info("Démarrage de la surveillance continue des réseaux sociaux")
        
        while True:
            try:
                for content in tracked_contents:
                    # Génération de mots-clés de recherche
                    keywords = self._generate_search_keywords(content)
                    
                    # Recherche de violations
                    violations = await self.track_content_across_platforms(content, keywords)
                    
                    # Traitement des violations
                    for violation in violations:
                        await self._handle_violation_detection(violation)
                
                # Pause avant le prochain cycle
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Erreur dans la surveillance continue: {e}")
                await asyncio.sleep(60)

    def _generate_search_keywords(self, content: SocialContent) -> List[str]:
        """        Génère des mots-clés de recherche pour un contenu
        
        Args:
            content: Contenu à rechercher
            
        Returns:
            List[str]: Mots-clés générés
        """        keywords = []
        
        # Titre et description
        if content.title:
            keywords.append(content.title)
            # Mots-clés extraits du titre
            title_words = [word for word in content.title.split() if len(word) > 3]
            keywords.extend(title_words[:5])  # Top 5 mots
        
        # Nom de l'auteur
        if content.author:
            keywords.append(content.author)
        
        # Tags
        if content.tags:
            keywords.extend(content.tags[:3])  # Top 3 tags
        
        return list(set(keywords))  # Déduplication

    async def _handle_violation_detection(self, violation: ViolationDetection) -> None:
        """        Traite une violation détectée
        
        Args:
            violation: Violation détectée
        """        self.logger.warning(
            f"Violation détectée: {violation.violating_content.url} "
            f"(confiance: {violation.violation_confidence:.2f})"
        )
        
        # Notification
        await self._send_violation_notification(violation)
        
        # Collecte d'évidence si pas encore fait
        if not violation.evidence_collected:
            await self._collect_violation_evidence(violation)
        
        # Initiation du takedown si configuré
        if self.config.get('auto_takedown', False) and violation.violation_confidence > 0.9:
            await self._initiate_takedown_request(violation)

    async def _send_violation_notification(self, violation: ViolationDetection) -> None:
        """Envoie une notification de violation"""        notification_data = {
            'type': 'social_media_violation',
            'original_url': violation.original_content.url,
            'violation_url': violation.violating_content.url,
            'platform': violation.violating_content.platform.value,
            'confidence': violation.violation_confidence,
            'similarity_score': violation.similarity_score,
            'detected_at': violation.detected_at.isoformat()
        }
        
        # Envoi de la notification (implémentation spécifique)
        pass

    async def _collect_violation_evidence(self, violation: ViolationDetection) -> None:
        """Collecte les preuves de violation"""        try:
            # Capture d'écran/enregistrement
            evidence_path = await self._capture_violation_evidence(violation.violating_content)
            
            # Sauvegarde des métadonnées
            metadata_path = await self._save_violation_metadata(violation)
            
            violation.evidence_collected = True
            
            self.logger.info(f"Évidence collectée pour {violation.violating_content.url}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte d'évidence: {e}")

    async def _capture_violation_evidence(self, content: SocialContent) -> str:
        """Capture des preuves visuelles"""        # Implémentation de capture d'écran/enregistrement
        return f"/evidence/{content.platform.value}_{content.content_id}.png"

    async def _save_violation_metadata(self, violation: ViolationDetection) -> str:
        """Sauvegarde les métadonnées de violation"""        metadata = {
            'violation': asdict(violation),
            'timestamp': datetime.now().isoformat(),
            'detection_version': '2.0.0'
        }
        
        file_path = f"/evidence/metadata_{violation.violating_content.content_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return file_path

    async def _initiate_takedown_request(self, violation: ViolationDetection) -> None:
        """Initie une demande de retrait"""        try:
            platform = violation.violating_content.platform
            
            if platform == SocialPlatform.YOUTUBE:
                await self._youtube_takedown_request(violation)
            elif platform == SocialPlatform.INSTAGRAM:
                await self._instagram_takedown_request(violation)
            # Autres plateformes...
            
            violation.takedown_initiated = True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initiation du takedown: {e}")

    async def _youtube_takedown_request(self, violation: ViolationDetection) -> None:
        """Demande de retrait YouTube"""        # Implémentation via l'API YouTube Content ID ou copyright claim
        pass

    async def _instagram_takedown_request(self, violation: ViolationDetection) -> None:
        """Demande de retrait Instagram"""        # Implémentation via l'API Instagram/Facebook
        pass

    def get_tracking_statistics(self) -> Dict[str, Any]:
        """        Retourne les statistiques de tracking
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """        total_violations = len(self.detected_violations)
        platform_stats = {}
        
        for violation in self.detected_violations:
            platform = violation.violating_content.platform.value
            if platform not in platform_stats:
                platform_stats[platform] = 0
            platform_stats[platform] += 1
        
        return {
            'tracked_content_count': len(self.tracked_content),
            'total_violations_detected': total_violations,
            'violations_by_platform': platform_stats,
            'high_confidence_violations': len([
                v for v in self.detected_violations 
                if v.violation_confidence > 0.8
            ]),
            'evidence_collected': len([
                v for v in self.detected_violations 
                if v.evidence_collected
            ]),
            'takedowns_initiated': len([
                v for v in self.detected_violations 
                if v.takedown_initiated
            ])
        }

    async def cleanup_old_data(self) -> None:
        """Nettoie les anciennes données"""        cutoff_date = datetime.now() - timedelta(
            days=self.config.get('data_retention_days', 90)
        )
        
        # Suppression des anciennes violations
        self.detected_violations = [
            v for v in self.detected_violations 
            if v.detected_at > cutoff_date
        ]
        
        self.logger.info("Nettoyage des données anciennes effectué")

    def __del__(self):
        """Nettoyage lors de la destruction"""        try:
            if hasattr(self, 'selenium_driver'):
                self.selenium_driver.quit()
        except Exception:
            pass
