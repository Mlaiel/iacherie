#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔴 AINFLUENCER REDDIT ENGINE
============================

Module d'intégration avec l'API Reddit pour :
- Récupération de posts populaires
- Analyse de commentaires
- Extraction de tendances
- Monitoring de communautés

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
import base64

class AinfluencerRedditAPI:
    """
    🔴 Moteur Reddit pour Ainfluencer
    
    Fonctionnalités:
    - Récupération de posts par subreddit
    - Analyse de sentiments des commentaires
    - Extraction de tendances
    - Monitoring de communautés
    - Analytics d'engagement
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialise le moteur Reddit
        
        Args:
            client_id (str): ID client Reddit
            client_secret (str): Secret client Reddit
        """
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("❌ Clés Reddit manquantes!")
            
        # Configuration API
        self.base_url = "https://www.reddit.com/api/v1"
        self.oauth_url = "https://oauth.reddit.com"
        self.user_agent = "Ainfluencer-Platform/2.0"
        
        # Token d'accès
        self.access_token = None
        self.token_expires = None
        
        # Cache et stockage
        self.cache_dir = Path("cache/reddit")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistiques
        self.stats = {
            'posts_fetched': 0,
            'comments_analyzed': 0,
            'api_calls': 0,
            'communities_monitored': 0,
            'cache_hits': 0
        }
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔴 Reddit Engine initialisé avec succès!")

    async def _get_access_token(self) -> str:
        """
        Obtient un token d'accès OAuth2 pour Reddit
        
        Returns:
            str: Token d'accès
        """
        try:
            # Vérifier si le token existant est encore valide
            if self.access_token and self.token_expires and datetime.now() < self.token_expires:
                return self.access_token
            
            # Préparer les credentials
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': self.user_agent,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/access_token",
                    headers=headers,
                    data=data
                ) as response:
                    
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data['access_token']
                        # Le token expire dans 1 heure (3600 secondes)
                        self.token_expires = datetime.now() + timedelta(seconds=3600)
                        
                        self.logger.info("✅ Token Reddit obtenu avec succès")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Erreur OAuth Reddit: {response.status} - {error_text}")
                        raise Exception(f"Erreur OAuth: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur token Reddit: {str(e)}")
            raise

    async def get_subreddit_posts(
        self,
        subreddit: str,
        sort: str = "hot",
        limit: int = 25,
        time_filter: str = "day"
    ) -> Dict[str, Any]:
        """
        Récupère les posts d'un subreddit
        
        Args:
            subreddit (str): Nom du subreddit (sans r/)
            sort (str): Type de tri (hot, new, top, rising)
            limit (int): Nombre de posts (max 100)
            time_filter (str): Filtre temporel pour 'top' (hour, day, week, month, year, all)
            
        Returns:
            dict: Posts du subreddit avec métadonnées
        """
        try:
            self.stats['api_calls'] += 1
            
            # Obtenir le token d'accès
            token = await self._get_access_token()
            
            # Headers avec authentification
            headers = {
                'Authorization': f'Bearer {token}',
                'User-Agent': self.user_agent
            }
            
            # Paramètres de requête
            params = {
                'limit': min(limit, 100),
                'raw_json': 1
            }
            
            # Ajouter le filtre temporel pour 'top'
            if sort == 'top':
                params['t'] = time_filter
            
            # URL de l'endpoint
            url = f"{self.oauth_url}/r/{subreddit}/{sort}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        posts_data = data.get('data', {}).get('children', [])
                        
                        # Traiter les posts
                        processed_posts = []
                        for post_container in posts_data:
                            post = post_container.get('data', {})
                            processed_post = await self._process_post_data(post)
                            processed_posts.append(processed_post)
                        
                        self.stats['posts_fetched'] += len(processed_posts)
                        
                        result = {
                            'status': 'success',
                            'subreddit': subreddit,
                            'sort': sort,
                            'time_filter': time_filter if sort == 'top' else None,
                            'total_posts': len(processed_posts),
                            'posts': processed_posts,
                            'fetched_at': datetime.now().isoformat(),
                            'reddit_info': {
                                'subreddit_url': f"https://reddit.com/r/{subreddit}",
                                'sort_type': sort
                            }
                        }
                        
                        self.logger.info(f"📋 Subreddit r/{subreddit}: {len(processed_posts)} posts récupérés")
                        return result
                        
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Erreur API Reddit: {response.status} - {error_text}")
                        return {
                            'status': 'error',
                            'message': f'Erreur API Reddit: {response.status}',
                            'details': error_text
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération subreddit r/{subreddit}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }

    async def _process_post_data(self, post: Dict) -> Dict:
        """
        Traite et enrichit les données d'un post Reddit
        
        Args:
            post (dict): Données brutes du post
            
        Returns:
            dict: Post traité et enrichi
        """
        try:
            processed = {
                # Identifiants
                'id': post.get('id'),
                'fullname': post.get('name'),
                'permalink': f"https://reddit.com{post.get('permalink', '')}",
                
                # Contenu
                'title': post.get('title', ''),
                'text': post.get('selftext', ''),
                'url': post.get('url', ''),
                'is_self': post.get('is_self', False),
                
                # Auteur et subreddit
                'author': post.get('author', '[deleted]'),
                'subreddit': post.get('subreddit', ''),
                'subreddit_prefixed': post.get('subreddit_name_prefixed', ''),
                
                # Engagement
                'score': post.get('score', 0),
                'upvote_ratio': post.get('upvote_ratio', 0.0),
                'num_comments': post.get('num_comments', 0),
                'num_crossposts': post.get('num_crossposts', 0),
                
                # Métadonnées temporelles
                'created_utc': post.get('created_utc', 0),
                'created_human': self._format_reddit_time(post.get('created_utc', 0)),
                
                # Flags et statut
                'over_18': post.get('over_18', False),
                'spoiler': post.get('spoiler', False),
                'locked': post.get('locked', False),
                'stickied': post.get('stickied', False),
                'archived': post.get('archived', False),
                
                # Awards et distinctions
                'gilded': post.get('gilded', 0),
                'total_awards_received': post.get('total_awards_received', 0),
                
                # Flair
                'link_flair_text': post.get('link_flair_text'),
                'author_flair_text': post.get('author_flair_text'),
                
                # Médias
                'thumbnail': post.get('thumbnail'),
                'is_video': post.get('is_video', False),
                'domain': post.get('domain', ''),
            }
            
            # Calcul de métriques d'engagement
            processed['engagement_score'] = self._calculate_engagement_score(processed)
            processed['engagement_level'] = self._get_engagement_level(processed['engagement_score'])
            
            # Catégorisation du contenu
            processed['content_type'] = self._categorize_post_content(processed)
            
            # Score de viralité potentielle
            processed['viral_potential'] = self._calculate_viral_potential(processed)
            
            return processed
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur traitement post {post.get('id', 'unknown')}: {e}")
            return post

    def _calculate_engagement_score(self, post: Dict) -> float:
        """
        Calcule un score d'engagement pour un post
        
        Args:
            post (dict): Données du post
            
        Returns:
            float: Score d'engagement de 0 à 100
        """
        try:
            score = 0.0
            
            # Score basé sur les upvotes (40% du total)
            upvotes = max(post.get('score', 0), 0)
            if upvotes > 0:
                # Échelle logarithmique pour éviter la domination des posts très populaires
                import math
                upvote_score = min(math.log10(upvotes + 1) * 10, 40)
                score += upvote_score
            
            # Ratio upvote/downvote (25% du total)
            ratio = post.get('upvote_ratio', 0.5)
            ratio_score = (ratio - 0.5) * 50  # Convertir de 0.5-1.0 vers 0-25
            score += max(ratio_score, 0)
            
            # Engagement commentaires (25% du total)
            comments = post.get('num_comments', 0)
            if comments > 0:
                comment_score = min(math.log10(comments + 1) * 8, 25)
                score += comment_score
            
            # Awards et distinctions (10% du total)
            awards = post.get('total_awards_received', 0)
            if awards > 0:
                award_score = min(awards * 2, 10)
                score += award_score
            
            return round(score, 1)
            
        except Exception:
            return 0.0

    def _get_engagement_level(self, score: float) -> str:
        """
        Détermine le niveau d'engagement basé sur le score
        
        Args:
            score (float): Score d'engagement
            
        Returns:
            str: Niveau d'engagement
        """
        if score >= 80:
            return "Viral"
        elif score >= 60:
            return "Très Élevé"
        elif score >= 40:
            return "Élevé"
        elif score >= 20:
            return "Moyen"
        else:
            return "Faible"

    def _categorize_post_content(self, post: Dict) -> str:
        """
        Catégorise automatiquement le contenu d'un post
        
        Args:
            post (dict): Données du post
            
        Returns:
            str: Catégorie de contenu
        """
        title = post.get('title', '').lower()
        text = post.get('text', '').lower()
        domain = post.get('domain', '').lower()
        
        # Images et médias
        if post.get('is_video') or any(img in domain for img in ['imgur', 'i.redd.it', 'youtube', 'youtu.be']):
            return "Média"
        
        # Questions
        if any(q in title for q in ['?', 'how', 'what', 'why', 'where', 'when', 'eli5', 'question']):
            return "Question"
        
        # Actualités
        if any(news in domain for news in ['bbc', 'cnn', 'reuters', 'news', 'guardian']):
            return "Actualité"
        
        # Discussions
        if any(disc in title for disc in ['discussion', 'thoughts', 'opinion', 'unpopular']):
            return "Discussion"
        
        # Aide/Support
        if any(help_word in title for help_word in ['help', 'support', 'advice', 'tips']):
            return "Aide"
        
        # Memes/Humour
        if any(fun in title for fun in ['meme', 'funny', 'joke', 'lol', 'humor']):
            return "Humour"
        
        return "Général"

    def _calculate_viral_potential(self, post: Dict) -> float:
        """
        Calcule le potentiel viral d'un post
        
        Args:
            post (dict): Données du post
            
        Returns:
            float: Score de viralité de 0 à 100
        """
        try:
            # Facteurs de viralité
            factors = []
            
            # Ratio commentaires/score élevé (discussion active)
            score = max(post.get('score', 1), 1)
            comments = post.get('num_comments', 0)
            if score > 0:
                comment_ratio = comments / score
                factors.append(min(comment_ratio * 50, 25))
            
            # Ratio upvote élevé
            upvote_ratio = post.get('upvote_ratio', 0.5)
            factors.append((upvote_ratio - 0.5) * 50)
            
            # Présence d'awards (signal de qualité)
            awards = post.get('total_awards_received', 0)
            factors.append(min(awards * 5, 15))
            
            # Type de contenu viral
            content_type = post.get('content_type', '')
            if content_type in ['Média', 'Humour']:
                factors.append(10)
            elif content_type in ['Question', 'Discussion']:
                factors.append(5)
            
            # Fraîcheur du post (nouveaux posts ont plus de potentiel)
            import time
            created = post.get('created_utc', time.time())
            age_hours = (time.time() - created) / 3600
            if age_hours < 2:
                factors.append(15)
            elif age_hours < 6:
                factors.append(10)
            elif age_hours < 24:
                factors.append(5)
            
            return round(sum(factors), 1)
            
        except Exception:
            return 0.0

    def _format_reddit_time(self, timestamp: float) -> str:
        """
        Formate un timestamp Reddit en format lisible
        
        Args:
            timestamp (float): Timestamp UTC
            
        Returns:
            str: Date formatée
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Date inconnue"

    async def search_reddit(
        self,
        query: str,
        subreddit: str = None,
        sort: str = "relevance",
        time_filter: str = "all",
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Recherche dans Reddit
        
        Args:
            query (str): Terme de recherche
            subreddit (str): Limiter à un subreddit (optionnel)
            sort (str): Tri (relevance, hot, top, new, comments)
            time_filter (str): Filtre temporel (hour, day, week, month, year, all)
            limit (int): Nombre de résultats
            
        Returns:
            dict: Résultats de recherche
        """
        try:
            self.stats['api_calls'] += 1
            
            # Obtenir le token d'accès
            token = await self._get_access_token()
            
            headers = {
                'Authorization': f'Bearer {token}',
                'User-Agent': self.user_agent
            }
            
            # Paramètres de recherche
            params = {
                'q': query,
                'sort': sort,
                't': time_filter,
                'limit': min(limit, 100),
                'raw_json': 1
            }
            
            # URL de recherche (globale ou dans subreddit)
            if subreddit:
                url = f"{self.oauth_url}/r/{subreddit}/search"
                params['restrict_sr'] = 'true'
            else:
                url = f"{self.oauth_url}/search"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        posts_data = data.get('data', {}).get('children', [])
                        
                        # Traiter les résultats
                        processed_results = []
                        for post_container in posts_data:
                            post = post_container.get('data', {})
                            processed_post = await self._process_post_data(post)
                            processed_results.append(processed_post)
                        
                        return {
                            'status': 'success',
                            'query': query,
                            'subreddit': subreddit,
                            'total_results': len(processed_results),
                            'results': processed_results,
                            'search_params': {
                                'sort': sort,
                                'time_filter': time_filter,
                                'limit': limit
                            },
                            'searched_at': datetime.now().isoformat()
                        }
                        
                    else:
                        error_text = await response.text()
                        return {
                            'status': 'error',
                            'message': f'Erreur recherche Reddit: {response.status}',
                            'details': error_text
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche Reddit '{query}': {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation
        
        Returns:
            dict: Statistiques complètes
        """
        return {
            'reddit_stats': self.stats.copy(),
            'cache_info': {
                'cache_dir': str(self.cache_dir),
                'cached_files': len(list(self.cache_dir.glob("*.json")))
            },
            'api_info': {
                'client_id_configured': bool(self.client_id),
                'token_valid': bool(self.access_token and self.token_expires and datetime.now() < self.token_expires),
                'oauth_url': self.oauth_url
            }
        }


# Test du module
async def test_reddit_engine():
    """
    Test complet du moteur Reddit
    """
    print("🔴 Test Ainfluencer Reddit Engine")
    print("=" * 50)
    
    try:
        # Initialisation
        reddit = AinfluencerRedditAPI()
        
        # Test 1: Récupération de posts populaires
        print("📋 Test 1: Posts populaires de r/technology...")
        posts_result = await reddit.get_subreddit_posts(
            subreddit="technology",
            sort="hot",
            limit=5
        )
        
        if posts_result['status'] == 'success':
            print(f"✅ {posts_result['total_posts']} posts récupérés")
            for post in posts_result['posts'][:2]:
                print(f"   - {post['title'][:60]}...")
                print(f"     Score: {post['score']} | Commentaires: {post['num_comments']} | Engagement: {post['engagement_level']}")
        else:
            print(f"❌ Erreur posts: {posts_result.get('message')}")
        
        # Test 2: Recherche
        print("\n🔍 Test 2: Recherche 'artificial intelligence'...")
        search_result = await reddit.search_reddit(
            query="artificial intelligence",
            sort="top",
            time_filter="week",
            limit=3
        )
        
        if search_result['status'] == 'success':
            print(f"✅ {search_result['total_results']} résultats trouvés")
            for result in search_result['results'][:2]:
                print(f"   - r/{result['subreddit']}: {result['title'][:50]}...")
                print(f"     Viral potential: {result['viral_potential']:.1f}/100")
        else:
            print(f"❌ Erreur recherche: {search_result.get('message')}")
        
        # Statistiques finales
        print("\n📊 Statistiques:")
        stats = reddit.get_stats()
        print(f"   Posts récupérés: {stats['reddit_stats']['posts_fetched']}")
        print(f"   Appels API: {stats['reddit_stats']['api_calls']}")
        print(f"   Token valide: {stats['api_info']['token_valid']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return False


if __name__ == "__main__":
    # Exécution des tests
    asyncio.run(test_reddit_engine())