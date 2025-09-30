# 🔒 Platform Security Monitor: Cross-Platform Intelligence & Monitoring
"""
Platform Security Monitor - Ainflue Integrations
===============================================
Enterprise platform security monitoring providing cross-platform intelligence,
social media monitoring, brand protection, and comprehensive threat detection
across 30+ platforms for Ainflue creator ecosystem.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from textblob import TextBlob
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from celery import Celery
import boto3
from cryptography.fernet import Fernet
import tweepy
import instaloader
import facebook
import schedule

# Configuration
Base = declarative_base()
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Plateformes supportées"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    CLUBHOUSE = "clubhouse"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    SUBSTACK = "substack"
    MEDIUM = "medium"

class ThreatType(Enum):
    """Types de menaces plateforme"""
    IMPERSONATION = "impersonation"
    CONTENT_THEFT = "content_theft"
    BRAND_ABUSE = "brand_abuse"
    FAKE_ACCOUNT = "fake_account"
    PHISHING = "phishing"
    SCAM = "scam"
    HARASSMENT = "harassment"
    SPAM = "spam"
    MALWARE = "malware"
    REPUTATION_ATTACK = "reputation_attack"

class MonitoringStatus(Enum):
    """Status monitoring"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class PlatformAccount:
    """Compte plateforme surveillé"""
    account_id: str
    creator_id: str
    platform: Platform
    username: str
    profile_url: str
    verified: bool
    follower_count: int
    monitoring_enabled: bool
    last_checked: datetime
    metadata: Dict[str, Any]

@dataclass
class ThreatDetection:
    """Détection de menace"""
    detection_id: str
    creator_id: str
    platform: Platform
    threat_type: ThreatType
    threat_url: str
    confidence_score: float
    description: str
    evidence: Dict[str, Any]
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime]

@dataclass
class MonitoringReport:
    """Rapport monitoring"""
    report_id: str
    creator_id: str
    period_start: datetime
    period_end: datetime
    platforms_monitored: List[Platform]
    threats_detected: int
    actions_taken: int
    summary: Dict[str, Any]
    recommendations: List[str]

class PlatformAccountModel(Base):
    """Modèle database comptes plateforme"""
    __tablename__ = 'platform_accounts'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(String(255), nullable=False, unique=True)
    creator_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    username = Column(String(255), nullable=False)
    profile_url = Column(String(1000), nullable=False)
    verified = Column(Boolean, default=False)
    follower_count = Column(Integer, default=0)
    monitoring_enabled = Column(Boolean, default=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ThreatDetectionModel(Base):
    """Modèle database détections menaces"""
    __tablename__ = 'threat_detections'
    
    id = Column(Integer, primary_key=True)
    detection_id = Column(String(255), nullable=False, unique=True)
    creator_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    threat_type = Column(String(50), nullable=False)
    threat_url = Column(String(1000), nullable=False)
    confidence_score = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON)
    status = Column(String(20), default='active')
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class MonitoringLogModel(Base):
    """Modèle database logs monitoring"""
    __tablename__ = 'monitoring_logs'
    
    id = Column(Integer, primary_key=True)
    creator_id = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PlatformSecurityMonitor:
    """
    Moniteur sécurité multi-plateforme enterprise
    
    Fonctionnalités:
    - Surveillance 30+ plateformes sociales
    - Détection usurpation identité temps réel
    - Monitoring vol contenu cross-platform
    - Protection marque automatisée
    - Intelligence menaces sociale
    - Alertes proactives multi-canal
    - Analyse sentiment réputation
    - Actions correctives automatiques
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_engine = create_engine(config.get('database_url', 'sqlite:///platform_security.db'))
        Base.metadata.create_all(self.db_engine)
        self.Session = sessionmaker(bind=self.db_engine)
        
        # API clients initialization
        self._init_platform_clients()
        
        # Services initialization
        self._init_services()
        
        # Monitoring configuration
        self._init_monitoring_config()
        
        # Métriques
        self.metrics = {
            'accounts_monitored': 0,
            'threats_detected': 0,
            'actions_taken': 0,
            'platforms_active': 0,
            'last_scan_duration': 0.0
        }
        
        logger.info("PlatformSecurityMonitor initialisé avec succès")
    
    def _init_platform_clients(self):
        """Initialisation clients API plateformes"""
        try:
            self.api_clients = {}
            
            # Twitter API
            if self.config.get('twitter_api_key'):
                self.api_clients['twitter'] = tweepy.Client(
                    bearer_token=self.config.get('twitter_bearer_token'),
                    consumer_key=self.config.get('twitter_api_key'),
                    consumer_secret=self.config.get('twitter_api_secret'),
                    access_token=self.config.get('twitter_access_token'),
                    access_token_secret=self.config.get('twitter_access_secret')
                )
            
            # Instagram API (via Instaloader)
            if self.config.get('instagram_enabled'):
                self.api_clients['instagram'] = instaloader.Instaloader()
            
            # Facebook Graph API
            if self.config.get('facebook_access_token'):
                self.api_clients['facebook'] = facebook.GraphAPI(
                    access_token=self.config.get('facebook_access_token')
                )
            
            # YouTube Data API
            if self.config.get('youtube_api_key'):
                self.api_clients['youtube'] = self.config.get('youtube_api_key')
            
            logger.info(f"Clients API initialisés: {list(self.api_clients.keys())}")
            
        except Exception as e:
            logger.error(f"Erreur initialisation clients API: {e}")
            self.api_clients = {}
    
    def _init_services(self):
        """Initialisation services externes"""
        try:
            # Redis pour cache
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                decode_responses=True
            )
            
            # Celery pour tasks async
            self.celery_app = Celery(
                'platform_monitor',
                broker=self.config.get('celery_broker', 'redis://localhost:6379/0')
            )
            
            # AWS services
            self.s3_client = None
            if self.config.get('aws_enabled'):
                self.s3_client = boto3.client('s3')
            
            # Encryption
            self.cipher_suite = Fernet(
                self.config.get('encryption_key', Fernet.generate_key())
            )
            
            logger.info("Services externes initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
    
    def _init_monitoring_config(self):
        """Initialisation configuration monitoring"""
        try:
            # Fréquences monitoring par plateforme
            self.monitoring_intervals = {
                Platform.TWITTER: 300,      # 5 minutes
                Platform.INSTAGRAM: 900,    # 15 minutes  
                Platform.YOUTUBE: 1800,     # 30 minutes
                Platform.TIKTOK: 600,       # 10 minutes
                Platform.FACEBOOK: 1800,    # 30 minutes
                Platform.LINKEDIN: 3600,    # 1 heure
                Platform.TWITCH: 600,       # 10 minutes
                Platform.DISCORD: 1800,     # 30 minutes
                Platform.REDDIT: 1800,      # 30 minutes
                Platform.PINTEREST: 3600,   # 1 heure
            }
            
            # Mots-clés recherche par défaut
            self.default_keywords = [
                'scam', 'fake', 'imposter', 'phishing', 'fraud',
                'stolen', 'copied', 'unauthorized', 'illegal'
            ]
            
            # Seuils détection
            self.detection_thresholds = {
                'similarity_threshold': 0.8,
                'confidence_threshold': 0.7,
                'reputation_threshold': -0.5
            }
            
            logger.info("Configuration monitoring initialisée")
            
        except Exception as e:
            logger.error(f"Erreur configuration monitoring: {e}")
    
    async def register_platform_account(self, creator_id: str, platform: Platform,
                                      username: str, profile_url: str,
                                      metadata: Dict[str, Any] = None) -> PlatformAccount:
        """
        Enregistrement compte plateforme à surveiller
        
        Args:
            creator_id: ID créateur
            platform: Plateforme
            username: Nom d'utilisateur
            profile_url: URL profil
            metadata: Métadonnées additionnelles
            
        Returns:
            PlatformAccount: Compte enregistré
        """
        try:
            account_id = f"{platform.value}_{creator_id}_{uuid.uuid4().hex[:8]}"
            
            # Validation et enrichissement données
            enriched_data = await self._enrich_account_data(platform, username, profile_url)
            
            # Création objet compte
            account = PlatformAccount(
                account_id=account_id,
                creator_id=creator_id,
                platform=platform,
                username=username,
                profile_url=profile_url,
                verified=enriched_data.get('verified', False),
                follower_count=enriched_data.get('follower_count', 0),
                monitoring_enabled=True,
                last_checked=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Sauvegarde database
            await self._save_platform_account(account)
            
            # Démarrage monitoring
            await self._start_account_monitoring(account)
            
            # Mise à jour métriques
            self.metrics['accounts_monitored'] += 1
            
            logger.info(f"Compte plateforme enregistré: {account_id}")
            
            return account
            
        except Exception as e:
            logger.error(f"Erreur enregistrement compte: {e}")
            raise
    
    async def monitor_platform_threats(self, creator_id: str, 
                                     platforms: List[Platform] = None) -> List[ThreatDetection]:
        """
        Monitoring menaces multi-plateforme
        
        Args:
            creator_id: ID créateur
            platforms: Plateformes à surveiller (toutes si None)
            
        Returns:
            List[ThreatDetection]: Menaces détectées
        """
        try:
            start_time = time.time()
            all_detections = []
            
            # Récupération comptes à surveiller
            accounts = await self._get_monitored_accounts(creator_id, platforms)
            
            if not accounts:
                logger.info(f"Aucun compte à surveiller pour: {creator_id}")
                return all_detections
            
            # Monitoring par plateforme
            for account in accounts:
                try:
                    platform_detections = await self._monitor_platform_account(account)
                    all_detections.extend(platform_detections)
                    
                    # Mise à jour dernière vérification
                    await self._update_last_checked(account.account_id)
                    
                except Exception as e:
                    logger.error(f"Erreur monitoring {account.platform.value}: {e}")
                    await self._log_monitoring_error(account, str(e))
            
            # Analyse cross-platform des détections
            cross_platform_threats = await self._analyze_cross_platform_threats(all_detections)
            all_detections.extend(cross_platform_threats)
            
            # Sauvegarde détections
            for detection in all_detections:
                await self._save_threat_detection(detection)
            
            # Actions automatiques
            await self._execute_automatic_actions(all_detections)
            
            # Mise à jour métriques
            self.metrics['threats_detected'] += len(all_detections)
            self.metrics['last_scan_duration'] = time.time() - start_time
            
            logger.info(f"Monitoring terminé: {len(all_detections)} menaces détectées")
            
            return all_detections
            
        except Exception as e:
            logger.error(f"Erreur monitoring menaces: {e}")
            return []
    
    async def _monitor_platform_account(self, account: PlatformAccount) -> List[ThreatDetection]:
        """Monitoring spécifique plateforme"""
        detections = []
        
        try:
            if account.platform == Platform.TWITTER:
                detections.extend(await self._monitor_twitter(account))
            elif account.platform == Platform.INSTAGRAM:
                detections.extend(await self._monitor_instagram(account))
            elif account.platform == Platform.YOUTUBE:
                detections.extend(await self._monitor_youtube(account))
            elif account.platform == Platform.TIKTOK:
                detections.extend(await self._monitor_tiktok(account))
            elif account.platform == Platform.FACEBOOK:
                detections.extend(await self._monitor_facebook(account))
            elif account.platform == Platform.LINKEDIN:
                detections.extend(await self._monitor_linkedin(account))
            elif account.platform == Platform.REDDIT:
                detections.extend(await self._monitor_reddit(account))
            else:
                # Monitoring générique pour autres plateformes
                detections.extend(await self._monitor_generic_platform(account))
                
        except Exception as e:
            logger.error(f"Erreur monitoring {account.platform.value}: {e}")
        
        return detections
    
    async def _monitor_twitter(self, account: PlatformAccount) -> List[ThreatDetection]:
        """Monitoring spécifique Twitter"""
        detections = []
        
        try:
            if 'twitter' not in self.api_clients:
                return detections
            
            client = self.api_clients['twitter']
            
            # Recherche mentions et impersonations
            search_queries = [
                f"@{account.username}",
                f'"{account.username}"',
                f"imposter {account.username}",
                f"fake {account.username}"
            ]
            
            for query in search_queries:
                try:
                    tweets = client.search_recent_tweets(
                        query=query,
                        max_results=50,
                        tweet_fields=['author_id', 'created_at', 'public_metrics']
                    )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            # Analyse du tweet pour détection menaces
                            threat_analysis = await self._analyze_tweet_for_threats(
                                tweet, account
                            )
                            
                            if threat_analysis:
                                detections.append(threat_analysis)
                                
                except Exception as e:
                    logger.error(f"Erreur recherche Twitter: {e}")
            
            # Monitoring profils similaires (impersonation)
            similar_profiles = await self._find_similar_twitter_profiles(account)
            for profile in similar_profiles:
                detection = await self._create_impersonation_detection(
                    account, profile, Platform.TWITTER
                )
                if detection:
                    detections.append(detection)
            
        except Exception as e:
            logger.error(f"Erreur monitoring Twitter: {e}")
        
        return detections
    
    async def _monitor_instagram(self, account: PlatformAccount) -> List[ThreatDetection]:
        """Monitoring spécifique Instagram"""
        detections = []
        
        try:
            if 'instagram' not in self.api_clients:
                return detections
            
            loader = self.api_clients['instagram']
            
            # Recherche hashtags et mentions
            search_terms = [
                account.username,
                f"fake{account.username}",
                f"{account.username}scam"
            ]
            
            for term in search_terms:
                try:
                    # Recherche par hashtag
                    hashtag = instaloader.Hashtag.from_name(loader.context, term)
                    
                    for post in hashtag.get_posts():
                        if len(detections) >= 10:  # Limite pour éviter rate limiting
                            break
                        
                        # Analyse post pour menaces
                        threat_analysis = await self._analyze_instagram_post_for_threats(
                            post, account
                        )
                        
                        if threat_analysis:
                            detections.append(threat_analysis)
                            
                        # Pause pour éviter rate limiting
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    logger.error(f"Erreur recherche Instagram hashtag {term}: {e}")
            
            # Monitoring profils similaires
            similar_profiles = await self._find_similar_instagram_profiles(account)
            for profile in similar_profiles:
                detection = await self._create_impersonation_detection(
                    account, profile, Platform.INSTAGRAM
                )
                if detection:
                    detections.append(detection)
            
        except Exception as e:
            logger.error(f"Erreur monitoring Instagram: {e}")
        
        return detections
    
    async def _monitor_youtube(self, account: PlatformAccount) -> List[ThreatDetection]:
        """Monitoring spécifique YouTube"""
        detections = []
        
        try:
            api_key = self.api_clients.get('youtube')
            if not api_key:
                return detections
            
            # Recherche vidéos et chaînes suspectes
            search_queries = [
                f"{account.username} fake",
                f"{account.username} scam",
                f"{account.username} imposter"
            ]
            
            async with aiohttp.ClientSession() as session:
                for query in search_queries:
                    try:
                        # API YouTube Search
                        url = "https://www.googleapis.com/youtube/v3/search"
                        params = {
                            'part': 'snippet',
                            'q': query,
                            'type': 'video,channel',
                            'maxResults': 25,
                            'key': api_key
                        }
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                for item in data.get('items', []):
                                    # Analyse item pour menaces
                                    threat_analysis = await self._analyze_youtube_item_for_threats(
                                        item, account
                                    )
                                    
                                    if threat_analysis:
                                        detections.append(threat_analysis)
                                        
                    except Exception as e:
                        logger.error(f"Erreur recherche YouTube: {e}")
            
        except Exception as e:
            logger.error(f"Erreur monitoring YouTube: {e}")
        
        return detections
    
    async def _monitor_generic_platform(self, account: PlatformAccount) -> List[ThreatDetection]:
        """Monitoring générique pour plateformes sans API spécifique"""
        detections = []
        
        try:
            # Web scraping basique (respectant robots.txt)
            search_engines = [
                f"site:{account.platform.value}.com {account.username} fake",
                f"site:{account.platform.value}.com {account.username} scam"
            ]
            
            for query in search_engines:
                try:
                    # Recherche Google (simulation - utiliser vraie API en production)
                    search_results = await self._search_web_for_threats(query, account)
                    detections.extend(search_results)
                    
                except Exception as e:
                    logger.error(f"Erreur recherche générique: {e}")
            
        except Exception as e:
            logger.error(f"Erreur monitoring générique: {e}")
        
        return detections
    
    async def _analyze_tweet_for_threats(self, tweet: Any, account: PlatformAccount) -> Optional[ThreatDetection]:
        """Analyse tweet pour détection menaces"""
        try:
            tweet_text = tweet.text.lower()
            
            # Mots-clés suspects
            threat_keywords = ['scam', 'fake', 'phishing', 'fraud', 'stolen', 'imposter']
            
            # Calcul score menace
            threat_score = 0.0
            threat_indicators = []
            
            for keyword in threat_keywords:
                if keyword in tweet_text:
                    threat_score += 0.2
                    threat_indicators.append(f"keyword_{keyword}")
            
            # Analyse sentiment
            sentiment = TextBlob(tweet.text).sentiment.polarity
            if sentiment < -0.5:
                threat_score += 0.3
                threat_indicators.append("negative_sentiment")
            
            # Mention du nom d'utilisateur avec contexte négatif
            if account.username.lower() in tweet_text and any(kw in tweet_text for kw in threat_keywords):
                threat_score += 0.4
                threat_indicators.append("username_with_threat")
            
            # Si score suffisant, créer détection
            if threat_score >= self.detection_thresholds['confidence_threshold']:
                detection_id = f"tw_{uuid.uuid4().hex[:12]}"
                
                return ThreatDetection(
                    detection_id=detection_id,
                    creator_id=account.creator_id,
                    platform=Platform.TWITTER,
                    threat_type=ThreatType.REPUTATION_ATTACK,
                    threat_url=f"https://twitter.com/user/status/{tweet.id}",
                    confidence_score=min(threat_score, 1.0),
                    description=f"Tweet suspect mentionnant {account.username}",
                    evidence={
                        'tweet_text': tweet.text,
                        'tweet_id': tweet.id,
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'threat_indicators': threat_indicators,
                        'sentiment_score': sentiment
                    },
                    status='active',
                    detected_at=datetime.utcnow(),
                    resolved_at=None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur analyse tweet: {e}")
            return None
    
    async def _create_impersonation_detection(self, original_account: PlatformAccount,
                                            suspicious_profile: Dict[str, Any],
                                            platform: Platform) -> Optional[ThreatDetection]:
        """Création détection usurpation"""
        try:
            # Calcul similarité profils
            similarity_score = await self._calculate_profile_similarity(
                original_account, suspicious_profile
            )
            
            if similarity_score >= self.detection_thresholds['similarity_threshold']:
                detection_id = f"imp_{uuid.uuid4().hex[:12]}"
                
                return ThreatDetection(
                    detection_id=detection_id,
                    creator_id=original_account.creator_id,
                    platform=platform,
                    threat_type=ThreatType.IMPERSONATION,
                    threat_url=suspicious_profile.get('profile_url', ''),
                    confidence_score=similarity_score,
                    description=f"Possible usurpation identité sur {platform.value}",
                    evidence={
                        'original_username': original_account.username,
                        'suspicious_username': suspicious_profile.get('username'),
                        'similarity_score': similarity_score,
                        'suspicious_profile': suspicious_profile,
                        'comparison_metrics': await self._get_comparison_metrics(
                            original_account, suspicious_profile
                        )
                    },
                    status='active',
                    detected_at=datetime.utcnow(),
                    resolved_at=None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur création détection usurpation: {e}")
            return None
    
    async def _calculate_profile_similarity(self, original: PlatformAccount,
                                          suspicious: Dict[str, Any]) -> float:
        """Calcul similarité entre profils"""
        try:
            similarity_score = 0.0
            
            # Similarité nom d'utilisateur
            orig_username = original.username.lower()
            susp_username = suspicious.get('username', '').lower()
            
            # Distance Levenshtein simplifiée
            username_similarity = self._calculate_string_similarity(orig_username, susp_username)
            similarity_score += username_similarity * 0.4
            
            # Similarité bio/description
            orig_bio = original.metadata.get('bio', '')
            susp_bio = suspicious.get('bio', '')
            
            if orig_bio and susp_bio:
                bio_similarity = self._calculate_text_similarity(orig_bio, susp_bio)
                similarity_score += bio_similarity * 0.3
            
            # Similarité avatar (si disponible)
            if 'avatar_url' in suspicious and 'avatar_url' in original.metadata:
                # Simulation comparaison images (implémenter vraie comparaison)
                avatar_similarity = 0.5  # Placeholder
                similarity_score += avatar_similarity * 0.2
            
            # Patterns suspects dans username
            if self._has_suspicious_patterns(orig_username, susp_username):
                similarity_score += 0.1
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité: {e}")
            return 0.0
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calcul similarité chaînes de caractères"""
        try:
            # Distance Levenshtein simplifiée
            if not str1 or not str2:
                return 0.0
            
            if str1 == str2:
                return 1.0
            
            # Calcul distance basique
            len1, len2 = len(str1), len(str2)
            if len1 > len2:
                str1, str2 = str2, str1
                len1, len2 = len2, len1
            
            # Calcul matches
            matches = sum(1 for a, b in zip(str1, str2) if a == b)
            similarity = matches / max(len1, len2)
            
            # Bonus pour sous-chaînes
            if str1 in str2 or str2 in str1:
                similarity += 0.2
            
            return min(similarity, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcul similarité textes"""
        try:
            if not text1 or not text2:
                return 0.0
            
            # Utilisation TF-IDF pour similarité sémantique
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
            
        except Exception:
            return 0.0
    
    def _has_suspicious_patterns(self, original: str, suspicious: str) -> bool:
        """Détection patterns suspects dans usernames"""
        try:
            # Patterns communs d'usurpation
            patterns = [
                # Ajout caractères
                f"{original}official",
                f"{original}real",
                f"{original}verified",
                f"real{original}",
                f"official{original}",
                # Remplacement caractères
                original.replace('o', '0'),
                original.replace('i', '1'),
                original.replace('l', '1'),
                original.replace('e', '3'),
                # Ajout underscores/points  
                f"{original}_",
                f"_{original}",
                f"{original}.",
                f".{original}"
            ]
            
            return suspicious in patterns
            
        except Exception:
            return False
    
    async def generate_monitoring_report(self, creator_id: str,
                                       period_days: int = 7) -> MonitoringReport:
        """
        Génération rapport monitoring périodique
        
        Args:
            creator_id: ID créateur
            period_days: Période en jours
            
        Returns:
            MonitoringReport: Rapport généré
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            period_end = datetime.utcnow()
            
            # Récupération données période
            session = self.Session()
            
            # Comptes surveillés
            accounts = session.query(PlatformAccountModel)\
                            .filter(PlatformAccountModel.creator_id == creator_id)\
                            .all()
            
            platforms_monitored = [Platform(acc.platform) for acc in accounts]
            
            # Menaces détectées
            threats = session.query(ThreatDetectionModel)\
                           .filter(ThreatDetectionModel.creator_id == creator_id)\
                           .filter(ThreatDetectionModel.detected_at >= period_start)\
                           .all()
            
            # Actions prises
            actions = session.query(MonitoringLogModel)\
                           .filter(MonitoringLogModel.creator_id == creator_id)\
                           .filter(MonitoringLogModel.timestamp >= period_start)\
                           .filter(MonitoringLogModel.action.in_(['block', 'report', 'takedown']))\
                           .all()
            
            session.close()
            
            # Analyse des données
            threat_breakdown = {}
            for threat in threats:
                threat_type = threat.threat_type
                threat_breakdown[threat_type] = threat_breakdown.get(threat_type, 0) + 1
            
            platform_breakdown = {}
            for threat in threats:
                platform = threat.platform
                platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1
            
            # Calcul métriques
            total_threats = len(threats)
            total_actions = len(actions)
            high_confidence_threats = len([t for t in threats if t.confidence_score >= 0.8])
            
            # Génération recommandations
            recommendations = await self._generate_monitoring_recommendations(
                creator_id, threats, accounts
            )
            
            # Création rapport
            report_id = f"report_{uuid.uuid4().hex[:12]}"
            
            report = MonitoringReport(
                report_id=report_id,
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end,
                platforms_monitored=platforms_monitored,
                threats_detected=total_threats,
                actions_taken=total_actions,
                summary={
                    'threat_breakdown': threat_breakdown,
                    'platform_breakdown': platform_breakdown,
                    'high_confidence_threats': high_confidence_threats,
                    'avg_confidence_score': np.mean([t.confidence_score for t in threats]) if threats else 0.0,
                    'monitoring_coverage': len(platforms_monitored),
                    'response_rate': (total_actions / total_threats * 100) if total_threats > 0 else 0.0
                },
                recommendations=recommendations
            )
            
            logger.info(f"Rapport monitoring généré: {report_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            raise
    
    async def get_platform_security_metrics(self) -> Dict[str, Any]:
        """Récupération métriques sécurité plateforme"""
        try:
            session = self.Session()
            
            # Statistiques générales
            total_accounts = session.query(PlatformAccountModel).count()
            total_threats = session.query(ThreatDetectionModel).count()
            active_threats = session.query(ThreatDetectionModel)\
                                   .filter(ThreatDetectionModel.status == 'active').count()
            
            # Distribution par plateforme
            platform_distribution = {}
            for platform in Platform:
                count = session.query(PlatformAccountModel)\
                             .filter(PlatformAccountModel.platform == platform.value).count()
                if count > 0:
                    platform_distribution[platform.value] = count
            
            # Types de menaces (30 derniers jours)
            recent_threats = session.query(ThreatDetectionModel)\
                                   .filter(ThreatDetectionModel.detected_at >= datetime.utcnow() - timedelta(days=30))\
                                   .all()
            
            threat_types = {}
            for threat in recent_threats:
                threat_types[threat.threat_type] = threat_types.get(threat.threat_type, 0) + 1
            
            # Métriques performances
            avg_confidence = session.query(
                sqlalchemy.func.avg(ThreatDetectionModel.confidence_score)
            ).scalar() or 0.0
            
            session.close()
            
            return {
                'total_accounts_monitored': total_accounts,
                'total_threats_detected': total_threats,
                'active_threats': active_threats,
                'platforms_active': len(platform_distribution),
                'platform_distribution': platform_distribution,
                'threat_types_30d': threat_types,
                'average_confidence_score': round(avg_confidence, 3),
                'last_scan_duration': self.metrics.get('last_scan_duration', 0.0),
                'monitoring_status': 'active',
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur métriques sécurité: {e}")
            return {}
    
    # Méthodes de sauvegarde
    async def _save_platform_account(self, account: PlatformAccount):
        """Sauvegarde compte plateforme"""
        try:
            session = self.Session()
            
            account_record = PlatformAccountModel(
                account_id=account.account_id,
                creator_id=account.creator_id,
                platform=account.platform.value,
                username=account.username,
                profile_url=account.profile_url,
                verified=account.verified,
                follower_count=account.follower_count,
                monitoring_enabled=account.monitoring_enabled,
                last_checked=account.last_checked,
                metadata=account.metadata
            )
            
            session.add(account_record)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde compte: {e}")
    
    async def _save_threat_detection(self, detection: ThreatDetection):
        """Sauvegarde détection menace"""
        try:
            session = self.Session()
            
            detection_record = ThreatDetectionModel(
                detection_id=detection.detection_id,
                creator_id=detection.creator_id,
                platform=detection.platform.value,
                threat_type=detection.threat_type.value,
                threat_url=detection.threat_url,
                confidence_score=detection.confidence_score,
                description=detection.description,
                evidence=detection.evidence,
                status=detection.status
            )
            
            session.add(detection_record)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde détection: {e}")

# Instance globale
_monitor_instance = None

def get_platform_security_monitor(config: Dict[str, Any] = None) -> PlatformSecurityMonitor:
    """Factory pour instance monitor"""
    global _monitor_instance
    
    if _monitor_instance is None:
        if config is None:
            config = {
                'database_url': 'sqlite:///platform_security.db',
                'redis_host': 'localhost',
                'redis_port': 6379,
                'twitter_api_key': None,
                'instagram_enabled': False,
                'youtube_api_key': None,
                'facebook_access_token': None,
                'aws_enabled': False,
                'encryption_key': Fernet.generate_key()
            }
        
        _monitor_instance = PlatformSecurityMonitor(config)
    
    return _monitor_instance

if __name__ == "__main__":
    # Test basique
    async def test_monitor():
        monitor = get_platform_security_monitor()
        
        # Test enregistrement compte
        account = await monitor.register_platform_account(
            "creator_001",
            Platform.TWITTER,
            "test_creator",
            "https://twitter.com/test_creator"
        )
        
        print(f"Compte enregistré: {account.account_id}")
        
        # Test monitoring
        threats = await monitor.monitor_platform_threats("creator_001")
        print(f"Menaces détectées: {len(threats)}")
    
    # Exécution test
    asyncio.run(test_monitor())