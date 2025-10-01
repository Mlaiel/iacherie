#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐦 IA CHÉRIES TWITTER ENGINE
=============================

Module d'intégration avec l'API Twitter v2 pour :
- Récupération de tweets et tendances
- Analyse de sentiment Twitter
- Monitoring d'hashtags et mentions
- Extraction de métriques d'engagement

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

class IaCheriesTwitterAPI:
    """
    🐦 Moteur Twitter pour IA Chéries
    
    Fonctionnalités:
    - Récupération de tweets par utilisateur
    - Recherche de tweets par mots-clés
    - Monitoring de hashtags
    - Analyse de tendances
    - Métriques d'engagement
    """
    
    def __init__(self, bearer_token: str = None):
        """
        Initialise le moteur Twitter
        
        Args:
            bearer_token (str): Bearer Token Twitter API v2
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        
        if not self.bearer_token:
            raise ValueError("❌ Bearer Token Twitter manquant!")
            
        # Configuration API
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'IA Chéries-Platform/2.0'
        }
        
        # Cache et stockage
        self.cache_dir = Path("cache/twitter")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistiques
        self.stats = {
            'tweets_fetched': 0,
            'searches_performed': 0,
            'users_analyzed': 0,
            'api_calls': 0,
            'cache_hits': 0
        }
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🐦 Twitter Engine initialisé avec succès!")

    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 10,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> Dict[str, Any]:
        """
        Récupère les tweets d'un utilisateur
        
        Args:
            username (str): Nom d'utilisateur Twitter (sans @)
            max_results (int): Nombre de tweets à récupérer (5-100)
            exclude_replies (bool): Exclure les réponses
            exclude_retweets (bool): Exclure les retweets
            
        Returns:
            dict: Tweets de l'utilisateur avec métadonnées
        """
        try:
            self.stats['api_calls'] += 1
            
            # D'abord, obtenir l'ID de l'utilisateur
            user_info = await self._get_user_by_username(username)
            if not user_info or user_info['status'] != 'success':
                return {
                    'status': 'error',
                    'message': f'Utilisateur @{username} non trouvé'
                }
            
            user_id = user_info['user']['id']
            
            # Paramètres pour les tweets
            params = {
                'max_results': min(max(max_results, 5), 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations,lang,possibly_sensitive,reply_settings,source',
                'user.fields': 'name,username,verified,public_metrics,description,profile_image_url',
                'expansions': 'author_id'
            }
            
            # Exclusions
            excludes = []
            if exclude_replies:
                excludes.append('replies')
            if exclude_retweets:
                excludes.append('retweets')
            
            if excludes:
                params['exclude'] = ','.join(excludes)
            
            # Requête API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/{user_id}/tweets",
                    headers=self.headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        tweets = data.get('data', [])
                        
                        # Traiter les tweets
                        processed_tweets = []
                        for tweet in tweets:
                            processed_tweet = await self._process_tweet_data(tweet, user_info['user'])
                            processed_tweets.append(processed_tweet)
                        
                        self.stats['tweets_fetched'] += len(processed_tweets)
                        self.stats['users_analyzed'] += 1
                        
                        result = {
                            'status': 'success',
                            'username': username,
                            'user_info': user_info['user'],
                            'total_tweets': len(processed_tweets),
                            'tweets': processed_tweets,
                            'filters': {
                                'exclude_replies': exclude_replies,
                                'exclude_retweets': exclude_retweets,
                                'max_results': max_results
                            },
                            'fetched_at': datetime.now().isoformat()
                        }
                        
                        self.logger.info(f"📱 @{username}: {len(processed_tweets)} tweets récupérés")
                        return result
                        
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Erreur API Twitter: {response.status} - {error_text}")
                        return {
                            'status': 'error',
                            'message': f'Erreur API Twitter: {response.status}',
                            'details': error_text
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération tweets @{username}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }

    async def _get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        Récupère les informations d'un utilisateur par son nom
        
        Args:
            username (str): Nom d'utilisateur
            
        Returns:
            dict: Informations utilisateur
        """
        try:
            params = {
                'user.fields': 'name,username,verified,public_metrics,description,profile_image_url,created_at'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/by/username/{username}",
                    headers=self.headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        user_data = data.get('data', {})
                        
                        return {
                            'status': 'success',
                            'user': {
                                'id': user_data.get('id'),
                                'name': user_data.get('name'),
                                'username': user_data.get('username'),
                                'verified': user_data.get('verified', False),
                                'description': user_data.get('description', ''),
                                'profile_image_url': user_data.get('profile_image_url', ''),
                                'created_at': user_data.get('created_at'),
                                'followers_count': user_data.get('public_metrics', {}).get('followers_count', 0),
                                'following_count': user_data.get('public_metrics', {}).get('following_count', 0),
                                'tweet_count': user_data.get('public_metrics', {}).get('tweet_count', 0),
                                'listed_count': user_data.get('public_metrics', {}).get('listed_count', 0)
                            }
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Utilisateur non trouvé: {response.status}'
                        }
                        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erreur récupération utilisateur: {str(e)}'
            }

    async def _process_tweet_data(self, tweet: Dict, user_info: Dict) -> Dict:
        """
        Traite et enrichit les données d'un tweet
        
        Args:
            tweet (dict): Données brutes du tweet
            user_info (dict): Informations de l'utilisateur
            
        Returns:
            dict: Tweet traité et enrichi
        """
        try:
            metrics = tweet.get('public_metrics', {})
            
            processed = {
                # Identifiants
                'id': tweet.get('id'),
                'url': f"https://twitter.com/{user_info['username']}/status/{tweet.get('id')}",
                
                # Contenu
                'text': tweet.get('text', ''),
                'lang': tweet.get('lang', 'und'),
                'possibly_sensitive': tweet.get('possibly_sensitive', False),
                
                # Métadonnées temporelles
                'created_at': tweet.get('created_at'),
                'created_human': self._format_twitter_time(tweet.get('created_at', '')),
                
                # Métriques d'engagement
                'retweet_count': metrics.get('retweet_count', 0),
                'like_count': metrics.get('like_count', 0),
                'reply_count': metrics.get('reply_count', 0),
                'quote_count': metrics.get('quote_count', 0),
                
                # Source et paramètres
                'source': tweet.get('source', ''),
                'reply_settings': tweet.get('reply_settings', 'everyone'),
                
                # Contexte et annotations
                'context_annotations': tweet.get('context_annotations', []),
                
                # Informations utilisateur
                'author': {
                    'username': user_info['username'],
                    'name': user_info['name'],
                    'verified': user_info.get('verified', False)
                }
            }
            
            # Calcul de métriques d'engagement
            processed['engagement_score'] = self._calculate_twitter_engagement(processed)
            processed['engagement_level'] = self._get_engagement_level(processed['engagement_score'])
            
            # Analyse du contenu
            processed['content_analysis'] = self._analyze_tweet_content(processed)
            
            # Potentiel viral
            processed['viral_potential'] = self._calculate_viral_potential(processed, user_info)
            
            return processed
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur traitement tweet {tweet.get('id', 'unknown')}: {e}")
            return tweet

    def _calculate_twitter_engagement(self, tweet: Dict) -> float:
        """
        Calcule un score d'engagement pour un tweet
        
        Args:
            tweet (dict): Données du tweet
            
        Returns:
            float: Score d'engagement de 0 à 100
        """
        try:
            # Récupérer les métriques
            likes = tweet.get('like_count', 0)
            retweets = tweet.get('retweet_count', 0)
            replies = tweet.get('reply_count', 0)
            quotes = tweet.get('quote_count', 0)
            
            # Poids différents pour chaque type d'engagement
            engagement_total = (likes * 1) + (retweets * 3) + (replies * 2) + (quotes * 4)
            
            # Échelle logarithmique pour normaliser
            if engagement_total > 0:
                import math
                score = min(math.log10(engagement_total + 1) * 20, 100)
            else:
                score = 0
                
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

    def _analyze_tweet_content(self, tweet: Dict) -> Dict:
        """
        Analyse le contenu d'un tweet
        
        Args:
            tweet (dict): Données du tweet
            
        Returns:
            dict: Analyse de contenu
        """
        text = tweet.get('text', '').lower()
        
        analysis = {
            'has_hashtags': '#' in text,
            'has_mentions': '@' in text,
            'has_links': 'http' in text,
            'hashtag_count': text.count('#'),
            'mention_count': text.count('@'),
            'word_count': len(text.split()),
            'char_count': len(tweet.get('text', '')),
            'is_thread': 'thread' in text or '1/' in text,
            'has_emoji': any(ord(char) > 127 for char in tweet.get('text', '')),
        }
        
        # Classification du type de tweet
        if analysis['has_links']:
            analysis['type'] = 'Partage de lien'
        elif analysis['mention_count'] > 0 and not analysis['has_hashtags']:
            analysis['type'] = 'Conversation'
        elif analysis['hashtag_count'] > 2:
            analysis['type'] = 'Promotion/Marketing'
        elif '?' in text:
            analysis['type'] = 'Question'
        elif analysis['is_thread']:
            analysis['type'] = 'Thread'
        else:
            analysis['type'] = 'Statut général'
            
        return analysis

    def _calculate_viral_potential(self, tweet: Dict, user_info: Dict) -> float:
        """
        Calcule le potentiel viral d'un tweet
        
        Args:
            tweet (dict): Données du tweet
            user_info (dict): Informations de l'utilisateur
            
        Returns:
            float: Score de viralité de 0 à 100
        """
        try:
            factors = []
            
            # Taille de l'audience (followers)
            followers = user_info.get('followers_count', 0)
            if followers > 0:
                import math
                audience_score = min(math.log10(followers) * 5, 20)
                factors.append(audience_score)
            
            # Ratio engagement/followers
            engagement_total = (
                tweet.get('like_count', 0) +
                tweet.get('retweet_count', 0) +
                tweet.get('reply_count', 0)
            )
            
            if followers > 0 and engagement_total > 0:
                engagement_ratio = (engagement_total / followers) * 100
                factors.append(min(engagement_ratio * 10, 25))
            
            # Vérification du compte
            if user_info.get('verified', False):
                factors.append(10)
            
            # Analyse de contenu
            content = tweet.get('content_analysis', {})
            if content.get('has_hashtags'):
                factors.append(5)
            if content.get('has_links'):
                factors.append(5)
            if content.get('type') in ['Thread', 'Question']:
                factors.append(8)
            
            # Fraîcheur (tweets récents ont plus de potentiel)
            created_at = tweet.get('created_at', '')
            if created_at:
                try:
                    tweet_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - tweet_time.replace(tzinfo=None)).total_seconds() / 3600
                    if age_hours < 1:
                        factors.append(15)
                    elif age_hours < 6:
                        factors.append(10)
                    elif age_hours < 24:
                        factors.append(5)
                except:
                    pass
            
            return round(sum(factors), 1)
            
        except Exception:
            return 0.0

    def _format_twitter_time(self, twitter_time: str) -> str:
        """
        Formate un timestamp Twitter en format lisible
        
        Args:
            twitter_time (str): Timestamp Twitter ISO
            
        Returns:
            str: Date formatée
        """
        try:
            if twitter_time:
                dt = datetime.fromisoformat(twitter_time.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return "Date inconnue"
        except:
            return "Date inconnue"

    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        sort_order: str = "relevancy"
    ) -> Dict[str, Any]:
        """
        Recherche de tweets
        
        Args:
            query (str): Requête de recherche
            max_results (int): Nombre de résultats (10-100)
            sort_order (str): Ordre de tri (recency, relevancy)
            
        Returns:
            dict: Résultats de recherche
        """
        try:
            self.stats['api_calls'] += 1
            self.stats['searches_performed'] += 1
            
            params = {
                'query': query,
                'max_results': min(max(max_results, 10), 100),
                'sort_order': sort_order,
                'tweet.fields': 'created_at,public_metrics,context_annotations,lang,possibly_sensitive',
                'user.fields': 'name,username,verified,public_metrics',
                'expansions': 'author_id'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/tweets/search/recent",
                    headers=self.headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        tweets = data.get('data', [])
                        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                        
                        # Traiter les tweets
                        processed_tweets = []
                        for tweet in tweets:
                            author_id = tweet.get('author_id')
                            user_info = users.get(author_id, {})
                            processed_tweet = await self._process_tweet_data(tweet, user_info)
                            processed_tweets.append(processed_tweet)
                        
                        self.stats['tweets_fetched'] += len(processed_tweets)
                        
                        return {
                            'status': 'success',
                            'query': query,
                            'total_results': len(processed_tweets),
                            'results': processed_tweets,
                            'search_params': {
                                'sort_order': sort_order,
                                'max_results': max_results
                            },
                            'searched_at': datetime.now().isoformat()
                        }
                        
                    else:
                        error_text = await response.text()
                        return {
                            'status': 'error',
                            'message': f'Erreur recherche Twitter: {response.status}',
                            'details': error_text
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche Twitter '{query}': {str(e)}")
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
            'twitter_stats': self.stats.copy(),
            'cache_info': {
                'cache_dir': str(self.cache_dir),
                'cached_files': len(list(self.cache_dir.glob("*.json")))
            },
            'api_info': {
                'bearer_token_configured': bool(self.bearer_token),
                'token_preview': f"{self.bearer_token[:20]}..." if self.bearer_token else "Non configuré",
                'base_url': self.base_url
            }
        }


# Test du module
async def test_twitter_engine():
    """
    Test complet du moteur Twitter
    """
    print("🐦 Test IA Chéries Twitter Engine")
    print("=" * 50)
    
    try:
        # Initialisation
        twitter = IaCheriesTwitterAPI()
        
        # Test 1: Recherche de tweets
        print("🔍 Test 1: Recherche 'AI artificial intelligence'...")
        search_result = await twitter.search_tweets(
            query="AI artificial intelligence",
            max_results=5,
            sort_order="relevancy"
        )
        
        if search_result['status'] == 'success':
            print(f"✅ {search_result['total_results']} tweets trouvés")
            for tweet in search_result['results'][:2]:
                print(f"   - @{tweet['author']['username']}: {tweet['text'][:60]}...")
                print(f"     Engagement: {tweet['engagement_level']} | Viral: {tweet['viral_potential']:.1f}/100")
        else:
            print(f"❌ Erreur recherche: {search_result.get('message')}")
        
        # Test 2: Tweets d'un utilisateur spécifique (exemple public)
        print("\n📱 Test 2: Tweets d'un utilisateur...")
        user_result = await twitter.get_user_tweets(
            username="elonmusk",  # Exemple d'utilisateur public
            max_results=3,
            exclude_replies=True
        )
        
        if user_result['status'] == 'success':
            print(f"✅ {user_result['total_tweets']} tweets récupérés")
            user_info = user_result['user_info']
            print(f"   Utilisateur: {user_info['name']} (@{user_info['username']})")
            print(f"   Followers: {user_info['followers_count']:,}")
            
            for tweet in user_result['tweets'][:1]:
                print(f"   - {tweet['text'][:70]}...")
                print(f"     ❤️ {tweet['like_count']} | 🔁 {tweet['retweet_count']} | 💬 {tweet['reply_count']}")
        else:
            print(f"❌ Erreur utilisateur: {user_result.get('message')}")
        
        # Statistiques finales
        print("\n📊 Statistiques:")
        stats = twitter.get_stats()
        print(f"   Tweets récupérés: {stats['twitter_stats']['tweets_fetched']}")
        print(f"   Recherches: {stats['twitter_stats']['searches_performed']}")
        print(f"   Appels API: {stats['twitter_stats']['api_calls']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return False


if __name__ == "__main__":
    # Exécution des tests
    asyncio.run(test_twitter_engine())