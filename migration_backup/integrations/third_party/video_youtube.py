#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📺 IA CHÉRIES YOUTUBE ENGINE
=============================

Module d'intégration avec l'API YouTube Data v3 pour :
- Recherche de vidéos et chaînes
- Analyse des statistiques
- Récupération des commentaires
- Suivi des tendances
- Analytics de performance

Auteur: Fahed Mlaiel
Date: 28 Septembre 2025
Version: Enterprise 2.0
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import urllib.parse
from pathlib import Path

class IaCheriesYouTubeAPI:
    """
    📺 Moteur YouTube pour IA Chéries
    
    Fonctionnalités:
    - Recherche intelligente de vidéos
    - Analytics détaillées des chaînes
    - Suivi des commentaires
    - Analyse des tendances
    - Extraction de métadonnées
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialise le moteur YouTube
        
        Args:
            api_key (str): Clé API YouTube Data v3
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        
        if not self.api_key:
            raise ValueError("❌ Clé API YouTube manquante!")
            
        # Configuration API
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Cache et statistiques
        self.cache_dir = Path("cache/youtube")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistiques d'utilisation
        self.stats = {
            'video_searches': 0,
            'channel_analyses': 0,
            'comments_retrieved': 0,
            'api_calls': 0,
            'quota_used': 0
        }
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("📺 YouTube Engine initialisé avec succès!")

    async def search_videos(
        self,
        query: str,
        max_results: int = 25,
        order: str = "relevance",
        published_after: str = None,
        video_duration: str = None,
        video_definition: str = None
    ) -> Dict[str, Any]:
        """
        Recherche de vidéos YouTube avec filtres avancés
        
        Args:
            query (str): Terme de recherche
            max_results (int): Nombre de résultats (max 50)
            order (str): Tri (date, rating, relevance, title, viewCount)
            published_after (str): Date ISO 8601 (ex: "2025-01-01T00:00:00Z")
            video_duration (str): any, long, medium, short
            video_definition (str): any, high, standard
            
        Returns:
            dict: Résultats de recherche enrichis
        """
        try:
            self.stats['video_searches'] += 1
            
            # Paramètres de base
            params = {
                'part': 'snippet,statistics',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order,
                'key': self.api_key
            }
            
            # Filtres optionnels
            if published_after:
                params['publishedAfter'] = published_after
            if video_duration:
                params['videoDuration'] = video_duration
            if video_definition:
                params['videoDefinition'] = video_definition
            
            # Requête API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params
                ) as response:
                    
                    self.stats['api_calls'] += 1
                    self.stats['quota_used'] += 100  # Coût quota pour search
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Enrichir les résultats avec des statistiques détaillées
                        enriched_videos = []
                        if 'items' in data:
                            video_ids = [item['id']['videoId'] for item in data['items']]
                            video_stats = await self._get_video_statistics(video_ids)
                            
                            for item in data['items']:
                                video_id = item['id']['videoId']
                                enriched_video = await self._enrich_video_data(item, video_stats.get(video_id))
                                enriched_videos.append(enriched_video)
                        
                        result = {
                            'status': 'success',
                            'query': query,
                            'total_results': data.get('pageInfo', {}).get('totalResults', 0),
                            'results_per_page': len(enriched_videos),
                            'videos': enriched_videos,
                            'search_params': {
                                'query': query,
                                'order': order,
                                'max_results': max_results,
                                'filters': {
                                    'published_after': published_after,
                                    'duration': video_duration,
                                    'definition': video_definition
                                }
                            },
                            'next_page_token': data.get('nextPageToken'),
                            'search_time': datetime.now().isoformat()
                        }
                        
                        self.logger.info(f"🔍 Recherche YouTube '{query}': {len(enriched_videos)} vidéos trouvées")
                        return result
                        
                    else:
                        error_data = await response.json()
                        self.logger.error(f"❌ Erreur API YouTube: {response.status}")
                        return {
                            'status': 'error',
                            'message': f'Erreur API YouTube: {response.status}',
                            'details': error_data
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche YouTube: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur de recherche: {str(e)}'
            }

    async def _get_video_statistics(self, video_ids: List[str]) -> Dict[str, Dict]:
        """
        Récupère les statistiques détaillées des vidéos
        
        Args:
            video_ids (list): Liste des IDs de vidéos
            
        Returns:
            dict: Statistiques par video_id
        """
        try:
            if not video_ids:
                return {}
            
            params = {
                'part': 'statistics,contentDetails',
                'id': ','.join(video_ids),
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/videos",
                    params=params
                ) as response:
                    
                    self.stats['api_calls'] += 1
                    self.stats['quota_used'] += 1  # Coût quota pour videos
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        stats_dict = {}
                        for item in data.get('items', []):
                            video_id = item['id']
                            stats_dict[video_id] = {
                                'statistics': item.get('statistics', {}),
                                'contentDetails': item.get('contentDetails', {})
                            }
                        
                        return stats_dict
                    
            return {}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur récupération stats vidéos: {e}")
            return {}

    async def _enrich_video_data(self, video_item: Dict, stats: Dict = None) -> Dict:
        """
        Enrichit les données d'une vidéo avec des métadonnées utiles
        
        Args:
            video_item (dict): Données de base de la vidéo
            stats (dict): Statistiques détaillées
            
        Returns:
            dict: Données enrichies
        """
        try:
            enriched = {
                'video_id': video_item['id']['videoId'],
                'title': video_item['snippet']['title'],
                'description': video_item['snippet']['description'][:300] + '...' if len(video_item['snippet']['description']) > 300 else video_item['snippet']['description'],
                'channel_id': video_item['snippet']['channelId'],
                'channel_title': video_item['snippet']['channelTitle'],
                'published_at': video_item['snippet']['publishedAt'],
                'thumbnail_url': video_item['snippet']['thumbnails'].get('high', {}).get('url') or video_item['snippet']['thumbnails'].get('default', {}).get('url'),
                'video_url': f"https://www.youtube.com/watch?v={video_item['id']['videoId']}",
                'channel_url': f"https://www.youtube.com/channel/{video_item['snippet']['channelId']}"
            }
            
            # Ajouter les statistiques si disponibles
            if stats:
                video_stats = stats.get('statistics', {})
                content_details = stats.get('contentDetails', {})
                
                # Statistiques de performance
                enriched.update({
                    'view_count': int(video_stats.get('viewCount', 0)),
                    'like_count': int(video_stats.get('likeCount', 0)),
                    'comment_count': int(video_stats.get('commentCount', 0)),
                    'duration': content_details.get('duration', 'Unknown'),
                    'duration_seconds': self._parse_duration(content_details.get('duration', 'PT0S'))
                })
                
                # Métriques calculées
                views = enriched['view_count']
                likes = enriched['like_count']
                
                # Score d'engagement (likes/vues * 100)
                engagement_rate = (likes / views * 100) if views > 0 else 0
                enriched['engagement_rate'] = round(engagement_rate, 2)
                
                # Niveau de popularité
                enriched['popularity_level'] = self._calculate_popularity_level(views, likes, engagement_rate)
                
                # Performance score global
                enriched['performance_score'] = self._calculate_performance_score(
                    views, likes, enriched['comment_count'], engagement_rate
                )
            
            # Analyse du titre et description
            enriched['title_analysis'] = self._analyze_title(enriched['title'])
            enriched['content_category'] = self._categorize_content(enriched['title'], enriched['description'])
            
            # Date lisible
            try:
                published_date = datetime.fromisoformat(enriched['published_at'].replace('Z', '+00:00'))
                enriched['published_human'] = published_date.strftime('%d %B %Y')
                enriched['days_since_published'] = (datetime.now(published_date.tzinfo) - published_date).days
            except:
                enriched['published_human'] = 'Date inconnue'
                enriched['days_since_published'] = 0
            
            return enriched
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur enrichissement vidéo: {e}")
            return video_item

    def _parse_duration(self, duration_str: str) -> int:
        """
        Convertit une durée YouTube ISO 8601 en secondes
        
        Args:
            duration_str (str): Durée format PT1H2M3S
            
        Returns:
            int: Durée en secondes
        """
        try:
            # Exemple: PT1H2M3S -> 3723 secondes
            import re
            
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration_str)
            
            if not match:
                return 0
            
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            return hours * 3600 + minutes * 60 + seconds
            
        except:
            return 0

    def _calculate_popularity_level(self, views: int, likes: int, engagement_rate: float) -> str:
        """
        Détermine le niveau de popularité d'une vidéo
        
        Args:
            views (int): Nombre de vues
            likes (int): Nombre de likes
            engagement_rate (float): Taux d'engagement
            
        Returns:
            str: Niveau de popularité
        """
        if views >= 1000000:  # 1M+ vues
            return "Virale"
        elif views >= 100000:  # 100K+ vues
            return "Très populaire"
        elif views >= 10000:  # 10K+ vues
            return "Populaire"
        elif views >= 1000:  # 1K+ vues
            return "Modérée"
        else:
            return "Faible"

    def _calculate_performance_score(self, views: int, likes: int, comments: int, engagement_rate: float) -> float:
        """
        Calcule un score de performance global (0-100)
        
        Args:
            views (int): Nombre de vues
            likes (int): Nombre de likes
            comments (int): Nombre de commentaires
            engagement_rate (float): Taux d'engagement
            
        Returns:
            float: Score de performance
        """
        try:
            # Score basé sur plusieurs métriques
            view_score = min(views / 100000, 1.0) * 30  # Max 30 points pour les vues
            like_score = min(likes / 1000, 1.0) * 25    # Max 25 points pour les likes
            comment_score = min(comments / 100, 1.0) * 20  # Max 20 points pour les commentaires
            engagement_score = min(engagement_rate / 5.0, 1.0) * 25  # Max 25 points pour l'engagement
            
            total_score = view_score + like_score + comment_score + engagement_score
            return round(total_score, 1)
            
        except:
            return 0.0

    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """
        Analyse le titre d'une vidéo pour extraire des insights
        
        Args:
            title (str): Titre de la vidéo
            
        Returns:
            dict: Analyse du titre
        """
        try:
            title_lower = title.lower()
            
            # Mots-clés d'engagement
            engagement_keywords = ['comment', 'pourquoi', 'comment faire', 'top', 'meilleur', 'secret', 'astuce', 'guide']
            found_keywords = [kw for kw in engagement_keywords if kw in title_lower]
            
            # Émoticônes et ponctuation
            has_emojis = any(ord(char) > 127 for char in title)
            has_caps = title != title.lower()
            has_numbers = any(char.isdigit() for char in title)
            has_question = '?' in title
            has_exclamation = '!' in title
            
            # Score d'attractivité
            attractiveness_score = 0
            if found_keywords:
                attractiveness_score += len(found_keywords) * 10
            if has_emojis:
                attractiveness_score += 15
            if has_caps and title != title.upper():  # Éviter le spam CAPS
                attractiveness_score += 10
            if has_numbers:
                attractiveness_score += 5
            if has_question or has_exclamation:
                attractiveness_score += 10
            
            attractiveness_score = min(attractiveness_score, 100)
            
            return {
                'length': len(title),
                'word_count': len(title.split()),
                'engagement_keywords': found_keywords,
                'has_emojis': has_emojis,
                'has_caps': has_caps,
                'has_numbers': has_numbers,
                'has_question': has_question,
                'has_exclamation': has_exclamation,
                'attractiveness_score': attractiveness_score,
                'attractiveness_level': 'Élevée' if attractiveness_score >= 60 else 'Moyenne' if attractiveness_score >= 30 else 'Faible'
            }
            
        except:
            return {'length': len(title), 'analysis_error': True}

    def _categorize_content(self, title: str, description: str) -> str:
        """
        Catégorise automatiquement le contenu d'une vidéo
        
        Args:
            title (str): Titre de la vidéo
            description (str): Description de la vidéo
            
        Returns:
            str: Catégorie détectée
        """
        text = (title + ' ' + description).lower()
        
        # Catégories avec mots-clés
        categories = {
            'Gaming': ['gaming', 'jeu', 'game', 'gameplay', 'gamer', 'play', 'minecraft', 'fortnite'],
            'Éducation': ['tutorial', 'comment', 'apprendre', 'cours', 'formation', 'éducation', 'school'],
            'Musique': ['music', 'song', 'clip', 'concert', 'album', 'musique', 'chanson'],
            'Lifestyle': ['lifestyle', 'vlog', 'daily', 'routine', 'vie', 'quotidien'],
            'Tech': ['tech', 'technology', 'review', 'test', 'smartphone', 'ordinateur', 'app'],
            'Beauté': ['makeup', 'beauty', 'beauté', 'maquillage', 'skincare', 'cosmetics'],
            'Cuisine': ['cooking', 'recipe', 'cuisine', 'food', 'recette', 'chef'],
            'Sport': ['sport', 'fitness', 'workout', 'training', 'exercise', 'gym'],
            'Voyage': ['travel', 'voyage', 'trip', 'destination', 'vacation'],
            'Comédie': ['funny', 'comedy', 'humor', 'drôle', 'marrant', 'blague']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'Général'

    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Récupère les informations détaillées d'une chaîne
        
        Args:
            channel_id (str): ID de la chaîne YouTube
            
        Returns:
            dict: Informations complètes de la chaîne
        """
        try:
            self.stats['channel_analyses'] += 1
            
            params = {
                'part': 'snippet,statistics,brandingSettings',
                'id': channel_id,
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/channels",
                    params=params
                ) as response:
                    
                    self.stats['api_calls'] += 1
                    self.stats['quota_used'] += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'items' in data and len(data['items']) > 0:
                            channel = data['items'][0]
                            
                            # Enrichir les données de la chaîne
                            enriched_channel = await self._enrich_channel_data(channel)
                            
                            return {
                                'status': 'success',
                                'channel': enriched_channel,
                                'retrieved_at': datetime.now().isoformat()
                            }
                        else:
                            return {
                                'status': 'error',
                                'message': 'Chaîne non trouvée'
                            }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Erreur API: {response.status}'
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse chaîne {channel_id}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }

    async def _enrich_channel_data(self, channel: Dict) -> Dict:
        """
        Enrichit les données d'une chaîne avec des analyses avancées
        
        Args:
            channel (dict): Données brutes de la chaîne
            
        Returns:
            dict: Données enrichies
        """
        try:
            snippet = channel.get('snippet', {})
            stats = channel.get('statistics', {})
            
            # Données de base
            enriched = {
                'channel_id': channel['id'],
                'title': snippet.get('title'),
                'description': snippet.get('description', '')[:500] + '...' if len(snippet.get('description', '')) > 500 else snippet.get('description', ''),
                'custom_url': snippet.get('customUrl'),
                'published_at': snippet.get('publishedAt'),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'country': snippet.get('country'),
                'channel_url': f"https://www.youtube.com/channel/{channel['id']}"
            }
            
            # Statistiques
            subscriber_count = int(stats.get('subscriberCount', 0))
            video_count = int(stats.get('videoCount', 0))
            view_count = int(stats.get('viewCount', 0))
            
            enriched.update({
                'subscriber_count': subscriber_count,
                'video_count': video_count,
                'view_count': view_count,
                'subscribers_human': self._format_number(subscriber_count),
                'views_human': self._format_number(view_count),
                'videos_human': self._format_number(video_count)
            })
            
            # Métriques calculées
            if video_count > 0:
                enriched['avg_views_per_video'] = view_count // video_count
                enriched['avg_views_per_video_human'] = self._format_number(enriched['avg_views_per_video'])
            
            # Niveau de la chaîne
            enriched['channel_size'] = self._determine_channel_size(subscriber_count)
            
            # Score de performance de la chaîne
            enriched['performance_score'] = self._calculate_channel_performance(
                subscriber_count, video_count, view_count
            )
            
            # Analyse de la description
            enriched['category_detected'] = self._categorize_content(
                enriched['title'], enriched['description']
            )
            
            # Date de création lisible
            try:
                created_date = datetime.fromisoformat(enriched['published_at'].replace('Z', '+00:00'))
                enriched['created_human'] = created_date.strftime('%d %B %Y')
                enriched['channel_age_days'] = (datetime.now(created_date.tzinfo) - created_date).days
                enriched['channel_age_years'] = round(enriched['channel_age_days'] / 365.25, 1)
            except:
                enriched['created_human'] = 'Date inconnue'
                enriched['channel_age_days'] = 0
                enriched['channel_age_years'] = 0
            
            return enriched
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur enrichissement chaîne: {e}")
            return channel

    def _format_number(self, number: int) -> str:
        """
        Formate un nombre en format lisible (1.2K, 3.4M, etc.)
        
        Args:
            number (int): Nombre à formater
            
        Returns:
            str: Nombre formaté
        """
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return str(number)

    def _determine_channel_size(self, subscribers: int) -> str:
        """
        Détermine la taille d'une chaîne YouTube
        
        Args:
            subscribers (int): Nombre d'abonnés
            
        Returns:
            str: Taille de la chaîne
        """
        if subscribers >= 10_000_000:
            return "Mega Chaîne (10M+)"
        elif subscribers >= 1_000_000:
            return "Grande Chaîne (1M+)"
        elif subscribers >= 100_000:
            return "Chaîne Établie (100K+)"
        elif subscribers >= 10_000:
            return "Chaîne Montante (10K+)"
        elif subscribers >= 1_000:
            return "Petite Chaîne (1K+)"
        else:
            return "Nouvelle Chaîne (<1K)"

    def _calculate_channel_performance(self, subscribers: int, videos: int, views: int) -> float:
        """
        Calcule un score de performance pour une chaîne (0-100)
        
        Args:
            subscribers (int): Nombre d'abonnés
            videos (int): Nombre de vidéos
            views (int): Vues totales
            
        Returns:
            float: Score de performance
        """
        try:
            # Score basé sur plusieurs métriques
            subscriber_score = min(subscribers / 1_000_000, 1.0) * 40  # Max 40 points
            view_score = min(views / 100_000_000, 1.0) * 30  # Max 30 points
            
            # Ratio vues/abonnés (engagement)
            if subscribers > 0:
                views_per_sub = views / subscribers
                engagement_score = min(views_per_sub / 50, 1.0) * 20  # Max 20 points
            else:
                engagement_score = 0
            
            # Productivité (vidéos publiées)
            productivity_score = min(videos / 100, 1.0) * 10  # Max 10 points
            
            total_score = subscriber_score + view_score + engagement_score + productivity_score
            return round(total_score, 1)
            
        except:
            return 0.0

    async def get_trending_videos(self, region_code: str = "FR", category_id: str = "0") -> Dict[str, Any]:
        """
        Récupère les vidéos en tendance
        
        Args:
            region_code (str): Code région (FR, US, etc.)
            category_id (str): ID de catégorie (0=tous)
            
        Returns:
            dict: Vidéos en tendance
        """
        try:
            params = {
                'part': 'snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': 25,
                'key': self.api_key
            }
            
            if category_id != "0":
                params['videoCategoryId'] = category_id
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/videos",
                    params=params
                ) as response:
                    
                    self.stats['api_calls'] += 1
                    self.stats['quota_used'] += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Enrichir les vidéos tendance
                        trending_videos = []
                        for item in data.get('items', []):
                            enriched_video = await self._enrich_video_data_from_full(item)
                            trending_videos.append(enriched_video)
                        
                        return {
                            'status': 'success',
                            'region': region_code,
                            'category': category_id,
                            'total_trending': len(trending_videos),
                            'videos': trending_videos,
                            'retrieved_at': datetime.now().isoformat()
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Erreur API: {response.status}'
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur tendances YouTube: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }

    async def _enrich_video_data_from_full(self, video_item: Dict) -> Dict:
        """
        Enrichit les données d'une vidéo à partir de l'API videos (pas search)
        
        Args:
            video_item (dict): Données complètes de la vidéo
            
        Returns:
            dict: Données enrichies
        """
        # Adapter la structure pour réutiliser la logique d'enrichissement
        adapted_item = {
            'id': {'videoId': video_item['id']},
            'snippet': video_item['snippet']
        }
        
        stats_data = {
            video_item['id']: {
                'statistics': video_item.get('statistics', {}),
                'contentDetails': video_item.get('contentDetails', {})
            }
        }
        
        return await self._enrich_video_data(adapted_item, stats_data.get(video_item['id']))

    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation du moteur YouTube
        
        Returns:
            dict: Statistiques complètes
        """
        return {
            'youtube_stats': self.stats.copy(),
            'cache_info': {
                'cache_dir': str(self.cache_dir),
                'cached_files': len(list(self.cache_dir.glob("*.json")))
            },
            'api_info': {
                'api_key_configured': bool(self.api_key),
                'base_url': self.base_url,
                'quota_remaining': 10000 - self.stats['quota_used']  # Quota quotidien approximatif
            }
        }

    async def search_channels(self, query: str, max_results: int = 25) -> Dict[str, Any]:
        """
        Recherche de chaînes YouTube
        
        Args:
            query (str): Terme de recherche
            max_results (int): Nombre de résultats max
            
        Returns:
            dict: Chaînes trouvées
        """
        try:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'channel',
                'maxResults': min(max_results, 50),
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params
                ) as response:
                    
                    self.stats['api_calls'] += 1
                    self.stats['quota_used'] += 100
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Enrichir les chaînes avec leurs statistiques
                        enriched_channels = []
                        for item in data.get('items', []):
                            channel_id = item['id']['channelId']
                            channel_info = await self.get_channel_info(channel_id)
                            
                            if channel_info['status'] == 'success':
                                enriched_channels.append(channel_info['channel'])
                        
                        return {
                            'status': 'success',
                            'query': query,
                            'total_results': len(enriched_channels),
                            'channels': enriched_channels,
                            'search_time': datetime.now().isoformat()
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Erreur API: {response.status}'
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche chaînes: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }


# Test du module
async def test_youtube_engine():
    """
    Test complet du moteur YouTube
    """
    print("📺 Test IA Chéries YouTube Engine")
    print("=" * 50)
    
    try:
        # Initialisation
        engine = IaCheriesYouTubeAPI()
        
        # Test 1: Recherche de vidéos
        print("📝 Test 1: Recherche de vidéos...")
        video_results = await engine.search_videos(
            query="Python programming tutorial",
            max_results=5,
            order="relevance"
        )
        
        if video_results['status'] == 'success':
            print(f"✅ {len(video_results['videos'])} vidéos trouvées")
            for video in video_results['videos'][:2]:
                print(f"   - {video['title'][:60]}...")
                print(f"     Vues: {video.get('view_count', 'N/A')} | Engagement: {video.get('engagement_rate', 0)}%")
        else:
            print(f"❌ Erreur recherche vidéos: {video_results.get('message')}")
        
        # Test 2: Analyse d'une chaîne (si des résultats)
        if video_results['status'] == 'success' and video_results['videos']:
            print("\n📺 Test 2: Analyse d'une chaîne...")
            first_video = video_results['videos'][0]
            channel_info = await engine.get_channel_info(first_video['channel_id'])
            
            if channel_info['status'] == 'success':
                channel = channel_info['channel']
                print(f"✅ Chaîne analysée: {channel['title']}")
                print(f"   Abonnés: {channel.get('subscribers_human', 'N/A')} | Taille: {channel.get('channel_size', 'N/A')}")
                print(f"   Score performance: {channel.get('performance_score', 0)}/100")
            else:
                print(f"❌ Erreur analyse chaîne: {channel_info.get('message')}")
        
        # Test 3: Tendances
        print("\n🔥 Test 3: Vidéos en tendance...")
        trending = await engine.get_trending_videos(region_code="FR")
        
        if trending['status'] == 'success':
            print(f"✅ {len(trending['videos'])} vidéos en tendance trouvées")
            for video in trending['videos'][:3]:
                print(f"   - {video['title'][:50]}... | {video.get('popularity_level', 'N/A')}")
        else:
            print(f"❌ Erreur tendances: {trending.get('message')}")
        
        # Statistiques finales
        print("\n📊 Statistiques:")
        stats = engine.get_stats()
        print(f"   Recherches vidéos: {stats['youtube_stats']['video_searches']}")
        print(f"   Analyses chaînes: {stats['youtube_stats']['channel_analyses']}")
        print(f"   Appels API: {stats['youtube_stats']['api_calls']}")
        print(f"   Quota utilisé: {stats['youtube_stats']['quota_used']}/10000")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return False


if __name__ == "__main__":
    # Exécution des tests
    asyncio.run(test_youtube_engine())