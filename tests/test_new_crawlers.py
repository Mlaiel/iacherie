# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test New Crawlers
Basic tests for the newly added crawler modules.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime

from crawlers import (
    SpotifyCrawler, AppleMusicCrawler, SoundCloudCrawler, DeezerCrawler, YouTubeMusicCrawler,
    BeRealCrawler, TwitchCrawler, ThreadsCrawler,
    RedditCrawler, DiscordCrawler, FacebookCrawler,
    PatreonCrawler, SubstackCrawler
)


class TestNewCrawlers:
    """Test cases for new crawler modules"""    @pytest.mark.asyncio
    async def test_spotify_crawler(self):
        """Test Spotify crawler basic functionality"""        async with SpotifyCrawler() as crawler:
            results = await crawler.search_tracks(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                track = results[0]
                assert hasattr(track, 'track_id')
                assert hasattr(track, 'name')
                assert hasattr(track, 'artist')
                assert isinstance(track.similarity_score, float)

    @pytest.mark.asyncio
    async def test_apple_music_crawler(self):
        """Test Apple Music crawler basic functionality"""        async with AppleMusicCrawler() as crawler:
            results = await crawler.search_tracks(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                track = results[0]
                assert hasattr(track, 'track_id')
                assert hasattr(track, 'name')
                assert hasattr(track, 'artist_name')

    @pytest.mark.asyncio
    async def test_soundcloud_crawler(self):
        """Test SoundCloud crawler basic functionality"""        async with SoundCloudCrawler() as crawler:
            results = await crawler.search_tracks(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                track = results[0]
                assert hasattr(track, 'track_id')
                assert hasattr(track, 'title')
                assert hasattr(track, 'user')

    @pytest.mark.asyncio
    async def test_bereal_crawler(self):
        """Test BeReal crawler basic functionality"""        async with BeRealCrawler() as crawler:
            results = await crawler.search_content(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                post = results[0]
                assert hasattr(post, 'post_id')
                assert hasattr(post, 'username')
                assert hasattr(post, 'primary_photo_url')

    @pytest.mark.asyncio
    async def test_twitch_crawler_streams(self):
        """Test Twitch crawler stream search functionality"""        async with TwitchCrawler() as crawler:
            results = await crawler.search_streams(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                stream = results[0]
                assert hasattr(stream, 'stream_id')
                assert hasattr(stream, 'user_login')
                assert hasattr(stream, 'title')

    @pytest.mark.asyncio
    async def test_reddit_crawler(self):
        """Test Reddit crawler basic functionality"""        async with RedditCrawler() as crawler:
            results = await crawler.search_content(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                post = results[0]
                assert hasattr(post, 'post_id')
                assert hasattr(post, 'title')
                assert hasattr(post, 'subreddit')

    @pytest.mark.asyncio
    async def test_facebook_crawler(self):
        """Test Facebook crawler basic functionality"""        async with FacebookCrawler() as crawler:
            results = await crawler.search_content(
                content_id="test_content",
                fingerprint="test_fingerprint",
                similarity_threshold=0.8
            )
            
            assert isinstance(results, list)
            if results:
                post = results[0]
                assert hasattr(post, 'post_id')
                assert hasattr(post, 'message')
                assert hasattr(post, 'author_name')


if __name__ == "__main__":
    # Simple test runner for development
    import asyncio
    
    async def run_simple_tests():
        """Run simple tests without pytest"""        print("Testing new crawlers...")
        
        # Test Spotify
        async with SpotifyCrawler() as crawler:
            results = await crawler.search_tracks("test", "test", 0.8)
            print(f"Spotify: Found {len(results)} results")
        
        # Test Twitch
        async with TwitchCrawler() as crawler:
            results = await crawler.search_streams("test", "test", 0.8)
            print(f"Twitch streams: Found {len(results)} results")
        
        # Test Reddit
        async with RedditCrawler() as crawler:
            results = await crawler.search_content("test", "test", 0.8)
            print(f"Reddit: Found {len(results)} results")
        
        # Test Facebook  
        async with FacebookCrawler() as crawler:
            results = await crawler.search_content("test", "test", 0.8)
            print(f"Facebook: Found {len(results)} results")
        
        # Test Substack
        async with SubstackCrawler() as crawler:
            results = await crawler.search_content("test", "test", 0.8)
            print(f"Substack: Found {len(results)} results")
        
        print("All basic tests passed!")
    
    asyncio.run(run_simple_tests())