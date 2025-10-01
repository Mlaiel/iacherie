#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 IA CHÉRIES FREESOUND ENGINE
================================

Module d'intégration avec l'API Freesound pour :
- Recherche de sons et musiques libres
- Téléchargement d'effets audio
- Analyse de métadonnées sonores
- Génération de playlists thématiques

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

class IaCheriesFreesoundAPI:
    """
    🎵 Moteur Freesound pour IA Chéries
    
    Fonctionnalités:
    - Recherche intelligente de sons
    - Téléchargement automatique
    - Filtrage par qualité/durée/licence
    - Cache local optimisé
    - Analytics d'utilisation
    """
    
    def __init__(self, api_key: str = None, client_id: str = None):
        """
        Initialise le moteur Freesound
        
        Args:
            api_key (str): Clé API Freesound
            client_id (str): ID client Freesound
        """
        self.api_key = api_key or os.getenv('FREESOUND_API_KEY')
        self.client_id = client_id or os.getenv('FREESOUND_CLIENT_ID')
        
        if not self.api_key:
            raise ValueError("❌ Clé API Freesound manquante!")
            
        # Configuration API
        self.base_url = "https://freesound.org/apiv2"
        self.headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'IA Chéries-Platform/2.0'
        }
        
        # Cache et stockage
        self.cache_dir = Path("cache/freesound")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistiques
        self.stats = {
            'searches': 0,
            'downloads': 0,
            'cache_hits': 0,
            'api_calls': 0,
            'total_sounds': 0
        }
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🎵 Freesound Engine initialisé avec succès!")

    async def search_sounds(
        self,
        query: str,
        filter_params: Dict = None,
        page: int = 1,
        page_size: int = 15,
        sort: str = "score"
    ) -> Dict[str, Any]:
        """
        Recherche de sons avec filtres avancés
        
        Args:
            query (str): Terme de recherche
            filter_params (dict): Filtres (durée, licence, qualité, etc.)
            page (int): Page de résultats
            page_size (int): Taille de page (max 150)
            sort (str): Tri (score, downloads, rating, duration)
            
        Returns:
            dict: Résultats de recherche avec métadonnées
        """
        try:
            self.stats['searches'] += 1
            
            # Paramètres de base
            params = {
                'query': query,
                'page': page,
                'page_size': min(page_size, 150),
                'sort': sort,
                'fields': 'id,name,description,url,previews,download,filesize,type,duration,bitdepth,bitrate,samplerate,username,license,tags,num_downloads,avg_rating,created'
            }
            
            # Filtres avancés
            if filter_params:
                # Durée (en secondes)
                if 'min_duration' in filter_params:
                    params['filter'] = f"duration:[{filter_params['min_duration']} TO *]"
                if 'max_duration' in filter_params:
                    current_filter = params.get('filter', '')
                    if current_filter:
                        params['filter'] = f"{current_filter} duration:[* TO {filter_params['max_duration']}]"
                    else:
                        params['filter'] = f"duration:[* TO {filter_params['max_duration']}]"
                
                # Licence
                if 'license' in filter_params:
                    license_filter = f"license:{filter_params['license']}"
                    if 'filter' in params:
                        params['filter'] += f" {license_filter}"
                    else:
                        params['filter'] = license_filter
                
                # Format
                if 'type' in filter_params:
                    type_filter = f"type:{filter_params['type']}"
                    if 'filter' in params:
                        params['filter'] += f" {type_filter}"
                    else:
                        params['filter'] = type_filter
            
            # Requête API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search/text/",
                    headers=self.headers,
                    params=params
                ) as response:
                    
                    self.stats['api_calls'] += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Enrichissement des résultats
                        enriched_results = []
                        for sound in data.get('results', []):
                            enriched_sound = await self._enrich_sound_data(sound)
                            enriched_results.append(enriched_sound)
                        
                        result = {
                            'status': 'success',
                            'query': query,
                            'total_count': data.get('count', 0),
                            'page': page,
                            'page_size': page_size,
                            'total_pages': (data.get('count', 0) + page_size - 1) // page_size,
                            'sounds': enriched_results,
                            'filters_applied': filter_params or {},
                            'search_time': datetime.now().isoformat()
                        }
                        
                        self.logger.info(f"🔍 Recherche '{query}': {len(enriched_results)} sons trouvés")
                        return result
                        
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Erreur API Freesound: {response.status} - {error_text}")
                        return {
                            'status': 'error',
                            'message': f'Erreur API: {response.status}',
                            'details': error_text
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche Freesound: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur de recherche: {str(e)}'
            }

    async def _enrich_sound_data(self, sound: Dict) -> Dict:
        """
        Enrichit les données d'un son avec des métadonnées utiles
        
        Args:
            sound (dict): Données de base du son
            
        Returns:
            dict: Données enrichies
        """
        try:
            enriched = sound.copy()
            
            # URL de preview sécurisée
            if 'previews' in sound and sound['previews']:
                preview_url = sound['previews'].get('preview-hq-mp3')
                if not preview_url:
                    preview_url = sound['previews'].get('preview-lq-mp3')
                enriched['preview_url'] = preview_url
            
            # Taille lisible
            if 'filesize' in sound:
                enriched['filesize_human'] = self._format_filesize(sound['filesize'])
            
            # Durée lisible
            if 'duration' in sound:
                enriched['duration_human'] = self._format_duration(sound['duration'])
            
            # Score de qualité (basé sur rating, downloads, bitrate)
            quality_score = self._calculate_quality_score(sound)
            enriched['quality_score'] = quality_score
            enriched['quality_level'] = self._get_quality_level(quality_score)
            
            # Catégorisation automatique
            enriched['auto_category'] = self._categorize_sound(sound)
            
            # URL de téléchargement direct
            if 'id' in sound:
                enriched['download_endpoint'] = f"/api/audio/freesound/download/{sound['id']}"
            
            return enriched
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur enrichissement son {sound.get('id', 'unknown')}: {e}")
            return sound

    def _calculate_quality_score(self, sound: Dict) -> float:
        """
        Calcule un score de qualité pour un son
        
        Args:
            sound (dict): Données du son
            
        Returns:
            float: Score de 0 à 100
        """
        score = 0.0
        
        # Rating utilisateur (30% du score)
        if 'avg_rating' in sound and sound['avg_rating']:
            score += (sound['avg_rating'] / 5.0) * 30
        
        # Nombre de téléchargements (25% du score)
        if 'num_downloads' in sound and sound['num_downloads']:
            downloads_score = min(sound['num_downloads'] / 1000, 1.0) * 25
            score += downloads_score
        
        # Qualité audio technique (25% du score)
        if 'bitrate' in sound and sound['bitrate']:
            # 320kbps = score parfait pour cette partie
            bitrate_score = min(sound['bitrate'] / 320000, 1.0) * 25
            score += bitrate_score
        
        # Complétude des métadonnées (20% du score)
        metadata_fields = ['name', 'description', 'tags', 'license']
        filled_fields = sum(1 for field in metadata_fields if sound.get(field))
        metadata_score = (filled_fields / len(metadata_fields)) * 20
        score += metadata_score
        
        return round(score, 1)

    def _get_quality_level(self, score: float) -> str:
        """
        Détermine le niveau de qualité basé sur le score
        
        Args:
            score (float): Score de qualité
            
        Returns:
            str: Niveau de qualité
        """
        if score >= 80:
            return "Excellente"
        elif score >= 60:
            return "Bonne"
        elif score >= 40:
            return "Correcte"
        elif score >= 20:
            return "Basique"
        else:
            return "Faible"

    def _categorize_sound(self, sound: Dict) -> str:
        """
        Catégorise automatiquement un son
        
        Args:
            sound (dict): Données du son
            
        Returns:
            str: Catégorie détectée
        """
        name = (sound.get('name', '') + ' ' + sound.get('description', '')).lower()
        tags = ' '.join(sound.get('tags', [])).lower()
        text = name + ' ' + tags
        
        # Catégories musicales
        if any(word in text for word in ['music', 'song', 'melody', 'chord', 'guitar', 'piano', 'drum', 'bass']):
            return "Musique"
        
        # Effets sonores
        elif any(word in text for word in ['effect', 'fx', 'sound-effect', 'whoosh', 'explosion', 'bang']):
            return "Effets"
        
        # Voix
        elif any(word in text for word in ['voice', 'speech', 'talk', 'word', 'human', 'vocal']):
            return "Voix"
        
        # Nature
        elif any(word in text for word in ['nature', 'bird', 'water', 'wind', 'rain', 'ocean', 'forest']):
            return "Nature"
        
        # Transport
        elif any(word in text for word in ['car', 'train', 'plane', 'engine', 'motor', 'vehicle']):
            return "Transport"
        
        # Ambiances
        elif any(word in text for word in ['ambient', 'atmosphere', 'room', 'space', 'background']):
            return "Ambiance"
        
        else:
            return "Autre"

    async def download_sound(self, sound_id: int, quality: str = "hq") -> Dict[str, Any]:
        """
        Télécharge un son depuis Freesound
        
        Args:
            sound_id (int): ID du son à télécharger
            quality (str): Qualité souhaitée (hq, lq, original)
            
        Returns:
            dict: Informations sur le téléchargement
        """
        try:
            self.stats['downloads'] += 1
            
            # Vérifier le cache local
            cache_file = self.cache_dir / f"sound_{sound_id}_{quality}.mp3"
            if cache_file.exists():
                self.stats['cache_hits'] += 1
                return {
                    'status': 'success',
                    'source': 'cache',
                    'file_path': str(cache_file),
                    'sound_id': sound_id,
                    'quality': quality,
                    'size': cache_file.stat().st_size
                }
            
            # Obtenir les infos du son
            async with aiohttp.ClientSession() as session:
                # Récupérer les métadonnées
                async with session.get(
                    f"{self.base_url}/sounds/{sound_id}/",
                    headers=self.headers
                ) as response:
                    
                    if response.status != 200:
                        return {
                            'status': 'error',
                            'message': f'Son {sound_id} introuvable'
                        }
                    
                    sound_info = await response.json()
                
                # Déterminer l'URL de téléchargement
                download_url = None
                if quality == "original" and 'download' in sound_info:
                    download_url = sound_info['download']
                elif 'previews' in sound_info:
                    if quality == "hq" and 'preview-hq-mp3' in sound_info['previews']:
                        download_url = sound_info['previews']['preview-hq-mp3']
                    elif 'preview-lq-mp3' in sound_info['previews']:
                        download_url = sound_info['previews']['preview-lq-mp3']
                
                if not download_url:
                    return {
                        'status': 'error',
                        'message': 'URL de téléchargement non disponible'
                    }
                
                # Télécharger le fichier
                async with session.get(download_url) as download_response:
                    if download_response.status == 200:
                        # Sauvegarder en cache
                        with open(cache_file, 'wb') as f:
                            f.write(await download_response.read())
                        
                        self.logger.info(f"📥 Son {sound_id} téléchargé: {cache_file.name}")
                        
                        return {
                            'status': 'success',
                            'source': 'download',
                            'file_path': str(cache_file),
                            'sound_id': sound_id,
                            'quality': quality,
                            'size': cache_file.stat().st_size,
                            'metadata': {
                                'name': sound_info.get('name'),
                                'duration': sound_info.get('duration'),
                                'license': sound_info.get('license'),
                                'username': sound_info.get('username')
                            }
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Erreur téléchargement: {download_response.status}'
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur téléchargement son {sound_id}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur de téléchargement: {str(e)}'
            }

    async def get_user_sounds(self, username: str, limit: int = 50) -> Dict[str, Any]:
        """
        Récupère les sons d'un utilisateur spécifique
        
        Args:
            username (str): Nom d'utilisateur Freesound
            limit (int): Limite de résultats
            
        Returns:
            dict: Sons de l'utilisateur
        """
        try:
            params = {
                'fields': 'id,name,description,url,previews,duration,license,tags,num_downloads,avg_rating',
                'page_size': min(limit, 150)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/{username}/sounds/",
                    headers=self.headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            'status': 'success',
                            'username': username,
                            'total_sounds': data.get('count', 0),
                            'sounds': data.get('results', []),
                            'retrieved_at': datetime.now().isoformat()
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'Utilisateur {username} non trouvé'
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération utilisateur {username}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur: {str(e)}'
            }

    async def create_playlist(
        self,
        theme: str,
        duration_target: int = 300,
        filters: Dict = None
    ) -> Dict[str, Any]:
        """
        Crée une playlist thématique automatique
        
        Args:
            theme (str): Thème de la playlist
            duration_target (int): Durée cible en secondes
            filters (dict): Filtres supplémentaires
            
        Returns:
            dict: Playlist générée
        """
        try:
            # Recherche initiale
            search_result = await self.search_sounds(
                query=theme,
                filter_params=filters or {},
                page_size=50,
                sort="rating"
            )
            
            if search_result['status'] != 'success':
                return search_result
            
            sounds = search_result['sounds']
            if not sounds:
                return {
                    'status': 'error',
                    'message': 'Aucun son trouvé pour ce thème'
                }
            
            # Sélection intelligente pour atteindre la durée cible
            selected_sounds = []
            total_duration = 0
            
            # Trier par score de qualité
            sorted_sounds = sorted(sounds, key=lambda x: x.get('quality_score', 0), reverse=True)
            
            for sound in sorted_sounds:
                if total_duration >= duration_target:
                    break
                
                sound_duration = sound.get('duration', 10)  # Défaut 10s si pas d'info
                
                # Éviter les sons trop longs qui dépasseraient largement la cible
                if sound_duration > (duration_target - total_duration) + 30:
                    continue
                
                selected_sounds.append(sound)
                total_duration += sound_duration
            
            return {
                'status': 'success',
                'playlist': {
                    'theme': theme,
                    'total_sounds': len(selected_sounds),
                    'total_duration': total_duration,
                    'duration_human': self._format_duration(total_duration),
                    'target_duration': duration_target,
                    'sounds': selected_sounds,
                    'created_at': datetime.now().isoformat(),
                    'average_quality': sum(s.get('quality_score', 0) for s in selected_sounds) / len(selected_sounds) if selected_sounds else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création playlist '{theme}': {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur création playlist: {str(e)}'
            }

    def _format_filesize(self, bytes_size: int) -> str:
        """Formate une taille en bytes en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    def _format_duration(self, seconds: float) -> str:
        """Formate une durée en secondes en format MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation
        
        Returns:
            dict: Statistiques complètes
        """
        return {
            'freesound_stats': self.stats.copy(),
            'cache_info': {
                'cache_dir': str(self.cache_dir),
                'cached_files': len(list(self.cache_dir.glob("*.mp3"))),
                'cache_size': sum(f.stat().st_size for f in self.cache_dir.glob("*.mp3"))
            },
            'api_info': {
                'api_key_configured': bool(self.api_key),
                'client_id_configured': bool(self.client_id),
                'base_url': self.base_url
            }
        }

    async def clear_cache(self, older_than_days: int = 7) -> Dict[str, Any]:
        """
        Nettoie le cache des fichiers anciens
        
        Args:
            older_than_days (int): Supprimer fichiers plus anciens que X jours
            
        Returns:
            dict: Résultat du nettoyage
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            deleted_count = 0
            deleted_size = 0
            
            for cache_file in self.cache_dir.glob("*.mp3"):
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_date:
                    deleted_size += cache_file.stat().st_size
                    cache_file.unlink()
                    deleted_count += 1
            
            return {
                'status': 'success',
                'deleted_files': deleted_count,
                'freed_space': self._format_filesize(deleted_size),
                'older_than_days': older_than_days
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erreur nettoyage cache: {str(e)}'
            }


# Test du module
async def test_freesound_engine():
    """
    Test complet du moteur Freesound
    """
    print("🎵 Test IA Chéries Freesound Engine")
    print("=" * 50)
    
    try:
        # Initialisation
        engine = IaCheriesFreesoundAPI()
        
        # Test 1: Recherche de base
        print("📝 Test 1: Recherche de sons...")
        results = await engine.search_sounds(
            query="nature forest birds",
            filter_params={
                'max_duration': 30,
                'license': 'Creative Commons 0'
            },
            page_size=5
        )
        
        if results['status'] == 'success':
            print(f"✅ {len(results['sounds'])} sons trouvés")
            for sound in results['sounds'][:2]:
                print(f"   - {sound['name']} ({sound['duration_human']}) - Qualité: {sound['quality_level']}")
        else:
            print(f"❌ Erreur recherche: {results.get('message')}")
        
        # Test 2: Téléchargement (si des résultats)
        if results['status'] == 'success' and results['sounds']:
            print("\n📥 Test 2: Téléchargement d'un son...")
            first_sound = results['sounds'][0]
            download_result = await engine.download_sound(first_sound['id'], quality='hq')
            
            if download_result['status'] == 'success':
                print(f"✅ Téléchargement réussi: {download_result['file_path']}")
                print(f"   Taille: {engine._format_filesize(download_result['size'])}")
            else:
                print(f"❌ Erreur téléchargement: {download_result.get('message')}")
        
        # Test 3: Création de playlist
        print("\n🎵 Test 3: Création de playlist...")
        playlist = await engine.create_playlist(
            theme="relaxing ambient",
            duration_target=120,
            filters={'max_duration': 60}
        )
        
        if playlist['status'] == 'success':
            pl_info = playlist['playlist']
            print(f"✅ Playlist créée: {pl_info['total_sounds']} sons, {pl_info['duration_human']}")
            print(f"   Qualité moyenne: {pl_info['average_quality']:.1f}/100")
        else:
            print(f"❌ Erreur playlist: {playlist.get('message')}")
        
        # Statistiques finales
        print("\n📊 Statistiques:")
        stats = engine.get_stats()
        print(f"   Recherches: {stats['freesound_stats']['searches']}")
        print(f"   Téléchargements: {stats['freesound_stats']['downloads']}")
        print(f"   Appels API: {stats['freesound_stats']['api_calls']}")
        print(f"   Fichiers en cache: {stats['cache_info']['cached_files']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return False


if __name__ == "__main__":
    # Exécution des tests
    asyncio.run(test_freesound_engine())