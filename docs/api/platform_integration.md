# Platform Integration Guide

**Ainflue Platform - Social Media & Content Platform Integration**  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Version**: 1.0  
**Date**: January 2025

## Overview

This guide covers the complete integration process for all supported social media and content platforms, enabling automatic content protection, monetization tracking, and cross-platform analytics.

## Supported Platforms

### Tier 1 Platforms (Full Integration)
- **YouTube** - Video monetization, content ID, analytics
- **Instagram** - Stories, Posts, Reels protection
- **TikTok** - Video protection, creator fund tracking
- **Spotify** - Music protection, streaming analytics
- **Twitter/X** - Content monitoring, engagement tracking
- **Facebook** - Content protection, monetization tracking

### Tier 2 Platforms (Growing Support)
- **Apple Music** - Artist protection, revenue tracking
- **SoundCloud** - Audio fingerprinting, monetization
- **Discord** - Server content monitoring
- **Twitch** - Stream protection, subscriber tracking
- **LinkedIn** - Professional content protection
- **Pinterest** - Visual content monitoring

## YouTube API Integration

### Setup Process

1. **Google Cloud Console Setup**
```bash
# Install Google API client
pip install google-api-python-client google-auth google-auth-oauthlib
```

2. **OAuth2 Configuration**
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# OAuth2 configuration
YOUTUBE_CLIENT_ID = "your_client_id.apps.googleusercontent.com"
YOUTUBE_CLIENT_SECRET = "your_client_secret"
YOUTUBE_REDIRECT_URI = "https://app.ainflue.com/auth/youtube/callback"

# Scopes required
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtubepartner",
    "https://www.googleapis.com/auth/youtube-paid-content"
]
```

3. **Authentication Flow**
```python
class YouTubeIntegration:
    def __init__(self):
        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": YOUTUBE_CLIENT_ID,
                    "client_secret": YOUTUBE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [YOUTUBE_REDIRECT_URI]
                }
            },
            scopes=YOUTUBE_SCOPES
        )
        self.flow.redirect_uri = YOUTUBE_REDIRECT_URI
    
    def get_auth_url(self, user_id):
        """Generate authorization URL"""
        auth_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=f"user_{user_id}"
        )
        return auth_url
    
    def handle_callback(self, authorization_code):
        """Handle OAuth callback"""
        self.flow.fetch_token(code=authorization_code)
        credentials = self.flow.credentials
        
        # Build YouTube service
        youtube = build('youtube', 'v3', credentials=credentials)
        return youtube, credentials
```

4. **Content Protection Setup**
```python
def setup_content_id(youtube_service, video_file_path):
    """Setup YouTube Content ID for protection"""
    try:
        # Upload reference file for Content ID
        request = youtube_service.assets().insert(
            part="snippet,metadata",
            body={
                "snippet": {
                    "title": "Ainflue Protected Content",
                    "description": "Protected by Ainflue AI System"
                },
                "metadata": {
                    "type": "VIDEO",
                    "policy": {
                        "rules": [
                            {
                                "action": "CLAIM",
                                "conditions": {
                                    "requiredTerritories": {
                                        "type": "ALLOWED",
                                        "territories": ["WORLDWIDE"]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            media_body=video_file_path
        )
        
        response = request.execute()
        return response
        
    except Exception as e:
        logger.error(f"Content ID setup failed: {str(e)}")
        raise
```

5. **Analytics Data Collection**
```python
def collect_youtube_analytics(youtube_service, channel_id, start_date, end_date):
    """Collect comprehensive YouTube analytics"""
    try:
        # Channel analytics
        channel_request = youtube_service.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained",
            dimensions="day"
        )
        
        channel_data = channel_request.execute()
        
        # Revenue analytics
        revenue_request = youtube_service.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="grossRevenue,adRevenue,redRevenue",
            dimensions="day"
        )
        
        revenue_data = revenue_request.execute()
        
        return {
            "channel_metrics": channel_data,
            "revenue_metrics": revenue_data
        }
        
    except Exception as e:
        logger.error(f"Analytics collection failed: {str(e)}")
        raise
```

## Instagram API Integration

### Setup Process

1. **Facebook Developer Account Setup**
```python
import requests

# Instagram Basic Display API
INSTAGRAM_CLIENT_ID = "your_instagram_app_id"
INSTAGRAM_CLIENT_SECRET = "your_instagram_app_secret"
INSTAGRAM_REDIRECT_URI = "https://app.ainflue.com/auth/instagram/callback"

# Required scopes
INSTAGRAM_SCOPES = [
    "user_profile",
    "user_media",
    "instagram_business_basic",
    "instagram_business_manage_comments",
    "instagram_business_manage_messages"
]
```

2. **Authentication Implementation**
```python
class InstagramIntegration:
    def __init__(self):
        self.base_url = "https://api.instagram.com"
        self.graph_url = "https://graph.instagram.com"
    
    def get_auth_url(self, user_id):
        """Generate Instagram authorization URL"""
        params = {
            "client_id": INSTAGRAM_CLIENT_ID,
            "redirect_uri": INSTAGRAM_REDIRECT_URI,
            "scope": ",".join(INSTAGRAM_SCOPES),
            "response_type": "code",
            "state": f"user_{user_id}"
        }
        
        auth_url = f"{self.base_url}/oauth/authorize?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return auth_url
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        data = {
            "client_id": INSTAGRAM_CLIENT_ID,
            "client_secret": INSTAGRAM_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": INSTAGRAM_REDIRECT_URI,
            "code": code
        }
        
        response = requests.post(f"{self.base_url}/oauth/access_token", data=data)
        return response.json()
```

3. **Content Monitoring**
```python
def monitor_instagram_content(access_token, user_id):
    """Monitor Instagram content for violations"""
    try:
        # Get user media
        media_response = requests.get(
            f"{self.graph_url}/me/media",
            params={
                "fields": "id,media_type,media_url,thumbnail_url,permalink,timestamp",
                "access_token": access_token
            }
        )
        
        media_data = media_response.json()
        
        protected_content = []
        for media in media_data.get("data", []):
            # Download media for fingerprinting
            media_content = download_media(media["media_url"])
            
            # Generate fingerprint
            fingerprint = generate_content_fingerprint(media_content, media["media_type"])
            
            # Store for protection
            protected_content.append({
                "platform": "instagram",
                "media_id": media["id"],
                "media_type": media["media_type"],
                "fingerprint": fingerprint,
                "url": media["permalink"],
                "created_at": media["timestamp"]
            })
        
        return protected_content
        
    except Exception as e:
        logger.error(f"Instagram monitoring failed: {str(e)}")
        raise
```

## TikTok API Integration

### Setup Process

1. **TikTok Developer Platform Setup**
```python
import hashlib
import hmac
import time

TIKTOK_CLIENT_KEY = "your_tiktok_client_key"
TIKTOK_CLIENT_SECRET = "your_tiktok_client_secret"
TIKTOK_REDIRECT_URI = "https://app.ainflue.com/auth/tiktok/callback"

class TikTokIntegration:
    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self.auth_url = "https://www.tiktok.com/auth/authorize/"
    
    def generate_auth_url(self, user_id):
        """Generate TikTok authorization URL"""
        csrf_token = self.generate_csrf_token()
        
        params = {
            "client_key": TIKTOK_CLIENT_KEY,
            "scope": "user.info.basic,video.list,video.upload",
            "response_type": "code",
            "redirect_uri": TIKTOK_REDIRECT_URI,
            "state": f"user_{user_id}_{csrf_token}"
        }
        
        auth_url = self.auth_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return auth_url
    
    def generate_csrf_token(self):
        """Generate CSRF token for security"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()
```

2. **Access Token Management**
```python
def get_tiktok_access_token(authorization_code):
    """Exchange code for access token"""
    url = "https://open-api.tiktok.com/oauth/access_token/"
    
    data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": TIKTOK_REDIRECT_URI
    }
    
    response = requests.post(url, json=data)
    return response.json()

def refresh_tiktok_token(refresh_token):
    """Refresh expired access token"""
    url = "https://open-api.tiktok.com/oauth/refresh_token/"
    
    data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(url, json=data)
    return response.json()
```

## Spotify API Integration

### Setup Process

1. **Spotify Developer Dashboard Setup**
```python
import base64
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
SPOTIFY_REDIRECT_URI = "https://app.ainflue.com/auth/spotify/callback"

# Required scopes for full integration
SPOTIFY_SCOPES = [
    "user-read-private",
    "user-read-email",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "streaming",
    "app-remote-control",
    "user-top-read",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "user-read-recently-played"
]
```

2. **Authentication & Content Protection**
```python
class SpotifyIntegration:
    def __init__(self):
        self.sp_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=" ".join(SPOTIFY_SCOPES)
        )
    
    def get_auth_url(self, user_id):
        """Generate Spotify authorization URL"""
        return self.sp_oauth.get_authorize_url(state=f"user_{user_id}")
    
    def handle_callback(self, code):
        """Handle Spotify OAuth callback"""
        token_info = self.sp_oauth.get_access_token(code)
        return spotipy.Spotify(auth=token_info['access_token'])
    
    def protect_artist_content(self, sp, artist_id):
        """Protect all content from an artist"""
        try:
            # Get artist albums
            albums = sp.artist_albums(artist_id, album_type='album,single', limit=50)
            
            protected_tracks = []
            for album in albums['items']:
                # Get album tracks
                tracks = sp.album_tracks(album['id'])
                
                for track in tracks['items']:
                    # Generate audio fingerprint
                    if track['preview_url']:
                        audio_data = download_audio(track['preview_url'])
                        fingerprint = generate_audio_fingerprint(audio_data)
                        
                        protected_tracks.append({
                            "platform": "spotify",
                            "track_id": track['id'],
                            "track_name": track['name'],
                            "album_name": album['name'],
                            "fingerprint": fingerprint,
                            "duration_ms": track['duration_ms'],
                            "isrc": track.get('external_ids', {}).get('isrc')
                        })
            
            return protected_tracks
            
        except Exception as e:
            logger.error(f"Spotify content protection failed: {str(e)}")
            raise
```

## Twitter/X API Integration

### Setup Process

1. **X Developer Portal Setup**
```python
import tweepy

# X API v2 credentials
X_BEARER_TOKEN = "your_bearer_token"
X_API_KEY = "your_api_key"
X_API_SECRET = "your_api_secret"
X_ACCESS_TOKEN = "your_access_token"
X_ACCESS_TOKEN_SECRET = "your_access_token_secret"

class TwitterIntegration:
    def __init__(self):
        # Initialize both API v1.1 and v2 clients
        self.client_v2 = tweepy.Client(
            bearer_token=X_BEARER_TOKEN,
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET
        )
        
        # For media upload (still requires v1.1)
        auth = tweepy.OAuth1UserHandler(
            X_API_KEY,
            X_API_SECRET,
            X_ACCESS_TOKEN,
            X_ACCESS_TOKEN_SECRET
        )
        self.api_v1 = tweepy.API(auth)
```

2. **Content Monitoring & Protection**
```python
def monitor_twitter_content(client, username):
    """Monitor Twitter content for violations"""
    try:
        # Get user by username
        user = client.get_user(username=username, user_fields=['public_metrics'])
        
        # Get user tweets
        tweets = client.get_users_tweets(
            user.data.id,
            tweet_fields=['created_at', 'attachments', 'public_metrics', 'context_annotations'],
            media_fields=['url', 'type', 'duration_ms'],
            expansions=['attachments.media_keys'],
            max_results=100
        )
        
        protected_content = []
        for tweet in tweets.data:
            # Process text content
            text_fingerprint = generate_text_fingerprint(tweet.text)
            
            content_item = {
                "platform": "twitter",
                "tweet_id": tweet.id,
                "text": tweet.text,
                "text_fingerprint": text_fingerprint,
                "created_at": tweet.created_at,
                "public_metrics": tweet.public_metrics
            }
            
            # Process media attachments
            if tweet.attachments:
                media_items = []
                for media_key in tweet.attachments.get('media_keys', []):
                    media = next((m for m in tweets.includes['media'] if m.media_key == media_key), None)
                    if media:
                        if media.type in ['photo', 'video', 'animated_gif']:
                            media_fingerprint = generate_media_fingerprint(media.url, media.type)
                            media_items.append({
                                "media_key": media_key,
                                "type": media.type,
                                "url": media.url,
                                "fingerprint": media_fingerprint
                            })
                
                content_item["media"] = media_items
            
            protected_content.append(content_item)
        
        return protected_content
        
    except Exception as e:
        logger.error(f"Twitter monitoring failed: {str(e)}")
        raise
```

## Rate Limiting & Error Handling

### Universal Rate Limit Manager
```python
import time
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimitManager:
    def __init__(self):
        self.limits = {
            'youtube': {'requests': 10000, 'window': 3600},  # per hour
            'instagram': {'requests': 200, 'window': 3600},   # per hour
            'tiktok': {'requests': 1000, 'window': 86400},    # per day
            'spotify': {'requests': 100, 'window': 60},       # per minute
            'twitter': {'requests': 300, 'window': 900}       # per 15 minutes
        }
        self.usage = defaultdict(list)
    
    def can_make_request(self, platform):
        """Check if request can be made within rate limits"""
        now = datetime.now()
        window = self.limits[platform]['window']
        limit = self.limits[platform]['requests']
        
        # Remove old entries
        cutoff = now - timedelta(seconds=window)
        self.usage[platform] = [req_time for req_time in self.usage[platform] if req_time > cutoff]
        
        return len(self.usage[platform]) < limit
    
    def record_request(self, platform):
        """Record a request made"""
        self.usage[platform].append(datetime.now())
    
    def wait_time(self, platform):
        """Get wait time until next request can be made"""
        if self.can_make_request(platform):
            return 0
        
        window = self.limits[platform]['window']
        oldest_request = min(self.usage[platform])
        wait_until = oldest_request + timedelta(seconds=window)
        
        return (wait_until - datetime.now()).total_seconds()
```

### Error Handling Strategies
```python
import backoff
import requests

@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.RequestException, ConnectionError),
    max_tries=3,
    max_time=300
)
def robust_api_call(platform, endpoint, method='GET', **kwargs):
    """Make robust API calls with retry logic"""
    rate_limiter = RateLimitManager()
    
    # Check rate limits
    if not rate_limiter.can_make_request(platform):
        wait_time = rate_limiter.wait_time(platform)
        logger.warning(f"Rate limit reached for {platform}. Waiting {wait_time} seconds.")
        time.sleep(wait_time)
    
    try:
        response = requests.request(method, endpoint, **kwargs)
        rate_limiter.record_request(platform)
        
        if response.status_code == 429:  # Rate limited
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited by {platform}. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            raise requests.exceptions.RequestException("Rate limited")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API call to {platform} failed: {str(e)}")
        raise
```

## Webhooks Implementation

### Universal Webhook Handler
```python
from fastapi import FastAPI, HTTPException, Request
import hmac
import hashlib

app = FastAPI()

@app.post("/webhooks/{platform}")
async def handle_platform_webhook(platform: str, request: Request):
    """Handle webhooks from various platforms"""
    try:
        payload = await request.body()
        headers = request.headers
        
        # Verify webhook signature
        if not verify_webhook_signature(platform, payload, headers):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = await request.json()
        
        # Route to appropriate handler
        handlers = {
            'youtube': handle_youtube_webhook,
            'instagram': handle_instagram_webhook,
            'tiktok': handle_tiktok_webhook,
            'spotify': handle_spotify_webhook,
            'twitter': handle_twitter_webhook
        }
        
        if platform in handlers:
            await handlers[platform](webhook_data)
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")
            
    except Exception as e:
        logger.error(f"Webhook handling failed for {platform}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def verify_webhook_signature(platform, payload, headers):
    """Verify webhook signature for security"""
    signature_header = {
        'youtube': 'X-Goog-Signature',
        'instagram': 'X-Hub-Signature-256',
        'tiktok': 'X-TikTok-Signature',
        'spotify': 'X-Spotify-Signature',
        'twitter': 'X-Twitter-Webhooks-Signature'
    }.get(platform)
    
    if not signature_header or signature_header not in headers:
        return False
    
    expected_signature = headers[signature_header]
    webhook_secret = get_webhook_secret(platform)
    
    computed_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, f"sha256={computed_signature}")
```

## Configuration Management

### Environment Configuration
```bash
# .env.production
# Platform API Keys
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret

# Webhook Secrets
YOUTUBE_WEBHOOK_SECRET=your_youtube_webhook_secret
INSTAGRAM_WEBHOOK_SECRET=your_instagram_webhook_secret
TIKTOK_WEBHOOK_SECRET=your_tiktok_webhook_secret
SPOTIFY_WEBHOOK_SECRET=your_spotify_webhook_secret
TWITTER_WEBHOOK_SECRET=your_twitter_webhook_secret

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ainflue
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
```

## Copyright & License

**© 2025 Fahed Mlaiel (mlaiel@live.de). All rights reserved.**

This integration guide and all associated code are protected by copyright and other intellectual property laws. Unauthorized use, reproduction, or distribution is strictly prohibited.

**Contact**: mlaiel@live.de  
**Documentation**: https://docs.ainflue.com/integrations  
**Support**: https://support.ainflue.com